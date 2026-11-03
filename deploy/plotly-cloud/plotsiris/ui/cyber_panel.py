"""Cyber Intelligence & Recon Findings UI Component."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import List, Dict, Any
from plotsiris.domain.models import GeoEntity


def create_cyber_panel(cisa_vulns: List[Dict[str, Any]], recon_findings: List[GeoEntity]) -> dbc.Offcanvas:
    """Create sliding offcanvas drawer for Cyber Threat Intelligence."""
    vuln_cards = []
    for v in cisa_vulns:
        vuln_cards.append(
            html.Div(
                className="glass-panel p-2 mb-2 border-secondary",
                children=[
                    html.Div(
                        className="d-flex justify-content-between align-items-center mb-1",
                        children=[
                            html.Span(v.get("cveID"), className="fw-bold text-danger small"),
                            dbc.Badge(f"CVSS {v.get('cvss', 9.0):.1f}", color="danger", className="small")
                        ]
                    ),
                    html.Div(f"{v.get('vendorProject')} — {v.get('product')}", className="text-light fw-bold small"),
                    html.P(v.get("vulnerabilityName"), className="text-muted small m-0 mb-1"),
                    html.Small(f"Added: {v.get('dateAdded')} | Action: {v.get('requiredAction')}", className="text-info d-block", style={"fontSize": "0.68rem"})
                ]
            )
        )

    # Recon findings
    findings_rows = []
    for rf in recon_findings:
        findings_rows.append(
            html.Tr([
                html.Td(rf.subcategory, className="small text-info"),
                html.Td(rf.title, className="small text-white"),
                html.Td(f"{rf.lat:.2f}, {rf.lon:.2f}", className="small text-muted"),
                html.Td(dbc.Badge(rf.severity, color="danger" if rf.severity == "CRITICAL" else "info", className="small"))
            ])
        )

    findings_table = html.Table(
        className="table table-sm table-dark table-borderless small",
        children=[
            html.Thead(html.Tr([html.Th("Tool"), html.Th("Target"), html.Th("Coordinates"), html.Th("Severity")])),
            html.Tbody(findings_rows if findings_rows else [html.Tr(html.Td("No active recon findings pinned yet.", colSpan=4, className="text-muted text-center py-3"))])
        ]
    )

    return dbc.Offcanvas(
        id="cyber-offcanvas",
        title=html.Div([
            html.I(className="bi bi-shield-lock me-2 text-info"),
            html.Span("CYBER THREAT INTELLIGENCE", style={"fontWeight": "700", "letterSpacing": "1.5px"})
        ]),
        is_open=False,
        placement="end",
        backdrop=False,
        scrollable=True,
        className="offcanvas-custom",
        children=[
            dbc.Tabs([
                dbc.Tab(
                    label="CISA KEV CATALOG",
                    tab_id="tab-kev",
                    children=[
                        html.P("Active Known Exploited Vulnerabilities monitored by CISA with mandatory remediation directives.", className="text-muted small my-2"),
                        html.Div(vuln_cards, style={"maxHeight": "calc(100vh - 200px)", "overflowY": "auto"})
                    ]
                ),
                dbc.Tab(
                    label="RECON FINDINGS",
                    tab_id="tab-recon-findings",
                    children=[
                        html.P("Target nodes and domains pinned to live geospatial map via OSINT tools.", className="text-muted small my-2"),
                        html.Div(findings_table, style={"maxHeight": "calc(100vh - 200px)", "overflowY": "auto"})
                    ]
                ),
                dbc.Tab(
                    label="MITRE & APT GROUPS",
                    tab_id="tab-mitre",
                    children=[
                        html.P("Tracked state-sponsored Advanced Persistent Threat actors.", className="text-muted small my-2"),
                        html.Ul([
                            html.Li([html.Strong("APT28 (Fancy Bear): "), "Russian GRU Unit 26165; military command targeting."], className="mb-2 small text-light"),
                            html.Li([html.Strong("Volt Typhoon (UNC3236): "), "Living-off-the-Land stealth persistence in US critical infrastructure."], className="mb-2 small text-light"),
                            html.Li([html.Strong("Lazarus Group: "), "DPRK RGB Reconnaissance General Bureau; cryptocurrency operations."], className="mb-2 small text-light"),
                            html.Li([html.Strong("LockBit 3.0: "), "Ransomware-as-a-service syndicate."], className="mb-2 small text-light"),
                            html.Li([html.Strong("Scattered Spider (UNC3944): "), "Social engineering, SIM swapping, and Okta cloud identity compromise."], className="mb-2 small text-light"),
                        ], className="p-0 ps-3")
                    ]
                )
            ], className="border-secondary")
        ]
    )
