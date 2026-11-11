"""Unit tests for Plotsiris rendering and application factory."""

from plotsiris.services.data_manager import DataManager
from plotsiris.rendering.map_builder import MapBuilder
from plotsiris.rendering.graph_builder import EntityGraphBuilder
from plotsiris.app import create_app


def test_map_builder():
    dm = DataManager()
    entities = dm.get_all_entities()
    routes = dm.get_route_paths()
    fig = MapBuilder.build_map(entities, routes, theme="ghost")
    assert fig is not None
    assert len(fig.data) > 0


def test_entity_graph_builder():
    fig = EntityGraphBuilder.build_graph(theme="ghost")
    assert fig is not None
    assert len(fig.data) >= 2  # edge trace, background star nodes, and core node trace


def test_create_app():
    app = create_app()
    assert app is not None
    assert app.title.startswith("Plotsiris")
    assert app.layout is not None


def test_inspector_modal_action_buttons_close_modal():
    """Verify that clicking action buttons (CCTV, OSINT, AI, Close) closes the inspector modal."""
    import inspect
    from unittest.mock import patch

    app = create_app()
    cb_key = '..selected-entity-store.data...inspector-card-backdrop.style...inspector-title.children...inspector-category.children...inspector-description.children...inspector-coords.children...inspector-severity-badge.children...inspector-severity-badge.color...btn-inspector-camera.style..'
    callback_fn = app.callback_map[cb_key]['callback']
    inspect_fn = inspect.unwrap(callback_fn)

    with patch('plotsiris.ui.callbacks.callback_context') as mock_ctx:
        # Open modal via map click
        mock_ctx.triggered = True
        mock_ctx.triggered_id = 'main-map'
        map_click = {'points': [{'customdata': {'title': 'Test CCTV', 'category': 'cctv', 'severity': 'INFO', 'lat': 37.79, 'lon': -122.37}}]}
        res = inspect_fn(map_click, None, 0, 0, 0, 0, None)
        assert res[1] == {'display': 'flex'}, f'Expected flex, got {res[1]}'

        # Click LIVE CCTV -> modal closes
        mock_ctx.triggered_id = 'btn-inspector-camera'
        res_cam = inspect_fn(None, None, 0, 1, 0, 0, res[0])
        assert res_cam[1] == {'display': 'none'}

        # Click OSINT RECON -> modal closes
        mock_ctx.triggered_id = 'btn-inspector-osint'
        res_osint = inspect_fn(None, None, 0, 0, 1, 0, res[0])
        assert res_osint[1] == {'display': 'none'}

        # Click AI ASSESS -> modal closes
        mock_ctx.triggered_id = 'btn-inspector-ai'
        res_ai = inspect_fn(None, None, 0, 0, 0, 1, res[0])
        assert res_ai[1] == {'display': 'none'}

        # Click Close -> modal closes
        mock_ctx.triggered_id = 'btn-close-inspector'
        res_close = inspect_fn(None, None, 1, 0, 0, 0, res[0])
        assert res_close[1] == {'display': 'none'}


def test_map_update_preserves_user_camera_on_refresh_and_layers():
    """Verify background feed refreshes & layer toggles return a data-only Patch preserving camera."""
    import inspect
    from unittest.mock import patch
    from dash import Patch
    import plotly.graph_objects as go

    app = create_app()
    map_cb_key = next(k for k in app.callback_map if "main-map.figure" in k)
    update_map_fn = inspect.unwrap(app.callback_map[map_cb_key]["callback"])

    preset_cb_key = next(k for k in app.callback_map if k == "map-camera-store.data")
    preset_fn = inspect.unwrap(app.callback_map[preset_cb_key]["callback"])

    toggle_ids = [{"index": "aviation"}, {"index": "cctv"}]
    toggle_vals = [True, True]

    with patch("plotsiris.ui.callbacks.callback_context") as mock_ctx:
        # 1. Explicit Locate click increments rev and sets new target coords
        mock_ctx.triggered = True
        mock_ctx.triggered_id = "btn-alert-locate"
        cam_1 = preset_fn([], 1, {"lat": 12.8, "lon": 44.5, "zoom": 5.8}, {"lat": 20.0, "lon": 15.0, "zoom": 1.6, "rev": 0})
        assert cam_1["rev"] == 1
        assert cam_1["lat"] == 12.8 and cam_1["lon"] == 44.5

        # Repeated Locate click on the same coordinates still bumps rev so camera jumps back
        cam_2 = preset_fn([], 2, {"lat": 12.8, "lon": 44.5, "zoom": 5.8}, cam_1)
        assert cam_2["rev"] == 2

        # 2. Explicit map-camera-store change returns full go.Figure with updated uirevision
        mock_ctx.triggered_id = "map-camera-store"
        fig_jump, _ = update_map_fn(toggle_vals, cam_2, "ghost", 0, toggle_ids)
        assert isinstance(fig_jump, go.Figure)
        assert fig_jump.layout.uirevision == "cam_rev_2"
        assert fig_jump.layout.map.uirevision == "cam_rev_2"

        # 3. Feed refresh interval returns Patch touching ONLY data (no map center/zoom reset)
        mock_ctx.triggered_id = "feed-refresh-interval"
        fig_patch, _ = update_map_fn(toggle_vals, cam_2, "ghost", 1, toggle_ids)
        assert isinstance(fig_patch, Patch)
        ops = fig_patch.to_plotly_json()["operations"]
        assert len(ops) == 1
        assert ops[0]["location"] == ["data"]

        # 4. Layer toggle returns Patch touching ONLY data
        mock_ctx.triggered_id = {"type": "layer-toggle", "index": "aviation"}
        layer_patch, _ = update_map_fn([False, True], cam_2, "ghost", 1, toggle_ids)
        assert isinstance(layer_patch, Patch)
        assert [op["location"] for op in layer_patch.to_plotly_json()["operations"]] == [["data"]]

