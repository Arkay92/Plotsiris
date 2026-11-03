"""Choreographed Walkthrough GIF Generator for Plotsiris with WebGL MapLibre enabled."""

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
    try:
        shot = page.screenshot(timeout=20000)
    except Exception as e:
        print(f"Notice on screenshot: {e}")
        try:
            shot = page.screenshot(timeout=25000)
        except Exception as e2:
            print(f"Fallback screenshot error: {e2}")
            return
    img = Image.open(BytesIO(shot)).resize((1152, 648), Image.Resampling.LANCZOS)
    framed = add_banner(img, title, subtitle)
    for _ in range(repeat):
        frames.append(framed.copy())

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
    
    # Wait until server is listening on LOCAL_PORT
    start_t = time.time()
    server_ready = False
    while time.time() - start_t < 15:
        if proc.poll() is not None:
            out, err = proc.communicate()
            print(f"[ERROR] app.py exited prematurely with code {proc.returncode}:\n{err}\n{out}")
            return
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex(('127.0.0.1', LOCAL_PORT)) == 0:
                    server_ready = True
                    break
        except Exception:
            pass
        time.sleep(0.5)

    if not server_ready:
        print(f"[ERROR] Server failed to bind to {LOCAL_PORT} within 15 seconds")
        return
    print(f"[*] Server listening on {LOCAL_PORT}!")
    time.sleep(1)

    frames = []
    try:
        with sync_playwright() as p:
            # Enable WebGL and GPU acceleration in headless chromium so MapLibre vector map renders
            browser = p.chromium.launch(
                channel="msedge",
                headless=True,
                args=[
                    "--enable-webgl",
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                    "--ignore-gpu-blocklist",
                    "--enable-unsafe-webgpu",
                    "--ignore-certificate-errors",
                    "--no-sandbox"
                ]
            )
            page = browser.new_page(viewport={"width": 1600, "height": 900})
            page.on("pageerror", lambda err: print(f"PAGEERROR: {err}"))
            
            print("[*] Navigating to Plotsiris interface...")
            page.goto(f"http://127.0.0.1:{LOCAL_PORT}/", timeout=60000)
            page.wait_for_selector("#layer-rail-container", timeout=45000)
            page.wait_for_selector("#main-map canvas", state="attached", timeout=45000)
            time.sleep(5)  # Allow MapLibre WebGL vector tiles, roads, and layers to load cleanly

            # Scene 1: Global Multi-Domain Intelligence
            print(" -> Scene 1: Multi-Domain Situational Awareness (Map Loaded)")
            record(
                page,
                "01 // MULTI-DOMAIN SITUATIONAL AWARENESS",
                "Unified common operating picture: ADS-B Aviation, AIS Maritime, Conflict Zones, Earthquakes & CCTV",
                frames,
                repeat=3
            )

            # Scene 1b: Hover on event / point showing cursor pointer
            print(" -> Scene 1b: Hovering on map event")
            try:
                page.mouse.move(780, 420)
                time.sleep(2)
            except Exception:
                pass
            record(
                page,
                "01 // INTERACTIVE TACTICAL HOVER",
                "High-precision vector inspection with real-time coordinate telemetries and threat classifications",
                frames,
                repeat=2
            )

            # Scene 2: Live CCTV Surveillance Video Feed & Tactical HUD
            print(" -> Scene 2: Live CCTV Surveillance Feed")
            try:
                page.click("#btn-open-cctv")
                page.wait_for_selector("#camera-stream-img", timeout=12000)
                time.sleep(2)
            except Exception as e:
                print(f"Notice on CCTV modal: {e}")
            record(
                page,
                "02 // LIVE SURVEILLANCE FEED & OPTICAL HUD",
                "Active H.264 video stream with live military HUD, NVG night vision, and FLIR thermal filters",
                frames,
                repeat=3
            )
            try:
                page.click("#btn-close-camera-modal")
            except Exception:
                page.keyboard.press("Escape")
            time.sleep(2)

            # Scene 3: 20-Tool Tactical OSINT Reconnaissance Suite
            print(" -> Scene 3: OSINT Recon Suite")
            try:
                page.click("#btn-open-osint")
                page.wait_for_selector("#btn-run-osint", timeout=12000)
                time.sleep(1)
                page.click("#btn-target-cloudflare")
                time.sleep(1)
                page.click("#btn-run-osint")
                time.sleep(3)
            except Exception as e:
                print(f"Notice on OSINT run: {e}")
            record(
                page,
                "03 // 20-TOOL TACTICAL OSINT RECONNAISSANCE",
                "Automated reconnaissance: DNS, WHOIS, Port Scan, Subdomains, IP Geolocation & Threat Reputation",
                frames,
                repeat=3
            )

            # Pin finding
            try:
                page.click("#btn-pin-recon-result")
                time.sleep(1)
            except Exception:
                pass
            record(
                page,
                "03 // GEOSPATIAL THREAT PINNING",
                "Target intelligence finding mapped in real-time onto multi-domain tactical canvas",
                frames,
                repeat=2
            )
            try:
                page.click("#osint-offcanvas .btn-close")
            except Exception:
                page.keyboard.press("Escape")
            time.sleep(2)

            # Scene 4: AI Intelligence Analyst (Gemini 2.5 Flash)
            print(" -> Scene 4: AI Intelligence Analyst & SITREP")
            try:
                page.click("#btn-open-ai")
                page.wait_for_selector("#btn-send-ai-query", timeout=12000)
                time.sleep(1)
                page.locator("#ai-query-input").fill("Assess multi-domain escalation in the Indo-Pacific and maritime choke points.")
                page.click("#btn-send-ai-query")
                time.sleep(3)
            except Exception as e:
                print(f"Notice on AI prompt: {e}")
            record(
                page,
                "04 // AI INTELLIGENCE ANALYST (GEMINI 2.5 FLASH)",
                "Natural language strategic synthesis and cross-domain intelligence fusion",
                frames,
                repeat=3
            )

            # SITREP Briefing
            try:
                page.click("#btn-generate-briefing")
                time.sleep(3)
            except Exception as e:
                print(f"Notice on SITREP: {e}")
            record(
                page,
                "04 // OPERATIONAL DEFCON COMMANDER SITREP",
                "Structured military briefing: Situation, Threat Vectors, Entity Correlation & Directives",
                frames,
                repeat=3
            )
            try:
                page.click("#ai-offcanvas .btn-close")
            except Exception:
                page.keyboard.press("Escape")
            time.sleep(2)

            # Scene 5: Force-Directed Entity Relationship Graph
            print(" -> Scene 5: Force-Directed Entity Relationship Graph")
            try:
                page.click("#btn-open-graph")
                page.wait_for_selector("#entity-graph-display", timeout=12000)
                time.sleep(3)
            except Exception as e:
                print(f"Notice on Graph modal: {e}")
            record(
                page,
                "05 // FORCE-DIRECTED ENTITY RELATIONSHIP GRAPH",
                "NetworkX topological mapping correlating Threat Actors, Malware, CVEs, Targets & C2 Infrastructure",
                frames,
                repeat=3
            )
            try:
                page.click("#btn-close-graph-modal")
            except Exception:
                page.keyboard.press("Escape")
            time.sleep(2)

            # Scene 6: Cyber Threat Intel (CISA KEV)
            print(" -> Scene 6: Cyber Threat Intel")
            try:
                page.click("#btn-open-cyber")
                page.wait_for_selector("#tab-kev", timeout=12000)
                time.sleep(2)
            except Exception as e:
                print(f"Notice on Cyber drawer: {e}")
            record(
                page,
                "06 // CYBER THREAT INTEL & CISA KEV CATALOG",
                "Known Exploited Vulnerabilities catalog with ransomware flags, CVSS scores, and threat status",
                frames,
                repeat=3
            )
            try:
                page.click("#cyber-offcanvas .btn-close")
            except Exception:
                page.keyboard.press("Escape")
            time.sleep(2)

            # Scene 7: Defense Equities & Sovereign Risk
            print(" -> Scene 7: Defense Equities")
            try:
                page.click("#btn-open-markets")
                page.wait_for_selector("#tab-markets-tickers", timeout=12000)
                time.sleep(2)
            except Exception as e:
                print(f"Notice on Markets drawer: {e}")
            record(
                page,
                "07 // DEFENSE EQUITIES & SOVEREIGN RISK",
                "Real-time defense prime stock tickers (LMT, RTX, GD), commodity movements, and geopolitical risk",
                frames,
                repeat=3
            )
            try:
                page.click("#markets-offcanvas .btn-close")
            except Exception:
                page.keyboard.press("Escape")
            time.sleep(2)

            # Scene 8: Cartographic Core Light Theme
            print(" -> Scene 8: Theme Switch")
            try:
                page.click("#btn-toggle-theme")
                time.sleep(3)
            except Exception as e:
                print(f"Notice on Light theme: {e}")
            record(
                page,
                "08 // DUAL TACTICAL CARTOGRAPHY THEMES",
                "Cartographic Core: Light tactical GIS mode with high-contrast situational vector rendering",
                frames,
                repeat=3
            )

            # Back to Ghost Dark
            try:
                page.click("#btn-toggle-theme")
                time.sleep(3)
            except Exception as e:
                print(f"Notice on Dark theme: {e}")
            record(
                page,
                "08 // GHOST PROTOCOL COMMAND THEME",
                "Ghost Protocol: Ultra-dark military situational interface with glowing vectors & radar sweep",
                frames,
                repeat=3
            )
            record(
                page,
                "08 // GHOST PROTOCOL COMMAND THEME",
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
        optimize=False,
        duration=850,
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
