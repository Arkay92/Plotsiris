"""Master UI Layout for Plotsiris dashboard matching the tactical operations HUD reference."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime

from plotsiris.domain.constants import REGION_PRESETS
from plotsiris.services.data_manager import data_manager
from plotsiris.rendering.map_builder import MapBuilder
from plotsiris.rendering.graph_builder import EntityGraphBuilder
from plotsiris.ui.telemetry_deck import create_telemetry_deck
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
    """Build the complete application layout matching the reference operations HUD."""
    # Compute initial baseline entities and counts
    entities = data_manager.get_all_entities()
    routes = data_manager.get_route_paths()
    counts = data_manager.get_layer_counts()
    tickers, risks = data_manager.get_markets()
    news_alerts = data_manager.get_news_alerts()
    cisa_vulns = data_manager.get_cisa_kev()
    recon_findings = data_manager.get_recon_findings()

    initial_fig = MapBuilder.build_map(entities, routes, center_lat=20.0, center_lon=15.0, zoom=1.6, theme="ghost")
    initial_graph = EntityGraphBuilder.build_graph(theme="ghost")

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
        className="position-relative w-100 min-vh-100 bg-black text-light font-mono",
        style={"overflowX": "hidden", "overflowY": "auto"},
        children=[
            # Hidden State Stores
            dcc.Store(id="selected-entity-store", data=None),
            dcc.Store(id="map-camera-store", data={"lat": 20.0, "lon": 15.0, "zoom": 1.6}),
            dcc.Store(id="theme-store", data="ghost"),
            dcc.Store(id="osint-latest-result-store", data=None),
            dcc.Store(id="chat-history-store", data=[]),
            dcc.Store(id="active-view-mode-store", data="map"),  # Default: "map", switchable to "graph"
            dcc.Interval(id="clock-interval", interval=1000, n_intervals=0),
            dcc.Interval(id="feed-refresh-interval", interval=60000, n_intervals=0),

            # Top Navigation Header matching reference image: AI CONFIGS / OPEN SOURCE
            html.Header(
                className="hud-header px-3 py-2 border-bottom border-secondary border-opacity-25 bg-black d-flex flex-wrap justify-content-between align-items-center gap-2",
                style={"minHeight": "52px", "zIndex": 1100},
                children=[
                    # Left: Main Title & Subtitle
                    html.Div([
                        html.Div(className="d-flex align-items-center gap-2", children=[
                            html.Span("GLOBAL OSINT / DEFCON TELEMETRY", className="fs-5 fw-bold text-white", style={"letterSpacing": "1.5px"}),
                            dbc.Badge("PLOTSIRIS v2.5", color="dark", className="text-info border border-secondary border-opacity-50 small font-mono")
                        ]),
                        html.Div(
                            "14 FEEDS  /  4,992 ENTITIES  /  CISA KEV  /  NASA EONET  /  RELIEFWEB  /  ABUSE.CH",
                            className="text-secondary small font-mono",
                            style={"fontSize": "0.68rem", "letterSpacing": "0.8px"}
                        )
                    ]),

                    # Center: Domain Filter Pills (+ AVIATION, + MARITIME, + CONFLICT, + C2 BOTNETS, + NASA EONET)
                    html.Div(
                        className="d-none d-xl-flex align-items-center gap-2",
                        children=[
                            dbc.Button("+ AVIATION", size="sm", color="secondary", outline=True, className="py-0 px-2 font-mono text-info fw-bold", style={"fontSize": "0.70rem"}),
                            dbc.Button("+ MARITIME", size="sm", color="secondary", outline=True, className="py-0 px-2 font-mono text-muted", style={"fontSize": "0.70rem"}),
                            dbc.Button("+ CONFLICT", size="sm", color="secondary", outline=True, className="py-0 px-2 font-mono text-muted", style={"fontSize": "0.70rem"}),
                            dbc.Button("+ C2 BOTNETS", size="sm", color="secondary", outline=True, className="py-0 px-2 font-mono text-muted", style={"fontSize": "0.70rem"}),
                            dbc.Button("+ NASA EONET", size="sm", color="secondary", outline=True, className="py-0 px-2 font-mono text-muted", style={"fontSize": "0.70rem"}),
                        ]
                    ),

                    # Command Input Prompt: > osint scan --target 1.1.1.1 --full-recon
                    html.Div(
                        className="d-flex align-items-center",
                        children=[
                            dbc.InputGroup([
                                dbc.InputGroupText(">", className="bg-dark border-secondary text-info font-mono small py-0"),
                                dbc.Input(
                                    id="top-cmd-bar",
                                    value="osint scan --target 1.1.1.1 --full-recon",
                                    type="text",
                                    className="bg-dark text-info font-mono small border-secondary py-0",
                                    style={"width": "260px", "fontSize": "0.75rem"}
                                )
                            ], size="sm")
                        ]
                    ),

                    # Right: Status Telemetry & Action Drawer Buttons
                    html.Div(
                        className="d-flex align-items-center gap-3",
                        children=[
                            html.Div(className="d-flex align-items-center gap-2 font-mono small", children=[
                                html.Span(className="pulse-indicator"),
                                html.Span("LIVE", className="text-success fw-bold", style={"fontSize": "0.72rem"}),
                                html.Span(id="live-clock-display", className="text-white fw-bold", style={"fontSize": "0.72rem"}, children="00:00:02:03"),
                                html.Span("30FPS", className="text-secondary", style={"fontSize": "0.70rem"})
                            ]),
                            # Drawer Trigger Action Buttons
                            dbc.ButtonGroup([
                                dbc.Button("OSINT", id="btn-open-osint", size="sm", color="dark", className="border-secondary text-info fw-bold py-0 px-2", style={"fontSize": "0.70rem"}),
                                dbc.Button("AI", id="btn-open-ai", size="sm", color="dark", className="border-secondary text-info fw-bold py-0 px-2", style={"fontSize": "0.70rem"}),
                                dbc.Button("CYBER", id="btn-open-cyber", size="sm", color="dark", className="border-secondary text-danger fw-bold py-0 px-2", style={"fontSize": "0.70rem"}),
                                dbc.Button("CCTV", id="btn-open-cctv", size="sm", color="dark", className="border-secondary text-success fw-bold py-0 px-2", style={"fontSize": "0.70rem"}),
                                dbc.Button("GRAPH", id="btn-open-graph", size="sm", color="dark", className="border-secondary text-primary fw-bold py-0 px-2", style={"fontSize": "0.70rem"}),
                                dbc.Button("MARKETS", id="btn-open-markets", size="sm", color="dark", className="border-secondary text-warning fw-bold py-0 px-2", style={"fontSize": "0.70rem"}),
                                dbc.Button("NEWS", id="btn-open-news", size="sm", color="dark", className="border-secondary text-success fw-bold py-0 px-2", style={"fontSize": "0.70rem"}),
                                dbc.Button(html.I(className="bi bi-moon-stars-fill"), id="btn-toggle-theme", size="sm", color="dark", className="border-secondary text-secondary py-0 px-2", title="Toggle Theme")
                            ], size="sm")
                        ]
                    )
                ]
            ),

            # Main Upper Viewport: Tactical Canvas with HUD Reticle Header
            html.Div(
                className="canvas-viewport position-relative border-bottom border-secondary border-opacity-25 bg-black",
                style={"height": "530px", "width": "100%"},
                children=[
                    # Canvas Top Subheader matching reference image
                    html.Div(
                        className="position-absolute top-0 start-0 w-100 px-3 py-1 d-flex justify-content-between align-items-center bg-black bg-opacity-75 font-mono",
                        style={"zIndex": 10, "fontSize": "0.75rem", "borderBottom": "1px solid rgba(30, 41, 59, 0.4)"},
                        children=[
                            html.Div(className="d-flex align-items-center gap-3", children=[
                                html.Span("COMMON OPERATING PICTURE / 14 ACTIVE FEEDS · 4,992 ENTITIES", className="text-info fw-bold", style={"letterSpacing": "1px"}),
                                # View switcher pills (Default: MAP VIEW active)
                                dbc.ButtonGroup([
                                    dbc.Button("🗺️ MAP VIEW", id="btn-view-map", size="sm", color="info", className="py-0 px-2 fw-bold font-mono", style={"fontSize": "0.68rem"}),
                                    dbc.Button("● GRAPH VIEW", id="btn-view-graph", size="sm", color="secondary", outline=True, className="py-0 px-2 font-mono", style={"fontSize": "0.68rem"})
                                ], size="sm")
                            ]),
                            html.Div(className="d-flex align-items-center gap-3 text-secondary font-mono", children=[
                                html.Span("LAT 38.8°N"),
                                html.Span("LON -77.0°W")
                            ])
                        ]
                    ),

                    # 1. Tactical MapLibre Map Container (Default View)
                    html.Div(
                        id="map-display-container",
                        className="w-100 h-100",
                        style={"paddingTop": "26px", "paddingBottom": "24px"},
                        children=[
                            dcc.Graph(
                                id="main-map",
                                figure=initial_fig,
                                responsive=True,
                                config={"displayModeBar": False, "scrollZoom": True, "doubleClick": "reset"},
                                style={"width": "100%", "height": "100%"}
                            )
                        ]
                    ),

                    # 2. Constellation Graph Container (Switchable)
                    html.Div(
                        id="graph-display-container",
                        className="w-100 h-100 d-none",
                        style={"paddingTop": "26px", "paddingBottom": "24px"},
                        children=[
                            dcc.Graph(
                                id="main-graph",
                                figure=initial_graph,
                                responsive=True,
                                config={"displayModeBar": False, "scrollZoom": True},
                                style={"width": "100%", "height": "100%"}
                            )
                        ]
                    ),

                    # Status Line at Bottom of Canvas
                    html.Div(
                        className="position-absolute bottom-0 start-0 w-100 px-3 py-1 font-mono bg-black bg-opacity-85 border-top border-secondary border-opacity-25 d-flex justify-content-between align-items-center",
                        style={"fontSize": "0.72rem", "zIndex": 10},
                        children=[
                            html.Div([
                                html.Span("02.13", className="text-secondary me-2"),
                                html.Span("INTEL :: ", className="text-light"),
                                html.Span("NASA EONET hazard detected", className="text-info fw-bold"),
                                html.Span(" · EONET-6124 = VOLCANIC ERUPTION =", className="text-muted")
                            ]),
                            html.Div(className="text-secondary", style={"fontSize": "0.68rem"}, children=[
                                html.Span("FEEDS: "),
                                html.Span("14 ACTIVE (OPENSKY, USGS, NASA EONET, RELIEFWEB, FEODO C2)", className="text-info")
                            ])
                        ]
                    )
                ]
            ),

            # Sub-Nav Divider Bar
            html.Div(
                className="subnav-bar px-3 py-1 bg-black border-bottom border-secondary border-opacity-25 d-flex justify-content-between align-items-center font-mono",
                style={"fontSize": "0.72rem"},
                children=[
                    html.Div(className="d-flex align-items-center gap-2", children=[
                        html.Span(">", className="text-info fw-bold"),
                        html.Span("COMMAND CONSOLE READY // MULTI-DOMAIN C2 FUSION", className="text-muted")
                    ]),
                    html.Div("DEFCON 3 // DEFENSE TELEMETRY DECK", className="text-info fw-bold")
                ]
            ),

            # Lower Modular Telemetry Deck: 12 Numbered Panels in 4x3 Grid
            create_telemetry_deck(),

            # Floating Panels & Modals (Preserved from existing Plotsiris architecture)
            create_layer_panel(counts),
            create_inspector_card(),
            create_osint_panel(),
            create_ai_panel(),
            create_cyber_panel(cisa_vulns, recon_findings),
            create_markets_panel(tickers, risks),
            create_news_panel(news_alerts),
            create_entity_graph_modal(),
            create_camera_modal()
        ]
    )
