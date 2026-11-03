"""Entity Intelligence Graph: Force-directed network visualization across threat domains."""

from __future__ import annotations

import logging
from typing import Dict, Any, List
import networkx as nx
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


class EntityGraphBuilder:
    """Builds interactive force-directed relationship graphs connecting threat actors, CVEs, C2s, and targets."""

    @staticmethod
    def build_graph(theme: str = "ghost") -> go.Figure:
        """Generate networkx spring layout graph rendered with Plotly."""
        G = nx.Graph()

        # Nodes: [id, label, category, severity, details]
        nodes = [
            # Central Hub
            ("mitre", "MITRE ATT&CK Enterprise Matrix", "framework", 28, "#00e5ff", "Framework hub correlating tactics and techniques."),
            # Threat Actor Groups
            ("apt28", "APT28 (Fancy Bear / GRU)", "actor", 22, "#dc2626", "Russian military intelligence cyber unit targeting defense and diplomacy."),
            ("volt_typhoon", "Volt Typhoon (UNC3236)", "actor", 22, "#dc2626", "State-sponsored actor targeting US critical infrastructure and SCADA."),
            ("lazarus", "Lazarus Group (RGB 121st)", "actor", 22, "#dc2626", "DPRK state group targeting financial institutions and cryptocurrency."),
            ("lockbit", "LockBit 3.0 Syndicate", "actor", 20, "#f97316", "Global ransomware-as-a-service cartel."),
            ("scattered_spider", "Scattered Spider (UNC3944)", "actor", 20, "#f97316", "Sophisticated social engineering and cloud identity compromise."),
            # Malware Families
            ("cobalt_strike", "Cobalt Strike Beacon", "malware", 16, "#a855f7", "Adversary simulation and post-exploitation framework."),
            ("mad_license", "MadLicense RPC Exploit", "malware", 18, "#ef4444", "Heap overflow payload targeting Windows Remote Desktop."),
            ("sliver", "Sliver C2 Implant", "malware", 16, "#a855f7", "Open-source cross-platform adversary emulation tool."),
            ("kv_botnet", "KV-Botnet SOHO Proxy", "malware", 16, "#a855f7", "Compromised SOHO routers utilized for covert command-and-control."),
            # Vulnerabilities (CVEs)
            ("cve_2024_38077", "CVE-2024-38077 (CVSS 9.8)", "cve", 16, "#ef4444", "Windows RDL Service unauthenticated remote code execution."),
            ("cve_2024_21887", "CVE-2024-21887 (CVSS 9.1)", "cve", 15, "#ef4444", "Ivanti Connect Secure command injection vulnerability."),
            ("cve_2024_1709", "CVE-2024-1709 (CVSS 10.0)", "cve", 16, "#ef4444", "ConnectWise ScreenConnect auth bypass leading to RCE."),
            # Target Sectors & Strategic Infrastructure
            ("defense_sector", "Defense Industrial Base (DIB)", "target", 20, "#38bdf8", "Contractors, avionics manufacturers, and logistics."),
            ("power_grid", "Energy & Electrical Substation SCADA", "target", 20, "#38bdf8", "Critical power generation, transmission, and water utilities."),
            ("maritime_shipping", "Global Maritime & Port Logistics", "target", 18, "#38bdf8", "Harbor traffic controllers, container ports, and AIS infrastructure."),
            ("finance_defi", "Financial & Crypto Infrastructure", "target", 18, "#38bdf8", "Banking networks, SWIFT endpoints, and liquidity bridges."),
            # C2 IP Nodes
            ("ip_185", "185.220.101.5 (Tor Exit / C2)", "c2", 14, "#ec4899", "German Tor exit node utilized for spearphishing exfiltration."),
            ("ip_198", "198.51.100.44 (Volt SOHO Relay)", "c2", 14, "#ec4899", "Compromised edge router functioning as operational relay.")
        ]

        for nid, label, cat, size, color, desc in nodes:
            G.add_node(nid, label=label, category=cat, size=size, color=color, desc=desc)

        # Edges
        edges = [
            ("apt28", "mitre"),
            ("volt_typhoon", "mitre"),
            ("lazarus", "mitre"),
            ("lockbit", "mitre"),
            ("scattered_spider", "mitre"),
            # Actor -> Malware
            ("apt28", "cobalt_strike"),
            ("apt28", "ip_185"),
            ("volt_typhoon", "kv_botnet"),
            ("volt_typhoon", "ip_198"),
            ("scattered_spider", "sliver"),
            ("lockbit", "cobalt_strike"),
            # Malware / Exploit -> CVE
            ("mad_license", "cve_2024_38077"),
            ("volt_typhoon", "cve_2024_21887"),
            ("lockbit", "cve_2024_1709"),
            ("apt28", "mad_license"),
            # Actor -> Targets
            ("apt28", "defense_sector"),
            ("volt_typhoon", "power_grid"),
            ("volt_typhoon", "maritime_shipping"),
            ("lazarus", "finance_defi"),
            ("lockbit", "defense_sector"),
            ("scattered_spider", "finance_defi"),
        ]

        for u, v in edges:
            G.add_edge(u, v)

        # Compute Spring Layout
        pos = nx.spring_layout(G, seed=42, k=0.45, iterations=60)

        # Build Edge Traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1.2, color="rgba(0, 229, 255, 0.35)" if theme == "ghost" else "rgba(100, 116, 139, 0.4)"),
            hoverinfo="none",
            mode="lines"
        )

        # Build Node Traces
        node_x = []
        node_y = []
        node_colors = []
        node_sizes = []
        node_texts = []
        hover_texts = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            data = G.nodes[node]
            node_colors.append(data["color"])
            node_sizes.append(data["size"])
            node_texts.append(data["label"])
            hover_texts.append(
                f"<b>{data['label']}</b><br>"
                f"Category: {data['category'].upper()}<br>"
                f"{data['desc']}"
            )

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=node_texts,
            textposition="top center",
            textfont=dict(
                size=9,
                color="#e2e8f0" if theme == "ghost" else "#1e293b",
                family="JetBrains Mono, monospace"
            ),
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=1.5, color="#00e5ff" if theme == "ghost" else "#0284c7"),
                opacity=0.95
            ),
            hovertext=hover_texts
        )

        bg_color = "#0a0e14" if theme == "ghost" else "#f8fafc"
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode="closest",
                margin=dict(b=10, l=10, r=10, t=10),
                paper_bgcolor=bg_color,
                plot_bgcolor=bg_color,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            )
        )
        return fig
