"""Services module exports."""

from plotsiris.services.data_manager import DataManager, data_manager
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

__all__ = [
    "DataManager",
    "data_manager",
    "AviationService",
    "MaritimeService",
    "HazardsService",
    "ThreatsService",
    "CyberService",
    "SpaceWeatherService",
    "CctvService",
    "MarketsService",
    "OsintToolkit",
    "AiAnalystService",
]
