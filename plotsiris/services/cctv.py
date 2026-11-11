"""Surveillance CCTV service: Traffic authorities and open webcam directory."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, List, Optional

import requests
import urllib3

from plotsiris.domain.models import GeoEntity, CameraFeed
from plotsiris.domain.constants import CCTV_REGISTRY

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)


class CctvService:
    """Manages global surveillance cameras and live feed resolution."""

    _sg_cache: Dict[str, Any] = {"ts": 0.0, "image_url": None, "captured_at": None, "camera_id": None}
    _tfl_cache: Dict[str, Any] = {"ts": 0.0, "cams": {}}

    def __init__(self):
        self._cameras = CCTV_REGISTRY

    def list_cameras(self) -> List[Dict[str, Any]]:
        """Return all registered CCTV camera entries."""
        return list(self._cameras)

    def get_camera_dict(self, cam_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve raw registry dict for cam_id, falling back to first camera."""
        if cam_id:
            for cam in self._cameras:
                if cam["id"] == cam_id:
                    return dict(cam)
        return dict(self._cameras[0]) if self._cameras else {}

    @staticmethod
    def _append_cache_buster(url: str, ts: Optional[int] = None) -> str:
        """Append cache-busting epoch query parameter to external HTTP/HTTPS URLs."""
        if not url or not url.startswith("http"):
            return url
        stamp = ts if ts is not None else int(time.time())
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}t={stamp}"

    def _resolve_sg_lta_snapshot(self) -> Optional[Dict[str, str]]:
        """Fetch latest live traffic image URL from Singapore LTA Data.gov.sg API."""
        now = time.time()
        if self._sg_cache["image_url"] and (now - self._sg_cache["ts"]) < 20.0:
            return {
                "url": self._sg_cache["image_url"],
                "captured_at": self._sg_cache["captured_at"] or "",
                "camera_id": self._sg_cache["camera_id"] or "",
            }
        try:
            resp = requests.get(
                "https://api.data.gov.sg/v1/transport/traffic-images",
                timeout=3.0,
                verify=False,
            )
            if resp.status_code == 200:
                payload = resp.json()
                items = payload.get("items") or []
                cams = (items[0].get("cameras") or []) if items else []
                # Prefer high-res 1920x1080 expressway/checkpoint cameras (e.g. Woodlands/MCE)
                chosen = None
                for c in cams:
                    if str(c.get("camera_id")) in ("2701", "1001", "4703", "1701") and c.get("image"):
                        chosen = c
                        break
                if not chosen:
                    for c in cams:
                        if c.get("image"):
                            chosen = c
                            break
                if chosen:
                    self._sg_cache["ts"] = now
                    self._sg_cache["image_url"] = chosen["image"]
                    self._sg_cache["captured_at"] = chosen.get("timestamp") or items[0].get("timestamp", "")
                    self._sg_cache["camera_id"] = str(chosen.get("camera_id", ""))
                    return {
                        "url": self._sg_cache["image_url"],
                        "captured_at": self._sg_cache["captured_at"],
                        "camera_id": self._sg_cache["camera_id"],
                    }
        except Exception as exc:
            logger.debug("SG LTA live camera resolution fallback triggered: %s", exc)
        if self._sg_cache["image_url"]:
            return {
                "url": self._sg_cache["image_url"],
                "captured_at": self._sg_cache["captured_at"] or "",
                "camera_id": self._sg_cache["camera_id"] or "",
            }
        return None

    def resolve_live_feed(
        self,
        cam_id: Optional[str] = None,
        cache_buster: bool = True,
        preferred_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resolve fresh live snapshot/stream URLs and capture metadata for a camera."""
        cam = self.get_camera_dict(cam_id)
        now_int = int(time.time())
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        stream_url = cam.get("stream_url", "/assets/surveillance_stream.mp4")
        snapshot_url = cam.get("snapshot_url") or cam.get("thumbnail_url") or "/assets/surveillance_stream.gif"
        feed_type = cam.get("feed_type", "live_snapshot")
        captured_at = now_utc

        if cam.get("live_api") == "sg_lta":
            sg_live = self._resolve_sg_lta_snapshot()
            if sg_live and sg_live.get("url"):
                snapshot_url = sg_live["url"]
                if sg_live.get("captured_at"):
                    captured_at = sg_live["captured_at"]
            else:
                # Fallback live optical image if external SG API is offline
                snapshot_url = "/assets/surveillance_stream.gif"

        if cache_buster:
            if snapshot_url.startswith("http"):
                snapshot_url = self._append_cache_buster(snapshot_url, now_int)
            if stream_url.startswith("http"):
                stream_url = self._append_cache_buster(stream_url, now_int)

        mode = preferred_mode if preferred_mode in ("live_snapshot", "video") else feed_type
        if mode not in ("live_snapshot", "video"):
            mode = "live_snapshot" if snapshot_url.startswith("http") else "video"

        is_external_live = snapshot_url.startswith("http") or stream_url.startswith("http")

        return {
            "id": cam.get("id", "cam_default"),
            "name": cam.get("name", "Live Surveillance Feed"),
            "country": cam.get("country", "Global"),
            "region": cam.get("region", "Operations"),
            "lat": cam.get("lat", 0.0),
            "lon": cam.get("lon", 0.0),
            "provider": cam.get("provider", "Authority"),
            "status": cam.get("status", "ONLINE"),
            "feed_type": feed_type,
            "mode": mode,
            "stream_url": stream_url,
            "snapshot_url": snapshot_url,
            "captured_at": captured_at,
            "resolved_utc": now_utc,
            "is_external_live": is_external_live,
        }

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
