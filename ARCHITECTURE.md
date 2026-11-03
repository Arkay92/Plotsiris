# Plotsiris Architecture & System Specification

This document details the software architecture, design patterns, data pipelines, and extension points of **Plotsiris**.

---

## 1. Architectural Philosophy

Plotsiris transitions Osiris from a Next.js / TypeScript / React / WebGL stack to a native **Python, Plotly, and Dash** application designed for:

1. **Python Data Science & OSINT Convergence**: Direct utilization of Python's scientific and reconnaissance ecosystem (`requests`, `networkx`, `pandas`, `socket`, `ssl`).
2. **Keyless-First & Fail-Soft Reliability**: Every external fetch (USGS earthquakes, OpenSky ADS-B, CISA KEV, NOAA space weather) operates under isolated timeouts. If network boundaries are unreachable or API quotas are exhausted, deterministic cached baselines maintain uninterrupted 60 fps situational awareness.
3. **GPU-Accelerated MapLibre / Plotly Rendering**: Unified Plotly MapLibre / Mapbox traces render thousands of georeferenced entities without client-side degradation.
4. **Cloud-Native Compatibility**: Fully compatible with Plotly Cloud, Dash Enterprise, Heroku, AWS ECS, GCP Cloud Run, and Docker.

---

## 2. Directory Structure

```
Plotsiris/
├── app.py                     # Plotly Cloud / WSGI entry point (app:server)
├── main.py                    # Local development runner
├── requirements.txt           # Python dependency specifications
├── pyproject.toml             # Build and test specifications
├── Dockerfile                 # Container image specification
├── README.md                  # Comprehensive user documentation
├── ARCHITECTURE.md            # System architecture guide
├── assets/
│   └── styles.css             # Military SIGINT HUD styling & dual theme tokens
├── deploy/
│   └── plotly-cloud/          # Self-contained Plotly Cloud distribution folder
├── scripts/
│   └── prepare_cloud.py       # Cloud deployment preparation script
├── tests/
│   ├── test_domain.py         # Domain models and constant test suite
│   ├── test_services.py       # Intelligence services and OSINT test suite
│   └── test_rendering.py      # Map, graph, and Dash app test suite
└── plotsiris/
    ├── __init__.py            # Package root exports
    ├── config.py              # Environment configuration and style constants
    ├── app.py                 # Dash application factory (create_app)
    ├── domain/
    │   ├── __init__.py        # Domain model exports
    │   ├── models.py          # GeoEntity, RoutePath, OsintResult, MarketTicker
    │   └── constants.py       # Region presets, layer metadata, chokepoints, cables
    ├── services/
    │   ├── __init__.py        # Services exports
    │   ├── data_manager.py    # Master stateful aggregator & cache coordinator
    │   ├── aviation.py        # ADS-B civil & military reconnaissance flights
    │   ├── maritime.py        # AIS vessels, strategic chokepoints, subsea cables
    │   ├── hazards.py         # USGS earthquakes, NASA FIRMS wildfires, storms
    │   ├── threats.py         # Armed conflict frontlines, nuclear plants, GPS jamming
    │   ├── cyber.py           # CISA KEV active vulnerabilities, Tor exit nodes
    │   ├── space_weather.py   # NOAA SWPC Kp index, satellite orbit tracks
    │   ├── cctv.py            # Global surveillance camera feed registry
    │   ├── markets.py         # Defense contractor equities, commodities, risk
    │   ├── osint_toolkit.py   # 20-tool reconnaissance engine
    │   └── ai_analyst.py      # Gemini 2.5 Flash / Tactical heuristic SITREP engine
    ├── rendering/
    │   ├── __init__.py        # Rendering exports
    │   ├── map_builder.py     # Plotly MapLibre multi-trace rendering engine
    │   ├── graph_builder.py   # Force-directed NetworkX entity relationship graph
    │   └── charts.py          # Space weather Kp index & market comparison charts
    └── ui/
        ├── __init__.py        # UI exports
        ├── layout.py          # Master HUD layout & responsive viewport assembly
        ├── callbacks.py       # Dash interactive callbacks
        ├── layer_panel.py     # Left-rail intelligence layer toggles & count badges
        ├── osint_panel.py     # 20-tool reconnaissance offcanvas panel
        ├── ai_panel.py        # AI Intelligence Analyst chat & briefing panel
        ├── cyber_panel.py     # Cyber Threat Intel & Recon Findings panel
        ├── entity_graph_panel.py # Force-directed graph explorer modal
        ├── markets_panel.py   # Financial equities & country risk panel
        ├── news_panel.py      # 24/7 SIGINT intelligence wire panel
        ├── camera_modal.py    # Live CCTV surveillance feed viewer modal
        └── inspector_panel.py # Interactive map entity detail card
```

---

## 3. Data Flow Architecture

```
[ External Feeds & APIs ]               [ Deterministic Fallback Caches ]
 (USGS, OpenSky, CISA, etc.)                  (Baseline GeoJSON / Seeds)
            │                                             │
            └───────────────┬─────────────────────────────┘
                            ▼
                  [ Domain Services ]
            (Aviation, Maritime, Hazards,
             Cyber, Space, CCTV, Markets)
                            │
                            ▼
                  [ Master DataManager ]
             (Layer aggregation, filtering,
             pinning, and state caching)
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
    [ MapBuilder Engine ]        [ UI Component Tree ]
    (Plotly Scattermap GPU        (Status bar, Drawers,
     traces & route arcs)          Inspector, Modals)
             │                             │
             └──────────────┬──────────────┘
                            ▼
              [ Dash Reactive Event Loop ]
               (User clicks, Presets,
                OSINT scans, AI Briefings)
```

---

## 4. Deployment Pipeline

The build script `scripts/prepare_cloud.py` creates a clean, test-free, self-contained deployment bundle in `deploy/plotly-cloud/`. 

This satisfies the requirements of **Plotly Cloud** and **Dash Enterprise**, where `app.py` exposes an explicit `server` instance (`server = app.server`) for Gunicorn WSGI workers.
