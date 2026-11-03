"""Left Rail Layer Panel component for toggling intelligence layers."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from plotsiris.domain.constants import LAYER_DEFINITIONS


def create_layer_panel(counts: dict[str, int]) -> html.Div:
    """Create collapsible left rail containing category layer toggles."""
    layer_checkboxes = []

    for lid, meta in LAYER_DEFINITIONS.items():
        count = counts.get(lid, 0)
        checkbox = html.Div(
            className="layer-item",
            children=[
                dbc.Checkbox(
                    id={"type": "layer-toggle", "index": lid},
                    label=html.Span([
                        html.I(className=f"{meta['icon']} me-2", style={"color": meta["color"]}),
                        meta["name"]
                    ]),
                    value=meta["default"],
                    className="m-0",
                    style={"fontSize": "0.82rem", "fontWeight": "500"}
                ),
                html.Span(f"{count}", id={"type": "layer-count", "index": lid}, className="layer-count-badge")
            ]
        )
        layer_checkboxes.append(checkbox)

    return html.Div(
        id="layer-rail-container",
        className="glass-panel layer-rail p-3",
        children=[
            html.Div(
                className="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom border-secondary",
                children=[
                    html.Div([
                        html.I(className="bi bi-stack me-2 text-info"),
                        html.Span("INTELLIGENCE LAYERS", style={"fontWeight": "700", "fontSize": "0.85rem", "letterSpacing": "1px"})
                    ]),
                    dbc.Button(
                        "All",
                        id="btn-select-all-layers",
                        size="sm",
                        color="link",
                        className="p-0 text-info text-decoration-none",
                        style={"fontSize": "0.75rem"}
                    )
                ]
            ),
            html.Div(layer_checkboxes, style={"maxHeight": "calc(100vh - 220px)", "overflowY": "auto"}),
            html.Div(
                className="pt-2 mt-2 border-top border-secondary text-muted text-center",
                style={"fontSize": "0.68rem"},
                children="Click any map entity to inspect details or run AI/OSINT queries."
            )
        ]
    )
