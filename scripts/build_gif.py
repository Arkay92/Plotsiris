"""Choreographed Walkthrough GIF Generator for Plotsiris using standalone process."""

from __future__ import annotations

import sys
import time
import socket
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GIF_PATH = OUTPUT_DIR / "plotsiris_walkthrough.gif"

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

LOCAL_PORT = find_free_port()

def add_banner(image: Image.Image, title: str, subtitle: str) -> Image.Image:
    img = image.convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    bar_h = 56
    overlay = Image.new("RGBA", (w, bar_h), (8, 14, 26, 230))
    img.paste(overlay, (0, h - bar_h), overlay)
    draw.line([(0, h - bar_h), (w, h - bar_h)], fill=(0, 229, 255, 200), width=2)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    draw.text((24, h - bar_h + 8), title, fill=(0, 229, 255, 255), font=font_title)
    draw.text((24, h - bar_h + 32), subtitle, fill=(185, 205, 225, 240), font=font_sub)
    draw.text((w - 230, h - bar_h + 18), "PLOTSIRIS // TACTICAL HUD", fill=(255, 68, 68, 255), font=font_title)
    return img.convert("RGB")

def record(page, title: str, subtitle: str, frames: list, repeat: int = 1):
    from io import BytesIO
    shot = page.screenshot()
    img = Image.open(BytesIO(shot)).resize((1152, 648), Image.Resampling.LANCZOS)
    framed = add_banner(img, title, subtitle)
    for _ in range(repeat):
        frames.append(framed)

