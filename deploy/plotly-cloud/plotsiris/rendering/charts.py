"""Supplementary HUD charts for space weather, markets, and threat metrics."""

from __future__ import annotations

from typing import List, Dict, Any
import plotly.graph_objects as go
from plotsiris.domain.models import MarketTicker


def build_kp_index_chart(kp_value: float = 3.67, theme: str = "ghost") -> go.Figure:
    """Build NOAA SWPC Kp index bar visualization."""
    levels = ["0", "1", "2", "3", "4", "5 (G1)", "6 (G2)", "7 (G3)", "8 (G4)", "9 (G5)"]
    colors = ["#10b981", "#10b981", "#10b981", "#eab308", "#f97316", "#ef4444", "#dc2626", "#b91c1c", "#7f1d1d", "#450a0a"]
    bar_colors = [colors[i] if i <= int(kp_value) else ("#1e293b" if theme == "ghost" else "#e2e8f0") for i in range(10)]

    fig = go.Figure(go.Bar(
        x=levels,
        y=[1] * 10,
        marker=dict(color=bar_colors),
        hoverinfo="x"
    ))

    bg = "#0a0e14" if theme == "ghost" else "#ffffff"
    text_color = "#e2e8f0" if theme == "ghost" else "#1e293b"

    fig.update_layout(
        height=70,
        margin=dict(l=0, r=0, t=0, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(size=8, color=text_color)),
        yaxis=dict(showgrid=False, showticklabels=False),
        showlegend=False
    )
    return fig


def build_market_summary_chart(tickers: List[MarketTicker], theme: str = "ghost") -> go.Figure:
    """Build horizontal comparison bar chart of top defense & commodity moves."""
    sample = [t for t in tickers if t.category in ("DEFENSE", "COMMODITY", "ENERGY")][:8]
    names = [t.symbol for t in sample]
    pcts = [t.change_pct for t in sample]
    colors = ["#10b981" if p >= 0 else "#ef4444" for p in pcts]

    fig = go.Figure(go.Bar(
        x=pcts,
        y=names,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{p:+.2f}%" for p in pcts],
        textposition="auto",
        hoverinfo="text"
    ))

    text_color = "#e2e8f0" if theme == "ghost" else "#1e293b"

    fig.update_layout(
        height=180,
        margin=dict(l=50, r=20, t=10, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#1e293b" if theme == "ghost" else "#e2e8f0", tickfont=dict(size=9, color=text_color)),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, color=text_color)),
        showlegend=False
    )
    return fig
