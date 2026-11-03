"""Generate an optimized, professional walkthrough animated GIF showcasing all Plotsiris capabilities.

Captures:
1. Multi-Domain Situational Awareness Map (Aviation, Maritime, Threats, Earthquakes, Space, CCTV)
2. Theater Quick Jumps (Global, Indo-Pacific, Middle East, Europe)
3. 20-Tool OSINT Reconnaissance Suite (Scanning 1.1.1.1 & pinning to tactical map)
4. AI Intelligence Analyst (Tactical Q&A & Military Operational SITREP)
5. Force-Directed Entity Relationship Intelligence Graph (NetworkX)
6. Cyber Threat Intelligence & CISA KEV Exploited Catalog
7. Defense Equities Tickers & Sovereign Risk Scoring
8. Dual Theme Switch (Ghost Protocol Dark <-> Cartographic Core Light)
"""

from __future__ import annotations

import sys
import time
import socket
import threading
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OUTPUT_DIR = ROOT_DIR / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GIF_PATH = OUTPUT_DIR / "plotsiris_walkthrough.gif"

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = find_free_port()

def add_banner(image: Image.Image, title: str, subtitle: str) -> Image.Image:
    """Add a sleek HUD banner to the frame."""
    img = image.convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    
    # Bottom HUD overlay bar
    bar_h = 56
    overlay = Image.new("RGBA", (w, bar_h), (8, 12, 22, 225))
    img.paste(overlay, (0, h - bar_h), overlay)
    
    # Border line
    draw.line([(0, h - bar_h), (w, h - bar_h)], fill=(0, 240, 255, 180), width=2)
    
    # Try default font
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.text((24, h - bar_h + 8), title, fill=(0, 240, 255, 255), font=font_title)
    draw.text((24, h - bar_h + 32), subtitle, fill=(180, 200, 220, 240), font=font_sub)
    
    # Right-hand branding
    badge_text = "PLOTSIRIS // DEFCON 3"
    draw.text((w - 220, h - bar_h + 18), badge_text, fill=(255, 59, 48, 255), font=font_title)
    
    return img.convert("RGB")

