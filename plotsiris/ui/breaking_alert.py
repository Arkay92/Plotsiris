"""Live breaking event alert box component for top-right HUD notification."""

from typing import List, Dict, Any
from dash import html, dcc
import dash_bootstrap_components as dbc

BREAKING_EVENTS: List[Dict[str, Any]] = [
    {
        "id": "break_01",
        "tag": "FLASH TRAFFIC // AIR DEFENSE",
        "sev": "CRITICAL",
        "title": "CENTCOM Intercepts Anti-Ship Missiles Over Gulf of Aden",
        "source": "DEFENSE TELEGRAPH",
        "time": "Just Now",
        "region": "Red Sea / Gulf of Aden",
        "summary": "Arleigh Burke-class DDG engaged 2 inbound anti-ship cruise missiles targeting commercial container ship. Air defense interception verified.",
        "lat": 12.8,
        "lon": 44.5,
        "zoom": 5.8
    },
    {
        "id": "break_02",
        "tag": "ZERO-DAY EXPLOIT // CISA EMERGENCY DIRECTIVE",
        "sev": "CRITICAL",
        "title": "CVE-2026-124194: Active Zero-Day in Microsoft 365 Parsing",
        "source": "CISA KEV / GITHUB ADVISORY",
        "time": "3m ago",
        "region": "Global / Federal Civilian",
        "summary": "Memory corruption in OLE stream parser actively exploited in the wild bypassing Mark-of-the-Web. Emergency mitigation directive issued.",
        "lat": 38.9,
        "lon": -77.0,
        "zoom": 5.5
    },
    {
        "id": "break_03",
        "tag": "VOLCANIC HAZARD // TRANS-PACIFIC AVIATION",
        "sev": "HIGH",
        "title": "Kamchatka Shiveluch Explosive Eruption Plume at 36,000 FT",
        "source": "NASA EONET v3 / SATELLITE",
        "time": "11m ago",
        "region": "North Pacific / Kamchatka",
        "summary": "Explosive ash column detected directly across trans-Pacific polar air corridors. Aviation Color Code RED declared.",
        "lat": 56.65,
        "lon": 161.36,
        "zoom": 5.2
    },
    {
        "id": "break_04",
        "tag": "INFRASTRUCTURE RISK // SUBSEA FIBER CABLE",
        "sev": "HIGH",
        "title": "C-Lion1 Undersea Fiber Optical Trunk Degradation in Baltic Sea",
        "source": "MARITIME AIS / TELEMETRY",
        "time": "18m ago",
        "region": "Baltic Sea (Helsinki - Rostock)",
        "summary": "Sudden signal attenuation and acoustic vibration logged along subsea optical route. Patrol vessels dispatched to investigate anomaly.",
        "lat": 59.8,
        "lon": 24.5,
        "zoom": 6.0
    },
    {
        "id": "break_05",
        "tag": "ELECTRONIC WARFARE // GPS SPOOFING SURGE",
        "sev": "CRITICAL",
        "title": "Severe GNSS Spoofing & Jamming Corridor Active Over Eastern Med",
        "source": "SIGINT STREAM // ADS-B RECON",
        "time": "25m ago",
        "region": "Eastern Mediterranean / Cyprus FIR",
        "summary": "Multiple commercial aircraft transponders reporting complete loss of GPS integrity and phantom runway positions.",
        "lat": 34.5,
        "lon": 33.5,
        "zoom": 5.5
    }
]


def create_breaking_alert() -> html.Div:
    """Create persistent HUD breaking alert box in top-right corner."""
    init_event = BREAKING_EVENTS[0]
    sev = init_event.get("sev", "CRITICAL")
    sev_color = "danger" if sev == "CRITICAL" else "warning"

    return html.Div(
        id="breaking-alert-wrapper",
        className="breaking-alert-wrapper",
        style={"display": "block"},
        children=[
            dcc.Store(
                id="breaking-alert-store",
                data={
                    "index": 0,
                    "visible": True,
                    "lat": init_event["lat"],
                    "lon": init_event["lon"],
                    "zoom": init_event.get("zoom", 5.8)
                }
            ),
            dcc.Interval(id="breaking-alert-interval", interval=22000, n_intervals=0),

            html.Div(
                id="breaking-alert-card",
                className="breaking-alert-card p-3",
                children=[
                    # Animated danger scanline
                    html.Div(id="alert-strip", className=f"breaking-alert-strip {sev.lower()}"),

                    # Header with pulsing radar dot, tag, and dismiss button
                    html.Div(
                        className="d-flex justify-content-between align-items-center mb-1",
                        children=[
                            html.Div(
                                className="d-flex align-items-center gap-2",
                                children=[
                                    html.Span(className="breaking-radar-dot"),
                                    html.Span(
                                        init_event.get("tag"),
                                        id="alert-tag",
                                        className="font-mono text-danger fw-bold small",
                                        style={"fontSize": "0.70rem", "letterSpacing": "1px"}
                                    )
                                ]
                            ),
                            html.Div(
                                className="d-flex align-items-center gap-2",
                                children=[
                                    dbc.Badge(
                                        sev,
                                        id="alert-badge",
                                        color=sev_color,
                                        className="font-mono small",
                                        style={"fontSize": "0.62rem"}
                                    ),
                                    html.Button(
                                        "✕",
                                        id="btn-dismiss-alert",
                                        className="btn-close-alert",
                                        title="Dismiss Alert"
                                    )
                                ]
                            )
                        ]
                    ),

                    # Headline Title
                    html.H6(
                        init_event.get("title"),
                        id="alert-title",
                        className="text-white fw-bold font-mono my-1",
                        style={"fontSize": "0.86rem", "lineHeight": "1.3"}
                    ),

                    # Metadata line
                    html.Div(
                        className="d-flex justify-content-between align-items-center font-mono text-muted mb-2",
                        style={"fontSize": "0.68rem"},
                        children=[
                            html.Span(
                                f"{init_event.get('source')} · {init_event.get('region')}",
                                id="alert-source-region",
                                className="text-info"
                            ),
                            html.Span(
                                init_event.get("time"),
                                id="alert-time",
                                className="text-warning"
                            )
                        ]
                    ),

                    # Summary narrative
                    html.P(
                        init_event.get("summary"),
                        id="alert-summary",
                        className="text-light small m-0 mb-2 font-mono",
                        style={"fontSize": "0.73rem", "lineHeight": "1.35", "opacity": "0.9"}
                    ),

                    # Action bar
                    html.Div(
                        className="d-flex align-items-center gap-2 mt-2 pt-2 border-top border-dark",
                        children=[
                            dbc.Button(
                                [html.I(className="bi bi-crosshair me-1"), "LOCATE ON MAP"],
                                id="btn-alert-locate",
                                size="sm",
                                color="danger",
                                outline=True,
                                className="font-mono fw-bold py-1 px-2 flex-grow-1",
                                style={"fontSize": "0.70rem", "letterSpacing": "0.5px"}
                            ),
                            dbc.Button(
                                [html.I(className="bi bi-broadcast me-1"), "INTEL WIRE"],
                                id="btn-alert-intel",
                                size="sm",
                                color="dark",
                                className="border-secondary text-info font-mono py-1 px-2",
                                style={"fontSize": "0.70rem"}
                            ),
                        ]
                    )
                ]
            )
        ]
    )
