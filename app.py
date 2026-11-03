"""Plotly Cloud entry point with an explicit, discoverable Dash instance."""

import os
from pathlib import Path

from plotsiris.app import create_app

# Locate assets folder
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

app = create_app(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8050)),
    debug=False,
    assets_folder=str(ASSETS_DIR) if ASSETS_DIR.is_dir() else None,
)
server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)
