"""Plotsiris Dash Application Factory & Entry Point."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from dash import Dash
import dash_bootstrap_components as dbc

from plotsiris.config import HOST, PORT, DEBUG
from plotsiris.ui.layout import create_layout
from plotsiris.ui.callbacks import register_callbacks


def create_app(
    host: str = HOST,
    port: int = PORT,
    debug: bool = DEBUG,
    assets_folder: str | None = None,
) -> Dash:
    """Create and configure the Plotsiris Dash application instance."""
    if assets_folder is None:
        candidate_parent = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        candidate_adjacent = os.path.join(os.getcwd(), "assets")
        if os.path.isdir(candidate_adjacent):
            assets_folder = candidate_adjacent
        else:
            assets_folder = candidate_parent

    app = Dash(
        __name__,
        title="Plotsiris - Open Source Intelligence & Reconnaissance Integrated System",
        assets_folder=assets_folder,
        external_stylesheets=[
            dbc.themes.DARKLY,
            dbc.icons.BOOTSTRAP,
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"},
            {"name": "description", "content": "Plotsiris: Python, Plotly & Dash real-time global intelligence dashboard clone of Osiris."},
            {"name": "theme-color", "content": "#0a0e14"}
        ],
        suppress_callback_exceptions=True,
    )

    # Register plotly component suite package path so dcc.Graph can load plotly.min.js without 500 error
    app.registered_paths["plotly"].add("package_data/plotly.min.js")
    app.registered_paths["plotly"].add("package_data/plotly.min.js.map")

    app.layout = create_layout()
    register_callbacks(app)

    return app


# Default module instance for WSGI servers
app = create_app()
server = app.server


def main():
    parser = argparse.ArgumentParser(description="Plotsiris OSINT Dashboard")
    parser.add_argument("--host", default=HOST, help="Binding host")
    parser.add_argument("--port", type=int, default=PORT, help="Port number")
    parser.add_argument("--debug", action="store_true", default=DEBUG, help="Debug mode")
    args = parser.parse_args()

    custom_app = create_app(host=args.host, port=args.port, debug=args.debug)
    custom_app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
