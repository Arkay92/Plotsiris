import os
import sys
import time
import socket
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent

def find_port():
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]

port = find_port()
print(f"Starting server on port {port}...", flush=True)

env = os.environ.copy()
env["PORT"] = str(port)
env["PYTHONPATH"] = str(ROOT)

proc = subprocess.Popen([sys.executable, str(ROOT / "app.py")], cwd=str(ROOT), env=env)

# Wait for server
ready = False
for _ in range(30):
    try:
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                ready = True
                break
    except Exception:
        pass
    time.sleep(0.5)

if not ready:
    print("Server failed to start!", flush=True)
    proc.kill()
    sys.exit(1)

print("Server is listening! Launching Edge...", flush=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="msedge",
        headless=True,
        args=[
            "--enable-webgl",
            "--use-gl=angle",
            "--use-angle=swiftshader",
            "--ignore-gpu-blocklist",
            "--enable-unsafe-webgpu"
        ]
    )
    page = browser.new_page(viewport={"width": 1600, "height": 900})
    page.on("console", lambda m: print(f"CONSOLE: [{m.type}] {m.text}", flush=True))
    page.on("pageerror", lambda e: print(f"PAGEERROR: {e}", flush=True))
    page.on("requestfailed", lambda req: print(f"REQ FAILED: {req.url} -> {req.failure}", flush=True))
    page.on("response", lambda res: print(f"RES: {res.status} {res.url}", flush=True) if "tile" in res.url or "carto" in res.url or "stream" in res.url else None)

    print(f"Navigating to http://127.0.0.1:{port}/ ...", flush=True)
    page.goto(f"http://127.0.0.1:{port}/")
    time.sleep(8)
    
    # Check if canvas exists
    canvas_count = page.locator("canvas").count()
    print(f"Found {canvas_count} canvas elements.", flush=True)
    
    # Take screenshot of main map
    page.screenshot(path="debug_map_initial.png")
    print("Saved debug_map_initial.png", flush=True)
    
    # Click CCTV button
    print("Clicking #btn-open-cctv...", flush=True)
    page.locator("#btn-open-cctv").click(force=True)
    time.sleep(3)
    page.screenshot(path="debug_cctv_modal.png")
    print("Saved debug_cctv_modal.png", flush=True)
    
    browser.close()

proc.terminate()
print("All done!", flush=True)
