"""Domain data structures and models for Plotsiris."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class GeoEntity:
    """Represents a geospatial entity displayed on the map."""
    id: str
    lat: float
    lon: float
    category: str  # aviation, maritime, cctv, earthquakes, fires, weather, conflict, cyber, satellites, recon
    subcategory: str
    title: str
    description: str = ""
    severity: str = "INFO"  # INFO, LOW, ELEVATED, HIGH, CRITICAL
    color: str = "#00e5ff"
    icon: str = "circle"
    size: float = 8.0
    heading: Optional[float] = None
    altitude_m: Optional[float] = None
    speed_knots: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "lat": self.lat,
            "lon": self.lon,
            "category": self.category,
            "subcategory": self.subcategory,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "color": self.color,
            "icon": self.icon,
            "size": self.size,
            "heading": self.heading,
            "altitude_m": self.altitude_m,
            "speed_knots": self.speed_knots,
            "timestamp": self.timestamp,
            "properties": self.properties,
        }


@dataclass
class RoutePath:
    """Represents a connected geographical line (flight trajectory, cable, border)."""
    id: str
    name: str
    category: str
    lats: List[float]
    lons: List[float]
    color: str = "#00e5ff"
    width: float = 2.0
    dash: str = "solid"
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CameraFeed:
    """Represents a CCTV or live webcam feed."""
    id: str
    name: str
    country: str
    region: str
    lat: float
    lon: float
    stream_url: str
    thumbnail_url: str
    feed_type: str = "snapshot"  # snapshot, mjpeg, hls, youtube
    status: str = "ONLINE"
    provider: str = ""


@dataclass
class OsintResult:
    """Represents an OSINT reconnaissance result."""
    tool: str
    target: str
    status: str  # SUCCESS, WARNING, MALICIOUS, ERROR
    verdict: str  # CLEAN, SUSPICIOUS, MALICIOUS, UNKNOWN
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    coordinates: Optional[tuple[float, float]] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "target": self.target,
            "status": self.status,
            "verdict": self.verdict,
            "summary": self.summary,
            "details": self.details,
            "coordinates": self.coordinates,
            "timestamp": self.timestamp,
        }


@dataclass
class MarketTicker:
    """Represents a financial or commodity market entry."""
    symbol: str
    name: str
    category: str  # DEFENSE, COMMODITY, CRYPTO, INDEX
    price: float
    change: float
    change_pct: float
    unit: str = "$"
    updated_at: str = field(default_factory=lambda: datetime.utcnow().strftime("%H:%M:%S UTC"))


@dataclass
class NewsAlert:
    """Represents a real-time intelligence wire alert."""
    id: str
    title: str
    source: str
    time_ago: str
    risk_level: str  # LOW, ELEVATED, HIGH, CRITICAL
    region: str
    summary: str
    category: str = "INTEL"
    url: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
