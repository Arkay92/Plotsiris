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


def test_osint_authorization_gate():
    toolkit = OsintToolkit()
    # 1. Unapproved target without authorization -> blocked under CMA 1990
    blocked_res = toolkit.run_tool("portscan", "unauthorized-target.org", is_authorized=False)
    assert blocked_res.status == "BLOCKED"
    assert "Computer Misuse Act 1990" in blocked_res.summary
    assert "10.5281/zenodo.23924318" in blocked_res.summary

    # 2. Approved demo target (scanme.nmap.org) -> allowed
    demo_res = toolkit.run_tool("portscan", "scanme.nmap.org", is_authorized=False)
    assert demo_res.status in ("SUCCESS", "WARNING", "ERROR")  # passes authorization check

    # 3. Passive tool (dns) -> allowed without authorization gate
    passive_res = toolkit.run_tool("dns", "google.com", is_authorized=False)
    assert passive_res.status in ("SUCCESS", "WARNING")
    assert passive_res.status != "BLOCKED"


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


def test_cctv_live_feed_resolution():
    from plotsiris.services.cctv import CctvService

    svc = CctvService()
    cams = svc.list_cameras()
    assert len(cams) >= 8

    # Live snapshot feed (Caltrans SF Bay Bridge) appends cache-buster timestamp
    sf_feed = svc.resolve_live_feed("cam_us_ca_01", cache_buster=True)
    assert sf_feed["id"] == "cam_us_ca_01"
    assert sf_feed["mode"] == "live_snapshot"
    assert sf_feed["is_external_live"] is True
    assert "?t=" in sf_feed["snapshot_url"]

    # Video feed (London Piccadilly TfL Live) supports snapshot mode override cleanly
    tfl_vid = svc.resolve_live_feed("cam_uk_piccadilly", cache_buster=True)
    assert tfl_vid["mode"] == "video"
    assert "jamcams.tfl.gov.uk" in tfl_vid["stream_url"]

    tfl_snap = svc.resolve_live_feed("cam_uk_piccadilly", cache_buster=True, preferred_mode="live_snapshot")
    assert tfl_snap["mode"] == "live_snapshot"
    assert "?t=" in tfl_snap["snapshot_url"]
