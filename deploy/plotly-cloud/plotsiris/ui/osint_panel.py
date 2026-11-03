"""OSINT Reconnaissance Suite UI Component (20 Tools)."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from plotsiris.domain.constants import OSINT_TOOLS


def create_osint_panel() -> dbc.Offcanvas:
    """Create sliding offcanvas drawer for 20-tool OSINT reconnaissance."""
    tool_options = [
        {"label": f"{t['name']} — {t['desc']}", "value": t["id"]}
        for t in OSINT_TOOLS
    ]

    return dbc.Offcanvas(
        id="osint-offcanvas",
        title=html.Div([
            html.I(className="bi bi-search me-2 text-info"),
            html.Span("OSINT RECONNAISSANCE SUITE", style={"fontWeight": "700", "letterSpacing": "1.5px"})
        ]),
        is_open=False,
        placement="end",
        className="offcanvas-custom",
        children=[
            html.P(
                "Execute active reconnaissance, network profiling, vulnerability auditing, and threat intelligence lookups across 20 specialized engines.",
                className="text-muted small mb-3"
            ),
            # Tool Selector
            html.Div(className="mb-3", children=[
                html.Label("SELECT RECON ENGINE", className="small text-info fw-bold mb-1"),
                dcc.Dropdown(
                    id="osint-tool-select",
                    options=tool_options,
                    value="dns",
                    clearable=False,
                    className="text-dark small"
                )
            ]),
            # Target Input
            html.Div(className="mb-3", children=[
                html.Label("TARGET (HOST / DOMAIN / IP / IDENTIFIER)", className="small text-info fw-bold mb-1"),
                dbc.InputGroup([
                    dbc.Input(
                        id="osint-target-input",
                        placeholder="e.g. google.com or 1.1.1.1",
                        type="text",
                        className="bg-dark text-white border-secondary small"
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-play-fill me-1"), "SCAN"],
                        id="btn-run-osint",
                        color="info",
                        className="fw-bold px-3"
                    )
                ])
            ]),
            # Quick Target Presets
            html.Div(className="mb-3", children=[
                html.Span("QUICK TARGETS: ", className="text-muted", style={"fontSize": "0.7rem"}),
                dbc.ButtonGroup([
                    dbc.Button("google.com", id="btn-target-google", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("1.1.1.1", id="btn-target-cloudflare", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("185.220.101.5", id="btn-target-tor", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("CVE-2024-38077", id="btn-target-cve", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"})
                ], size="sm")
            ]),
            # Execution Spinner & Results Container
            dcc.Loading(
                id="osint-loading",
                type="dot",
                color="#00e5ff",
                children=html.Div(id="osint-results-container", className="mt-3")
            )
        ]
    )


def render_osint_result(result_dict: dict) -> html.Div:
    """Render formatted result card for completed OSINT reconnaissance."""
    if not result_dict:
        return html.Div()

    verdict = result_dict.get("verdict", "UNKNOWN")
    status = result_dict.get("status", "SUCCESS")
    tool = result_dict.get("tool", "").upper()
    target = result_dict.get("target", "")
    summary = result_dict.get("summary", "")
    details = result_dict.get("details", {})
    coords = result_dict.get("coordinates")

    card_class = "osint-verdict-clean" if verdict == "CLEAN" else ("osint-verdict-malicious" if verdict == "MALICIOUS" else "osint-verdict-suspicious")
    badge_color = "info" if verdict == "CLEAN" else ("danger" if verdict == "MALICIOUS" else "warning")

    pin_btn = None
    if coords:
        pin_btn = dbc.Button(
            [html.I(className="bi bi-pin-map-fill me-1"), f"PIN FINDING TO MAP ({coords[0]:.2f}°, {coords[1]:.2f}°)",],
            id="btn-pin-recon-result",
            color="info",
            size="sm",
            className="w-100 fw-bold mt-2"
        )

    return html.Div(
        className=f"glass-panel p-3 border-secondary {card_class}",
        children=[
            html.Div(
                className="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom border-secondary",
                children=[
                    html.Div([
                        html.Span(f"[{tool}]", className="fw-bold text-info me-2"),
                        html.Span(target, className="text-white")
                    ]),
                    dbc.Badge(verdict, color=badge_color, className="px-2 py-1")
                ]
            ),
            html.P(summary, className="text-light small mb-2"),
            pin_btn if pin_btn else html.Div(),
            html.Details(
                className="mt-3",
                children=[
                    html.Summary("RAW ENGINE TELEMETRY", className="small text-info fw-bold cursor-pointer"),
                    html.Pre(
                        html.Code(
                            json_str(details),
                            className="small text-muted p-2 d-block",
                            style={"maxHeight": "240px", "overflowY": "auto", "backgroundColor": "rgba(0,0,0,0.5)"}
                        )
                    )
                ]
            )
        ]
    )


def json_str(obj: dict) -> str:
    import json
    try:
        return json.dumps(obj, indent=2)
    except Exception:
        return str(obj)
