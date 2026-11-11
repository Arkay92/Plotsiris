"""Interactive Map Entity Inspector Detail Floating Card.

Renders a prominent, high-contrast, centered modal HUD card with an animated
loading spinner upon target acquisition.
"""

from __future__ import annotations

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_inspector_card() -> html.Div:
    """Create prominent centered inspector card with loading spinner."""
    return html.Div(
        id="inspector-card-backdrop",
        className="inspector-backdrop",
        style={"display": "none"},
        children=[
            dcc.Loading(
                id="inspector-loading",
                type="circle",
                color="#00e5ff",
                className="inspector-loading-spinner",
                children=[
                    html.Div(
                        id="inspector-card-container",
                        className="glass-panel inspector-card p-4 font-mono",
                        children=[
                            # Header Bar
                            html.Div(
                                className="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom border-secondary border-opacity-50",
                                children=[
                                    html.Div(className="d-flex align-items-center gap-2", children=[
                                        html.I(id="inspector-icon", className="bi bi-crosshair text-info fs-5"),
                                        html.Span(
                                            id="inspector-category",
                                            className="text-info fw-bold font-mono text-uppercase small",
                                            children="ENTITY INSPECTOR"
                                        ),
                                        dbc.Badge(
                                            "GROUND TRUTH",
                                            color="dark",
                                            className="text-success border border-success border-opacity-50 font-mono small py-1 px-2"
                                        )
                                    ]),
                                    html.Div(className="d-flex align-items-center gap-2", children=[
                                        dbc.Badge(
                                            id="inspector-severity-badge",
                                            children="INFO",
                                            color="info",
                                            className="font-mono small py-1 px-2"
                                        ),
                                        dbc.Button(
                                            html.I(className="bi bi-x-lg"),
                                            id="btn-close-inspector",
                                            n_clicks=0,
                                            size="sm",
                                            color="link",
                                            className="p-1 text-secondary text-decoration-none hover-white",
                                            title="Close Inspector"
                                        )
                                    ])
                                ]
                            ),

                            # Entity Title & Subtitle Description
                            html.H5(
                                id="inspector-title",
                                className="text-white fw-bold mb-2 font-mono",
                                children="Target Entity"
                            ),
                            html.P(
                                id="inspector-description",
                                className="text-light text-opacity-80 small mb-3 font-mono",
                                style={"fontSize": "0.82rem", "lineHeight": "1.45"},
                                children="Telemetry and intelligence properties locked."
                            ),

                            # Telemetry & Geolocation Details Box
                            html.Div(
                                className="p-2 mb-3 rounded bg-black bg-opacity-70 border border-secondary border-opacity-40 font-mono d-flex justify-content-between align-items-center",
                                children=[
                                    html.Div([
                                        html.Span("GEO-COORDINATES: ", className="text-secondary small d-block", style={"fontSize": "0.65rem"}),
                                        html.Span(id="inspector-coords", className="text-info fw-bold small", children="0.000°, 0.000°")
                                    ]),
                                    html.Div(className="text-end", children=[
                                        html.Span("VERIFICATION: ", className="text-secondary small d-block", style={"fontSize": "0.65rem"}),
                                        html.Span("DETERMINISTIC TELEMETRY", className="text-success fw-bold small", style={"fontSize": "0.68rem"})
                                    ])
                                ]
                            ),

                            # Action Buttons
                            html.Div(
                                className="d-flex gap-2 font-mono",
                                children=[
                                    dbc.Button(
                                        [html.I(className="bi bi-cpu me-1"), "AI ASSESS"],
                                        id="btn-inspector-ai",
                                        n_clicks=0,
                                        color="info",
                                        size="sm",
                                        className="flex-fill fw-bold py-2"
                                    ),
                                    dbc.Button(
                                        [html.I(className="bi bi-search me-1"), "OSINT RECON"],
                                        id="btn-inspector-osint",
                                        n_clicks=0,
                                        color="secondary",
                                        outline=True,
                                        size="sm",
                                        className="flex-fill fw-bold py-2"
                                    ),
                                    dbc.Button(
                                        [html.I(className="bi bi-camera-video me-1"), "LIVE CCTV"],
                                        id="btn-inspector-camera",
                                        n_clicks=0,
                                        color="success",
                                        size="sm",
                                        className="flex-fill fw-bold py-2",
                                        style={"display": "none"}
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
