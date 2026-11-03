"""Threat & conflict intelligence: Frontlines, nuclear infrastructure, ransomware, and GPS jamming."""

import logging
import requests
from typing import List, Tuple
from plotsiris.domain.models import GeoEntity, RoutePath
from plotsiris.config import REQUEST_TIMEOUT_SEC

logger = logging.getLogger(__name__)

# Key Conflict Theatres & Frontlines
CONFLICT_ZONES = [
    {
        "id": "conf_ua_donbas",
        "name": "Eastern Ukraine Theatre (Pokrovsk - Chasiv Yar Sector)",
        "lat": 48.28,
        "lon": 37.18,
        "type": "Active High-Intensity War Zone",
        "severity": "CRITICAL",
        "parties": "Armed Forces of Ukraine vs. Russian Armed Forces",
        "color": "#dc2626",
        "description": "Heavy kinetic engagements, glide bomb strikes, and active drone reconnaissance."
    },
    {
        "id": "conf_ua_kursk",
        "name": "Kursk Border Operational Sector",
        "lat": 51.32,
        "lon": 35.25,
        "type": "Cross-Border Combat Zone",
        "severity": "CRITICAL",
        "parties": "Ukrainian Mobile Formations vs. Russian Border Defense",
        "color": "#dc2626",
        "description": "Maneuver warfare, interdiction strikes, and mechanized breakthroughs."
    },
    {
        "id": "conf_red_sea",
        "name": "Southern Red Sea / Bab el-Mandeb Combat Zone",
        "lat": 13.50,
        "lon": 42.80,
        "type": "Anti-Shipping / Naval Interdiction",
        "severity": "CRITICAL",
        "parties": "Houthi Forces vs. US/Coalition Naval Task Forces",
        "color": "#dc2626",
        "description": "Anti-ship ballistic missiles, uncrewed surface vessels (USVs), and naval interceptions."
    },
    {
        "id": "conf_lebanon",
        "name": "Israel - Southern Lebanon Border",
        "lat": 33.15,
        "lon": 35.35,
        "type": "Border Skirmishes & Rocket Interception",
        "severity": "CRITICAL",
        "parties": "Hezbollah vs. IDF",
        "color": "#dc2626",
        "description": "Artillery duels, air defense Iron Dome/David's Sling engagements, and drone attacks."
    },
    {
        "id": "conf_sudan",
        "name": "Khartoum / El Fasher (Darfur Sector)",
        "lat": 13.62,
        "lon": 25.35,
        "type": "Urban Civil Conflict & Humanitarian Crisis",
        "severity": "CRITICAL",
        "parties": "Sudanese Armed Forces (SAF) vs. Rapid Support Forces (RSF)",
        "color": "#ef4444",
        "description": "Mass displacement, encirclement battles, and artillery bombardment."
    },
    {
        "id": "conf_myanmar",
        "name": "Shan State / Northern Myanmar Frontier",
        "lat": 23.90,
        "lon": 97.90,
        "type": "Civil Resistance / Insurgency",
        "severity": "HIGH",
        "parties": "Three Brotherhood Alliance vs. Military Junta (SAC)",
        "color": "#f97316",
        "description": "Capture of border trade gates, drone bombing runs, and garrison surrenders."
    },
    {
        "id": "conf_sahel",
        "name": "Mali / Burkina Faso / Niger Tri-Border",
        "lat": 14.90,
        "lon": 0.15,
        "type": "Jihadist Insurgency & Military Junta Ops",
        "severity": "HIGH",
        "parties": "JNIM / ISGS vs. Alliance of Sahel States (AES)",
        "color": "#f97316",
        "description": "Ambush tactics, IED attacks on supply convoys, and contested territory."
    }
]

# Frontline Path Lines (e.g. Svatove - Kreminna - Bakhmut - Avdiivka - Zaporizhzhia)
FRONTLINE_LINES = [
    {
        "id": "frontline_ukraine_east",
        "name": "Ukraine Eastern Contact Line (Approximate)",
        "lats": [49.9, 49.0, 48.6, 48.0, 47.7, 47.5, 46.5],
        "lons": [37.9, 38.2, 38.0, 37.6, 37.2, 35.8, 35.3],
        "color": "#dc2626",
        "width": 3.0,
        "dash": "solid"
    }
]

