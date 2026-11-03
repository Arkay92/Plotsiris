"""Maritime intelligence service: AIS vessel tracking, chokepoints, and subsea cables."""

from typing import List, Tuple
from plotsiris.domain.models import GeoEntity, RoutePath
from plotsiris.domain.constants import MARITIME_CHOKEPOINTS, STRATEGIC_SUBSEA_CABLES

MAJOR_VESSELS = [
    {
        "mmsi": "636019825",
        "name": "MSC GULSUN",
        "type": "Ultra Large Container",
        "flag": "Liberia (LR)",
        "destination": "ROTTERDAM",
        "lat": 36.8,
        "lon": -4.2,
        "spd": 18.5,
        "hdg": 280,
        "draught": 16.2,
        "risk": "INFO",
        "color": "#0ea5e9"
    },
    {
        "mmsi": "311000854",
        "name": "EVER GIVEN",
        "type": "Container Ship",
        "flag": "Panama (PA)",
        "destination": "SINGAPORE",
        "lat": 13.5,
        "lon": 48.2,
        "spd": 16.2,
        "hdg": 95,
        "draught": 15.5,
        "risk": "ELEVATED",
        "color": "#f59e0b"
    },
    {
        "mmsi": "538008432",
        "name": "FRONT ALTAIR",
        "type": "VLCC Crude Oil Tanker",
        "flag": "Marshall Islands (MH)",
        "destination": "NINGBO",
        "lat": 24.8,
        "lon": 58.1,
        "spd": 13.8,
        "hdg": 110,
        "draught": 21.0,
        "risk": "HIGH",
        "color": "#f97316"
    },
    {
        "mmsi": "368926000",
        "name": "USS DWIGHT D. EISENHOWER (CVN-69)",
        "type": "Aircraft Carrier / Task Force",
        "flag": "United States (US Navy)",
        "destination": "PATROL OPS",
        "lat": 19.4,
        "lon": 39.8,
        "spd": 24.0,
        "hdg": 160,
        "draught": 11.8,
        "risk": "CRITICAL",
        "color": "#ef4444"
    },
    {
        "mmsi": "235010548",
        "name": "HMS DIAMOND (D34)",
        "type": "Type 45 Guided Missile Destroyer",
        "flag": "United Kingdom (Royal Navy)",
        "destination": "OPERATION PROSPERITY GUARDIAN",
        "lat": 14.1,
        "lon": 42.8,
        "spd": 22.5,
        "hdg": 340,
        "draught": 7.4,
        "risk": "CRITICAL",
        "color": "#ef4444"
    },
    {
        "mmsi": "477995300",
        "name": "COSCO SHIPPING TAURUS",
        "type": "Container Vessel",
        "flag": "Hong Kong (HK)",
        "destination": "PORT KLANG",
        "lat": 3.8,
        "lon": 100.5,
        "spd": 19.1,
        "hdg": 140,
        "draught": 14.8,
        "risk": "INFO",
        "color": "#0ea5e9"
    },
    {
        "mmsi": "219018476",
        "name": "MAERSK MC-KINNEY MOLLER",
        "type": "Triple-E Container",
        "flag": "Denmark (DK)",
        "destination": "SUEZ CANAL",
        "lat": 28.1,
        "lon": 33.5,
        "spd": 15.4,
        "hdg": 335,
        "draught": 15.0,
        "risk": "ELEVATED",
        "color": "#0ea5e9"
    },
    {
        "mmsi": "353139000",
        "name": "TI EUROPE",
        "type": "ULCC Supertanker",
        "flag": "Belgium (BE)",
        "destination": "RAS TANURA",
        "lat": 26.1,
        "lon": 53.2,
        "spd": 12.0,
        "hdg": 295,
        "draught": 22.5,
        "risk": "HIGH",
        "color": "#f97316"
    },
    {
        "mmsi": "412345678",
        "name": "YANGTZE FORTUNE",
        "type": "Bulk Carrier",
        "flag": "China (CN)",
        "destination": "DAMPIER",
        "lat": -18.5,
        "lon": 115.2,
        "spd": 11.2,
        "hdg": 210,
        "draught": 13.0,
        "risk": "INFO",
        "color": "#0ea5e9"
    }
]


class MaritimeService:
    """Manages AIS ships, critical straits, and global subsea telecom cables."""

    def __init__(self):
        self._vessels = MAJOR_VESSELS
        self._cables = STRATEGIC_SUBSEA_CABLES
        self._chokepoints = MARITIME_CHOKEPOINTS

    def fetch_maritime(self) -> Tuple[List[GeoEntity], List[GeoEntity], List[RoutePath]]:
        """Return (vessel_entities, chokepoint_entities, cable_routes)."""
        vessel_entities = []
        for v in self._vessels:
            # Subtle realistic drift
            v["lat"] += (0.01 if v["hdg"] < 180 else -0.01)
            v["lon"] += (0.01 if 90 < v["hdg"] < 270 else -0.01)

            is_naval = "Navy" in v["flag"] or "Destroyer" in v["type"] or "Carrier" in v["type"]
            vessel_entities.append(GeoEntity(
                id=f"vessel_{v['mmsi']}",
                lat=v["lat"],
                lon=v["lon"],
                category="maritime",
                subcategory=v["type"],
                title=f"{v['name']} ({v['flag']})",
                description=(
                    f"MMSI: {v['mmsi']} | Type: {v['type']} | Dest: {v['destination']} | "
                    f"Speed: {v['spd']} kts | Course: {v['hdg']}° | Draught: {v['draught']}m"
                ),
                severity=v["risk"],
                color=v["color"],
                icon="triangle" if is_naval else "circle",
                size=12 if is_naval else 9,
                heading=v["hdg"],
                speed_knots=v["spd"],
                properties={
                    "mmsi": v["mmsi"],
                    "vessel_name": v["name"],
                    "type": v["type"],
                    "flag": v["flag"],
                    "destination": v["destination"],
                    "draught": v["draught"],
                    "is_naval": is_naval
                }
            ))

        # Build Chokepoint entities
        chokepoint_entities = []
        for cp in self._chokepoints:
            color = "#ef4444" if cp["risk_level"] == "CRITICAL" else ("#f97316" if cp["risk_level"] == "HIGH" else "#f59e0b")
            chokepoint_entities.append(GeoEntity(
                id=cp["id"],
                lat=cp["lat"],
                lon=cp["lon"],
                category="chokepoints",
                subcategory="Strategic Strait",
                title=f"CHOKEPOINT: {cp['name']} ({cp['country']})",
                description=f"{cp['description']} | Volume: {cp['daily_volume']} | Risk: {cp['risk_level']}",
                severity=cp["risk_level"],
                color=color,
                icon="square",
                size=13,
                properties=cp
            ))

        # Build Subsea Cable RoutePaths
        cable_routes = []
        for cb in self._cables:
            cable_routes.append(RoutePath(
                id=cb["id"],
                name=cb["name"],
                category="subsea_cable",
                lats=cb["lats"],
                lons=cb["lons"],
                color=cb.get("color", "#818cf8"),
                width=2.5,
                dash="solid",
                properties={"capacity": cb.get("capacity", "N/A")}
            ))

        return vessel_entities, chokepoint_entities, cable_routes