def main():
    print(f"[*] Starting background Plotsiris server on port {LOCAL_PORT}...")
    import os
    env = os.environ.copy()
    env["PORT"] = str(LOCAL_PORT)
    env["PYTHONPATH"] = str(ROOT_DIR)
    proc = subprocess.Popen(
        [sys.executable, str(ROOT_DIR / "app.py")],
        cwd=str(ROOT_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(5)

    frames = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page(viewport={"width": 1600, "height": 900})
            
            print("[*] Navigating to Plotsiris interface...")
            page.goto(f"http://127.0.0.1:{LOCAL_PORT}/", timeout=30000)
            page.wait_for_selector("#layer-rail-container", timeout=25000)
            time.sleep(2)

            # Scene 1: Global Multi-Domain Intelligence
            print(" -> Scene 1: Multi-Domain Situational Awareness")
            record(
                page,
                "01 // MULTI-DOMAIN SITUATIONAL AWARENESS",
                "Unified common operating picture: ADS-B Aviation, AIS Maritime, Conflict Zones, Earthquakes & CCTV",
                frames,
                repeat=3
            )

            # Scene 2: 20-Tool Tactical OSINT Reconnaissance Suite
            print(" -> Scene 2: OSINT Recon Suite")
            try:
                page.locator("#btn-open-osint").click()
                page.wait_for_selector("#osint-offcanvas.show", timeout=15000)
                time.sleep(1)
                page.locator("#btn-target-cloudflare").click()
                time.sleep(1)
                page.locator("#btn-run-osint").click()
                time.sleep(4)
            except Exception as e:
                print(f"Notice on OSINT run: {e}")
            record(
                page,
                "02 // 20-TOOL TACTICAL OSINT RECONNAISSANCE",
                "Automated reconnaissance: DNS, WHOIS, Port Scan, Subdomains, IP Geolocation & Threat Reputation",
                frames,
                repeat=3
            )

            # Pin finding
            try:
                page.locator("#btn-pin-recon-result").click()
                time.sleep(1)
            except Exception:
                pass
            record(
                page,
                "02 // GEOSPATIAL THREAT PINNING",
                "Target intelligence finding mapped in real-time onto multi-domain tactical canvas",
                frames,
                repeat=2
            )
            page.keyboard.press("Escape")
            time.sleep(1)

            # Scene 3: AI Intelligence Analyst (Gemini 2.5 Flash)
            print(" -> Scene 3: AI Intelligence Analyst & SITREP")
            try:
                page.locator("#btn-open-ai").click()
                page.wait_for_selector("#ai-offcanvas.show", timeout=15000)
                time.sleep(1)
                page.locator("#ai-prompt-input").fill("Assess multi-domain escalation in the Indo-Pacific and maritime choke points.")
                page.locator("#btn-send-ai-prompt").click()
                time.sleep(3)
            except Exception as e:
                print(f"Notice on AI prompt: {e}")
            record(
                page,
                "03 // AI INTELLIGENCE ANALYST (GEMINI 2.5 FLASH)",
                "Natural language strategic synthesis and cross-domain intelligence fusion",
                frames,
                repeat=3
            )

            # SITREP
            try:
                page.locator("#btn-gen-sitrep").click()
                time.sleep(3)
            except Exception as e:
                print(f"Notice on SITREP: {e}")
            record(
                page,
                "03 // OPERATIONAL DEFCON COMMANDER SITREP",
                "Structured military briefing: Situation, Threat Vectors, Entity Correlation & Directives",
                frames,
                repeat=3
            )
            page.keyboard.press("Escape")
            time.sleep(1)

            # Scene 4: Force-Directed Entity Relationship Graph
            print(" -> Scene 4: Force-Directed Entity Relationship Graph")
            try:
                page.locator("#btn-open-graph").click()
                page.wait_for_selector(".modal.show", timeout=15000)
                time.sleep(3)
            except Exception as e:
                print(f"Notice on Graph modal: {e}")
            record(
                page,
                "04 // FORCE-DIRECTED ENTITY RELATIONSHIP GRAPH",
                "NetworkX topological mapping correlating Threat Actors, Malware, CVEs, Targets & C2 Infrastructure",
                frames,
                repeat=4
            )
            page.keyboard.press("Escape")
            time.sleep(1)

            # Scene 5: Cyber Threat Intel (CISA KEV)
            print(" -> Scene 5: Cyber Threat Intel")
            try:
                page.locator("#btn-open-cyber").click()
                page.wait_for_selector("#cyber-offcanvas.show", timeout=15000)
                time.sleep(2)
            except Exception as e:
                print(f"Notice on Cyber drawer: {e}")
            record(
                page,
                "05 // CYBER THREAT INTEL & CISA KEV CATALOG",
                "Known Exploited Vulnerabilities catalog with ransomware flags, CVSS scores, and threat status",
                frames,
                repeat=3
            )
            page.keyboard.press("Escape")
            time.sleep(1)

            # Scene 6: Defense Equities & Sovereign Risk
            print(" -> Scene 6: Defense Equities")
            try:
                page.locator("#btn-open-markets").click()
                page.wait_for_selector("#markets-offcanvas.show", timeout=15000)
                time.sleep(2)
            except Exception as e:
                print(f"Notice on Markets drawer: {e}")
            record(
                page,
                "06 // DEFENSE EQUITIES & SOVEREIGN RISK",
                "Real-time defense prime stock tickers (LMT, RTX, GD), commodity movements, and geopolitical risk",
                frames,
                repeat=3
            )
            page.keyboard.press("Escape")
            time.sleep(1)

            # Scene 7: Cartographic Core Light Theme
            print(" -> Scene 7: Theme Switch")
            try:
                page.locator("#btn-toggle-theme").click()
                time.sleep(3)
            except Exception as e:
                print(f"Notice on Light theme: {e}")
            record(
                page,
                "07 // DUAL TACTICAL CARTOGRAPHY THEMES",
                "Cartographic Core: Light tactical GIS mode with high-contrast situational vector rendering",
                frames,
                repeat=3
            )

            # Back to Ghost Dark
            try:
                page.locator("#btn-toggle-theme").click()
                time.sleep(3)
            except Exception as e:
                print(f"Notice on Dark theme: {e}")
            record(
                page,
                "07 // GHOST PROTOCOL COMMAND THEME",
                "Ghost Protocol: Ultra-dark military situational interface with glowing vectors & radar sweep",
                frames,
                repeat=3
            )

            browser.close()
    finally:
        print("[*] Terminating background server process...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

    print(f"[*] Assembling {len(frames)} frames into animated GIF: {GIF_PATH}...")
    frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=950,
        loop=0
    )
    
    # Also copy to artifacts directory and tests/artifacts
    import shutil
    shutil.copy(GIF_PATH, ROOT_DIR / "tests" / "artifacts" / "plotsiris_walkthrough.gif")
    brain_dir = Path(r"C:\Users\pc006\.gemini\antigravity\brain\6ccf11b3-d088-4ee3-a2fa-482c28f69287")
    if brain_dir.exists():
        shutil.copy(GIF_PATH, brain_dir / "plotsiris_walkthrough.gif")

    size_mb = GIF_PATH.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] Walkthrough GIF saved successfully: {GIF_PATH} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
