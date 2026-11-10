"""Generate an optimized walkthrough animated GIF showcasing the OSINT-wired Cyber-HUD in Plotsiris.

Captures:
1. Default Map View: Multi-Domain Common Operating Picture with NASA EONET hazards, UN ReliefWeb, Feodo C2 botnets
2. Switch to Constellation Graph View: C2-CORE hub, APT-29 threat actor, CISA-KEV catalog, range rings, crosshairs
3. Return to Map View (demonstrating view toggle)
4. 12-Tile Modular OSINT Telemetry Deck (Target Profile 1.1.1.1, Threat Matrix, 360° Radar, Threat Taxonomy, SIGINT Stream, Sector Heatmap, Sovereign Risk, YAML Briefing, Telemetry Ingress, Sensor Tracks, Payload Dump)
5. Scoped OSINT Recon Suite with Computer Misuse Act (CMA 1990) Legal Authorization Gate
6. Gemini AI Intelligence Analyst Synthesis Layer
"""

from __future__ import annotations

import sys
import time
import socket
import threading
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OUTPUT_DIR = ROOT_DIR / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GIF_PATH = OUTPUT_DIR / "plotsiris_new_hud_walkthrough.gif"
ARTIFACT_DIR = Path(r"C:\Users\pc006\.gemini\antigravity\brain\6ccf11b3-d088-4ee3-a2fa-482c28f69287")
ARTIFACT_GIF_PATH = ARTIFACT_DIR / "plotsiris_new_hud_walkthrough.gif"

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = find_free_port()

def add_banner(image: Image.Image, title: str, subtitle: str) -> Image.Image:
    """Add a sleek cyber HUD banner overlay to the frame."""
    img = image.convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Bottom HUD overlay bar
    bar_h = 56
    overlay = Image.new("RGBA", (w, bar_h), (5, 9, 17, 235))
    img.paste(overlay, (0, h - bar_h), overlay)
    
    # Glowing border line
    draw.line([(0, h - bar_h), (w, h - bar_h)], fill=(0, 229, 255, 200), width=2)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 18)
        font_sub = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.text((24, h - bar_h + 8), title, fill=(0, 229, 255, 255), font=font_title)
    draw.text((24, h - bar_h + 32), subtitle, fill=(180, 210, 230, 240), font=font_sub)
    
    badge_text = "PLOTSIRIS // DEFCON 3"
    draw.text((w - 240, h - bar_h + 18), badge_text, fill=(56, 189, 248, 255), font=font_title)
    
    return img.convert("RGB")

def record_frame(page, title: str, subtitle: str, frames: list, repeat: int = 1):
    screenshot_bytes = page.screenshot()
    from io import BytesIO
    raw_img = Image.open(BytesIO(screenshot_bytes))
    raw_img = raw_img.resize((1200, 675), Image.Resampling.LANCZOS)
    hud_frame = add_banner(raw_img, title, subtitle)
    for _ in range(repeat):
        frames.append(hud_frame)

