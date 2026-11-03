"""Dash Callbacks connecting UI components, map interactions, and reconnaissance services."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from dash import Dash, Input, Output, State, ALL, callback_context, html, no_update
import dash_bootstrap_components as dbc

from plotsiris.domain.constants import REGION_PRESETS, LAYER_DEFINITIONS
from plotsiris.services.data_manager import data_manager
from plotsiris.rendering.map_builder import MapBuilder
from plotsiris.ui.osint_panel import render_osint_result
from plotsiris.ui.ai_panel import render_user_message, render_analyst_message

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
        State("map-camera-store", "data"),
        prevent_initial_call=True
    )
    def handle_region_preset(n_clicks_list, current_camera):
        ctx = callback_context
        if not ctx.triggered:
            return current_camera

        triggered_id = ctx.triggered_id
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "region-preset-btn":
            preset_key = triggered_id.get("index")
            preset = REGION_PRESETS.get(preset_key)
            if preset:
                return {"lat": preset["lat"], "lon": preset["lon"], "zoom": preset["zoom"]}
        return current_camera

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
        active_layers = []
        for val, item_id in zip(toggle_values, toggle_ids):
            if val:
                active_layers.append(item_id["index"])

        entities = data_manager.get_all_entities(active_layers)
        routes = data_manager.get_route_paths(active_layers)
        counts = data_manager.get_layer_counts()

        camera = camera or {"lat": 20.0, "lon": 15.0, "zoom": 1.6}
        fig = MapBuilder.build_map(
            entities=entities,
            routes=routes,
            center_lat=camera["lat"],
            center_lon=camera["lon"],
            zoom=camera["zoom"],
            theme=theme or "ghost"
        )

        counts_list = [str(counts.get(item_id["index"], 0)) for item_id in toggle_ids]
        return fig, counts_list

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

    # 5. Map Click Inspection Card
    @app.callback(
        Output("selected-entity-store", "data"),
        Output("inspector-card-container", "style"),
        Output("inspector-title", "children"),
        Output("inspector-category", "children"),
        Output("inspector-description", "children"),
        Output("inspector-coords", "children"),
        Output("inspector-severity-badge", "children"),
        Output("inspector-severity-badge", "color"),
        Output("btn-inspector-camera", "style"),
        Input("main-map", "clickData"),
        Input("btn-close-inspector", "n_clicks"),
        State("selected-entity-store", "data"),
        prevent_initial_call=True
    )
    def inspect_map_point(click_data, close_clicks, current_entity):
        ctx = callback_context
        if not ctx.triggered:
            return None, {"display": "none"}, "", "", "", "", "", "info", {"display": "none"}

        triggered_id = ctx.triggered_id
        if triggered_id == "btn-close-inspector":
            return None, {"display": "none"}, "", "", "", "", "", "info", {"display": "none"}

        if click_data and "points" in click_data and len(click_data["points"]) > 0:
            point = click_data["points"][0]
            custom = point.get("customdata")
            if custom:
                sev = custom.get("severity", "INFO")
                color = "danger" if sev in ("CRITICAL", "HIGH") else ("warning" if sev == "ELEVATED" else "info")
                is_cctv = custom.get("category") == "cctv"
                camera_btn_style = {"display": "inline-block"} if is_cctv else {"display": "none"}

                lat = custom.get("lat", 0.0)
                lon = custom.get("lon", 0.0)

                return (
                    custom,
                    {"display": "block"},
                    custom.get("title", "Selected Entity"),
                    custom.get("subcategory", custom.get("category", "Intelligence Item")).upper(),
                    custom.get("description", "No details available."),
                    f"Coordinates: {lat:.4f}°, {lon:.4f}°",
                    sev,
                    color,
                    camera_btn_style
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
        return not is_open

    @app.callback(
        Output("ai-offcanvas", "is_open"),
        Input("btn-open-ai", "n_clicks"),
        Input("btn-inspector-ai", "n_clicks"),
        State("ai-offcanvas", "is_open"),
        prevent_initial_call=True
    )
    def toggle_ai(n1, n2, is_open):
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
        State("news-offcanvas", "is_open"),
        prevent_initial_call=True
    )
    def toggle_news(n, is_open):
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

    # 7. CCTV Camera Viewer Modal
    @app.callback(
        Output("camera-modal", "is_open"),
        Output("camera-modal-title", "children"),
        Output("camera-stream-video", "src"),
        Output("camera-stream-img", "src"),
        Output("camera-metadata", "children"),
        Output("camera-hud-timestamp", "children"),
        Input("btn-inspector-camera", "n_clicks"),
        Input("btn-open-cctv", "n_clicks"),
        Input("btn-close-camera-modal", "n_clicks"),
        State("selected-entity-store", "data"),
        State("camera-modal", "is_open"),
        prevent_initial_call=True
    )
    def open_camera_modal(n_insp, n_cctv, n_close, selected_entity, is_open):
        from plotsiris.domain.constants import CCTV_REGISTRY
        ctx = callback_context
        if not ctx.triggered:
            return is_open, no_update, no_update, no_update, no_update, no_update

        triggered_id = ctx.triggered_id
        if triggered_id == "btn-close-camera-modal":
            return False, no_update, no_update, no_update, no_update, no_update

        default_cam = CCTV_REGISTRY[0] if CCTV_REGISTRY else {}

        entity = selected_entity or {
            "title": default_cam.get("name", "San Francisco Bay Bridge / I-80"),
            "lat": default_cam.get("lat", 37.7983),
            "lon": default_cam.get("lon", -122.3778),
            "properties": default_cam
        }

        props = entity.get("properties", default_cam)
        stream_url = props.get("stream_url", "/assets/surveillance_stream.mp4")
        if not stream_url or "unsplash" in stream_url:
            stream_url = "/assets/surveillance_stream.mp4"
        thumb_url = props.get("thumbnail_url", "/assets/surveillance_stream.gif")
        if not thumb_url or thumb_url.endswith(".mp4") or "unsplash" in thumb_url:
            thumb_url = "/assets/surveillance_stream.gif"
        name = props.get("name", entity.get("title", "Surveillance Feed"))
        country = props.get("country", "United States")
        provider = props.get("provider", "Caltrans District 4")

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        meta_text = (
            f"Location: {country} ({entity.get('lat', 0):.4f}°, {entity.get('lon', 0):.4f}°) | "
            f"Authority: {provider} | Feed Status: ONLINE (Authenticated H.264 Live Stream)"
        )
        hud_text = f"STREAM ACTIVE // 30.0 FPS // {now_str}"
        return True, f"SURVEILLANCE: {name}", stream_url, thumb_url, meta_text, hud_text

    # 7b. Camera Optical Filters (Normal, NVG Green, FLIR Thermal)
    @app.callback(
        Output("camera-stream-video", "style"),
        Output("camera-stream-img", "style"),
        Input("btn-cam-opt-normal", "n_clicks"),
        Input("btn-cam-opt-nvg", "n_clicks"),
        Input("btn-cam-opt-flir", "n_clicks"),
        prevent_initial_call=True
    )
    def update_camera_filter(n_norm, n_nvg, n_flir):
        ctx = callback_context
        base_style = {"maxHeight": "440px", "objectFit": "cover", "backgroundColor": "#050810", "width": "100%", "display": "block"}
        if not ctx.triggered:
            return base_style, base_style
        tid = ctx.triggered_id
        if tid == "btn-cam-opt-nvg":
            st = {**base_style, "filter": "sepia(100%) hue-rotate(80deg) saturate(350%) contrast(160%) brightness(1.1)"}
            return st, st
        elif tid == "btn-cam-opt-flir":
            st = {**base_style, "filter": "invert(100%) hue-rotate(180deg) contrast(220%) saturate(200%)"}
            return st, st
        return base_style, base_style

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
        theme_class = "theme-core position-relative vh-100 vw-100 overflow-hidden" if new_theme == "core" else "theme-ghost position-relative vh-100 vw-100 overflow-hidden"
        return new_theme, theme_class
