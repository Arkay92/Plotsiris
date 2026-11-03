"""Surveillance CCTV camera viewer modal component."""

from dash import html
import dash_bootstrap_components as dbc


def create_camera_modal() -> dbc.Modal:
    """Create modal dialog for viewing CCTV surveillance streams."""
    return dbc.Modal(
        id="camera-modal",
        size="lg",
        is_open=False,
        centered=True,
        className="modal-dark",
        children=[
            dbc.ModalHeader(
                dbc.ModalTitle(id="camera-modal-title", children="LIVE SURVEILLANCE FEED"),
                close_button=True,
                className="bg-dark text-white border-secondary"
            ),
            dbc.ModalBody(
                className="bg-dark p-3 text-center",
                children=[
                    html.Div(
                        id="camera-modal-content",
                        children=[
                            html.Img(
                                id="camera-stream-img",
                                src="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&auto=format&fit=crop&q=80",
                                className="img-fluid rounded border border-secondary shadow",
                                style={"maxHeight": "480px", "objectFit": "cover", "width": "100%"}
                            ),
                            html.Div(
                                id="camera-metadata",
                                className="mt-3 text-start glass-panel p-3 border-secondary small",
                                children="Camera Telemetry: Initializing secure stream proxy..."
                            )
                        ]
                    )
                ]
            )
        ]
    )
