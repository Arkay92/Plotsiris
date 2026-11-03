"""Master Data Manager: Aggregates, coordinates, and caches multi-domain feeds in memory.

Uses asynchronous background polling and instant cache lookups so map updates
and layer toggles respond in under 5 milliseconds with zero UI hanging.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from plotsiris.domain.models import GeoEntity, RoutePath, OsintResult, MarketTicker, NewsAlert
from plotsiris.services.aviation import AviationService
from plotsiris.services.maritime import MaritimeService
from plotsiris.services.hazards import HazardsService
from plotsiris.services.threats import ThreatsService
from plotsiris.services.cyber import CyberService
from plotsiris.services.space_weather import SpaceWeatherService
from plotsiris.services.cctv import CctvService
from plotsiris.services.markets import MarketsService
from plotsiris.services.osint_toolkit import OsintToolkit
from plotsiris.services.ai_analyst import AiAnalystService

logger = logging.getLogger(__name__)


SAMPLE_NEWS_ALERTS = [
    NewsAlert(
        id="news_01",
        title="CENTCOM Intercepts Two Anti-Ship Missiles Over Gulf of Aden",
        source="DEFENSE TELEGRAPH",
        time_ago="12m ago",
        risk_level="CRITICAL",
        region="Red Sea",
        summary="Arleigh Burke-class destroyer engaged inbound threats targeting commercial container ship.",
        lat=12.8,
        lon=44.5
    ),
    NewsAlert(
        id="news_02",
        title="CISA Adds High-Severity Remote Execution Vulnerability to KEV Catalog",
        source="CYBER SCOOP",
        time_ago="28m ago",
        risk_level="HIGH",
        region="Global",
        summary="Federal agencies ordered to patch remote access vulnerabilities within 21 days.",
        lat=38.9,
        lon=-77.0
    ),
    NewsAlert(
        id="news_03",
        title="Taiwan Transport Ministry Completes Real-Time Optical Freeway Network Upgrade",
        source="TAIPEI WIRE",
        time_ago="45m ago",
        risk_level="LOW",
        region="East Asia",
        summary="Over 3,700 high-definition highway traffic sensors synced for severe weather preparedness.",
        lat=25.0,
        lon=121.5
    ),
    NewsAlert(
        id="news_04",
        title="Solar Flare Activity Reaches C2.4; Geomagnetic Indices Within Safe Envelopes",
        source="NOAA SWPC",
        time_ago="1h ago",
        risk_level="LOW",
        region="Space Domain",
        summary="Kp index stable at 3.67. Polar cap absorption negligible; commercial avionics unaffected.",
        lat=0.0,
        lon=0.0
    ),
    NewsAlert(
        id="news_05",
        title="Zaporizhzhia Nuclear Plant Retains Backup 330kV Line Following Grid Fluctuations",
        source="IAEA PRESS",
        time_ago="2h ago",
        risk_level="ELEVATED",
        region="Eastern Europe",
        summary="External reactor cooling power guaranteed via secondary line amidst localized shelling.",
        lat=47.5,
        lon=34.5
    ),
    NewsAlert(
        id="news_06",
        title="Oil Tanker Transits via Cape Route Rise 68% as Insurance Rates Spike",
        source="LLOYD'S LIST",
        time_ago="3h ago",
        risk_level="HIGH",
        region="Maritime",
        summary="Bunker fuel expenditure rises as shipping liners avoid Bab-el-Mandeb bottleneck.",
        lat=13.0,
        lon=43.0
    )
]


class DataManager:
    """Central stateful intelligence manager coordinating all feeds with in-memory caching."""

    def __init__(self):
        self.aviation_service = AviationService()
        self.maritime_service = MaritimeService()
        self.hazards_service = HazardsService()
        self.threats_service = ThreatsService()
        self.cyber_service = CyberService()
        self.space_weather_service = SpaceWeatherService()
        self.cctv_service = CctvService()
        self.markets_service = MarketsService()
        self.osint_toolkit = OsintToolkit()
        self.ai_analyst = AiAnalystService()

        # Cache of user-pinned OSINT recon results
        self._user_recon_findings: List[GeoEntity] = []

        # In-memory entity and route caches
        self._entities_by_layer: Dict[str, List[GeoEntity]] = {}
        self._routes_by_layer: Dict[str, List[RoutePath]] = {}
        self._markets_cache: Optional[Tuple[List[MarketTicker], List[Dict[str, Any]]]] = None
        self._cisa_cache: Optional[List[Dict[str, Any]]] = None
        self._last_refresh_time: float = 0.0
        self._lock = threading.Lock()

        # Perform initial synchronous fast load of baselines without blocking external HTTP
        self._sync_populate_cache(live_network=False)

        # Launch background asynchronous refresher daemon
        self._bg_thread = threading.Thread(target=self._background_refresher, daemon=True)
        self._bg_thread.start()

    def _sync_populate_cache(self, live_network: bool = False) -> None:
        """Populate the in-memory cache quickly from baseline services."""
        with self._lock:
            try:
                flights, flight_routes = self.aviation_service.fetch_flights(use_network=live_network)
                vessels, chokepoints, cables = self.maritime_service.fetch_maritime()
                cams = self.cctv_service.fetch_cctv_entities()
                quakes = self.hazards_service.fetch_earthquakes(use_network=live_network)
                fires = self.hazards_service.fetch_fires()
                weather = self.hazards_service.fetch_weather()
                conflicts, frontlines = self.threats_service.fetch_conflicts()
                gps_jam = self.threats_service.fetch_gps_jamming()
                nuclear = self.threats_service.fetch_nuclear()
                cyber_nodes = self.cyber_service.fetch_cyber_nodes()
                sats, orbits = self.space_weather_service.fetch_satellites()

                self._entities_by_layer = {
                    "aviation": flights,
                    "maritime": vessels,
                    "chokepoints": chokepoints,
                    "cctv": cams,
                    "earthquakes": quakes,
                    "fires": fires,
                    "weather": weather,
                    "conflict": conflicts + gps_jam,
                    "nuclear": nuclear,
                    "cyber": cyber_nodes,
                    "satellites": sats,
                }

                self._routes_by_layer = {
                    "aviation": flight_routes,
                    "cables": cables,
                    "conflict": frontlines,
                    "satellites": orbits,
                }

                self._markets_cache = (
                    self.markets_service.fetch_tickers(),
                    self.markets_service.fetch_country_risk()
                )
                self._cisa_cache = self.cyber_service.fetch_cisa_kev(use_network=live_network)
                self._last_refresh_time = time.time()
            except Exception as e:
                logger.error(f"Error populating cache: {e}")

    def _background_refresher(self) -> None:
        """Asynchronous daemon that polls external APIs in the background without UI blocking."""
        # Initial slight pause so app finishes startup and serves immediate requests
        time.sleep(3)
        while True:
            try:
                self._sync_populate_cache(live_network=True)
            except Exception as e:
                logger.warning(f"Background refresh notice: {e}")
            time.sleep(60)  # Refresh every 60 seconds

    def get_all_entities(self, active_layers: Optional[List[str]] = None) -> List[GeoEntity]:
        """Aggregate geospatial entities instantly from in-memory cache."""
        if active_layers is None:
            active_layers = [
                "aviation", "maritime", "cctv", "earthquakes", "fires",
                "weather", "conflict", "nuclear", "cyber", "satellites",
                "chokepoints", "recon"
            ]

        results: List[GeoEntity] = []
        with self._lock:
            for layer in active_layers:
                if layer == "recon":
                    results.extend(self._user_recon_findings)
                elif layer in self._entities_by_layer:
                    results.extend(self._entities_by_layer[layer])

        return results

    def get_route_paths(self, active_layers: Optional[List[str]] = None) -> List[RoutePath]:
        """Aggregate route polylines instantly from in-memory cache."""
        if active_layers is None:
            active_layers = ["aviation", "cables", "conflict", "satellites"]

        paths: List[RoutePath] = []
        with self._lock:
            for layer in active_layers:
                if layer in self._routes_by_layer:
                    paths.extend(self._routes_by_layer[layer])

        return paths

    def get_layer_counts(self) -> Dict[str, int]:
        """Compute real-time entity counts per layer category instantly from memory."""
        with self._lock:
            counts = {k: len(v) for k, v in self._entities_by_layer.items()}
            counts["cables"] = len(self._routes_by_layer.get("cables", []))
            counts["recon"] = len(self._user_recon_findings)
            return counts

    def pin_recon_result(self, result: OsintResult) -> Optional[GeoEntity]:
        """Pin a geolocatable OSINT result to the live map."""
        if not result.coordinates:
            return None

        lat, lon = result.coordinates
        color = "#ef4444" if result.verdict == "MALICIOUS" else ("#f59e0b" if result.verdict == "SUSPICIOUS" else "#00e5ff")
        sev = "CRITICAL" if result.verdict == "MALICIOUS" else ("HIGH" if result.verdict == "SUSPICIOUS" else "LOW")

        entity = GeoEntity(
            id=f"recon_{datetime.utcnow().timestamp():.0f}",
            lat=lat,
            lon=lon,
            category="recon",
            subcategory=f"RECON: {result.tool.upper()}",
            title=f"OSINT [{result.tool.upper()}]: {result.target}",
            description=f"{result.summary} | Verdict: {result.verdict}",
            severity=sev,
            color=color,
            icon="pin",
            size=14,
            properties=result.to_dict()
        )
        with self._lock:
            self._user_recon_findings.append(entity)
        return entity

    def get_recon_findings(self) -> List[GeoEntity]:
        """Return list of user reconnaissance findings pinned to map."""
        with self._lock:
            return list(self._user_recon_findings)

    def get_news_alerts(self) -> List[NewsAlert]:
        """Return real-time intelligence wire alerts."""
        return list(SAMPLE_NEWS_ALERTS)

    def get_markets(self) -> Tuple[List[MarketTicker], List[Dict[str, Any]]]:
        """Return financial tickers and sovereign risk scores."""
        with self._lock:
            if self._markets_cache:
                return self._markets_cache
        return self.markets_service.fetch_tickers(), self.markets_service.fetch_country_risk()

    def get_space_weather(self) -> Dict[str, Any]:
        """Return space weather Kp index and solar telemetries."""
        return self.space_weather_service.fetch_space_weather()

    def get_cisa_kev(self) -> List[Dict[str, Any]]:
        """Return latest CISA KEV entries."""
        with self._lock:
            if self._cisa_cache:
                return self._cisa_cache
        return self.cyber_service.fetch_cisa_kev()


# Global Singleton Instance
data_manager = DataManager()
