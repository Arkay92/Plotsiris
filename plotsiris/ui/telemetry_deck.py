"""12-Tile Modular Cyber & OSINT Telemetry Deck.

Recreates the dense, high-contrast, military-grade cyber-HUD interface with
12 modular panels (4x3 grid) wired directly into Plotsiris's real-time OSINT,
geospatial defense feeds, CISA KEV vulnerabilities, and threat telemetry.
"""

from __future__ import annotations

from dash import html, dcc
import plotly.graph_objects as go


def create_sparkline_fig(y_values: list[float], color: str = "#00e5ff") -> go.Figure:
    """Create lightweight minimalist sparkline for deck tiles."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=y_values,
        mode="lines+markers",
        line=dict(color=color, width=2, shape="spline"),
        marker=dict(size=4, color="#ffffff"),
        hoverinfo="y"
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=2, b=12),
        height=45,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False
    )
    return fig


def create_token_stream_fig() -> go.Figure:
    """Create mini throughput bar chart for Tile 10 (Telemetry Ingress rate)."""
    bars = [28, 42, 55, 68, 62, 85, 94, 78, 105, 128, 112, 120, 98, 135, 150, 142, 130, 160, 175, 165]
    fig = go.Figure(go.Bar(
        y=bars,
        marker=dict(
            color=["#00e5ff" if i > 15 else "#0284c7" for i in range(len(bars))],
            line=dict(width=0)
        )
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=4, b=4),
        height=52,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        showlegend=False
    )
    return fig


def create_telemetry_deck() -> html.Div:
    """Construct the 12-tile modular telemetry deck in a 4-column x 3-row grid wired to OSINT data."""

    # Tile 01: RECON TARGET / TARGET PROFILE
    tile_01 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("01 TARGET PROFILE", className="hud-tile-title"),
                html.Span("CMA-1990 / OK", className="hud-tile-badge text-success")
            ]),
            html.Div("cloudflare / dns-anycast", className="small text-muted font-mono"),
            html.H5("1.1.1.1", className="text-white fw-bold m-0 font-mono"),
            html.Div(className="d-flex align-items-center gap-2 my-1", children=[
                html.Span("0.0 THREAT", className="fw-bold text-success fs-5 font-mono"),
                html.Span("AS13335 (Cloudflare)", className="small text-secondary")
            ]),
            html.P(
                "Passive DNS resolved · Ports 53, 80, 443 open · 0 abuse flags on Feodo C2 / Tor Exit nodes",
                className="small text-muted m-0 font-mono",
                style={"fontSize": "0.72rem", "lineHeight": "1.2"}
            )
        ]
    )

    # Tile 02: THREAT MATRIX / ACTIVE VECTORS
    board_items = [
        ("KEV", "1,779", 95, "#f59e0b"),   # CISA KEV Exploited
        ("C2", "84", 75, "#ef4444"),       # Feodo C2 Botnets
        ("JAM", "14", 45, "#38bdf8"),      # GPS Jamming Zones
        ("NAT", "36", 32, "#10b981"),      # NASA EONET Hazards
        ("HUM", "18", 22, "#8b5cf6")       # ReliefWeb Crises
    ]
    tile_02_bars = []
    for label, val, pct, color in board_items:
        tile_02_bars.append(html.Div(
            className="d-flex align-items-center gap-2 mb-1 font-mono",
            style={"fontSize": "0.72rem"},
            children=[
                html.Span(label, className="text-secondary", style={"width": "30px"}),
                html.Div(
                    className="flex-grow-1 bg-dark rounded-1 overflow-hidden",
                    style={"height": "7px"},
                    children=[
                        html.Div(style={"width": f"{pct}%", "height": "100%", "backgroundColor": color})
                    ]
                ),
                html.Span(str(val), className="text-info fw-bold text-end", style={"width": "48px"})
            ]
        ))

    tile_02 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("02 THREAT MATRIX", className="hud-tile-title"),
                html.Span("DEFCON 3", className="hud-tile-badge text-warning")
            ]),
            html.Div(tile_02_bars, className="mt-1")
        ]
    )

    # Tile 03: RECON WORKFLOW / PIPELINE INSPECTOR
    tile_03 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("03 RECON WORKFLOW", className="hud-tile-title"),
                html.Span("PIPELINE", className="hud-tile-badge text-info")
            ]),
            html.H5("dns -> ports -> c2", className="text-white fw-bold font-mono m-0"),
            html.Div([
                html.Span("COMPLIANCE", className="small text-secondary font-mono d-block", style={"fontSize": "0.65rem"}),
                html.Span("CMA 1990 Scoped Authorization", className="small text-info font-mono fw-bold")
            ], className="my-1"),
            html.Div([
                html.Span("PIPELINE STAGE", className="small text-secondary font-mono d-block", style={"fontSize": "0.65rem"}),
                html.Span("Passive DNS > WHOIS > Port Scan > Tor/C2 Crosscheck", className="small text-light font-mono", style={"fontSize": "0.72rem"})
            ]),
            # Multi-segment progress bar showing recon verification stages
            html.Div(
                className="d-flex gap-1 mt-2",
                children=[
                    html.Div(className="flex-grow-1 bg-info rounded-1", style={"height": "4px"}, title="DNS Resolved"),
                    html.Div(className="flex-grow-1 bg-info rounded-1", style={"height": "4px"}, title="WHOIS Parsed"),
                    html.Div(className="flex-grow-1 bg-info rounded-1", style={"height": "4px"}, title="Active Ports Scoped"),
                    html.Div(className="flex-grow-1 bg-success rounded-1", style={"height": "4px"}, title="C2 Cleared"),
                ]
            )
        ]
    )

    # Tile 04: TACTICAL RADAR / 360° THREAT SWEEP
    tile_04 = html.Div(
        className="hud-tile p-2 position-relative",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("04 TACTICAL RADAR", className="hud-tile-title"),
                html.Span("360° SWEEP", className="hud-tile-badge text-info")
            ]),
            html.Div(
                className="d-flex align-items-center justify-content-between",
                children=[
                    # Circular radar scope SVG
                    html.Div(
                        className="radar-scope-container position-relative",
                        style={"width": "80px", "height": "80px"},
                        children=[
                            html.Div(className="radar-circle-outer"),
                            html.Div(className="radar-circle-mid"),
                            html.Div(className="radar-circle-inner"),
                            html.Div(className="radar-crosshair-h"),
                            html.Div(className="radar-crosshair-v"),
                            html.Div(className="radar-sweep-beam"),
                            html.Div(className="radar-blip", style={"top": "24%", "left": "60%"}, title="Red Sea Chokepoint"),
                            html.Div(className="radar-blip", style={"top": "68%", "left": "35%"}, title="Strait of Malacca"),
                            html.Div(className="radar-blip", style={"top": "40%", "left": "75%"}, title="Taiwan Strait"),
                            html.Div(className="radar-blip", style={"top": "50%", "left": "20%"}, title="Black Sea Front")
                        ]
                    ),
                    # Right stat metrics
                    html.Div(className="text-end font-mono", children=[
                        html.Span("CONTACTS", className="text-secondary d-block", style={"fontSize": "0.65rem"}),
                        html.Span("4,992", className="text-white fw-bold fs-4 d-block"),
                        html.Span("THEATERS", className="text-secondary d-block", style={"fontSize": "0.65rem"}),
                        html.Span("4 ACTIVE", className="text-info fw-bold fs-6")
                    ])
                ]
            ),
            html.Div("sweeps: Red Sea, Taiwan Strait, Black Sea", className="small text-secondary font-mono mt-1", style={"fontSize": "0.68rem"})
        ]
    )

    # Tile 05: THREAT TAXONOMY / APT INFRASTRUCTURE
    tree_lines = [
        ("GLOBAL THREAT TAXONOMY/", "text-secondary"),
        ("├── APT-29 (Cozy Bear)/", "text-info"),
        ("│   ├── CozyCar C2      [ACTIVE]", "text-danger"),
        ("│   └── CVE-2023-38831  [EXPLOITED]", "text-warning"),
        ("├── Sandworm SCADA/     [CRITICAL]", "text-white bg-danger bg-opacity-25 px-1 rounded"),
        ("├── Lazarus Group/     [FIN-SECTOR]", "text-info"),
        ("├── Feodo C2 Botnets/  [QAKBOT-84]", "text-danger"),
        ("└── The Tor Project/   [EXIT-NODES]", "text-muted")
    ]
    tile_05 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("05 THREAT TAXONOMY", className="hud-tile-title"),
                html.Span("MITRE ATT&CK", className="hud-tile-badge text-secondary")
            ]),
            html.Div(
                className="font-mono small p-1 rounded bg-black bg-opacity-50",
                style={"fontSize": "0.68rem", "lineHeight": "1.25", "maxHeight": "95px", "overflowY": "auto"},
                children=[
                    html.Div(line, className=cls) for line, cls in tree_lines
                ]
            )
        ]
    )

    # Tile 06: SIGINT STREAM / REAL-TIME INGESTION LOG
    log_lines = [
        ("12", "+", "ADS-B", "FORTE12 RQ-4B Global Hawk transponder active over Black Sea", "text-info"),
        ("14", "-", "EONET", "NASA thermal anomaly: active volcanic eruption cluster EONET-6124", "text-warning"),
        ("17", ">", "FEODO", "abuse.ch C2 Botnet 185.220.101.4 flag: Dridex C2 server", "text-danger"),
        ("20", "✓", "AIS", "Tanker MARAN GAS APOLLONIA transiting Strait of Malacca", "text-success"),
        ("24", "●", "CISA", "CVE-2024-21413 added to KEV catalog (CVSS 9.8 remote code execution)", "text-danger")
    ]
    tile_06 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("06 SIGINT STREAM", className="hud-tile-title"),
                html.Span("TAIL ->", className="hud-tile-badge text-success")
            ]),
            html.Div(
                className="font-mono small p-1 rounded bg-black bg-opacity-50",
                style={"fontSize": "0.68rem", "lineHeight": "1.25", "maxHeight": "95px", "overflowY": "auto"},
                children=[
                    html.Div(className="d-flex gap-2", children=[
                        html.Span(num, className="text-muted", style={"width": "18px"}),
                        html.Span(sym, className=cls, style={"width": "10px"}),
                        html.Span(action, className="text-secondary", style={"width": "42px"}),
                        html.Span(desc, className="text-light flex-grow-1 text-truncate")
                    ])
                    for num, sym, action, desc, cls in log_lines
                ]
            )
        ]
    )

    # Tile 07: INFRASTRUCTURE RISK / CRITICAL SECTOR HEATMAP
    matrix_rows = [
        ("NRG", ["bg-danger", "bg-danger", "bg-warning", "bg-info", "bg-danger", "bg-danger"]),
        ("MAR", ["bg-warning", "bg-info", "bg-dark", "bg-warning", "bg-dark", "bg-info"]),
        ("TEL", ["bg-dark", "bg-dark", "bg-info", "bg-info", "bg-dark", "bg-warning"]),
        ("FIN", ["bg-dark", "bg-dark", "bg-dark", "bg-info", "bg-dark", "bg-dark"]),
        ("GOV", ["bg-danger", "bg-warning", "bg-dark", "bg-danger", "bg-dark", "bg-info"]),
    ]
    col_labels = ["GRID", "PORT", "CABLE", "SATE", "PIPE", "SCADA"]
    tile_07_grid = []
    for label, cells in matrix_rows:
        tile_07_grid.append(html.Div(
            className="d-flex align-items-center gap-2 mb-1 font-mono",
            style={"fontSize": "0.65rem"},
            children=[
                html.Span(label, className="text-secondary fw-bold", style={"width": "28px", "flexShrink": "0"}),
                html.Div(
                    className="d-flex gap-1 flex-grow-1",
                    children=[
                        html.Div(
                            className=f"matrix-cell {c} flex-grow-1",
                            style={"height": "12px", "borderRadius": "2px"}
                        )
                        for c in cells
                    ]
                )
            ]
        ))

    tile_07 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("07 INFRASTRUCTURE RISK", className="hud-tile-title"),
                html.Span("SECTOR MATRIX", className="hud-tile-badge text-danger")
            ]),
            html.Div(
                className="d-flex align-items-center gap-2 text-muted font-mono mb-1",
                style={"fontSize": "0.58rem"},
                children=[
                    html.Span("", style={"width": "28px", "flexShrink": "0"}),
                    html.Div(
                        className="d-flex gap-1 flex-grow-1",
                        children=[
                            html.Span(col, className="flex-grow-1 text-center")
                            for col in col_labels
                        ]
                    )
                ]
            ),
            html.Div(tile_07_grid),
            html.Div("5 / 5 CRITICAL SECTORS MONITORED", className="small text-secondary font-mono mt-1", style={"fontSize": "0.65rem"})
        ]
    )

    # Tile 08: SOVEREIGN RISK / GEOPOLITICAL VOLATILITY
    tile_08 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("08 SOVEREIGN RISK", className="hud-tile-title"),
                html.Span("INDEX", className="hud-tile-badge text-warning")
            ]),
            html.H4("74.2 / 100", className="text-warning fw-bold font-mono m-0"),
            html.Span("elevated volatility across maritime chokepoints", className="small text-secondary font-mono d-block", style={"fontSize": "0.68rem"}),
            dcc.Graph(
                figure=create_sparkline_fig([54.2, 58.0, 64.5, 69.1, 71.8, 74.2], color="#f59e0b"),
                config={"displayModeBar": False},
                style={"height": "40px"}
            ),
            html.Div(
                className="d-flex justify-content-between text-muted font-mono",
                style={"fontSize": "0.58rem"},
                children=[html.Span("IND"), html.Span("MDE"), html.Span("EUR"), html.Span("SCS"), html.Span("AFR")]
            )
        ]
    )

    # Tile 09: INTEL BRIEFING / YAML OPERATIONAL SPEC
    tile_09 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("09 INTEL BRIEFING", className="hud-tile-title"),
                html.Span("YAML SPEC", className="hud-tile-badge text-info")
            ]),
            html.Pre(
                html.Code(
                    "1 ---\n"
                    "2 op_sitrep: DEFCON_3_FUSION\n"
                    "3 cisa_kev_unpatched: 1779\n"
                    "4 feodo_c2_botnets: 84\n"
                    "5 nasa_eonet_hazards: 36\n"
                    "6 cma_1990_scope: ENFORCED\n"
                    "7 human_in_the_loop: TRUE",
                    className="text-info font-mono small d-block"
                ),
                className="m-0 p-1 rounded bg-black bg-opacity-50",
                style={"fontSize": "0.68rem", "maxHeight": "90px", "overflowY": "hidden"}
            )
        ]
    )

    # Tile 10: TELEMETRY INGRESS / THROUGHPUT STREAM
    tile_10 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("10 TELEMETRY INGRESS", className="hud-tile-title"),
                html.Span("14 FEEDS", className="hud-tile-badge text-success")
            ]),
            dcc.Graph(
                figure=create_token_stream_fig(),
                config={"displayModeBar": False},
                style={"height": "48px"}
            ),
            html.Div(className="d-flex justify-content-between align-items-center mt-1", children=[
                html.Span("2.4k pkts/sec", className="text-white fw-bold font-mono small"),
                html.Span("latency 14ms", className="text-muted font-mono small", style={"fontSize": "0.68rem"})
            ]),
            html.Small("feed health 14/14 nominal · 0 dropped", className="text-info font-mono d-block", style={"fontSize": "0.65rem"})
        ]
    )

    # Tile 11: MULTI-DOMAIN C2 SENSORS
    tile_11 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("11 SENSOR TRACKS", className="hud-tile-title"),
                html.Span("GLOBAL COP", className="hud-tile-badge text-info")
            ]),
            html.Div(
                className="row g-2 text-center font-mono mt-1",
                children=[
                    html.Div(className="col-6", children=[
                        html.Span("AIR TRACKS", className="text-secondary d-block", style={"fontSize": "0.62rem"}),
                        html.Span("450+", className="text-info fw-bold fs-5")
                    ]),
                    html.Div(className="col-6", children=[
                        html.Span("SEA VESSELS", className="text-secondary d-block", style={"fontSize": "0.62rem"}),
                        html.Span("128", className="text-white fw-bold fs-5")
                    ]),
                    html.Div(className="col-6", children=[
                        html.Span("C2 BOTNETS", className="text-secondary d-block", style={"fontSize": "0.62rem"}),
                        html.Span("84", className="text-danger fw-bold fs-5")
                    ]),
                    html.Div(className="col-6", children=[
                        html.Span("CISA KEV", className="text-secondary d-block", style={"fontSize": "0.62rem"}),
                        html.Span("1,779", className="text-warning fw-bold fs-5")
                    ]),
                ]
            )
        ]
    )

    # Tile 12: OSINT RECON LOG / CERTIFICATE & PAYLOAD DUMP
    tile_12 = html.Div(
        className="hud-tile p-2",
        children=[
            html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                html.Span("12 RECON PAYLOAD DUMP", className="hud-tile-title"),
                html.Span("RAW DUMP", className="hud-tile-badge text-primary")
            ]),
            html.Div(
                className="font-mono small p-1 rounded bg-black bg-opacity-50",
                style={"fontSize": "0.65rem", "lineHeight": "1.2", "maxHeight": "90px", "overflowY": "hidden"},
                children=[
                    html.Div("TARGET: 1.1.1.1 (Cloudflare DNS)", className="text-info fw-bold"),
                    html.Div("CERT: CN=cloudflare-dns.com, O=Cloudflare Inc.", className="text-light"),
                    html.Div("PORTS: 53/udp open · 80/tcp open · 443/tcp open", className="text-success"),
                    html.Div("TOR EXIT: CLEAN · FEODO BOTNET: NO MATCH", className="text-success"),
                    html.Div("AUTHORIZATION: CMA-1990 CHECKBOX CONFIRMED", className="text-warning"),
                    html.Div("GEO: 37.7749,-122.4194 (US Anycast Hub)", className="text-muted")
                ]
            )
        ]
    )

    return html.Div(
        id="telemetry-deck-container",
        className="telemetry-grid w-100 p-2",
        children=[
            tile_01, tile_02, tile_03, tile_04,
            tile_05, tile_06, tile_07, tile_08,
            tile_09, tile_10, tile_11, tile_12
        ]
    )
