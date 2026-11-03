"""Master Data Manager: Aggregates, coordinates, and caches multi-domain feeds."""

from __future__ import annotations

import logging
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


# Curated Live Intelligence News Stream
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
    """Central stateful intelligence manager coordinating all feeds."""

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

    def get_all_entities(self, active_layers: Optional[List[str]] = None) -> List[GeoEntity]:
        """Aggregate geospatial entities matching active layer toggles."""
        if active_layers is None:
            active_layers = [
                "aviation", "maritime", "cctv", "earthquakes", "fires",
                "weather", "conflict", "nuclear", "cyber", "satellites",
                "chokepoints", "recon"
            ]

        results: List[GeoEntity] = []

        if "aviation" in active_layers:
            flights, _ = self.aviation_service.fetch_flights()
            results.extend(flights)

        if "maritime" in active_layers:
            vessels, chokepoints, _ = self.maritime_service.fetch_maritime()
            results.extend(vessels)

        if "chokepoints" in active_layers:
            _, chokepoints, _ = self.maritime_service.fetch_maritime()
            results.extend(chokepoints)

        if "cctv" in active_layers:
            results.extend(self.cctv_service.fetch_cctv_entities())

        if "earthquakes" in active_layers:
            results.extend(self.hazards_service.fetch_earthquakes())

        if "fires" in active_layers:
            results.extend(self.hazards_service.fetch_fires())

        if "weather" in active_layers:
            results.extend(self.hazards_service.fetch_weather())

        if "conflict" in active_layers:
            conflicts, _ = self.threats_service.fetch_conflicts()
            results.extend(conflicts)
            results.extend(self.threats_service.fetch_gps_jamming())

        if "nuclear" in active_layers:
            results.extend(self.threats_service.fetch_nuclear())

        if "cyber" in active_layers:
            results.extend(self.cyber_service.fetch_cyber_nodes())

        if "satellites" in active_layers:
            sats, _ = self.space_weather_service.fetch_satellites()
            results.extend(sats)

        if "recon" in active_layers:
            results.extend(self._user_recon_findings)

        return results

    def get_route_paths(self, active_layers: Optional[List[str]] = None) -> List[RoutePath]:
        """Aggregate route polylines (flight corridors, cables, frontlines, orbit tracks)."""
        if active_layers is None:
            active_layers = ["aviation", "cables", "conflict", "satellites"]

        paths: List[RoutePath] = []

        if "aviation" in active_layers:
            _, routes = self.aviation_service.fetch_flights()
            paths.extend(routes)

        if "cables" in active_layers:
            _, _, cables = self.maritime_service.fetch_maritime()
            paths.extend(cables)

        if "conflict" in active_layers:
            _, frontlines = self.threats_service.fetch_conflicts()
            paths.extend(frontlines)

        if "satellites" in active_layers:
            _, orbits = self.space_weather_service.fetch_satellites()
            paths.extend(orbits)

        return paths

    def get_layer_counts(self) -> Dict[str, int]:
        """Compute real-time entity counts per layer category."""
        flights, _ = self.aviation_service.fetch_flights()
        vessels, chokepoints, cables = self.maritime_service.fetch_maritime()
        cams = self.cctv_service.fetch_cctv_entities()
        quakes = self.hazards_service.fetch_earthquakes()
        fires = self.hazards_service.fetch_fires()
        weather = self.hazards_service.fetch_weather()
        conflicts, frontlines = self.threats_service.fetch_conflicts()
        nuclear = self.threats_service.fetch_nuclear()
        cyber = self.cyber_service.fetch_cyber_nodes()
        sats, orbits = self.space_weather_service.fetch_satellites()

        return {
            "aviation": len(flights),
            "maritime": len(vessels),
            "chokepoints": len(chokepoints),
            "cables": len(cables),
            "cctv": len(cams),
            "earthquakes": len(quakes),
            "fires": len(fires),
            "weather": len(weather),
            "conflict": len(conflicts),
            "nuclear": len(nuclear),
            "cyber": len(cyber),
            "satellites": len(sats),
            "recon": len(self._user_recon_findings),
        }

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
        self._user_recon_findings.append(entity)
        return entity

    def get_recon_findings(self) -> List[GeoEntity]:
        """Return list of user reconnaissance findings pinned to map."""
        return list(self._user_recon_findings)

    def get_news_alerts(self) -> List[NewsAlert]:
        """Return real-time intelligence wire alerts."""
        return list(SAMPLE_NEWS_ALERTS)

    def get_markets(self) -> Tuple[List[MarketTicker], List[Dict[str, Any]]]:
        """Return financial tickers and sovereign risk scores."""
        tickers = self.markets_service.fetch_tickers()
        risks = self.markets_service.fetch_country_risk()
        return tickers, risks

    def get_space_weather(self) -> Dict[str, Any]:
        """Return space weather Kp index and solar telemetries."""
        return self.space_weather_service.fetch_space_weather()

    def get_cisa_kev(self) -> List[Dict[str, Any]]:
        """Return latest CISA KEV entries."""
        return self.cyber_service.fetch_cisa_kev()


# Global Singleton Instance
data_manager = DataManager()
