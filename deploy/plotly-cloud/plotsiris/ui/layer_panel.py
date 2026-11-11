"""Left Sidebar Layer Panel component for toggling intelligence layers."""

from __future__ import annotations

from dash import html, dcc
import dash_bootstrap_components as dbc
from plotsiris.domain.constants import LAYER_DEFINITIONS


def create_sidebar_expand_tab() -> html.Button:
    """Create a vertical expand tab on the left edge of the map canvas shown when sidebar is collapsed."""
    return html.Button(
        id="btn-expand-sidebar-tab",
        className="expand-sidebar-tab d-none",
        title="Expand Intelligence Layers Sidebar",
        children=[
            html.I(className="bi bi-chevron-right text-info"),
            html.Span("LAYERS", className="expand-tab-text")
        ]
    )


def create_layer_panel(counts: dict[str, int]) -> html.Aside:
    """Create collapsible left sidebar containing category layer toggles."""
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
                    style={"fontSize": "0.78rem", "fontWeight": "500"}
                ),
                html.Span(f"{count}", id={"type": "layer-count", "index": lid}, className="layer-count-badge")
            ]
        )
        layer_checkboxes.append(checkbox)

    return html.Aside(
        id="layers-sidebar",
        className="layers-sidebar font-mono",
        children=[
            # Header with title, "All" selector, and Collapse button
            html.Div(
                className="layers-sidebar-header",
                children=[
                    html.Div(
                        id="layers-sidebar-header-title",
                        className="d-flex align-items-center",
                        children=[
                            html.I(className="bi bi-stack me-2 text-info"),
                            html.Span(
                                "INTELLIGENCE LAYERS",
                                style={"fontWeight": "700", "fontSize": "0.78rem", "letterSpacing": "1px"}
                            )
                        ]
                    ),
                    html.Div(
                        className="d-flex align-items-center gap-2",
                        children=[
                            dbc.Button(
                                "All",
                                id="btn-select-all-layers",
                                size="sm",
                                color="link",
                                className="p-0 text-info text-decoration-none fw-bold",
                                style={"fontSize": "0.74rem"},
                                title="Toggle All Layers"
                            ),
                            dbc.Button(
                                html.I(id="layer-rail-toggle-icon", className="bi bi-chevron-left text-info"),
                                id="btn-toggle-layer-rail",
                                size="sm",
                                color="link",
                                className="p-0 text-decoration-none",
                                style={"fontSize": "0.85rem", "lineHeight": "1"},
                                title="Collapse Sidebar"
                            )
                        ]
                    )
                ]
            ),

            # Scrollable Body with Layer Checkboxes
            html.Div(
                layer_checkboxes,
                className="layers-sidebar-content"
            ),

            # Footer Hint
            html.Div(
                className="layers-sidebar-footer text-secondary text-center",
                style={"fontSize": "0.68rem"},
                children="Click map markers for instant telemetry inspection."
            )
        ]
    )