def run():
    print(f"[*] Starting Plotsiris local test instance on {LOCAL_HOST}:{LOCAL_PORT}...")
    from plotsiris.app import create_app
    app = create_app(host=LOCAL_HOST, port=LOCAL_PORT, debug=False)
    server_thread = threading.Thread(
        target=lambda: app.run(host=LOCAL_HOST, port=LOCAL_PORT, debug=False, threaded=True),
        daemon=True
    )
    server_thread.start()
    time.sleep(3)

    frames: list[Image.Image] = []

    print("[*] Launching browser to record walkthrough...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.goto(f"http://{LOCAL_HOST}:{LOCAL_PORT}/", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_selector("#main-map", state="attached", timeout=25000)
        time.sleep(3)

        # 1. Header & Default Map View
        print("[1/6] Capturing Default Map View with Multi-Domain Feeds...")
        record_frame(
            page,
            "01 // DEFAULT COMMON OPERATING PICTURE (MAP VIEW)",
            "Multi-Domain C2 Fusion: OpenSky ADS-B, AIS Maritime, NASA EONET hazards & abuse.ch C2 Botnets",
            frames,
            repeat=3
        )

        # 2. Toggle to Tactical Constellation Graph View
        print("[2/6] Toggling to Constellation Graph View...")
        try:
            page.locator("#btn-view-graph").click()
            time.sleep(2)
        except Exception as e:
            print(f"Notice on graph toggle: {e}")

        record_frame(
            page,
            "02 // TOPOLOGICAL THREAT GRAPH & C2 CORE HUB",
            "C2-CORE correlation hub connecting APT-29 Cozy Bear, CISA KEV vulnerabilities, Tor relays & Feodo botnets",
            frames,
            repeat=3
        )

        # 3. Toggle back to Map View
        print("[3/6] Returning to Map View...")
        try:
            page.locator("#btn-view-map").click()
            time.sleep(1.5)
        except Exception as e:
            print(f"Notice on map toggle: {e}")

        record_frame(
            page,
            "03 // DUAL-VIEW TACTICAL SWITCHING",
            "Seamless instantaneous toggle between 3D geospatial cartography and topological threat networks",
            frames,
            repeat=2
        )

        # 4. Scroll down to 12-Tile Modular OSINT Telemetry Deck
        print("[4/6] Scrolling down to 12-Tile OSINT Telemetry Deck...")
        page.evaluate("window.scrollTo(0, 500)")
        time.sleep(1.5)

        record_frame(
            page,
            "04 // 12-TILE OSINT TELEMETRY DECK (ROW 1-2)",
            "Target Profile 1.1.1.1, Threat Matrix KEV/C2/JAM/NAT, Recon Pipeline, 360° Tactical Radar, Threat Taxonomy & SIGINT Log",
            frames,
            repeat=3
        )

        page.evaluate("window.scrollTo(0, 950)")
        time.sleep(1.5)

        record_frame(
            page,
            "04 // 12-TILE OSINT TELEMETRY DECK (ROW 2-3)",
            "Sector Risk Heatmap, Sovereign Risk Index (74.2/100), Structured YAML Briefing, Telemetry Ingress & Recon Payload Dump",
            frames,
            repeat=3
        )

        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        # 5. Open Scoped OSINT Suite (CMA 1990 legal authorization gate)
        print("[5/6] Opening Scoped OSINT Reconnaissance Suite...")
        try:
            page.locator("#btn-open-osint").click(force=True)
            time.sleep(2)
        except Exception as e:
            print(f"Notice on OSINT drawer: {e}")

        record_frame(
            page,
            "05 // SCOPED OSINT SUITE & LEGAL AUTHORIZATION GATE",
            "CMA 1990 compliance check: Active port scans require explicit target ownership & written testing consent",
            frames,
            repeat=3
        )

        try:
            page.keyboard.press("Escape")
            time.sleep(1)
        except Exception:
            pass

        # 6. Open Gemini AI Intelligence Analyst
        print("[6/6] Opening AI Intelligence Analyst...")
        try:
            page.locator("#btn-open-ai").click(force=True)
            time.sleep(2)
        except Exception as e:
            print(f"Notice on AI drawer: {e}")

        record_frame(
            page,
            "06 // AI SYNTHESIS & DEFCON SITREP ENGINE",
            "Probabilistic narrative synthesis with analyst verification disclaimers over multi-source feeds",
            frames,
            repeat=3
        )

        try:
            page.keyboard.press("Escape")
            time.sleep(1)
        except Exception:
            pass

        browser.close()

    print(f"[*] Assembling {len(frames)} frames into animated GIF: {GIF_PATH}...")
    duration_per_frame = 1000  # 1.0s per frame

    frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=duration_per_frame,
        loop=0
    )

    file_size_mb = GIF_PATH.stat().st_size / (1024 * 1024)
    print(f"[OK] Walkthrough GIF created successfully: {GIF_PATH} ({file_size_mb:.2f} MB)")

    # Also copy to Artifact directory so it is directly viewable
    if ARTIFACT_DIR.exists():
        shutil.copyfile(GIF_PATH, ARTIFACT_GIF_PATH)
        print(f"[OK] Copied to artifact directory: {ARTIFACT_GIF_PATH}")

if __name__ == "__main__":
    run()
