"""OSINT Reconnaissance Suite UI Component (20 Tools)."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from plotsiris.domain.constants import OSINT_TOOLS


def create_osint_panel() -> dbc.Offcanvas:
    """Create sliding offcanvas drawer for 20-tool OSINT reconnaissance."""
    tool_options = [
        {
            "label": f"[{t.get('category', 'passive').upper()}] {t['name']} — {t['desc']}",
            "value": t["id"]
        }
        for t in OSINT_TOOLS
    ]

    return dbc.Offcanvas(
        id="osint-offcanvas",
        title=html.Div([
            html.I(className="bi bi-shield-check me-2 text-info"),
            html.Span("OSINT RECONNAISSANCE SUITE", style={"fontWeight": "700", "letterSpacing": "1.5px"}),
            dbc.Badge("CMA 1990 SCOPED", color="secondary", className="ms-2", style={"fontSize": "0.62rem"})
        ]),
        is_open=False,
        placement="end",
        backdrop=False,
        scrollable=True,
        className="offcanvas-custom",
        children=[
            html.P(
                "Multi-engine reconnaissance with strict separation between passive directory intelligence and gated active connection probing.",
                className="text-muted small mb-2"
            ),
            # Tool Selector
            html.Div(className="mb-2", children=[
                html.Label("SELECT RECON ENGINE", className="small text-info fw-bold mb-1"),
                dcc.Dropdown(
                    id="osint-tool-select",
                    options=tool_options,
                    value="dns",
                    clearable=False,
                    className="text-dark small"
                )
            ]),
            # Scoping & Authorisation Boundary Alert (Dynamic via Callback)
            html.Div(id="osint-auth-gate-container", className="mb-2"),
            # Target Input
            html.Div(className="mb-2", children=[
                html.Label("TARGET (HOST / DOMAIN / IP / IDENTIFIER)", className="small text-info fw-bold mb-1"),
                dbc.InputGroup([
                    dbc.Input(
                        id="osint-target-input",
                        placeholder="e.g. google.com or scanme.nmap.org",
                        type="text",
                        className="bg-dark text-white border-secondary small"
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-play-fill me-1"), "EXECUTE"],
                        id="btn-run-osint",
                        color="info",
                        className="fw-bold px-3"
                    )
                ])
            ]),
            # Quick Target Presets
            html.Div(className="mb-2", children=[
                html.Span("QUICK TARGETS: ", className="text-muted", style={"fontSize": "0.7rem"}),
                dbc.ButtonGroup([
                    dbc.Button("google.com", id="btn-target-google", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("scanme.nmap.org", id="btn-target-nmap", size="sm", color="success", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("1.1.1.1", id="btn-target-cloudflare", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("185.220.101.5", id="btn-target-tor", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("CVE-2024-38077", id="btn-target-cve", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"})
                ], size="sm")
            ]),
            # Legal & Research Attribution Note
            html.Div(
                className="p-2 mb-2 rounded bg-black bg-opacity-50 border border-secondary border-opacity-25",
                children=[
                    html.Small([
                        html.I(className="bi bi-shield-lock-fill text-warning me-1"),
                        html.Strong("Authorisation Boundary: ", className="text-warning"),
                        html.Span("Active tools require explicit authorization confirmation under the Computer Misuse Act 1990. ", className="text-muted"),
                        html.Em('"The line between intelligence and intrusion is an authorisation boundary, not a capability one." ', className="text-light"),
                        html.Span("— Red Specter Security Research (", className="text-muted"),
                        html.A("DOI: 10.5281/zenodo.23924318", href="https://doi.org/10.5281/zenodo.23924318", target="_blank", className="text-info text-decoration-none"),
                        html.Span(")", className="text-muted")
                    ], style={"fontSize": "0.68rem"})
                ]
            ),
            # Execution Spinner & Results Container
            dcc.Loading(
                id="osint-loading",
                type="dot",
                color="#00e5ff",
                children=html.Div(id="osint-results-container", className="mt-2")
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
