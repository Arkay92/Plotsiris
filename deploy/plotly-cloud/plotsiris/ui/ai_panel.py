"""AI Intelligence Analyst UI component (Gemini 2.5 Flash / Tactical Heuristic)."""

from dash import html, dcc
import dash_bootstrap_components as dbc


def create_ai_panel() -> dbc.Offcanvas:
    """Create sliding offcanvas drawer for AI Intelligence Analyst."""
    return dbc.Offcanvas(
        id="ai-offcanvas",
        title=html.Div([
            html.I(className="bi bi-cpu me-2 text-info"),
            html.Span("AI INTELLIGENCE ANALYST", style={"fontWeight": "700", "letterSpacing": "1.5px"}),
            dbc.Badge("GEMINI 2.5 READY", color="success", className="ms-2", style={"fontSize": "0.65rem"})
        ]),
        is_open=False,
        placement="end",
        backdrop=False,
        scrollable=True,
        className="offcanvas-custom",
        children=[
            html.P(
                "Tactical intelligence analysis synthesizing multi-domain live feeds (ADS-B aviation, maritime AIS, seismic tremors, CISA KEV, conflict frontlines, and defense equities).",
                className="text-muted small mb-3"
            ),
            # SITREP Briefing Button
            dbc.Button(
                [html.I(className="bi bi-file-earmark-text-fill me-2"), "GENERATE OPERATIONAL SITREP BRIEFING"],
                id="btn-generate-briefing",
                color="info",
                className="w-100 fw-bold mb-3 shadow-sm py-2"
            ),
            # Quick Prompts
            html.Div(className="mb-3", children=[
                html.Span("TACTICAL PRESETS: ", className="text-muted", style={"fontSize": "0.7rem"}),
                dbc.ButtonGroup([
                    dbc.Button("Top 3 Threats", id="btn-prompt-top3", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("Red Sea Status", id="btn-prompt-redsea", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("Cyber KEV Risk", id="btn-prompt-cyber", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                    dbc.Button("Space Weather", id="btn-prompt-space", size="sm", color="secondary", outline=True, className="py-0 px-2", style={"fontSize": "0.7rem"}),
                ], size="sm")
            ]),
            # Chat History Container
            html.Div(
                id="ai-chat-history",
                className="p-3 mb-3 border border-secondary rounded",
                style={
                    "height": "calc(100vh - 360px)",
                    "overflowY": "auto",
                    "backgroundColor": "rgba(10, 14, 20, 0.75)"
                },
                children=[
                    render_analyst_message(
                        "Welcome to the Plotsiris Tactical Intelligence Center. All 40+ global data streams are ingested and correlated. Ask situational awareness questions or generate a full operational briefing above."
                    )
                ]
            ),
            # Query Input Group
            dcc.Loading(
                id="ai-loading",
                type="dot",
                color="#00e5ff",
                children=html.Div()
            ),
            dbc.InputGroup([
                dbc.Input(
                    id="ai-query-input",
                    placeholder="Enter intelligence query or strategic question...",
                    type="text",
                    className="bg-dark text-white border-secondary small"
                ),
                dbc.Button(
                    [html.I(className="bi bi-send-fill me-1"), "QUERY"],
                    id="btn-send-ai-query",
                    color="info",
                    className="fw-bold px-3"
                )
            ])
        ]
    )


def render_user_message(text: str) -> html.Div:
    """Render user query bubble."""
    return html.Div(
        className="d-flex justify-content-end mb-3",
        children=[
            html.Div(
                className="p-2 px-3 rounded bg-secondary text-white small",
                style={"maxWidth": "85%", "border": "1px solid rgba(255,255,255,0.15)"},
                children=[
                    html.Div(html.Small("OPERATOR QUERY", className="text-info fw-bold mb-1 d-block", style={"fontSize": "0.65rem"})),
                    html.Div(text)
                ]
            )
        ]
    )


def render_analyst_message(text: str) -> html.Div:
    """Render analyst response bubble with markdown support."""
    return html.Div(
        className="d-flex justify-content-start mb-3",
        children=[
            html.Div(
                className="p-3 rounded glass-panel text-light small",
                style={"maxWidth": "95%", "borderLeft": "3px solid #00e5ff"},
                children=[
                    html.Div(
                        className="d-flex align-items-center mb-1",
                        children=[
                            html.I(className="bi bi-shield-shaded me-1 text-info"),
                            html.Small("ANALYST ASSESSOR", className="text-info fw-bold", style={"fontSize": "0.68rem"})
                        ]
                    ),
                    dcc.Markdown(text, className="m-0")
                ]
            )
        ]
    )
