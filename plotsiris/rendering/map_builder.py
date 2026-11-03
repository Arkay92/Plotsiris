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


class MapBuilder:
    """Constructs GPU-accelerated Plotly Map figures with multi-trace layering."""

    @staticmethod
    def build_map(
        entities: List[GeoEntity],
        routes: List[RoutePath],
        center_lat: float = 20.0,
        center_lon: float = 15.0,
        zoom: float = 1.6,
        theme: str = "ghost"
    ) -> go.Figure:
        """Render a unified Plotly map with all active intelligence traces."""
        map_style = MAPBOX_STYLE_DARK if theme == "ghost" else MAPBOX_STYLE_LIGHT

        fig = go.Figure()

        # 1. Render Polylines / Route Paths (Cables, Flight paths, Orbits, Frontlines)
        for route in routes:
            fig.add_trace(TraceScatterGeo(
                lat=route.lats,
                lon=route.lons,
                mode="lines",
                name=route.name,
                line=dict(
                    width=route.width,
                    color=route.color,
                ),
                hoverinfo="text",
                hovertext=f"<b>{route.name}</b><br>Category: {route.category.replace('_', ' ').title()}",
                showlegend=False
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

        map_config = dict(
            style=map_style,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom,
        )

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
            "uirevision": "constant_camera"
        }

        layout_kwargs["autosize"] = True
        if HAS_SCATTERMAP:
            layout_kwargs["map"] = map_config
        else:
            layout_kwargs["mapbox"] = map_config

        fig.update_layout(**layout_kwargs)
        return fig
