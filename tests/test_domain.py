"""Unit tests for Plotsiris domain models and constants."""

from plotsiris.domain.models import GeoEntity, RoutePath, OsintResult, MarketTicker, NewsAlert
from plotsiris.domain.constants import REGION_PRESETS, LAYER_DEFINITIONS, MARITIME_CHOKEPOINTS, OSINT_TOOLS


def test_geo_entity_serialization():
    entity = GeoEntity(
        id="test_01",
        lat=25.0,
        lon=121.5,
        category="aviation",
        subcategory="Commercial",
        title="Test Flight",
        description="Origin -> Dest",
        severity="INFO"
    )
    d = entity.to_dict()
    assert d["id"] == "test_01"
    assert d["lat"] == 25.0
    assert d["lon"] == 121.5
    assert d["category"] == "aviation"


def test_osint_result_serialization():
    res = OsintResult(
        tool="dns",
        target="google.com",
        status="SUCCESS",
        verdict="CLEAN",
        summary="DNS resolved",
        coordinates=(37.42, -122.08)
    )
    d = res.to_dict()
    assert d["tool"] == "dns"
    assert d["target"] == "google.com"
    assert d["verdict"] == "CLEAN"
    assert d["coordinates"] == (37.42, -122.08)


def test_constants_and_presets():
    assert "global" in REGION_PRESETS
    assert "europe" in REGION_PRESETS
    assert "red_sea" in REGION_PRESETS
    assert len(LAYER_DEFINITIONS) >= 10
    assert len(MARITIME_CHOKEPOINTS) >= 5
    assert len(OSINT_TOOLS) == 20
