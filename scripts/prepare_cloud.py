"""Build a self-contained Plotly Cloud upload folder without testing caches or environments.

Run: python scripts/prepare_cloud.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


def copy_tree_without_cache(src: Path, dst: Path) -> None:
    """Copy directory tree excluding __pycache__ and hidden files."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name == "__pycache__" or item.name.startswith("."):
            continue
        target = dst / item.name
        if item.is_dir():
            copy_tree_without_cache(item, target)
        else:
            shutil.copy2(item, target)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    destination = root / "deploy" / "plotly-cloud"

    # Reset destination folder
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    # 1. Copy top-level entry files
    for name in ("app.py", "main.py", "requirements.txt", "README.md"):
        src = root / name
        if src.is_file():
            shutil.copy2(src, destination / name)

    # 2. Copy assets directory
    assets_src = root / "assets"
    if assets_src.is_dir():
        copy_tree_without_cache(assets_src, destination / "assets")

    # 3. Copy plotsiris package directory
    pkg_src = root / "plotsiris"
    if pkg_src.is_dir():
        copy_tree_without_cache(pkg_src, destination / "plotsiris")

    # 4. Clean up any residual __pycache__
    for cache in destination.rglob("__pycache__"):
        if cache.is_dir():
            shutil.rmtree(cache)

    print(f"\n[OK] Plotly Cloud deployment package prepared successfully at:")
    print(f"   {destination}\n")
    print("Deployment instructions for Plotly Cloud / Dash Enterprise:")
    print("1. Upload the contents of 'deploy/plotly-cloud/' to Plotly Cloud or Dash Enterprise.")
    print("2. Ensure the entrypoint file is set to 'app.py' (or 'main.py').")
    print("3. Set the Python version to 3.10, 3.11 or 3.12.")
    print("4. Plotly Cloud will automatically install dependencies from 'requirements.txt'")
    print("   and serve the app via gunicorn using 'app:server'.\n")


if __name__ == "__main__":
    main()
