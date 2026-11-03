"""Master UI Layout for Plotsiris dashboard."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime

from plotsiris.domain.constants import REGION_PRESETS
from plotsiris.services.data_manager import data_manager
from plotsiris.rendering.map_builder import MapBuilder
from plotsiris.ui.layer_panel import create_layer_panel
from plotsiris.ui.osint_panel import create_osint_panel
from plotsiris.ui.ai_panel import create_ai_panel
from plotsiris.ui.cyber_panel import create_cyber_panel
from plotsiris.ui.entity_graph_panel import create_entity_graph_modal
from plotsiris.ui.markets_panel import create_markets_panel
from plotsiris.ui.news_panel import create_news_panel
from plotsiris.ui.camera_modal import create_camera_modal
from plotsiris.ui.inspector_panel import create_inspector_card


def create_layout() -> html.Div:
    """Build the complete application layout."""
    # Compute initial baseline entities and counts
    entities = data_manager.get_all_entities()
    routes = data_manager.get_route_paths()
    counts = data_manager.get_layer_counts()
    tickers, risks = data_manager.get_markets()
    news_alerts = data_manager.get_news_alerts()
    cisa_vulns = data_manager.get_cisa_kev()
    recon_findings = data_manager.get_recon_findings()

    initial_fig = MapBuilder.build_map(entities, routes, center_lat=20.0, center_lon=15.0, zoom=1.6, theme="ghost")

    # Region preset button list
    preset_buttons = []
    for pid, meta in REGION_PRESETS.items():
        preset_buttons.append(
            html.Button(
                meta["name"],
                id={"type": "region-preset-btn", "index": pid},
                className="preset-btn me-1 mb-1"
            )
        )

    return html.Div(
        id="app-root",
        className="position-relative vh-100 vw-100 overflow-hidden",
        children=[
            # Hidden State Stores
            dcc.Store(id="selected-entity-store", data=None),
            dcc.Store(id="map-camera-store", data={"lat": 20.0, "lon": 15.0, "zoom": 1.6}),
            dcc.Store(id="theme-store", data="ghost"),
            dcc.Store(id="osint-latest-result-store", data=None),
            dcc.Store(id="chat-history-store", data=[]),
            dcc.Interval(id="clock-interval", interval=1000, n_intervals=0),
            dcc.Interval(id="feed-refresh-interval", interval=60000, n_intervals=0),

            # Top Navigation Status Bar
            html.Div(
                className="glass-panel status-bar d-flex justify-content-between align-items-center",
                children=[
                    # Brand & Live Status
                    html.Div(
                        className="d-flex align-items-center gap-3",
                        children=[
                            html.Div(className="brand-badge", children=[
                                html.Span("⬡", style={"color": "#00e5ff", "fontSize": "1.3rem"}),
                                "PLOTSIRIS",
                                html.Small("v2.5", className="text-secondary ms-1", style={"fontSize": "0.65rem"})
                            ]),
                            html.Div(className="d-flex align-items-center gap-2", children=[
                                html.Div(className="pulse-indicator"),
                                html.Span("DEFCON 3 // FEEDS ACTIVE", className="text-success fw-bold", style={"fontSize": "0.72rem", "letterSpacing": "1px"})
                            ]),
                            html.Div(id="live-clock-display", className="text-info fw-bold small ms-2", children="00:00:00 UTC")
                        ]
                    ),
                    # Region Presets Navigation
                    html.Div(
                        className="d-none d-lg-flex align-items-center",
                        children=preset_buttons[:7]
                    ),
                    # Action Drawer Triggers & Theme Toggle
                    html.Div(
                        className="d-flex align-items-center gap-2",
                        children=[
                            dbc.Button(
                                [html.I(className="bi bi-search me-1 text-info"), "OSINT (20)"],
                                id="btn-open-osint",
                                type="button",
                                n_clicks=0,
                                size="sm",
                                color="dark",
                                className="border-secondary fw-bold",
                                style={"fontSize": "0.78rem"}
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-cpu me-1 text-info"), "AI ANALYST"],
                                id="btn-open-ai",
                                type="button",
                                n_clicks=0,
                                size="sm",
                                color="dark",
                                className="border-secondary fw-bold",
                                style={"fontSize": "0.78rem"}
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-shield-lock me-1 text-danger"), "CYBER"],
                                id="btn-open-cyber",
                                type="button",
                                n_clicks=0,
                                size="sm",
                                color="dark",
                                className="border-secondary fw-bold",
                                style={"fontSize": "0.78rem"}
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-diagram-3 me-1 text-primary"), "GRAPH"],
                                id="btn-open-graph",
                                type="button",
                                n_clicks=0,
                                size="sm",
                                color="dark",
                                className="border-secondary fw-bold",
                                style={"fontSize": "0.78rem"}
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-graph-up me-1 text-warning"), "MARKETS"],
                                id="btn-open-markets",
                                type="button",
                                n_clicks=0,
                                size="sm",
                                color="dark",
                                className="border-secondary fw-bold",
                                style={"fontSize": "0.78rem"}
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-broadcast me-1 text-success"), "NEWS"],
                                id="btn-open-news",
                                type="button",
                                n_clicks=0,
                                size="sm",
                                color="dark",
                                className="border-secondary fw-bold",
                                style={"fontSize": "0.78rem"}
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-camera-video me-1 text-success"), "CCTV"],
                                id="btn-open-cctv",
                                type="button",
                                n_clicks=0,
                                size="sm",
                                color="dark",
                                className="border-secondary fw-bold",
                                style={"fontSize": "0.78rem"}
                            ),
                            dbc.Button(
                                html.I(className="bi bi-moon-stars-fill"),
                                id="btn-toggle-theme",
                                type="button",
                                n_clicks=0,
                                size="sm",
                                color="dark",
                                className="border-secondary ms-1",
                                title="Toggle Theme (Ghost / Core)"
                            )
                        ]
                    )
                ]
            ),

            # Center Full-Screen Map Canvas
            html.Div(
                className="position-absolute start-0 w-100",
                style={"top": "52px", "height": "calc(100vh - 52px)", "zIndex": 1},
                children=[
                    dcc.Graph(
                        id="main-map",
                        figure=initial_fig,
                        responsive=True,
                        config={
                            "displayModeBar": False,
                            "scrollZoom": True,
                            "doubleClick": "reset"
                        },
                        style={"width": "100%", "height": "calc(100vh - 52px)"}
                    )
                ]
            ),

            # Floating Left-Rail Layer Toggles
            create_layer_panel(counts),

            # Floating Map Entity Inspector Detail Card
            create_inspector_card(),

            # Offcanvas Panels & Modals
            create_osint_panel(),
            create_ai_panel(),
            create_cyber_panel(cisa_vulns, recon_findings),
            create_markets_panel(tickers, risks),
            create_news_panel(news_alerts),
            create_entity_graph_modal(),
            create_camera_modal()
        ]
    )
