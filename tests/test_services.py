"""Unit tests for Plotsiris intelligence services."""

from plotsiris.services.data_manager import DataManager
from plotsiris.services.osint_toolkit import OsintToolkit
from plotsiris.services.ai_analyst import AiAnalystService


def test_data_manager_layer_aggregation():
    dm = DataManager()
    entities = dm.get_all_entities()
    assert len(entities) > 30

    routes = dm.get_route_paths()
    assert len(routes) >= 5

    counts = dm.get_layer_counts()
    assert counts["aviation"] > 0
    assert counts["maritime"] > 0
    assert counts["earthquakes"] > 0
    assert counts["conflict"] > 0
    assert counts["cyber"] > 0


def test_osint_toolkit_dns():
    toolkit = OsintToolkit()
    res = toolkit.run_tool("dns", "google.com")
    assert res.tool == "dns"
    assert res.status == "SUCCESS"
    assert res.verdict in ("CLEAN", "SUSPICIOUS")
    assert "records" in res.details


def test_osint_toolkit_whois():
    toolkit = OsintToolkit()
    res = toolkit.run_tool("whois", "microsoft.com")
    assert res.tool == "whois"
    assert res.status in ("SUCCESS", "WARNING")


def test_osint_toolkit_portscan():
    toolkit = OsintToolkit()
    res = toolkit.run_tool("portscan", "1.1.1.1")
    assert res.tool == "portscan"
    assert res.status in ("SUCCESS", "WARNING")
    assert "open_ports" in res.details


def test_osint_toolkit_mac():
    toolkit = OsintToolkit()
    res = toolkit.run_tool("mac", "B8:27:EB:00:00:00")
    assert res.tool == "mac"
    assert "Raspberry Pi" in res.summary or "Hardware" in res.summary


def test_ai_analyst():
    ai = AiAnalystService()
    ans = ai.answer_query("top threats", {"active_layer_count": 12})
    assert len(ans) > 50
    assert "THREATS" in ans.upper() or "RED SEA" in ans.upper()

    briefing = ai.generate_full_briefing({"active_layer_count": 12})
    assert "SITREP" in briefing
    assert "KINETIC & CONFLICT" in briefing
