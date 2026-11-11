"""Record continuous live video walkthrough of Plotsiris and convert to animated GIF using FFmpeg.

Features showcased in motion:
1. Default Map-First View with translucent HUD vectors and collapsible intelligence rail.
2. Smooth sidebar collapse to 32px slim rail and expand.
3. Top-right Breaking Alert box with pulsing radar beacon and one-click 'LOCATE ON MAP' fly-in.
4. Clicking 'LIVE CCTV' immediately closes inspector modal and opens live motion camera stream.
5. Cyber Intelligence panel with 1,779+ live CISA KEV zero-days and 'OPEN OSINT FEEDS' tab.
6. 12-Tile Modular Telemetry Deck with aligned risk matrix and live threat bars.
"""

from __future__ import annotations

import os
import sys
import time
import socket
import shutil
import tempfile
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

ARTIFACT_DIR = Path(r"C:\Users\pc006\.gemini\antigravity\brain\6ccf11b3-d088-4ee3-a2fa-482c28f69287")
ASSETS_DIR = ROOT_DIR / "assets"
DEPLOY_DIR = ROOT_DIR / "deploy" / "plotly-cloud" / "assets"

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

LOCAL_PORT = find_free_port()
LOCAL_URL = f"http://127.0.0.1:{LOCAL_PORT}"

def main():
    print(f"[*] Starting local Plotsiris server on port {LOCAL_PORT}...")
    env = os.environ.copy()
    env["PORT"] = str(LOCAL_PORT)
    
    server_process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=str(ROOT_DIR),
        env=env
    )

    video_temp_dir = tempfile.mkdtemp(prefix="plotsiris_video_")
    print(f"[*] Recording video to temporary directory: {video_temp_dir}")

    try:
        import requests
        for _ in range(50):
            try:
                r = requests.get(LOCAL_URL)
                if r.status_code == 200:
                    print("[*] Server is healthy and responding.")
                    break
            except Exception:
                time.sleep(0.5)

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            context = browser.new_context(
                viewport={"width": 1600, "height": 900},
                record_video_dir=video_temp_dir,
                record_video_size={"width": 1280, "height": 720}
            )
            page = context.new_page()

            print("[*] Navigating to dashboard...")
            page.goto(LOCAL_URL, timeout=30000)
            page.wait_for_selector("#main-map", timeout=25000)
            page.wait_for_selector("#breaking-alert-card", timeout=15000)
            print("[*] Dashboard loaded. Beginning scripted interaction sequence...")

            # Scene 1: Map-First Overview with Translucent Vectors (2.5s)
            time.sleep(2.5)

            # Scene 2: Collapse Intelligence Layers Sidebar (2.0s)
            print("[*] Collapsing intelligence layers sidebar...")
            page.click("#btn-toggle-layers-bar", force=True)
            time.sleep(2.0)

            # Expand sidebar back (1.8s)
            print("[*] Expanding sidebar back...")
            page.click("#btn-expand-sidebar-tab", force=True)
            time.sleep(1.8)

            # Scene 3: Top-Right Breaking Alert & 'LOCATE ON MAP' Camera Fly-in (3.5s)
            print("[*] Clicking 'LOCATE ON MAP' on breaking alert card...")
            page.hover("#btn-alert-locate")
            time.sleep(0.6)
            page.click("#btn-alert-locate", force=True)
            # Map smoothly animates and centers on the Red Sea / Bab-el-Mandeb
            time.sleep(3.2)

            # Dismiss breaking alert box to demonstrate dismiss functionality
            print("[*] Dismissing alert box...")
            page.click("#btn-dismiss-alert", force=True)
            time.sleep(1.0)

            # Scene 4: Open CCTV Modal via Top Nav
            print("[*] Opening Live CCTV feed modal...")
            page.click("#btn-open-cctv", force=True)
            page.wait_for_selector("#camera-stream-video", timeout=10000)
            # Allow video playback to run smoothly in video recording
            time.sleep(4.0)

            # Close CCTV modal
            print("[*] Closing CCTV feed modal...")
            page.click("#btn-close-camera-modal", force=True)
            time.sleep(1.2)

            # Scene 5: Open Cyber Threat Intelligence Panel (3.0s)
            print("[*] Opening Cyber Threat Intelligence panel...")
            page.click("#btn-open-cyber", force=True)
            time.sleep(2.5)

            # Click OPEN OSINT FEEDS tab (2.5s)
            print("[*] Switching to OPEN OSINT FEEDS tab...")
            page.click(".nav-link:has-text('OPEN OSINT FEEDS')", force=True)
            time.sleep(2.8)

            # Close Cyber offcanvas (1.2s)
            print("[*] Closing Cyber panel...")
            page.click("#btn-open-cyber", force=True)
            time.sleep(1.2)

            # Scene 6: Smoothly scroll down to 12-Tile Modular Telemetry Deck (3.0s)
            print("[*] Scrolling to 12-Tile Modular Telemetry Deck...")
            page.evaluate("window.scrollTo({top: 420, behavior: 'smooth'})")
            time.sleep(2.8)

            # Scroll back up to top map (1.5s)
            page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
            time.sleep(1.5)

            print("[*] Interaction sequence complete. Closing browser context to finalize video...")
            page.close()
            context.close()
            browser.close()

        # Find the recorded .webm video file
        webm_files = list(Path(video_temp_dir).glob("*.webm"))
        if not webm_files:
            raise FileNotFoundError("No recorded video file found in " + video_temp_dir)
        recorded_video = webm_files[0]
        print(f"[*] Recorded video captured at: {recorded_video} ({recorded_video.stat().st_size / 1024:.1f} KB)")

        # Convert video to optimized animated GIF using FFmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        output_gif = ARTIFACT_DIR / "plotsiris_walkthrough.gif"

        print(f"[*] Converting video to high-quality GIF using FFmpeg: {ffmpeg_exe}...")
        # Two-pass palette filter for crisp colors without banding
        vf_filter = "fps=11,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3"
        
        cmd = [
            ffmpeg_exe,
            "-y",
            "-i", str(recorded_video),
            "-vf", vf_filter,
            "-loop", "0",
            str(output_gif)
        ]
        
        subprocess.run(cmd, check=True)
        print(f"[OK] High-quality GIF generated at: {output_gif} ({output_gif.stat().st_size / (1024*1024):.2f} MB)")

        # Also copy to assets and deploy directories
        shutil.copy2(output_gif, ASSETS_DIR / "plotsiris_walkthrough.gif")
        if DEPLOY_DIR.exists():
            shutil.copy2(output_gif, DEPLOY_DIR / "plotsiris_walkthrough.gif")
        print("[OK] Walkthrough GIF copied to assets/ and deploy/ directories.")

    finally:
        server_process.terminate()
        try:
            shutil.rmtree(video_temp_dir, ignore_errors=True)
        except Exception:
            pass

if __name__ == "__main__":
    main()
