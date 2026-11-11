"""Dash Callbacks connecting UI components, map interactions, and reconnaissance services."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from dash import Dash, Input, Output, State, ALL, Patch, callback_context, html, no_update
import dash_bootstrap_components as dbc

from plotsiris.domain.constants import REGION_PRESETS, LAYER_DEFINITIONS
from plotsiris.services.data_manager import data_manager
from plotsiris.rendering.map_builder import MapBuilder
from plotsiris.ui.osint_panel import render_osint_result
from plotsiris.ui.ai_panel import render_user_message, render_analyst_message
from plotsiris.ui.breaking_alert import BREAKING_EVENTS

logger = logging.getLogger(__name__)


def register_callbacks(app: Dash) -> None:
    """Register all operational callbacks with the Dash application."""

    # 1. Live UTC Clock Update (Clientside for zero server round-trips)
    app.clientside_callback(
        """
        function(n) {
            const d = new Date();
            return d.toISOString().slice(11, 19) + ' UTC';
        }
        """,
        Output("live-clock-display", "children"),
        Input("clock-interval", "n_intervals")
    )

    # 2. Region Presets: Update Map Camera Target
    @app.callback(
        Output("map-camera-store", "data"),
        Input({"type": "region-preset-btn", "index": ALL}, "n_clicks"),
        Input("btn-alert-locate", "n_clicks"),
        State("breaking-alert-store", "data"),
        State("map-camera-store", "data"),
        prevent_initial_call=True
    )
    def handle_region_preset(n_clicks_list, n_locate, alert_data, current_camera):
        ctx = callback_context
        if not ctx.triggered:
            return current_camera

        triggered_id = ctx.triggered_id
        curr_cam = current_camera or {"lat": 20.0, "lon": 15.0, "zoom": 1.6, "rev": 0}
        next_rev = curr_cam.get("rev", 0) + 1

        if triggered_id == "btn-alert-locate":
            if alert_data and "lat" in alert_data:
                return {
                    "lat": alert_data["lat"],
                    "lon": alert_data["lon"],
                    "zoom": alert_data.get("zoom", 5.8),
                    "rev": next_rev
                }
            return current_camera

        if isinstance(triggered_id, dict) and triggered_id.get("type") == "region-preset-btn":
            preset_key = triggered_id.get("index")
            preset = REGION_PRESETS.get(preset_key)
            if preset:
                return {
                    "lat": preset["lat"],
                    "lon": preset["lon"],
                    "zoom": preset["zoom"],
                    "rev": next_rev
                }

        return current_camera

    # 2b. Live Breaking Event Alert Manager (Top-Right HUD Alert)
    @app.callback(
        Output("alert-tag", "children"),
        Output("alert-badge", "children"),
        Output("alert-badge", "color"),
        Output("alert-title", "children"),
        Output("alert-source-region", "children"),
        Output("alert-time", "children"),
        Output("alert-summary", "children"),
        Output("alert-strip", "className"),
        Output("breaking-alert-wrapper", "style"),
        Output("breaking-alert-store", "data"),
        Input("breaking-alert-interval", "n_intervals"),
        Input("btn-dismiss-alert", "n_clicks"),
        State("breaking-alert-store", "data"),
        prevent_initial_call=True
    )
    def manage_breaking_alert(n_intervals, n_dismiss, store_data):
        ctx = callback_context
        if not ctx.triggered:
            return (no_update,) * 10

        triggered_id = ctx.triggered_id
        if store_data is None:
            store_data = {"index": 0, "visible": True}

        # Dismiss button clicked
        if triggered_id == "btn-dismiss-alert":
            new_store = dict(store_data)
            new_store["visible"] = False
            return (
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, {"display": "none"}, new_store
            )

        # Interval triggered -> cycle to next breaking event and make visible
        curr_idx = store_data.get("index", 0)
        next_idx = (curr_idx + 1) % len(BREAKING_EVENTS)
        event = BREAKING_EVENTS[next_idx]
        sev = event.get("sev", "CRITICAL")
        sev_color = "danger" if sev == "CRITICAL" else "warning"

        new_store = {
            "index": next_idx,
            "visible": True,
            "lat": event["lat"],
            "lon": event["lon"],
            "zoom": event.get("zoom", 5.8)
        }

        return (
            event.get("tag", "BREAKING INTEL // PRIORITY 1"),
            sev,
            sev_color,
            event.get("title", ""),
            f"{event.get('source')} · {event.get('region')}",
            event.get("time", "Just Now"),
            event.get("summary", ""),
            f"breaking-alert-strip {sev.lower()}",
            {"display": "block"},
            new_store
        )

    # 3. Main Map Figure Generation
    @app.callback(
        Output("main-map", "figure"),
        Output({"type": "layer-count", "index": ALL}, "children"),
        Input({"type": "layer-toggle", "index": ALL}, "value"),
        Input("map-camera-store", "data"),
        Input("theme-store", "data"),
        Input("feed-refresh-interval", "n_intervals"),
        State({"type": "layer-toggle", "index": ALL}, "id")
    )
    def update_map(toggle_values, camera, theme, _, toggle_ids):
        ctx = callback_context
        active_layers = []
        for val, item_id in zip(toggle_values, toggle_ids):
            if val:
                active_layers.append(item_id["index"])

        entities = data_manager.get_all_entities(active_layers)
        routes = data_manager.get_route_paths(active_layers)
        counts = data_manager.get_layer_counts()

        triggered_id = ctx.triggered_id if ctx.triggered else None
        is_explicit_camera_jump = (triggered_id == "map-camera-store") or (triggered_id is None)

        camera = camera or {"lat": 20.0, "lon": 15.0, "zoom": 1.6, "rev": 0}
        rev_id = f"cam_rev_{camera.get('rev', 0)}"

        fig = MapBuilder.build_map(
            entities=entities,
            routes=routes,
            center_lat=camera.get("lat", 20.0),
            center_lon=camera.get("lon", 15.0),
            zoom=camera.get("zoom", 1.6),
            theme=theme or "ghost",
            uirevision=rev_id
        )

        counts_list = [str(counts.get(item_id["index"], 0)) for item_id in toggle_ids]

        if is_explicit_camera_jump:
            return fig, counts_list

        # For background feed refreshes, layer toggles, and theme changes,
        # return a Patch that updates data/styling ONLY without touching map center/zoom!
        fig_dict = fig.to_dict()
        fig_patch = Patch()
        fig_patch["data"] = fig_dict["data"]
        if triggered_id == "theme-store":
            layout_d = fig_dict.get("layout", {})
            fig_patch["layout"]["paper_bgcolor"] = layout_d.get("paper_bgcolor")
            fig_patch["layout"]["plot_bgcolor"] = layout_d.get("plot_bgcolor")
            fig_patch["layout"]["font"] = layout_d.get("font")
            fig_patch["layout"]["legend"] = layout_d.get("legend")
            fig_patch["layout"]["hoverlabel"] = layout_d.get("hoverlabel")
            map_key = "map" if "map" in layout_d else "mapbox"
            if map_key in layout_d:
                fig_patch["layout"][map_key]["style"] = layout_d[map_key].get("style")

        return fig_patch, counts_list

    # 4. Select All Layers Button
    @app.callback(
        Output({"type": "layer-toggle", "index": ALL}, "value"),
        Input("btn-select-all-layers", "n_clicks"),
        State({"type": "layer-toggle", "index": ALL}, "value"),
        prevent_initial_call=True
    )
    def select_all_layers(n_clicks, current_values):
        all_on = all(current_values)
        return [not all_on] * len(current_values)

    # 5. Map & Graph Click Inspection Card (Prominent Centered Modal with Spinner)
    @app.callback(
        Output("selected-entity-store", "data"),
        Output("inspector-card-backdrop", "style"),
        Output("inspector-title", "children"),
        Output("inspector-category", "children"),
        Output("inspector-description", "children"),
        Output("inspector-coords", "children"),
        Output("inspector-severity-badge", "children"),
        Output("inspector-severity-badge", "color"),
        Output("btn-inspector-camera", "style"),
        Input("main-map", "clickData"),
        Input("main-graph", "clickData"),
        Input("btn-close-inspector", "n_clicks"),
        Input("btn-inspector-camera", "n_clicks"),
        Input("btn-inspector-osint", "n_clicks"),
        Input("btn-inspector-ai", "n_clicks"),
        State("selected-entity-store", "data"),
        prevent_initial_call=True
    )
    def inspect_map_point(map_click, graph_click, close_clicks, n_cam, n_osint, n_ai, current_entity):
        ctx = callback_context
        if not ctx.triggered:
            return current_entity, {"display": "none"}, no_update, no_update, no_update, no_update, no_update, no_update, no_update

        triggered_id = ctx.triggered_id
        # When user clicks Close or any action button on the inspector modal (CCTV, OSINT, AI), close the modal immediately
        if triggered_id in ("btn-close-inspector", "btn-inspector-camera", "btn-inspector-osint", "btn-inspector-ai"):
            return current_entity, {"display": "none"}, no_update, no_update, no_update, no_update, no_update, no_update, no_update

        click_data = map_click if triggered_id == "main-map" else graph_click

        if click_data and "points" in click_data and len(click_data["points"]) > 0:
            # Simulated high-precision target lock-in telemetry delay for spinner
            time.sleep(0.35)
            point = click_data["points"][0]
            custom = point.get("customdata")
            if custom and isinstance(custom, dict):
                sev = custom.get("severity", "INFO")
                color = "danger" if sev in ("CRITICAL", "HIGH") else ("warning" if sev == "ELEVATED" else "info")
                is_cctv = custom.get("category") == "cctv"
                camera_btn_style = {"display": "inline-block"} if is_cctv else {"display": "none"}

                lat = custom.get("lat", 0.0)
                lon = custom.get("lon", 0.0)

                return (
                    custom,
                    {"display": "flex"},
                    custom.get("title", "Selected Entity"),
                    custom.get("subcategory", custom.get("category", "Intelligence Item")).upper(),
                    custom.get("description", "No details available."),
                    f"Coordinates: {lat:.4f}°, {lon:.4f}°",
                    sev,
                    color,
                    camera_btn_style
                )
            else:
                # Handle graph nodes or points without full customdata dict
                node_text = point.get("text", "Topological Node")
                if isinstance(node_text, str) and node_text.strip():
                    clean_title = node_text.strip()
                else:
                    clean_title = "Selected Intelligence Node"
                return (
                    {"title": clean_title, "category": "threat_graph", "severity": "HIGH", "lat": 0.0, "lon": 0.0},
                    {"display": "flex"},
                    clean_title,
                    "TOPOLOGICAL THREAT NODE",
                    f"Correlated cluster node active in C2 focal matrix: {clean_title}",
                    "Normalized Vectors: [AZ 38.8°, Z 235]",
                    "ACTIVE",
                    "info",
                    {"display": "none"}
                )

        return None, {"display": "none"}, "", "", "", "", "", "info", {"display": "none"}

    # 6. Offcanvas Drawers Toggle
    @app.callback(
        Output("osint-offcanvas", "is_open"),
        Input("btn-open-osint", "n_clicks"),
        Input("btn-inspector-osint", "n_clicks"),
        State("osint-offcanvas", "is_open"),
        prevent_initial_call=True
    )
    def toggle_osint(n1, n2, is_open):
        ctx = callback_context
        if ctx.triggered_id == "btn-inspector-osint":
            return True
        return not is_open

    @app.callback(
        Output("ai-offcanvas", "is_open"),
        Input("btn-open-ai", "n_clicks"),
        Input("btn-inspector-ai", "n_clicks"),
        State("ai-offcanvas", "is_open"),
        prevent_initial_call=True
    )
    def toggle_ai(n1, n2, is_open):
        ctx = callback_context
        if ctx.triggered_id == "btn-inspector-ai":
            return True
        return not is_open

    @app.callback(
        Output("cyber-offcanvas", "is_open"),
        Input("btn-open-cyber", "n_clicks"),
        State("cyber-offcanvas", "is_open"),
        prevent_initial_call=True
    )
    def toggle_cyber(n, is_open):
        return not is_open

    @app.callback(
        Output("markets-offcanvas", "is_open"),
        Input("btn-open-markets", "n_clicks"),
        State("markets-offcanvas", "is_open"),
        prevent_initial_call=True
    )
    def toggle_markets(n, is_open):
        return not is_open

    @app.callback(
        Output("news-offcanvas", "is_open"),
        Input("btn-open-news", "n_clicks"),
        Input("btn-alert-intel", "n_clicks"),
        State("news-offcanvas", "is_open"),
        prevent_initial_call=True
    )
    def toggle_news(n_open, n_alert, is_open):
        return not is_open

    @app.callback(
        Output("entity-graph-modal", "is_open"),
        Input("btn-open-graph", "n_clicks"),
        Input("btn-close-graph-modal", "n_clicks"),
        State("entity-graph-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_graph(n_open, n_close, is_open):
        return not is_open

    # 7. CCTV Camera Viewer Modal (Real DOT Snapshots, TfL Streams & Channel Switching)
    app.clientside_callback(
        """
        function(n_intervals, active_feed, ptz_state) {
            const d = new Date();
            const utc = d.toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
            const mode = (active_feed && active_feed.mode === 'video') ? 'STREAM' : 'LIVE SENSOR';
            const z = (ptz_state && ptz_state.zoom) ? Number(ptz_state.zoom) : 1.0;
            const zoom = (z === 1.0) ? '1.0' : z.toFixed(2).replace(/0$/, '');
            return 'LIVE // ' + utc + ' // ' + mode + ' // PTZ ' + zoom + 'x';
        }
        """,
        Output("camera-hud-timestamp", "children"),
        Input("camera-live-tick-interval", "n_intervals"),
        Input("camera-active-feed-store", "data"),
        Input("camera-ptz-store", "data"),
    )

    @app.callback(
        Output("camera-modal", "is_open"),
        Output("camera-live-tick-interval", "disabled"),
        Output("camera-snapshot-refresh-interval", "disabled"),
        Output("camera-modal-title", "children"),
        Output("camera-stream-video", "src"),
        Output("camera-stream-img", "src"),
        Output("camera-metadata", "children"),
        Output("camera-active-feed-store", "data"),
        Output("camera-channel-select", "value"),
        Output("camera-hud-channel-badge", "children"),
        Output("btn-cam-mode-snapshot", "outline"),
        Output("btn-cam-mode-video", "outline"),
        Input("btn-inspector-camera", "n_clicks"),
        Input("btn-open-cctv", "n_clicks"),
        Input("btn-close-camera-modal", "n_clicks"),
        Input("camera-channel-select", "value"),
        Input("btn-cam-next", "n_clicks"),
        Input("btn-cam-refresh", "n_clicks"),
        Input("btn-cam-mode-snapshot", "n_clicks"),
        Input("btn-cam-mode-video", "n_clicks"),
        Input("camera-snapshot-refresh-interval", "n_intervals"),
        State("selected-entity-store", "data"),
        State("camera-modal", "is_open"),
        State("camera-active-feed-store", "data"),
        prevent_initial_call=True
    )
    def manage_camera_viewer(
        n_insp,
        n_cctv,
        n_close,
        selected_channel,
        n_next,
        n_refresh,
        n_mode_snap,
        n_mode_vid,
        n_intervals,
        selected_entity,
        is_open,
        active_feed,
    ):
        from plotsiris.domain.constants import CCTV_REGISTRY
        from plotsiris.services.cctv import CctvService

        ctx = callback_context
        if not ctx.triggered:
            return (no_update,) * 12

        triggered_id = ctx.triggered_id

        if triggered_id == "btn-close-camera-modal":
            # Stop active video/network stream cleanly when modal closes
            return False, True, True, no_update, "", no_update, no_update, no_update, no_update, no_update, no_update, no_update

        cctv_service = CctvService()

        # Background 5s timer inside modal: auto-refresh live snapshot feeds
        if triggered_id == "camera-snapshot-refresh-interval":
            if not is_open or not active_feed:
                return (no_update,) * 12
            mode = active_feed.get("mode", "live_snapshot")
            if mode != "live_snapshot":
                return (no_update,) * 12

            feed = cctv_service.resolve_live_feed(
                active_feed.get("id"),
                cache_buster=True,
                preferred_mode="live_snapshot",
            )
            badge = "LIVE SENSOR // AUTO-REFRESH 5s" if feed["is_external_live"] else "OPTICAL SENSOR // STANDBY"
            meta_text = (
                f"Location: {feed['country']} ({feed['lat']:.4f}°, {feed['lon']:.4f}°) | "
                f"Authority: {feed['provider']} | Mode: LIVE DOT SNAPSHOT (Synced {feed['resolved_utc']})"
            )
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                feed["snapshot_url"],
                meta_text,
                feed,
                no_update,
                badge,
                False,
                True,
            )

        # Resolve target cam_id and preferred mode based on trigger
        target_cam_id: Optional[str] = None
        preferred_mode: Optional[str] = None

        if triggered_id in ("btn-inspector-camera", "btn-open-cctv"):
            entity = selected_entity or {}
            props = entity.get("properties") or {}
            if props.get("id") and any(c["id"] == props["id"] for c in CCTV_REGISTRY):
                target_cam_id = props["id"]
            elif CCTV_REGISTRY:
                target_cam_id = CCTV_REGISTRY[0]["id"]
        elif triggered_id == "camera-channel-select":
            if not is_open:
                return (no_update,) * 12
            if active_feed and selected_channel == active_feed.get("id"):
                return (no_update,) * 12
            target_cam_id = selected_channel
        elif triggered_id == "btn-cam-next":
            ids = [c["id"] for c in CCTV_REGISTRY]
            curr_id = (active_feed or {}).get("id") or selected_channel
            if curr_id in ids:
                target_cam_id = ids[(ids.index(curr_id) + 1) % len(ids)]
            else:
                target_cam_id = ids[0] if ids else None
        elif triggered_id == "btn-cam-refresh":
            target_cam_id = (active_feed or {}).get("id") or selected_channel
            preferred_mode = (active_feed or {}).get("mode")
        elif triggered_id == "btn-cam-mode-snapshot":
            target_cam_id = (active_feed or {}).get("id") or selected_channel
            preferred_mode = "live_snapshot"
        elif triggered_id == "btn-cam-mode-video":
            target_cam_id = (active_feed or {}).get("id") or selected_channel
            preferred_mode = "video"

        feed = cctv_service.resolve_live_feed(
            cam_id=target_cam_id,
            cache_buster=True,
            preferred_mode=preferred_mode,
        )
        mode = feed["mode"]

        if mode == "live_snapshot":
            video_src = ""
            img_src = feed["snapshot_url"]
            badge = "LIVE SENSOR // AUTO-REFRESH 5s" if feed["is_external_live"] else "OPTICAL SENSOR // STANDBY"
            status_desc = f"ONLINE (Live DOT Frame Sync · {feed['resolved_utc']})"
            snap_outline = False
            vid_outline = True
            snap_refresh_disabled = False
        else:
            video_src = feed["stream_url"]
            img_src = feed["snapshot_url"]
            is_ext_vid = str(feed["stream_url"]).startswith("http")
            badge = "LIVE MUNICIPAL STREAM" if is_ext_vid else "OPTICAL ARCHIVE STREAM"
            status_desc = (
                f"ONLINE (Live Authority Stream · {feed['resolved_utc']})"
                if is_ext_vid
                else f"ONLINE (Optical Sector Clip · {feed['resolved_utc']})"
            )
            snap_outline = True
            vid_outline = False
            snap_refresh_disabled = True

        meta_text = (
            f"Location: {feed['country']} ({feed['lat']:.4f}°, {feed['lon']:.4f}°) | "
            f"Authority: {feed['provider']} | Feed Status: {status_desc}"
        )

        return (
            True,
            False,
            snap_refresh_disabled,
            f"SURVEILLANCE: {feed['name']}",
            video_src,
            img_src,
            meta_text,
            feed,
            feed["id"],
            badge,
            snap_outline,
            vid_outline,
        )

    # 7b. Camera PTZ Zoom & Optical Filters (Normal, NVG Green, FLIR Thermal)
    @app.callback(
        Output("camera-ptz-store", "data"),
        Output("btn-cam-opt-normal", "color"),
        Output("btn-cam-opt-nvg", "color"),
        Output("btn-cam-opt-flir", "color"),
        Input("btn-cam-opt-normal", "n_clicks"),
        Input("btn-cam-opt-nvg", "n_clicks"),
        Input("btn-cam-opt-flir", "n_clicks"),
        Input("btn-cam-zoom-in", "n_clicks"),
        Input("btn-cam-zoom-out", "n_clicks"),
        State("camera-ptz-store", "data"),
        prevent_initial_call=True
    )
    def update_camera_ptz_store(n_norm, n_nvg, n_flir, n_zin, n_zout, ptz_state):
        ctx = callback_context
        state = dict(ptz_state or {"zoom": 1.0, "filter": "normal"})
        if not ctx.triggered:
            return state, "info", "outline-success", "outline-warning"

        tid = ctx.triggered_id
        zoom_steps = [1.0, 1.35, 1.75, 2.2, 2.6]
        curr_zoom = float(state.get("zoom", 1.0))

        if tid == "btn-cam-opt-normal":
            state["filter"] = "normal"
        elif tid == "btn-cam-opt-nvg":
            state["filter"] = "nvg"
        elif tid == "btn-cam-opt-flir":
            state["filter"] = "flir"
        elif tid == "btn-cam-zoom-in":
            next_steps = [z for z in zoom_steps if z > curr_zoom + 0.05]
            state["zoom"] = next_steps[0] if next_steps else zoom_steps[-1]
        elif tid == "btn-cam-zoom-out":
            prev_steps = [z for z in zoom_steps if z < curr_zoom - 0.05]
            state["zoom"] = prev_steps[-1] if prev_steps else zoom_steps[0]

        filt = state.get("filter", "normal")
        c_norm = "info" if filt == "normal" else "outline-info"
        c_nvg = "success" if filt == "nvg" else "outline-success"
        c_flir = "warning" if filt == "flir" else "outline-warning"
        return state, c_norm, c_nvg, c_flir

    @app.callback(
        Output("camera-stream-video", "style"),
        Output("camera-stream-img", "style"),
        Input("camera-active-feed-store", "data"),
        Input("camera-ptz-store", "data"),
    )
    def apply_camera_display_style(active_feed, ptz_state):
        mode = (active_feed or {}).get("mode", "live_snapshot")
        ptz = ptz_state or {"zoom": 1.0, "filter": "normal"}
        zoom = float(ptz.get("zoom", 1.0))
        filt = ptz.get("filter", "normal")

        filter_css = "none"
        if filt == "nvg":
            filter_css = "sepia(100%) hue-rotate(80deg) saturate(350%) contrast(160%) brightness(1.1)"
        elif filt == "flir":
            filter_css = "invert(100%) hue-rotate(180deg) contrast(220%) saturate(200%)"

        common_style = {
            "maxHeight": "440px",
            "objectFit": "cover",
            "backgroundColor": "#050810",
            "width": "100%",
            "transform": f"scale({zoom:.2f})",
            "transformOrigin": "center center",
            "transition": "transform 0.2s ease, filter 0.2s ease",
            "filter": filter_css,
        }
        v_style = {**common_style, "display": "block" if mode == "video" else "none"}
        i_style = {**common_style, "display": "block" if mode == "live_snapshot" else "none"}
        return v_style, i_style

    # 8. OSINT Quick Target Presets
    @app.callback(
        Output("osint-target-input", "value"),
        Input("btn-target-google", "n_clicks"),
        Input("btn-target-nmap", "n_clicks"),
        Input("btn-target-cloudflare", "n_clicks"),
        Input("btn-target-tor", "n_clicks"),
        Input("btn-target-cve", "n_clicks"),
        Input("btn-inspector-osint", "n_clicks"),
        State("selected-entity-store", "data"),
        prevent_initial_call=True
    )
    def fill_osint_target(n1, n_nmap, n2, n3, n4, n_insp, entity):
        ctx = callback_context
        if not ctx.triggered:
            return ""
        tid = ctx.triggered_id
        if tid == "btn-target-google":
            return "google.com"
        elif tid == "btn-target-nmap":
            return "scanme.nmap.org"
        elif tid == "btn-target-cloudflare":
            return "1.1.1.1"
        elif tid == "btn-target-tor":
            return "185.220.101.5"
        elif tid == "btn-target-cve":
            return "CVE-2024-38077"
        elif tid == "btn-inspector-osint" and entity:
            props = entity.get("properties", {})
            return props.get("ip") or props.get("callsign") or entity.get("title", "")
        return ""

    # 8b. Dynamic Authorisation & Scoping Gate
    @app.callback(
        Output("osint-auth-gate-container", "children"),
        Input("osint-tool-select", "value")
    )
    def render_auth_gate(tool_id):
        from plotsiris.domain.constants import ACTIVE_OSINT_TOOLS
        if tool_id in ACTIVE_OSINT_TOOLS:
            return dbc.Alert(
                children=[
                    html.Div(className="d-flex align-items-center mb-1", children=[
                        html.I(className="bi bi-shield-exclamation text-danger fs-5 me-2"),
                        html.Strong("ACTIVE RECONNAISSANCE GATEWAY — AUTHORISATION REQUIRED", className="text-danger small")
                    ]),
                    html.P(
                        "This engine generates direct network packets against the target. "
                        "Under the Computer Misuse Act 1990 and international cyber regulations, "
                        "unauthorized connection attempts without explicit permission carry clear legal exposure.",
                        className="small text-light mb-2"
                    ),
                    html.Div(
                        className="p-2 mb-2 rounded bg-black bg-opacity-50 border border-danger border-opacity-50",
                        children=[
                            dbc.Checklist(
                                id="osint-auth-checkbox",
                                options=[{
                                    "label": " I certify that I own this target or possess formal written authorization to conduct connection probes against it.",
                                    "value": "authorized"
                                }],
                                value=[],
                                className="small text-warning fw-bold"
                            )
                        ]
                    ),
                    html.Small([
                        html.Span("For testing without written consent, use the pre-authorized test target: "),
                        html.Code("scanme.nmap.org", className="text-info")
                    ], className="text-muted")
                ],
                color="danger",
                className="py-2 px-3 border-danger shadow-sm"
            )
        else:
            return html.Div(
                children=[
                    # Hidden dummy checkbox so Dash callback State resolution succeeds for passive tools
                    html.Div(dbc.Checklist(id="osint-auth-checkbox", options=[], value=[]), style={"display": "none"}),
                    html.Div(
                        className="p-2 mb-2 rounded bg-black bg-opacity-25 border border-success border-opacity-25 d-flex align-items-center",
                        children=[
                            html.I(className="bi bi-shield-check text-success fs-6 me-2"),
                            html.Div([
                                html.Span("PASSIVE DIRECTORY QUERY: ", className="text-success fw-bold small"),
                                html.Span("Queries public DNS, RDAP, or Certificate Transparency caches. Zero packets generated against target.", className="text-muted small")
                            ])
                        ]
                    )
                ]
            )

    # 9. Execute OSINT Reconnaissance Tool
    @app.callback(
        Output("osint-results-container", "children"),
        Output("osint-latest-result-store", "data"),
        Input("btn-run-osint", "n_clicks"),
        State("osint-tool-select", "value"),
        State("osint-target-input", "value"),
        State("osint-auth-checkbox", "value"),
        prevent_initial_call=True
    )
    def execute_osint_scan(n_clicks, tool_id, target, auth_values):
        if not target:
            return dbc.Alert("Please specify a target hostname, IP, or identifier.", color="warning", className="small"), None

        from plotsiris.domain.constants import ACTIVE_OSINT_TOOLS, APPROVED_DEMO_TARGETS
        target_clean = target.strip().replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]

        if tool_id in ACTIVE_OSINT_TOOLS:
            is_authorized = bool(auth_values and "authorized" in auth_values)
            is_demo = target_clean in APPROVED_DEMO_TARGETS
            if not is_authorized and not is_demo:
                blocked_alert = dbc.Alert(
                    children=[
                        html.Div(className="d-flex align-items-center mb-2", children=[
                            html.I(className="bi bi-x-octagon-fill text-danger fs-4 me-2"),
                            html.H6("ACTIVE RECONNAISSANCE BLOCKED — AUTHORISATION REQUIRED", className="text-danger fw-bold m-0")
                        ]),
                        html.P(
                            f"Execution of '{tool_id.upper()}' against '{target}' was aborted. "
                            "Active port scanning generates outbound connection attempts against the target system. "
                            "In accordance with the Computer Misuse Act 1990 and responsible disclosure standards, "
                            "operators must explicitly confirm ownership or written authorization before initiating active scans.",
                            className="small text-light mb-2"
                        ),
                        html.P([
                            html.Em('"The line between intelligence and intrusion is an authorisation boundary, not a capability one." '),
                            html.Span("— Red Specter Security Research (DOI: 10.5281/zenodo.23924318)")
                        ], className="small text-warning mb-2"),
                        html.Small("Action: Check the authorization certification box above, or select an authorized target such as 'scanme.nmap.org'.", className="text-muted d-block")
                    ],
                    color="danger",
                    className="p-3 border-danger shadow-sm"
                )
                return blocked_alert, None

        result = data_manager.osint_toolkit.run_tool(tool_id=tool_id, target=target, is_authorized=True)
        result_dict = result.to_dict()
        return render_osint_result(result_dict), result_dict

    # 10. Pin OSINT Finding to Map
    @app.callback(
        Output("btn-pin-recon-result", "disabled"),
        Output("btn-pin-recon-result", "children"),
        Input("btn-pin-recon-result", "n_clicks"),
        State("osint-latest-result-store", "data"),
        prevent_initial_call=True
    )
    def pin_finding_to_map(n_clicks, result_dict):
        if not result_dict:
            return True, "No Coordinates"

        coords = result_dict.get("coordinates")
        if coords:
            from plotsiris.domain.models import OsintResult
            res_obj = OsintResult(
                tool=result_dict.get("tool", "recon"),
                target=result_dict.get("target", ""),
                status=result_dict.get("status", "SUCCESS"),
                verdict=result_dict.get("verdict", "CLEAN"),
                summary=result_dict.get("summary", ""),
                details=result_dict.get("details", {}),
                coordinates=coords
            )
            data_manager.pin_recon_result(res_obj)
            return True, "✓ PINNED TO MAP"
        return False, "Failed to Pin"

    # 11. AI Analyst Tactical Prompts
    @app.callback(
        Output("ai-query-input", "value"),
        Input("btn-prompt-top3", "n_clicks"),
        Input("btn-prompt-redsea", "n_clicks"),
        Input("btn-prompt-cyber", "n_clicks"),
        Input("btn-prompt-space", "n_clicks"),
        Input("btn-inspector-ai", "n_clicks"),
        State("selected-entity-store", "data"),
        prevent_initial_call=True
    )
    def fill_ai_prompt(n1, n2, n3, n4, n_insp, entity):
        ctx = callback_context
        if not ctx.triggered:
            return ""
        tid = ctx.triggered_id
        if tid == "btn-prompt-top3":
            return "What are the top 3 global strategic threats right now?"
        elif tid == "btn-prompt-redsea":
            return "Assess maritime transit security in the Red Sea and Bab el-Mandeb."
        elif tid == "btn-prompt-cyber":
            return "Summarize active CISA KEV vulnerabilities and critical infrastructure exposure."
        elif tid == "btn-prompt-space":
            return "Evaluate current space weather Kp index and orbital tracking risks."
        elif tid == "btn-inspector-ai" and entity:
            return f"Assess strategic and tactical implications of {entity.get('title')} ({entity.get('subcategory')})."
        return ""

    # 12. AI Analyst Q&A Chat & Briefing Generator
    @app.callback(
        Output("ai-chat-history", "children"),
        Output("chat-history-store", "data"),
        Input("btn-send-ai-query", "n_clicks"),
        Input("btn-generate-briefing", "n_clicks"),
        State("ai-query-input", "value"),
        State("chat-history-store", "data"),
        prevent_initial_call=True
    )
    def process_ai_interaction(n_send, n_briefing, query_text, history):
        ctx = callback_context
        if not ctx.triggered:
            return [], history

        history = history or []
        tid = ctx.triggered_id

        context = {
            "active_layer_count": 12,
            "layer_counts": data_manager.get_layer_counts(),
            "space_weather": data_manager.get_space_weather(),
            "latest_alerts": [a.title for a in data_manager.get_news_alerts()[:3]]
        }

        if tid == "btn-generate-briefing":
            briefing_text = data_manager.ai_analyst.generate_full_briefing(context)
            history.append({"role": "user", "text": "GENERATE FULL OPERATIONAL SITREP BRIEFING"})
            history.append({"role": "analyst", "text": briefing_text})
        elif tid == "btn-send-ai-query" and query_text:
            ans = data_manager.ai_analyst.answer_query(query_text, context)
            history.append({"role": "user", "text": query_text})
            history.append({"role": "analyst", "text": ans})

        # Render chat bubbles
        rendered_bubbles = [
            render_analyst_message(
                "Plotsiris Tactical Intelligence Center connected. Correlating multi-domain feeds."
            )
        ]
        for msg in history:
            if msg["role"] == "user":
                rendered_bubbles.append(render_user_message(msg["text"]))
            else:
                rendered_bubbles.append(render_analyst_message(msg["text"]))

        return rendered_bubbles, history

    # 13. Theme Switcher: Ghost Protocol (Dark) vs Core (Light)
    @app.callback(
        Output("theme-store", "data"),
        Output("app-root", "className"),
        Input("btn-toggle-theme", "n_clicks"),
        State("theme-store", "data"),
        prevent_initial_call=True
    )
    def toggle_theme(n_clicks, current_theme):
        new_theme = "core" if current_theme == "ghost" else "ghost"
        theme_class = "theme-core position-relative w-100 min-vh-100 bg-white text-dark font-mono" if new_theme == "core" else "theme-ghost position-relative w-100 min-vh-100 bg-black text-light font-mono"
        return new_theme, theme_class

    # 14. Tactical Canvas View Switcher (Constellation Graph vs MapLibre Map)
    @app.callback(
        Output("graph-display-container", "className"),
        Output("map-display-container", "className"),
        Output("btn-view-graph", "color"),
        Output("btn-view-graph", "outline"),
        Output("btn-view-map", "color"),
        Output("btn-view-map", "outline"),
        Output("active-view-mode-store", "data"),
        Input("btn-view-graph", "n_clicks"),
        Input("btn-view-map", "n_clicks"),
        State("active-view-mode-store", "data"),
        prevent_initial_call=True
    )
    def switch_canvas_view(n_graph, n_map, current_mode):
        tid = callback_context.triggered_id
        if tid == "btn-view-map":
            return "w-100 h-100 d-none", "w-100 h-100", "secondary", True, "info", False, "map"
        else:
            return "w-100 h-100", "w-100 h-100 d-none", "info", False, "secondary", True, "graph"

    # 15. Collapsible Left Intelligence Layers Sidebar (Docked & Non-Obscuring)
    @app.callback(
        Output("layers-sidebar", "className"),
        Output("btn-expand-sidebar-tab", "className"),
        Output("btn-toggle-layers-bar", "className"),
        Output("layers-sidebar-open-store", "data"),
        Input("btn-toggle-layer-rail", "n_clicks"),
        Input("btn-toggle-layers-bar", "n_clicks"),
        Input("btn-expand-sidebar-tab", "n_clicks"),
        Input("layers-sidebar-header-title", "n_clicks"),
        State("layers-sidebar-open-store", "data"),
        prevent_initial_call=True
    )
    def toggle_layer_sidebar(n_btn, n_bar, n_tab, n_title, is_open):
        new_state = not is_open if is_open is not None else False
        if new_state:
            sidebar_cls = "layers-sidebar font-mono"
            tab_cls = "expand-sidebar-tab d-none"
            bar_cls = "btn btn-sm btn-dark border-secondary text-info fw-bold py-0 px-2 font-mono"
        else:
            sidebar_cls = "layers-sidebar layers-sidebar-collapsed font-mono"
            tab_cls = "expand-sidebar-tab d-flex"
            bar_cls = "btn btn-sm btn-dark border-secondary text-muted py-0 px-2 font-mono"
        return sidebar_cls, tab_cls, bar_cls, new_state
