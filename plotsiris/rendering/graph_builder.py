"""Entity Intelligence & Constellation Graph Builder.

Generates the cyber tactical constellation graph matching the reference
HUD operations layout: concentric range rings, azimuth reticles, dense node
clusters, targeting callout brackets ([ to / MATCHED ]), and status telemetry.
"""

from __future__ import annotations

import math
import random
from typing import Dict, Any, List
import plotly.graph_objects as go


class EntityGraphBuilder:
    """Builds interactive cyber constellation graph matching the operations HUD reference."""

    @staticmethod
    def build_graph(theme: str = "ghost") -> go.Figure:
        """Construct the high-density constellation network with targeting reticles."""
        random.seed(42)

        # Primary Core Clusters representing real-time OSINT & multi-domain defense entities
        core_nodes = [
            ("c2_core", 0.0, 0.0, "C2-CORE", 32, "#00e5ff", "Focal Root: Multi-Domain C2 Correlation Hub"),
            ("apt_29", 0.12, -0.32, "APT-29", 22, "#ef4444", "Threat Actor: APT-29 (Cozy Bear) [MATCHED]"),
            ("cisa_kev", 0.02, 0.38, "CISA-KEV", 20, "#f59e0b", "Known Exploited Catalog: 1,288 Active CVEs"),
            ("feodo_c2", 0.08, 0.22, "FEODO-C2", 18, "#ef4444", "abuse.ch Botnet Tracker: 84 Active C2s"),
            ("adsb_radar", -0.42, 0.68, "ADS-B-RADAR", 22, "#00e5ff", "OpenSky Network: Military & Commercial Flights"),
            ("ais_maritime", 0.18, 0.62, "AIS-MARITIME", 20, "#38bdf8", "Global AIS: Tankers, Cargo & Chokepoint Transit"),
            ("nasa_eonet", -0.15, 0.45, "NASA-EONET", 20, "#10b981", "NASA Natural Events: Volcanoes & Wildfires"),
            ("relief_web", -0.68, 0.32, "RELIEF-WEB", 20, "#8b5cf6", "UN OCHA: Global Crisis & Humanitarian Alerts"),
            ("gps_jamming", 0.25, -0.38, "GPS-JAMMING", 20, "#f59e0b", "Electronic Warfare: Black Sea/Baltic Spoofing"),
            ("tor_exit", 0.72, 0.52, "TOR-EXIT", 18, "#38bdf8", "The Tor Project: Live Directory of Exit Relays"),
            ("subsea_cables", 0.62, 0.28, "SUBSEA-CABLES", 16, "#0ea5e9", "Infrastructure: Transoceanic Fiber Routes"),
            ("defense_primes", 0.28, -0.68, "DEFENSE-PRIMES", 16, "#38bdf8", "Defense Equities: LMT, RTX, GD Tickers"),
            ("cma_1990", 0.75, -0.58, "CMA-1990-GATE", 16, "#10b981", "Authorization: UK Computer Misuse Act Scoping"),
            ("sigint_stream", -0.12, -0.72, "SIGINT-STREAM", 16, "#38bdf8", "Telemetry Ingress: 2.4k pkts/sec Live"),
        ]

        # Generate dense surrounding constellation nodes (star field)
        bg_x = []
        bg_y = []
        bg_text = []
        bg_colors = []
        bg_sizes = []

        num_bg_nodes = 140
        for i in range(num_bg_nodes):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.15, 0.95)
            # Add subtle cluster biasing towards top-left and center
            if random.random() < 0.35:
                bx = -0.35 + random.gauss(0, 0.18)
                by = 0.45 + random.gauss(0, 0.20)
            else:
                bx = dist * math.cos(angle)
                by = dist * math.sin(angle)

            bg_x.append(bx)
            bg_y.append(by)
            tag_id = f"node_{i:03d} (0x{random.randint(0x1000, 0xffff):04x})"
            bg_text.append(tag_id)
            if dist < 0.45:
                bg_colors.append("#38bdf8")
                bg_sizes.append(random.choice([4, 6, 8]))
            else:
                bg_colors.append("#0284c7" if random.random() < 0.5 else "#1e293b")
                bg_sizes.append(random.choice([3, 4, 5]))

        # Edges between nodes
        edge_x = []
        edge_y = []

        # Connect core nodes to focal 'to' node (radial spokes)
        focal_x, focal_y = 0.0, 0.0
        for nid, cx, cy, label, sz, col, desc in core_nodes[1:]:
            edge_x.extend([focal_x, cx, None])
            edge_y.extend([focal_y, cy, None])

        # Inter-cluster edges between intelligence domains
        inter_edges = [
            ("apt_29", "feodo_c2"),
            ("apt_29", "cisa_kev"),
            ("cisa_kev", "tor_exit"),
            ("feodo_c2", "tor_exit"),
            ("adsb_radar", "gps_jamming"),
            ("ais_maritime", "subsea_cables"),
            ("nasa_eonet", "relief_web"),
            ("cma_1990", "apt_29"),
            ("defense_primes", "sigint_stream"),
        ]
        core_pos = {nid: (cx, cy) for nid, cx, cy, label, sz, col, desc in core_nodes}
        for u, v in inter_edges:
            if u in core_pos and v in core_pos:
                x0, y0 = core_pos[u]
                x1, y1 = core_pos[v]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        # Dense web connecting random bg nodes to nearby core nodes
        for i in range(0, len(bg_x), 2):
            bx, by = bg_x[i], bg_y[i]
            # Find closest core node
            closest = min(core_nodes, key=lambda c: (c[1] - bx)**2 + (c[2] - by)**2)
            edge_x.extend([bx, closest[1], None])
            edge_y.extend([by, closest[2], None])

        fig = go.Figure()

        # 1. Edge Web Lines
        fig.add_trace(go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=0.8, color="rgba(0, 229, 255, 0.22)"),
            hoverinfo="none",
            showlegend=False
        ))

        # 2. Background Constellation Star Nodes
        fig.add_trace(go.Scatter(
            x=bg_x,
            y=bg_y,
            mode="markers",
            marker=dict(
                size=bg_sizes,
                color=bg_colors,
                opacity=0.85
            ),
            text=bg_text,
            hoverinfo="text",
            showlegend=False
        ))

        # 3. Core Labeled Nodes
        core_x = [c[1] for c in core_nodes]
        core_y = [c[2] for c in core_nodes]
        core_labels = [f"  {c[3]}" for c in core_nodes]
        core_colors = [c[5] for c in core_nodes]
        core_sizes = [c[4] for c in core_nodes]
        core_hover = [f"<b>{c[3]}</b><br>{c[6]}" for c in core_nodes]

        fig.add_trace(go.Scatter(
            x=core_x,
            y=core_y,
            mode="markers+text",
            text=core_labels,
            textposition="top right",
            textfont=dict(
                family="JetBrains Mono, monospace",
                size=11,
                color="#e0f2fe"
            ),
            marker=dict(
                size=core_sizes,
                color=core_colors,
                line=dict(width=2, color="#00e5ff"),
                symbol="circle"
            ),
            hovertext=core_hover,
            hoverinfo="text",
            showlegend=False
        ))

        # 4. Concentric Circular Radar/Range Rings (HUD Reticles)
        shapes = []
        for r, dash_style, opacity in [(0.25, "dash", 0.28), (0.50, "dot", 0.22), (0.75, "solid", 0.15)]:
            shapes.append(dict(
                type="circle",
                xref="x",
                yref="y",
                x0=-r,
                y0=-r,
                x1=r,
                y1=r,
                line=dict(color="rgba(0, 229, 255, 1.0)", width=1.2, dash=dash_style),
                opacity=opacity
            ))

        # Crosshair lines through center
        shapes.append(dict(
            type="line",
            xref="x",
            yref="y",
            x0=-1.1,
            y0=0,
            x1=1.1,
            y1=0,
            line=dict(color="rgba(0, 229, 255, 0.18)", width=1),
        ))
        shapes.append(dict(
            type="line",
            xref="x",
            yref="y",
            x0=0,
            y0=-1.0,
            x1=0,
            y1=1.0,
            line=dict(color="rgba(0, 229, 255, 0.18)", width=1),
        ))

        # 5. Targeting Callout Box: [ C2-CORE / MATCHED ] and [ APT-29 ]
        annotations = [
            # Main focal target bracket [ C2-CORE / MATCHED ]
            dict(
                x=0.0,
                y=0.0,
                xref="x",
                yref="y",
                text="<b>&nbsp;&nbsp;C2-CORE &nbsp;&nbsp;&nbsp;&nbsp;/ MATCHED&nbsp;&nbsp;</b>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor="#00e5ff",
                ax=80,
                ay=-20,
                bgcolor="rgba(8, 14, 26, 0.92)",
                bordercolor="#00e5ff",
                borderwidth=1.5,
                borderpad=4,
                font=dict(family="JetBrains Mono, monospace", size=13, color="#00e5ff")
            ),
            # Detailed callout box for APT-29 (lower left)
            dict(
                x=0.12,
                y=-0.32,
                xref="x",
                yref="y",
                text=(
                    "<span style='color:#ef4444;font-weight:bold;'>APT-29 (Cozy Bear)</span><br>"
                    "<span style='color:#64748b;font-size:9px;'>THREAT: CRITICAL · C2 ACTIVE</span><br>"
                    "<span style='color:#38bdf8;font-size:9px;'>CVE: CVE-2023-38831</span>"
                ),
                showarrow=True,
                arrowhead=1,
                arrowsize=1,
                arrowcolor="#ef4444",
                ax=-90,
                ay=30,
                bgcolor="rgba(8, 14, 26, 0.90)",
                bordercolor="rgba(239, 68, 68, 0.5)",
                borderwidth=1,
                borderpad=5,
                font=dict(family="JetBrains Mono, monospace", size=10, color="#f8fafc")
            )
        ]

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="#050810",
            plot_bgcolor="#050810",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.1, 1.1]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.95, 0.95]),
            shapes=shapes,
            annotations=annotations,
            hoverlabel=dict(
                bgcolor="#080e1a",
                bordercolor="#00e5ff",
                font=dict(family="JetBrains Mono, monospace", size=11, color="#f8fafc")
            ),
            uirevision="constant_graph"
        )

        return fig
