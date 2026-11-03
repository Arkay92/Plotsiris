"""Dash Callbacks connecting UI components, map interactions, and reconnaissance services."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from dash import Dash, Input, Output, State, ALL, callback_context, html
import dash_bootstrap_components as dbc

from plotsiris.domain.constants import REGION_PRESETS, LAYER_DEFINITIONS
from plotsiris.services.data_manager import data_manager
from plotsiris.rendering.map_builder import MapBuilder
from plotsiris.ui.osint_panel import render_osint_result
from plotsiris.ui.ai_panel import render_user_message, render_analyst_message

logger = logging.getLogger(__name__)


def register_callbacks(app: Dash) -> None:
    """Register all operational callbacks with the Dash application."""

    # 1. Live UTC Clock Update
    @app.callback(
        Output("live-clock-display", "children"),
        Input("clock-interval", "n_intervals")
    )
    def update_clock(_):
        return datetime.utcnow().strftime("%H:%M:%S UTC")

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
        State("entity-graph-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_graph(n, is_open):
        return not is_open

    # 7. CCTV Camera Viewer Modal
    @app.callback(
        Output("camera-modal", "is_open"),
        Output("camera-modal-title", "children"),
        Output("camera-stream-img", "src"),
        Output("camera-metadata", "children"),
        Input("btn-inspector-camera", "n_clicks"),
        State("selected-entity-store", "data"),
        State("camera-modal", "is_open"),
        prevent_initial_call=True
    )
    def open_camera_modal(n_clicks, selected_entity, is_open):
        if not selected_entity:
            return is_open, "SURVEILLANCE FEED", "", ""

        props = selected_entity.get("properties", {})
        stream_url = props.get("stream_url", "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&auto=format&fit=crop&q=80")
        name = props.get("name", selected_entity.get("title", "Camera"))
        country = props.get("country", "Unknown")
        provider = props.get("provider", "Authority")

        meta_text = (
            f"Location: {country} ({selected_entity.get('lat', 0):.4f}°, {selected_entity.get('lon', 0):.4f}°) | "
            f"Authority: {provider} | Feed Status: ONLINE (Authenticated)"
        )
        return True, f"SURVEILLANCE: {name}", stream_url, meta_text

    # 8. OSINT Quick Target Presets
    @app.callback(
        Output("osint-target-input", "value"),
        Input("btn-target-google", "n_clicks"),
        Input("btn-target-cloudflare", "n_clicks"),
        Input("btn-target-tor", "n_clicks"),
        Input("btn-target-cve", "n_clicks"),
        Input("btn-inspector-osint", "n_clicks"),
        State("selected-entity-store", "data"),
        prevent_initial_call=True
    )
    def fill_osint_target(n1, n2, n3, n4, n_insp, entity):
        ctx = callback_context
        if not ctx.triggered:
            return ""
        tid = ctx.triggered_id
        if tid == "btn-target-google":
            return "google.com"
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

    # 9. Execute OSINT Reconnaissance Tool
    @app.callback(
        Output("osint-results-container", "children"),
        Output("osint-latest-result-store", "data"),
        Input("btn-run-osint", "n_clicks"),
        State("osint-tool-select", "value"),
        State("osint-target-input", "value"),
        prevent_initial_call=True
    )
    def execute_osint_scan(n_clicks, tool_id, target):
        if not target:
            return dbc.Alert("Please specify a target hostname, IP, or identifier.", color="warning", className="small"), None

        result = data_manager.osint_toolkit.run_tool(tool_id=tool_id, target=target)
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
