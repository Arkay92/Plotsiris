"""Interactive Map Entity Inspector Detail Floating Card."""

from dash import html
import dash_bootstrap_components as dbc
from typing import Optional, Dict, Any


def create_inspector_card() -> html.Div:
    """Create floating inspector card for selected map entity."""
    return html.Div(
        id="inspector-card-container",
        className="glass-panel inspector-card p-3",
        style={"display": "none"},
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom border-secondary",
                children=[
                    html.Div([
                        html.I(id="inspector-icon", className="bi bi-crosshair me-2 text-info"),
                        html.Span(id="inspector-category", className="text-info fw-bold small text-uppercase", children="ENTITY INSPECTOR")
                    ]),
                    html.Div([
                        dbc.Badge(id="inspector-severity-badge", children="INFO", color="info", className="me-2 small"),
                        dbc.Button(
                            html.I(className="bi bi-x-lg"),
                            id="btn-close-inspector",
                            size="sm",
                            color="link",
                            className="p-0 text-white text-decoration-none"
                        )
                    ])
                ]
            ),
            html.H6(id="inspector-title", className="text-white fw-bold mb-1", children="Entity Selected"),
            html.P(id="inspector-description", className="text-muted small mb-2", children="Click any marker on the map to inspect full telemetry and intelligence properties."),
            html.Div(
                id="inspector-coords",
                className="text-secondary small mb-3",
                style={"fontSize": "0.72rem"},
                children="Coordinates: 0.000°, 0.000°"
            ),
            html.Div(
                className="d-flex gap-2",
                children=[
                    dbc.Button(
                        [html.I(className="bi bi-cpu me-1"), "AI Assess"],
                        id="btn-inspector-ai",
                        color="info",
                        size="sm",
                        className="flex-fill fw-bold"
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-search me-1"), "OSINT Recon"],
                        id="btn-inspector-osint",
                        color="secondary",
                        outline=True,
                        size="sm",
                        className="flex-fill fw-bold"
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-camera-video me-1"), "View Stream"],
                        id="btn-inspector-camera",
                        color="success",
                        size="sm",
                        className="flex-fill fw-bold",
                        style={"display": "none"}
                    )
                ]
            )
        ]
    )
