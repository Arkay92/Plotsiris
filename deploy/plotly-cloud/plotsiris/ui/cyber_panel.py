"""Cyber Intelligence & Recon Findings UI Component."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import List, Dict, Any
from plotsiris.domain.models import GeoEntity


def create_cyber_panel(cisa_vulns: List[Dict[str, Any]], recon_findings: List[GeoEntity]) -> dbc.Offcanvas:
    """Create sliding offcanvas drawer for Cyber Threat Intelligence."""
    vuln_cards = []
    for v in cisa_vulns:
        known_ransomware = v.get("knownRansomware", "Unknown")
        is_ransomware = str(known_ransomware).strip().lower() == "known"
        source = "GITHUB ADVISORY" if "github" in str(v.get("vendorProject", "")).lower() else "CISA KEV"

        vuln_cards.append(
            html.Div(
                className="glass-panel p-2 mb-2 border-secondary",
                children=[
                    html.Div(
                        className="d-flex justify-content-between align-items-center mb-1",
                        children=[
                            html.Div([
                                html.Span(v.get("cveID"), className="fw-bold text-danger small font-mono"),
                                dbc.Badge(source, color="dark", className="text-info border border-secondary small ms-2", style={"fontSize": "0.62rem"})
                            ]),
                            dbc.Badge(f"CVSS {v.get('cvss', 9.0):.1f}", color="danger", className="small font-mono")
                        ]
                    ),
                    html.Div(
                        className="d-flex justify-content-between align-items-center mb-1",
                        children=[
                            html.Span(f"{v.get('vendorProject')} — {v.get('product')}", className="text-light fw-bold small"),
                            dbc.Badge(
                                "RANSOMWARE: KNOWN" if is_ransomware else "RANSOMWARE: UNKNOWN",
                                color="danger" if is_ransomware else "secondary",
                                className="small",
                                style={"fontSize": "0.6rem"}
                            )
                        ]
                    ),
                    html.P(v.get("vulnerabilityName"), className="text-info small m-0 mb-1 fw-bold"),
                    html.P(v.get("shortDescription", ""), className="text-muted small m-0 mb-1", style={"fontSize": "0.72rem", "lineHeight": "1.3"}),
                    html.Div(
                        className="d-flex justify-content-between align-items-center mt-1 pt-1 border-top border-dark",
                        children=[
                            html.Small(f"Added: {v.get('dateAdded')}", className="text-secondary font-mono", style={"fontSize": "0.68rem"}),
                            html.Small(f"Action: {v.get('requiredAction', 'Patch immediately')}", className="text-warning font-mono", style={"fontSize": "0.68rem"})
                        ]
                    )
                ]
            )
        )

    # Recon findings
    findings_rows = []
    for rf in recon_findings:
        findings_rows.append(
            html.Tr([
                html.Td(rf.subcategory, className="small text-info font-mono"),
                html.Td(rf.title, className="small text-white"),
                html.Td(f"{rf.lat:.2f}, {rf.lon:.2f}", className="small text-muted font-mono"),
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

    # Free Open Intelligence Feeds Breakdown
    open_feeds = [
        {"name": "CISA Known Exploited Vulnerabilities (KEV)", "records": "1,779 Exploits", "cadence": "Daily / Hourly", "status": "LIVE STREAM", "tag": "Gov / Federal"},
        {"name": "GitHub Security Advisory Database", "records": "Global Open-Source CVEs", "cadence": "Real-Time REST API", "status": "LIVE STREAM", "tag": "DevSecOps"},
        {"name": "abuse.ch Feodo Tracker (Botnet C2)", "records": "Live Emotet/QakBot IPs", "cadence": "Hourly Blocklist", "status": "LIVE STREAM", "tag": "Threat Intel"},
        {"name": "USGS Global Earthquake API", "records": "Past 24H M2.5+ Quakes", "cadence": "5-Minute Poll", "status": "LIVE STREAM", "tag": "Geophysical"},
        {"name": "NASA EONET v3 Natural Events", "records": "Wildfires, Volcanoes, Storms", "cadence": "15-Minute Sync", "status": "LIVE STREAM", "tag": "Earth Science"},
        {"name": "NOAA Space Weather Prediction Center", "records": "Kp Index & Solar Alerts", "cadence": "1-Minute Ingest", "status": "LIVE STREAM", "tag": "Space Weather"},
        {"name": "OpenSky Network ADS-B", "records": "Global Aircraft Transponders", "cadence": "Dynamic State Vectors", "status": "LIVE STREAM", "tag": "Air Telemetry"},
    ]

    feed_cards = []
    for f in open_feeds:
        feed_cards.append(
            html.Div(
                className="glass-panel p-2 mb-2 border-secondary",
                children=[
                    html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                        html.Span(f["name"], className="fw-bold text-white small"),
                        dbc.Badge(f["status"], color="success", className="small font-mono", style={"fontSize": "0.62rem"})
                    ]),
                    html.Div(className="d-flex justify-content-between align-items-center text-muted small font-mono", children=[
                        html.Span(f"Coverage: {f['records']}", className="text-info", style={"fontSize": "0.72rem"}),
                        html.Span(f"Cadence: {f['cadence']}", className="text-secondary", style={"fontSize": "0.70rem"})
                    ]),
                    html.Div(className="mt-1", children=[
                        dbc.Badge(f["tag"], color="dark", className="text-light border border-secondary", style={"fontSize": "0.6rem"}),
                        html.Span(" · Zero-Cost Open API · Windows SSL Resilient", className="text-muted ms-1", style={"fontSize": "0.65rem"})
                    ])
                ]
            )
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
                    label=f"CISA KEV CATALOG ({len(cisa_vulns)}+)",
                    tab_id="tab-kev",
                    children=[
                        html.Div(
                            className="p-2 mb-2 bg-dark rounded border border-secondary d-flex justify-content-between align-items-center font-mono small",
                            children=[
                                html.Span("FEED STATUS: LIVE STREAMING", className="text-success fw-bold"),
                                html.Span(f"{len(cisa_vulns)} CVEs PARSED (NEWEST FIRST)", className="text-info")
                            ]
                        ),
                        html.P("Active Known Exploited Vulnerabilities monitored by CISA & GitHub Advisory DB with mandatory remediation directives.", className="text-muted small my-2"),
                        html.Div(vuln_cards, style={"maxHeight": "calc(100vh - 230px)", "overflowY": "auto"})
                    ]
                ),
                dbc.Tab(
                    label="OPEN OSINT FEEDS",
                    tab_id="tab-open-feeds",
                    children=[
                        html.P("Connected open and free public threat and hazard telemetry pipelines feeding Plotsiris in real-time.", className="text-muted small my-2"),
                        html.Div(feed_cards, style={"maxHeight": "calc(100vh - 230px)", "overflowY": "auto"})
                    ]
                ),
                dbc.Tab(
                    label="RECON FINDINGS",
                    tab_id="tab-recon-findings",
                    children=[
                        html.P("Target nodes and domains pinned to live geospatial map via OSINT tools.", className="text-muted small my-2"),
                        html.Div(findings_table, style={"maxHeight": "calc(100vh - 230px)", "overflowY": "auto"})
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
