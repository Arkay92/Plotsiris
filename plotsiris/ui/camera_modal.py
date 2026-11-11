"""Surveillance CCTV camera viewer modal component with live DOT/JamCam feeds and PTZ HUD."""

from dash import html
import dash_bootstrap_components as dbc

from plotsiris.domain.constants import CCTV_REGISTRY


def create_camera_modal() -> dbc.Modal:
    """Create modal dialog for viewing live CCTV surveillance streams, DOT snapshots & PTZ HUD."""
    channel_options = [
        {
            "label": f"{cam['name']} ({cam['country']})",
            "value": cam["id"],
        }
        for cam in CCTV_REGISTRY
    ]
    default_cam_id = CCTV_REGISTRY[0]["id"] if CCTV_REGISTRY else ""

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
                        children=[
                            # Live Global Camera Channel Selector & Feed Mode Bar
                            html.Div(
                                className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2",
                                children=[
                                    html.Div(
                                        className="d-flex align-items-center gap-2 flex-grow-1",
                                        style={"minWidth": "240px"},
                                        children=[
                                            html.Span("FEED:", className="small text-info fw-bold font-monospace"),
                                            dbc.Select(
                                                id="camera-channel-select",
                                                options=channel_options,
                                                value=default_cam_id,
                                                size="sm",
                                                className="bg-black text-light border-secondary font-monospace",
                                            ),
                                            dbc.Button(
                                                [html.I(className="bi bi-skip-forward-fill me-1"), "NEXT"],
                                                id="btn-cam-next",
                                                n_clicks=0,
                                                size="sm",
                                                color="secondary",
                                                outline=True,
                                                className="fw-bold font-monospace flex-shrink-0",
                                                title="Cycle to Next Live World Camera",
                                            ),
                                        ],
                                    ),
                                    dbc.ButtonGroup(
                                        size="sm",
                                        children=[
                                            dbc.Button(
                                                "LIVE SENSOR",
                                                id="btn-cam-mode-snapshot",
                                                n_clicks=0,
                                                size="sm",
                                                color="info",
                                                outline=True,
                                                className="fw-bold font-monospace",
                                                title="Live Updating DOT Sensor Snapshots (5s refresh)",
                                            ),
                                            dbc.Button(
                                                "VIDEO STREAM",
                                                id="btn-cam-mode-video",
                                                n_clicks=0,
                                                size="sm",
                                                color="info",
                                                outline=False,
                                                className="fw-bold font-monospace",
                                                title="Live Clip / Motion Video Stream",
                                            ),
                                        ],
                                    ),
                                ],
                            ),

                            # Viewport Container (overflow-hidden so PTZ scale clips cleanly)
                            html.Div(
                                className="position-relative overflow-hidden rounded border border-secondary shadow",
                                style={"backgroundColor": "#050810", "minHeight": "320px", "maxHeight": "440px"},
                                children=[
                                    # Primary Real-Time Surveillance Video Player
                                    html.Video(
                                        id="camera-stream-video",
                                        src="",
                                        controls=True,
                                        autoPlay=True,
                                        loop=True,
                                        muted=True,
                                        playsInline=True,
                                        className="w-100",
                                        style={
                                            "maxHeight": "440px",
                                            "objectFit": "cover",
                                            "width": "100%",
                                            "backgroundColor": "#050810",
                                            "display": "none",
                                            "transition": "transform 0.2s ease, filter 0.2s ease",
                                        }
                                    ),

                                    # Live Snapshot / External DOT Camera Display
                                    html.Img(
                                        id="camera-stream-img",
                                        src="/assets/surveillance_stream.gif",
                                        className="img-fluid w-100",
                                        style={
                                            "maxHeight": "440px",
                                            "objectFit": "cover",
                                            "width": "100%",
                                            "backgroundColor": "#050810",
                                            "display": "block",
                                            "transition": "transform 0.2s ease, filter 0.2s ease",
                                        }
                                    ),

                                    # Military HUD Overlay over Stream
                                    html.Div(
                                        id="camera-hud-overlay",
                                        className="position-absolute top-0 start-0 w-100 p-3 d-flex justify-content-between align-items-start",
                                        style={"pointerEvents": "none", "zIndex": 5},
                                        children=[
                                            html.Div(
                                                className="d-flex align-items-center gap-2 flex-wrap",
                                                children=[
                                                    html.Span(className="badge bg-danger text-white fw-bold d-flex align-items-center gap-1 shadow", children=[
                                                        html.Span("●", className="pulse-dot text-white"),
                                                        "LIVE REC"
                                                    ]),
                                                    html.Span(
                                                        id="camera-hud-channel-badge",
                                                        children="LIVE SENSOR // AUTO-REFRESH",
                                                        className="badge bg-dark border border-secondary text-info small font-monospace",
                                                    )
                                                ]
                                            ),
                                            html.Div(
                                                id="camera-hud-timestamp",
                                                className="badge bg-dark border border-secondary text-white font-monospace small shadow",
                                                children="LIVE // SYNCING..."
                                            )
                                        ]
                                    ),
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
                                            dbc.Button([html.I(className="bi bi-zoom-in")], id="btn-cam-zoom-in", size="sm", color="dark", className="border-secondary px-2 py-0", title="PTZ Zoom In"),
                                            dbc.Button([html.I(className="bi bi-zoom-out")], id="btn-cam-zoom-out", size="sm", color="dark", className="border-secondary px-2 py-0", title="PTZ Zoom Out"),
                                            dbc.Button([html.I(className="bi bi-arrow-clockwise")], id="btn-cam-refresh", size="sm", color="dark", className="border-secondary px-2 py-0", title="Pull Fresh Live Frame / Reconnect")
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
