"""Plotly MapLibre / Mapbox rendering engine for Plotsiris multi-domain intelligence display."""

from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any
import plotly.graph_objects as go

from plotsiris.domain.models import GeoEntity, RoutePath
from plotsiris.config import MAPBOX_STYLE_DARK, MAPBOX_STYLE_LIGHT

logger = logging.getLogger(__name__)

# Prefer modern MapLibre Scattermap if available, with graceful fallback to Scattermapbox
HAS_SCATTERMAP = hasattr(go, "Scattermap")
TraceScatterGeo = go.Scattermap if HAS_SCATTERMAP else go.Scattermapbox


def _to_rgba(color_str: str, alpha: float = 0.22) -> str:
    """Convert hex or color string to semi-transparent rgba string for subtle HUD vector lines."""
    if not color_str:
        return f"rgba(0, 229, 255, {alpha})"
    c = str(color_str).strip()
    if c.startswith("#"):
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join([x * 2 for x in c])
        if len(c) == 6:
            try:
                r = int(c[0:2], 16)
                g = int(c[2:4], 16)
                b = int(c[4:6], 16)
                return f"rgba({r}, {g}, {b}, {alpha})"
            except ValueError:
                pass
    elif c.startswith("rgba"):
        parts = c.replace("rgba(", "").replace(")", "").split(",")
        if len(parts) >= 3:
            return f"rgba({parts[0].strip()}, {parts[1].strip()}, {parts[2].strip()}, {alpha})"
    elif c.startswith("rgb("):
        parts = c.replace("rgb(", "").replace(")", "").split(",")
        if len(parts) >= 3:
            return f"rgba({parts[0].strip()}, {parts[1].strip()}, {parts[2].strip()}, {alpha})"
    return f"rgba(0, 229, 255, {alpha})"


