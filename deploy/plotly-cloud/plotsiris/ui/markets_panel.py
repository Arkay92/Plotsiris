"""Financial Markets & Sovereign Risk UI component."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import List, Dict, Any
from plotsiris.domain.models import MarketTicker
from plotsiris.rendering.charts import build_market_summary_chart


def create_markets_panel(tickers: List[MarketTicker], risks: List[Dict[str, Any]]) -> dbc.Offcanvas:
    """Create sliding offcanvas drawer for financial markets and country risk."""
    ticker_cards = []
    for t in tickers:
        color = "text-success" if t.change >= 0 else "text-danger"
        icon = "bi-arrow-up-right" if t.change >= 0 else "bi-arrow-down-right"
        ticker_cards.append(
            html.Div(
                className="glass-panel p-2 mb-2 d-flex justify-content-between align-items-center",
                children=[
                    html.Div([
                        html.Span(t.symbol, className="fw-bold text-white me-2 small"),
                        html.Span(t.name, className="text-muted small", style={"fontSize": "0.75rem"})
                    ]),
                    html.Div(className="text-end", children=[
                        html.Span(f"{t.unit}{t.price:,.2f}", className="fw-bold text-light me-2 small"),
                        html.Span([
                            html.I(className=f"bi {icon} me-1"),
                            f"{t.change_pct:+.2f}%"
                        ], className=f"fw-bold small {color}")
                    ])
                ]
            )
        )

    risk_rows = []
    for r in risks:
        risk_rows.append(
            html.Div(
                className="glass-panel p-2 mb-2 border-secondary",
                children=[
                    html.Div(className="d-flex justify-content-between align-items-center mb-1", children=[
                        html.Span(r["country"], className="fw-bold text-light small"),
                        dbc.Badge(f"{r['rating']} ({r['risk_index']}/100)", color="danger" if r["risk_index"] > 80 else "warning")
                    ]),
                    html.Small(r["status"], className="text-muted")
                ]
            )
        )

    summary_chart = build_market_summary_chart(tickers, theme="ghost")

    return dbc.Offcanvas(
        id="markets-offcanvas",
        title=html.Div([
            html.I(className="bi bi-graph-up me-2 text-info"),
            html.Span("DEFENSE MARKETS & COUNTRY RISK", style={"fontWeight": "700", "letterSpacing": "1.5px"})
        ]),
        is_open=False,
        placement="end",
        className="offcanvas-custom",
        children=[
            dbc.Tabs([
                dbc.Tab(
                    label="EQUITIES & COMMODITIES",
                    tab_id="tab-markets-tickers",
                    children=[
                        html.P("Real-time movements across defense primes, energy, commodities, and digital assets.", className="text-muted small my-2"),
                        dcc.Graph(figure=summary_chart, config={"displayModeBar": False}),
                        html.Div(ticker_cards, style={"maxHeight": "calc(100vh - 360px)", "overflowY": "auto"})
                    ]
                ),
                dbc.Tab(
                    label="SOVEREIGN RISK",
                    tab_id="tab-country-risk",
                    children=[
                        html.P("Geopolitical conflict and maritime transit disruption risk scoring.", className="text-muted small my-2"),
                        html.Div(risk_rows, style={"maxHeight": "calc(100vh - 200px)", "overflowY": "auto"})
                    ]
                )
            ], className="border-secondary")
        ]
    )
