"""Surveillance CCTV camera viewer modal component with active streaming video player."""

from dash import html
import dash_bootstrap_components as dbc


def create_camera_modal() -> dbc.Modal:
    """Create modal dialog for viewing CCTV surveillance streams with active video player & HUD."""
    return dbc.Modal(
        id="camera-modal",
        size="lg",
        is_open=False,
        centered=True,
        className="modal-dark",
        children=[
            dbc.ModalHeader(
                [
                    dbc.ModalTitle(id="camera-modal-title", children="LIVE SURVEILLANCE FEED"),
                    dbc.Button(
                        html.I(className="bi bi-x-lg"),
                        id="btn-close-camera-modal",
                        n_clicks=0,
                        size="sm",
                        color="link",
                        className="ms-auto text-white text-decoration-none"
                    )
                ],
                close_button=False,
                className="bg-dark text-white border-secondary d-flex align-items-center"
            ),
            dbc.ModalBody(
                className="bg-dark p-3 text-center",
                children=[
                    html.Div(
                        id="camera-modal-content",
                        className="position-relative",
                        children=[
                            # Live Surveillance Stream Display (Active Animated Tactical Loop)
                            html.Img(
                                id="camera-stream-img",
                                src="/assets/surveillance_stream.gif",
                                className="img-fluid rounded border border-secondary shadow",
                                style={
                                    "maxHeight": "440px",
                                    "objectFit": "cover",
                                    "width": "100%",
                                    "backgroundColor": "#050810",
                                    "display": "block"
                                }
                            ),

                            # Fallback / Alternate Surveillance Video Player
                            html.Video(
                                id="camera-stream-video",
                                src="/assets/surveillance_stream.mp4",
                                controls=True,
                                autoPlay=True,
                                loop=True,
                                muted=True,
                                playsInline=True,
                                className="w-100 rounded border border-secondary shadow d-none",
                                style={
                                    "maxHeight": "440px",
                                    "objectFit": "cover",
                                    "backgroundColor": "#050810"
                                }
                            ),

                            # Military HUD Overlay over Stream
                            html.Div(
                                id="camera-hud-overlay",
                                className="position-absolute top-0 start-0 w-100 p-3 d-flex justify-content-between pointer-events-none",
                                style={"pointerEvents": "none"},
                                children=[
                                    html.Div(
                                        className="d-flex align-items-center gap-2",
                                        children=[
                                            html.Span(className="badge bg-danger text-white fw-bold d-flex align-items-center gap-1 shadow", children=[
                                                html.Span("●", className="pulse-dot text-white"),
                                                "LIVE REC"
                                            ]),
                                            html.Span("CH-01 OPTICAL FEED", className="badge bg-dark border border-secondary text-info small")
                                        ]
                                    ),
                                    html.Div(
                                        id="camera-hud-timestamp",
                                        className="badge bg-dark border border-secondary text-white font-monospace small",
                                        children="STREAM ACTIVE // 30.0 FPS"
                                    )
                                ]
                            ),

                            # Interactive Sensor Controls (FLIR, NVG, PTZ)
                            html.Div(
                                className="d-flex flex-wrap justify-content-between align-items-center mt-3 pt-2 border-top border-secondary gap-2",
                                children=[
                                    html.Div(
                                        className="btn-group btn-group-sm",
                                        children=[
                                            dbc.Button("NORMAL", id="btn-cam-opt-normal", color="info", size="sm", className="fw-bold active"),
                                            dbc.Button("NVG GREEN", id="btn-cam-opt-nvg", color="outline-success", size="sm", className="fw-bold"),
                                            dbc.Button("FLIR THERMAL", id="btn-cam-opt-flir", color="outline-warning", size="sm", className="fw-bold"),
                                        ]
                                    ),
                                    html.Div(
                                        className="d-flex align-items-center gap-1 small text-muted font-monospace",
                                        children=[
                                            html.Span("PTZ:"),
                                            dbc.Button([html.I(className="bi bi-zoom-in")], id="btn-cam-zoom-in", size="sm", color="dark", className="border-secondary px-2 py-0"),
                                            dbc.Button([html.I(className="bi bi-zoom-out")], id="btn-cam-zoom-out", size="sm", color="dark", className="border-secondary px-2 py-0"),
                                            dbc.Button([html.I(className="bi bi-arrow-clockwise")], id="btn-cam-refresh", size="sm", color="dark", className="border-secondary px-2 py-0", title="Reconnect Stream")
                                        ]
                                    )
                                ]
                            ),

                            # Detailed Metadata Bar
                            html.Div(
                                id="camera-metadata",
                                className="mt-2 text-start glass-panel p-2 px-3 border-secondary small text-muted font-monospace",
                                children="Camera Telemetry: Initializing secure stream proxy..."
                            )
                        ]
                    )
                ]
            )
        ]
    )