# Nuclear Power Facilities & Strategic Infrastructure
NUCLEAR_FACILITIES = [
    {
        "id": "nuc_zaporizhzhia",
        "name": "Zaporizhzhia Nuclear Power Plant (ZNPP)",
        "country": "Ukraine (Contested / Enerhodar)",
        "lat": 47.5100,
        "lon": 34.5850,
        "capacity_mwe": 5700,
        "reactors": "6x VVER-1000",
        "status": "Cold Shutdown / Military Occupation",
        "risk_level": "CRITICAL",
        "color": "#dc2626"
    },
    {
        "id": "nuc_chernobyl",
        "name": "Chernobyl New Safe Confinement",
        "country": "Ukraine (Pripyat)",
        "lat": 51.3892,
        "lon": 30.0997,
        "capacity_mwe": 0,
        "reactors": "Decommissioned Shelter Object",
        "status": "Monitored Exclusion Zone",
        "risk_level": "ELEVATED",
        "color": "#eab308"
    },
    {
        "id": "nuc_bushehr",
        "name": "Bushehr Nuclear Power Plant",
        "country": "Iran",
        "lat": 28.8300,
        "lon": 50.8850,
        "capacity_mwe": 1000,
        "reactors": "1x VVER-1000",
        "status": "Operational / IAEA Safeguards Monitored",
        "risk_level": "HIGH",
        "color": "#f97316"
    },
    {
        "id": "nuc_natanz",
        "name": "Natanz Fuel Enrichment Complex",
        "country": "Iran",
        "lat": 33.7240,
        "lon": 51.7280,
        "capacity_mwe": 0,
        "reactors": "Centrifuge Underground Facility",
        "status": "Hardened Subterranean Facility",
        "risk_level": "HIGH",
        "color": "#ef4444"
    },
    {
        "id": "nuc_dimona",
        "name": "Shimon Peres Negev Nuclear Research Center",
        "country": "Israel (Dimona)",
        "lat": 31.0010,
        "lon": 35.1440,
        "capacity_mwe": 0,
        "reactors": "Heavy Water Research Reactor",
        "status": "Restricted High-Security Zone",
        "risk_level": "HIGH",
        "color": "#ef4444"
    },
    {
        "id": "nuc_gravelines",
        "name": "Gravelines Nuclear Power Station",
        "country": "France (Nord)",
        "lat": 51.0150,
        "lon": 2.1360,
        "capacity_mwe": 5460,
        "reactors": "6x PWR",
        "status": "Active Commercial Generation",
        "risk_level": "LOW",
        "color": "#10b981"
    },
    {
        "id": "nuc_fukushima",
        "name": "Fukushima Daiichi Site",
        "country": "Japan",
        "lat": 37.4214,
        "lon": 141.0326,
        "capacity_mwe": 0,
        "reactors": "Decommissioning / ALPS Treated Water Storage",
        "status": "Active Long-Term Remediation",
        "risk_level": "ELEVATED",
        "color": "#eab308"
    },
    {
        "id": "nuc_barakah",
        "name": "Barakah Nuclear Energy Plant",
        "country": "United Arab Emirates (Al Dhafra)",
        "lat": 23.9700,
        "lon": 52.2600,
        "capacity_mwe": 5600,
        "reactors": "4x APR-1400",
        "status": "Fully Operational (Supplying 25% UAE Grid)",
        "risk_level": "LOW",
        "color": "#10b981"
    }
]

# Strategic GPS Jamming Interference Hotspots (ADS-B spoofing & GNSS degradation)
GPS_JAMMING_ZONES = [
    {"id": "gps_baltic", "name": "Baltic Sea / Kaliningrad Pocket GNSS Jamming", "lat": 55.20, "lon": 20.50, "sev": "HIGH", "color": "#a855f7", "desc": "Widespread civil aviation GPS loss, circle spoofing reported by Eurocontrol."},
    {"id": "gps_black_sea", "name": "Crimea & Eastern Black Sea GPS Denial", "lat": 44.80, "lon": 34.00, "sev": "CRITICAL", "color": "#dc2626", "desc": "Total GNSS spoofing, ship automatic identification system (AIS) distortion."},
    {"id": "gps_east_med", "name": "Eastern Mediterranean / Cyprus GPS Disruption", "lat": 34.50, "lon": 33.50, "sev": "HIGH", "color": "#a855f7", "desc": "Electronic warfare spillover impacting Tel Aviv and Beirut flight approaches."}
]


class ThreatsService:
    """Manages armed conflict zones, frontlines, nuclear facilities, and GPS warfare."""

    def fetch_conflicts(self) -> Tuple[List[GeoEntity], List[RoutePath]]:
        """Return (conflict_entities, frontline_routes)."""
        entities = []
        for c in CONFLICT_ZONES:
            entities.append(GeoEntity(
                id=c["id"],
                lat=c["lat"],
                lon=c["lon"],
                category="conflict",
                subcategory=c["type"],
                title=f"WAR ZONE: {c['name']}",
                description=f"{c['description']} | Belligerents: {c['parties']} | Alert: {c['severity']}",
                severity=c["severity"],
                color=c["color"],
                icon="crosshair",
                size=13,
                properties=c
            ))

        routes = []
        for fl in FRONTLINE_LINES:
            routes.append(RoutePath(
                id=fl["id"],
                name=fl["name"],
                category="frontline",
                lats=fl["lats"],
                lons=fl["lons"],
                color=fl["color"],
                width=fl["width"],
                dash=fl["dash"]
            ))

        return entities, routes

    def fetch_nuclear(self) -> List[GeoEntity]:
        """Return nuclear power plants and strategic atomic installations."""
        entities = []
        for n in NUCLEAR_FACILITIES:
            entities.append(GeoEntity(
                id=n["id"],
                lat=n["lat"],
                lon=n["lon"],
                category="nuclear",
                subcategory="Nuclear Facility",
                title=f"NUCLEAR: {n['name']}",
                description=f"Status: {n['status']} | Output: {n['capacity_mwe']} MWe | Reactors: {n['reactors']} | Nation: {n['country']}",
                severity=n["risk_level"],
                color=n["color"],
                icon="shield",
                size=12,
                properties=n
            ))
        return entities

    def fetch_gps_jamming(self) -> List[GeoEntity]:
        """Return areas of significant electronic warfare GNSS jamming."""
        entities = []
        for j in GPS_JAMMING_ZONES:
            entities.append(GeoEntity(
                id=j["id"],
                lat=j["lat"],
                lon=j["lon"],
                category="conflict",
                subcategory="GPS/GNSS Jamming",
                title=f"EW JAMMING: {j['name']}",
                description=f"{j['desc']} | Intensity: {j['sev']}",
                severity=j["sev"],
                color=j["color"],
                icon="broadcast",
                size=11,
                properties=j
            ))
        return entities