class MapBuilder:
    """Constructs GPU-accelerated Plotly Map figures with multi-trace layering."""

    @staticmethod
    def build_map(
        entities: List[GeoEntity],
        routes: List[RoutePath],
        center_lat: float = 20.0,
        center_lon: float = 15.0,
        zoom: float = 1.6,
        theme: str = "ghost",
        uirevision: str = "constant_camera"
    ) -> go.Figure:
        """Render a unified Plotly map with all active intelligence traces."""
        map_style = MAPBOX_STYLE_DARK if theme == "ghost" else MAPBOX_STYLE_LIGHT

        fig = go.Figure()

        # 1. Render Polylines as subtle transparent HUD vector paths
        # Plus clickable target endpoint icons with full telemetry inspection
        endpoint_lats = []
        endpoint_lons = []
        endpoint_colors = []
        endpoint_hover_texts = []
        endpoint_custom_data = []

        for route in routes:
            # Alpha based on category for optimal balance
            if route.category in ["conflict", "frontline"]:
                alpha = 0.28
                line_width = 1.2
            elif route.category in ["cables"]:
                alpha = 0.20
                line_width = 1.0
            else:
                alpha = 0.22
                line_width = 1.0

            trans_color = _to_rgba(route.color, alpha)

            # Faint, non-distracting vector line
            fig.add_trace(TraceScatterGeo(
                lat=route.lats,
                lon=route.lons,
                mode="lines",
                name=f"{route.name} (Vector)",
                line=dict(
                    width=line_width,
                    color=trans_color
                ),
                hoverinfo="text",
                hovertext=f"<b>VECTOR TRACK:</b> {route.name}<br><span style='color:#94a3b8;'>Category:</span> {route.category.replace('_', ' ').title()}",
                showlegend=False
            ))

            # Clickable icon at the active endpoint of what's being tracked
            if route.lats and route.lons:
                end_lat = route.lats[-1]
                end_lon = route.lons[-1]
                cat_display = route.category.replace('_', ' ').title()
                sev = "HIGH" if route.category in ["conflict", "frontline"] else ("MEDIUM" if route.category in ["satellites", "satellite_orbit"] else "LOW")

                desc = (
                    f"Active telemetry track for {route.name}. "
                    f"Current terminal coordinate fix: {end_lat:.3f}°, {end_lon:.3f}°. "
                    f"Vector contains {len(route.lats)} telemetry waypoints along corridor."
                )

                hover_html = (
                    f"<b>TARGET TRACK: {route.name}</b><br>"
                    f"<span style='color:#a0aec0;'>Vector:</span> {cat_display}<br>"
                    f"<span style='color:#00e5ff;'>Fix:</span> {end_lat:.3f}°, {end_lon:.3f}°<br>"
                    f"<span style='color:#38bdf8; font-size:10px;'>● Click icon for telemetry brief</span>"
                )

                endpoint_customdata = {
                    "id": f"track_{route.id}",
                    "category": route.category,
                    "subcategory": f"ACTIVE TRACK // {cat_display.upper()}",
                    "title": f"TARGET TRACK: {route.name}",
                    "description": desc,
                    "severity": sev,
                    "color": route.color,
                    "lat": end_lat,
                    "lon": end_lon,
                    "properties": {
                        "target_name": route.name,
                        "vector_type": cat_display,
                        "tracking_status": "LOCKED / ACTIVE VECTOR",
                        "origin_fix": f"{route.lats[0]:.2f}°, {route.lons[0]:.2f}°",
                        "terminal_fix": f"{end_lat:.2f}°, {end_lon:.2f}°",
                        "total_fixes": len(route.lats),
                        **route.properties
                    }
                }

                endpoint_lats.append(end_lat)
                endpoint_lons.append(end_lon)
                endpoint_colors.append(route.color)
                endpoint_hover_texts.append(hover_html)
                endpoint_custom_data.append(endpoint_customdata)

        # Add clickable tracking endpoint icons
        if endpoint_lats:
            fig.add_trace(TraceScatterGeo(
                lat=endpoint_lats,
                lon=endpoint_lons,
                mode="markers",
                name="Tracked Vectors",
                marker=dict(
                    size=10,
                    color=endpoint_colors,
                    opacity=0.95,
                    symbol="circle"
                ),
                text=endpoint_hover_texts,
                hoverinfo="text",
                customdata=endpoint_custom_data,
                showlegend=True
            ))

        # 2. Group Entities by Category for Layered Traces and Legend Toggles
        grouped_entities: Dict[str, List[GeoEntity]] = {}
        for entity in entities:
            grouped_entities.setdefault(entity.category, []).append(entity)

        # Category display configuration
        cat_meta = {
            "aviation": {"name": "Aviation (ADS-B)", "default_color": "#38bdf8"},
            "maritime": {"name": "Maritime (AIS)", "default_color": "#0ea5e9"},
            "chokepoints": {"name": "Strategic Chokepoints", "default_color": "#f59e0b"},
            "cctv": {"name": "CCTV Feeds", "default_color": "#10b981"},
            "earthquakes": {"name": "Earthquakes (USGS)", "default_color": "#ef4444"},
            "fires": {"name": "Wildfires (FIRMS)", "default_color": "#f97316"},
            "weather": {"name": "Severe Weather", "default_color": "#06b6d4"},
            "conflict": {"name": "Conflict Frontlines", "default_color": "#dc2626"},
            "nuclear": {"name": "Nuclear Facilities", "default_color": "#eab308"},
            "cyber": {"name": "Cyber C2 / Threats", "default_color": "#a855f7"},
            "satellites": {"name": "Satellites", "default_color": "#ec4899"},
            "recon": {"name": "OSINT Findings", "default_color": "#00e5ff"},
        }

        for cat, cat_items in grouped_entities.items():
            meta = cat_meta.get(cat, {"name": cat.title(), "default_color": "#00e5ff"})
            lats = [e.lat for e in cat_items]
            lons = [e.lon for e in cat_items]
            colors = [e.color for e in cat_items]
            sizes = [e.size for e in cat_items]
            hover_texts = []
            custom_data = []

            for e in cat_items:
                hover_html = (
                    f"<b>{e.title}</b><br>"
                    f"<span style='color:#a0aec0;'>Category:</span> {e.subcategory}<br>"
                    f"<span style='color:#a0aec0;'>Location:</span> {e.lat:.3f}°, {e.lon:.3f}°<br>"
                    f"{e.description}"
                )
                hover_texts.append(hover_html)
                custom_data.append({
                    "id": e.id,
                    "category": e.category,
                    "subcategory": e.subcategory,
                    "title": e.title,
                    "description": e.description,
                    "severity": e.severity,
                    "color": e.color,
                    "lat": e.lat,
                    "lon": e.lon,
                    "properties": e.properties
                })

            fig.add_trace(TraceScatterGeo(
                lat=lats,
                lon=lons,
                mode="markers",
                name=meta["name"],
                marker=dict(
                    size=sizes,
                    color=colors,
                    opacity=0.92,
                ),
                text=hover_texts,
                hoverinfo="text",
                customdata=custom_data,
                showlegend=True
            ))

        # Layout styling with map controls
        bg_color = "#0a0e14" if theme == "ghost" else "#f8fafc"
        text_color = "#e2e8f0" if theme == "ghost" else "#1e293b"

        rev = uirevision or "constant_camera"
        map_config = dict(
            style=map_style,
            uirevision=rev,
        )
        if center_lat is not None and center_lon is not None:
            map_config["center"] = dict(lat=center_lat, lon=center_lon)
        if zoom is not None:
            map_config["zoom"] = zoom

        layout_kwargs = {
            "margin": dict(l=0, r=0, t=0, b=0),
            "paper_bgcolor": bg_color,
            "plot_bgcolor": bg_color,
            "font": dict(family="JetBrains Mono, monospace, Inter, sans-serif", color=text_color, size=11),
            "legend": dict(
                x=0.015,
                y=0.03,
                bgcolor="rgba(10, 14, 20, 0.85)" if theme == "ghost" else "rgba(255, 255, 255, 0.9)",
                bordercolor="#00e5ff" if theme == "ghost" else "#cbd5e1",
                borderwidth=1,
                font=dict(size=10),
                orientation="h"
            ),
            "hoverlabel": dict(
                bgcolor="#0f172a" if theme == "ghost" else "#ffffff",
                bordercolor="#00e5ff" if theme == "ghost" else "#0284c7",
                font=dict(family="JetBrains Mono, monospace", size=11, color="#f8fafc" if theme == "ghost" else "#0f172a")
            ),
            "uirevision": rev
        }

        layout_kwargs["autosize"] = True
        if HAS_SCATTERMAP:
            layout_kwargs["map"] = map_config
        else:
            layout_kwargs["mapbox"] = map_config

        fig.update_layout(**layout_kwargs)
        return fig