def record_frame(page, title: str, subtitle: str, frames: list, repeat: int = 1):
    screenshot_bytes = page.screenshot()
    from io import BytesIO
    raw_img = Image.open(BytesIO(screenshot_bytes))
    # Resize to 1200x675 for crisp 16:9 standard and optimized GIF file size
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

    print("[*] Launching headless browser for choreographed walkthrough capture...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 900})
        page.goto(f"http://{LOCAL_HOST}:{LOCAL_PORT}/", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_selector("#main-map", state="attached", timeout=25000)
        time.sleep(4)

        # 1. Global Tactical Multi-Domain Overview
        print("[1/8] Capturing Multi-Domain Global View...")
        record_frame(
            page,
            "01 // MULTI-DOMAIN SITUATIONAL AWARENESS",
            "Real-time aggregation of ADS-B Aviation, Maritime AIS, Conflict Zones, USGS Earthquakes & Space Weather",
            frames,
            repeat=3
        )

        # 2. Theater Jumps (Indo-Pacific & Middle East)
        print("[2/8] Capturing Theater Jumps...")
        try:
            page.locator(".preset-btn:has-text('Indo-Pacific')").first.click()
            time.sleep(2)
        except Exception as e:
            print(f"Warning on Indo-Pacific preset: {e}")
        record_frame(
            page,
            "02 // STRATEGIC THEATER PRESETS",
            "Instant vector repositioning to Indo-Pacific, South China Sea, and Malacca Strait transit corridors",
            frames,
            repeat=2
        )

        try:
            page.locator(".preset-btn:has-text('Middle East')").first.click()
            time.sleep(2)
        except Exception as e:
            print(f"Warning on Middle East preset: {e}")
        record_frame(
            page,
            "02 // STRATEGIC THEATER PRESETS",
            "Strait of Hormuz & Red Sea maritime security watch and critical energy infrastructure",
            frames,
            repeat=2
        )

        try:
            page.locator(".preset-btn:has-text('Global')").first.click()
            time.sleep(2)
        except Exception:
            pass

        # 3. 20-Tool Tactical OSINT Reconnaissance Suite
        print("[3/8] Capturing OSINT Reconnaissance Suite...")
        page.locator("#btn-open-osint").click()
        page.wait_for_selector("#osint-offcanvas.show", timeout=12000)
        time.sleep(1)

        # Run 1.1.1.1 scan
        page.locator("#btn-target-cloudflare").click()
        time.sleep(1)
        page.locator("#btn-run-osint").click()
        page.wait_for_selector("#osint-result-container .glass-panel", timeout=15000)
        time.sleep(1)

        record_frame(
            page,
            "03 // 20-TOOL TACTICAL OSINT RECONNAISSANCE SUITE",
            "Automated DNS, WHOIS, Port Scan, Subdomains, IP Geolocation, Tor exit & threat reputation analysis",
            frames,
            repeat=3
        )

        # Pin finding to map
        try:
            page.locator("#btn-pin-recon-result").click()
            time.sleep(1)
        except Exception as e:
            print(f"Notice on OSINT pin: {e}")

        record_frame(
            page,
            "03 // GEOSPATIAL OSINT CORRELATION",
            "Threat finding pinned directly onto live multi-domain tactical map canvas with geo-coordinates",
            frames,
            repeat=2
        )
        page.keyboard.press("Escape")
        time.sleep(1)

        # 4. AI Operational Intelligence Analyst
        print("[4/8] Capturing Gemini AI Analyst & SITREP Generator...")
        page.locator("#btn-open-ai").click()
        page.wait_for_selector("#ai-offcanvas.show", timeout=12000)
        time.sleep(1)

        # Ask tactical query
        page.locator("#ai-prompt-input").fill("Assess multi-domain escalation in the Indo-Pacific and maritime choke points.")
        page.locator("#btn-send-ai-prompt").click()
        page.wait_for_selector("#ai-chat-history .glass-panel", timeout=15000)
        time.sleep(1)

        record_frame(
            page,
            "04 // AI INTELLIGENCE ANALYST (GEMINI 2.5 FLASH)",
            "Real-time strategic tactical intelligence synthesis and operational threat evaluation",
            frames,
            repeat=3
        )

        # Generate SITREP
        try:
            page.locator("#btn-gen-sitrep").click()
            page.wait_for_selector("#ai-chat-history .text-warning", timeout=15000)
            time.sleep(2)
        except Exception as e:
            print(f"Notice on SITREP generator: {e}")

        record_frame(
            page,
            "04 // AUTOMATED MILITARY OPERATIONAL SITREP",
            "Structured DEFCON commander briefing: Situation, Correlation, Attack Vectors & Strategic Recommendations",
            frames,
            repeat=3
        )
        page.keyboard.press("Escape")
        time.sleep(1)

        # 5. Entity Relationship Intelligence Graph
        print("[5/8] Capturing Force-Directed Entity Relationship Graph...")
        page.locator("#btn-open-graph").click()
        page.wait_for_selector(".modal.show", timeout=12000)
        time.sleep(2)

        record_frame(
            page,
            "05 // FORCE-DIRECTED ENTITY RELATIONSHIP GRAPH",
            "NetworkX topological correlation connecting Threat Actors, Malware, CVEs, Target Sectors & C2 Nodes",
            frames,
            repeat=4
        )
        page.keyboard.press("Escape")
        time.sleep(1)

        # 6. Cyber Threat Intelligence & CISA KEV
        print("[6/8] Capturing Cyber Threat Intel & KEV Catalog...")
        page.locator("#btn-open-cyber").click()
        page.wait_for_selector("#cyber-offcanvas.show", timeout=10000)
        time.sleep(1)

        record_frame(
            page,
            "06 // CYBER THREAT INTEL & CISA KEV CATALOG",
            "Known Exploited Vulnerabilities catalog with ransomware tags, CVSS ratings, and zero-day advisories",
            frames,
            repeat=3
        )
        page.keyboard.press("Escape")
        time.sleep(1)

        # 7. Financial Markets & Defense Equities
        print("[7/8] Capturing Defense Equities & Sovereign Risk...")
        page.locator("#btn-open-markets").click()
        page.wait_for_selector("#markets-offcanvas.show", timeout=10000)
        time.sleep(1)

        record_frame(
            page,
            "07 // DEFENSE EQUITIES & SOVEREIGN RISK INDEX",
            "Tracking defense primes (LMT, RTX, GD), energy, critical commodities, and geopolitical risk indexes",
            frames,
            repeat=3
        )
        page.keyboard.press("Escape")
        time.sleep(1)

        # 8. Dual Tactical Theme Switching
        print("[8/8] Capturing Theme Switching...")
        try:
            page.locator("#btn-toggle-theme").click()
            time.sleep(2)
        except Exception as e:
            print(f"Notice on theme switch: {e}")

        record_frame(
            page,
            "08 // DUAL TACTICAL CARTOGRAPHY THEMES",
            "Instant toggle to Cartographic Core (high-readability light situational cartography)",
            frames,
            repeat=3
        )

        try:
            page.locator("#btn-toggle-theme").click()
            time.sleep(2)
        except Exception:
            pass

        record_frame(
            page,
            "08 // DUAL TACTICAL CARTOGRAPHY THEMES",
            "Ghost Protocol: military command dark mode with luminous high-contrast threat vectors",
            frames,
            repeat=3
        )

        browser.close()

    print(f"[*] Assembling {len(frames)} frames into animated GIF: {GIF_PATH}...")
    # Quantize and optimize palette for smooth colors and small file size
    duration_per_frame = 900  # 900ms per frame
    
    # Save optimized GIF
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

if __name__ == "__main__":
    run()
