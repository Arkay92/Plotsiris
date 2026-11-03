"""Global configuration and environment parameters for Plotsiris."""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_CACHE_DIR = PROJECT_ROOT / ".cache"
DATA_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Server options
HOST = os.environ.get("PLOTSIRIS_HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", os.environ.get("PLOTSIRIS_PORT", 8050)))
DEBUG = os.environ.get("PLOTSIRIS_DEBUG", "false").lower() in ("true", "1", "yes")

# API Keys (all are fully optional and gracefully degrade)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
URLHAUS_KEY = os.environ.get("URLHAUS_KEY", "")
NVD_API_KEY = os.environ.get("NVD_API_KEY", "")
OPENSKY_USERNAME = os.environ.get("OPENSKY_USERNAME", "")
OPENSKY_PASSWORD = os.environ.get("OPENSKY_PASSWORD", "")
AIS_API_KEY = os.environ.get("AIS_API_KEY", "")

# Map Styles (Free high-performance CartoDB tiles)
MAPBOX_STYLE_DARK = "carto-darkmatter"
MAPBOX_STYLE_LIGHT = "carto-positron"
DEFAULT_THEME = os.environ.get("PLOTSIRIS_THEME", "ghost")  # "ghost" (dark) or "core" (light)

# Refresh intervals (seconds)
FEED_REFRESH_INTERVAL_SEC = 60
CACHE_EXPIRY_SEC = 300
REQUEST_TIMEOUT_SEC = 5.0
