"""24/7 Intelligence News Wire UI component."""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import List
from plotsiris.domain.models import NewsAlert


def create_news_panel(alerts: List[NewsAlert]) -> dbc.Offcanvas:
    """Create sliding offcanvas drawer for 24/7 real-time intelligence wire."""
    alert_cards = []
    for a in alerts:
        color = "danger" if a.risk_level == "CRITICAL" else ("warning" if a.risk_level == "HIGH" else "info")
        alert_cards.append(
            html.Div(
                className="glass-panel p-3 mb-3 border-secondary",
                children=[
                    html.Div(
                        className="d-flex justify-content-between align-items-center mb-1",
                        children=[
                            html.Span(a.source, className="text-info fw-bold small"),
                            html.Div([
                                html.Span(a.time_ago, className="text-muted small me-2", style={"fontSize": "0.7rem"}),
                                dbc.Badge(a.risk_level, color=color, className="small")
                            ])
                        ]
                    ),
                    html.H6(a.title, className="text-light fw-bold mb-1", style={"fontSize": "0.88rem"}),
                    html.P(a.summary, className="text-muted small m-0"),
                    html.Small(f"Region: {a.region}", className="text-secondary mt-1 d-block", style={"fontSize": "0.68rem"})
                ]
            )
        )

    return dbc.Offcanvas(
        id="news-offcanvas",
        title=html.Div([
            html.I(className="bi bi-broadcast me-2 text-info"),
            html.Span("24/7 INTELLIGENCE WIRE", style={"fontWeight": "700", "letterSpacing": "1.5px"})
        ]),
        is_open=False,
        placement="end",
        className="offcanvas-custom",
        children=[
            html.P("Live machine-scored geopolitical events, kinetic skirmishes, and tactical cyber incidents.", className="text-muted small mb-3"),
            html.Div(alert_cards, style={"maxHeight": "calc(100vh - 120px)", "overflowY": "auto"})
        ]
    )
