"""Entity Intelligence Relationship Graph Modal component."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from plotsiris.rendering.graph_builder import EntityGraphBuilder


def create_entity_graph_modal() -> dbc.Modal:
    """Create modal dialog for exploring the force-directed entity relationship graph."""
    graph_fig = EntityGraphBuilder.build_graph(theme="ghost")

    return dbc.Modal(
        id="entity-graph-modal",
        size="xl",
        is_open=False,
        centered=True,
        className="modal-dark",
        children=[
            dbc.ModalHeader(
                dbc.ModalTitle([
                    html.I(className="bi bi-diagram-3-fill me-2 text-info"),
                    "ENTITY RELATIONSHIP INTELLIGENCE GRAPH"
                ]),
                close_button=True,
                className="bg-dark text-white border-secondary"
            ),
            dbc.ModalBody(
                className="bg-dark p-2",
                children=[
                    html.Div(
                        className="d-flex justify-content-between align-items-center px-3 py-1 mb-2 border-bottom border-secondary small text-muted",
                        children=[
                            html.Span("Force-directed correlation mapping threat actors, malware vectors, CVEs, target sectors, and command-and-control nodes."),
                            html.Div([
                                html.Span("● Actor", className="text-danger me-2"),
                                html.Span("● Malware", style={"color": "#a855f7"}, className="me-2"),
                                html.Span("● Target", className="text-info me-2"),
                                html.Span("● CVE", style={"color": "#ef4444"}, className="me-2"),
                                html.Span("● C2", style={"color": "#ec4899"}),
                            ])
                        ]
                    ),
                    dcc.Graph(
                        id="entity-graph-display",
                        figure=graph_fig,
                        config={"displayModeBar": True, "scrollZoom": True},
                        style={"height": "650px", "width": "100%"}
                    )
                ]
            )
        ]
    )
