"""Surveillance CCTV service: Traffic authorities and open webcam directory."""

from typing import List, Optional
from plotsiris.domain.models import GeoEntity, CameraFeed
from plotsiris.domain.constants import CCTV_REGISTRY


class CctvService:
    """Manages global surveillance cameras and feeds."""

    def __init__(self):
        self._cameras = CCTV_REGISTRY

    def fetch_cctv_entities(self) -> List[GeoEntity]:
        """Convert CCTV registry entries to GeoEntity points for map display."""
        entities = []
        for cam in self._cameras:
            entities.append(GeoEntity(
                id=cam["id"],
                lat=cam["lat"],
                lon=cam["lon"],
                category="cctv",
                subcategory="Surveillance Camera",
                title=f"CCTV: {cam['name']}",
                description=f"Authority: {cam['provider']} | Country: {cam['country']} | Status: {cam['status']}",
                severity="INFO",
                color="#10b981",
                icon="camera",
                size=10,
                properties=cam
            ))
        return entities

    def get_camera_by_id(self, cam_id: str) -> Optional[CameraFeed]:
        """Retrieve camera feed metadata by camera ID."""
        for cam in self._cameras:
            if cam["id"] == cam_id:
                return CameraFeed(
                    id=cam["id"],
                    name=cam["name"],
                    country=cam["country"],
                    region=cam["region"],
                    lat=cam["lat"],
                    lon=cam["lon"],
                    stream_url=cam["stream_url"],
                    thumbnail_url=cam["thumbnail_url"],
                    feed_type=cam.get("feed_type", "snapshot"),
                    status=cam.get("status", "ONLINE"),
                    provider=cam.get("provider", "Authority")
                )
        return None
