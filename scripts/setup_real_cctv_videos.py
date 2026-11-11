"""Download and prepare real, authentic surveillance traffic camera video files for Plotsiris CCTV."""

from __future__ import annotations

import os
import subprocess
import urllib.request
from pathlib import Path
import imageio_ffmpeg

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

SOURCES = {
    "london": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9a/London_Traffic.webm",
        "output_mp4": ASSETS_DIR / "cctv_london.mp4",
        "start": "0",
        "duration": "12"
    },
    "highway": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/68/Avtocesta.webm",
        "output_mp4": ASSETS_DIR / "cctv_highway.mp4",
        "start": "2",
        "duration": "12"
    },
    "sf_bay": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/70/Street_traffic.webm",
        "output_mp4": ASSETS_DIR / "cctv_sf_bay.mp4",
        "start": "4",
        "duration": "12"
    }
}


def download_file(url: str, dest: Path) -> bool:
    print(f"[*] Downloading {url} -> {dest}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Plotsiris/2.5 (contact@plotsiris.org)"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        print(f"[OK] Downloaded {dest.name} ({dest.stat().st_size / (1024*1024):.2f} MB)")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download {url}: {e}")
        return False


def transcode_to_mp4(src: Path, dest: Path, start: str, duration: str):
    print(f"[*] Transcoding {src.name} to {dest.name} (start={start}s, duration={duration}s)...")
    cmd = [
        FFMPEG, "-y",
        "-ss", start,
        "-i", str(src),
        "-t", duration,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-an",
        str(dest)
    ]
    subprocess.run(cmd, check=True)
    print(f"[OK] Generated {dest.name} ({dest.stat().st_size / (1024*1024):.2f} MB)")


def main():
    temp_dir = ROOT_DIR / "temp_video"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Process London Traffic
        london_raw = temp_dir / "london_raw.webm"
        if download_file(SOURCES["london"]["url"], london_raw):
            transcode_to_mp4(london_raw, SOURCES["london"]["output_mp4"], SOURCES["london"]["start"], SOURCES["london"]["duration"])

        # 2. Process Highway / Autobahn Traffic
        highway_raw = temp_dir / "highway_raw.webm"
        if download_file(SOURCES["highway"]["url"], highway_raw):
            transcode_to_mp4(highway_raw, SOURCES["highway"]["output_mp4"], SOURCES["highway"]["start"], SOURCES["highway"]["duration"])

        # 3. Process San Francisco Street/Bay Traffic
        sf_raw = temp_dir / "sf_raw.webm"
        if download_file(SOURCES["sf_bay"]["url"], sf_raw):
            transcode_to_mp4(sf_raw, SOURCES["sf_bay"]["output_mp4"], SOURCES["sf_bay"]["start"], SOURCES["sf_bay"]["duration"])

        # Set default surveillance_stream.mp4 to real SF Bay traffic
        default_mp4 = ASSETS_DIR / "surveillance_stream.mp4"
        if SOURCES["sf_bay"]["output_mp4"].exists():
            import shutil
            shutil.copyfile(SOURCES["sf_bay"]["output_mp4"], default_mp4)
            print(f"[OK] Replaced default surveillance_stream.mp4 with real SF Bay traffic footage!")
            
            # Also generate gif thumbnail from real video for fallback
            cmd_gif = [
                FFMPEG, "-y",
                "-i", str(default_mp4),
                "-t", "3",
                "-vf", "fps=10,scale=480:-1:flags=lanczos",
                "-c:v", "gif",
                str(ASSETS_DIR / "surveillance_stream.gif")
            ]
            subprocess.run(cmd_gif, check=True)
            print("[OK] Generated real surveillance_stream.gif thumbnail!")

    finally:
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
