"""Generate high-tech tactical CCTV surveillance stream loop MP4 for Plotsiris."""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT_DIR / "assets" / "surveillance_stream.mp4"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 640, 360
FPS = 15
NUM_FRAMES = 45  # 3-second loop

frames = []

try:
    font_lg = ImageFont.truetype("arialbd.ttf", 16)
    font_sm = ImageFont.truetype("arial.ttf", 11)
except Exception:
    font_lg = ImageFont.load_default()
    font_sm = ImageFont.load_default()

for i in range(NUM_FRAMES):
    # Base tactical dark background with subtle scanlines
    t = i / FPS
    img = Image.new("RGB", (WIDTH, HEIGHT), (12, 18, 26))
    draw = ImageDraw.Draw(img)

    # Road / Bridge perspective grid
    draw.line([(0, HEIGHT - 40), (WIDTH, HEIGHT - 40)], fill=(30, 45, 60), width=2)
    draw.line([(WIDTH * 0.2, HEIGHT * 0.4), (0, HEIGHT)], fill=(25, 40, 55), width=2)
    draw.line([(WIDTH * 0.8, HEIGHT * 0.4), (WIDTH, HEIGHT)], fill=(25, 40, 55), width=2)
    draw.line([(WIDTH * 0.45, HEIGHT * 0.4), (WIDTH * 0.35, HEIGHT)], fill=(40, 60, 80), width=1)
    draw.line([(WIDTH * 0.55, HEIGHT * 0.4), (WIDTH * 0.65, HEIGHT)], fill=(40, 60, 80), width=1)

    # Moving vehicles (light streaks)
    for v_idx in range(4):
        offset = ((i * 3 + v_idx * 15) % 45) / 45.0
        # Lane 1 (inbound)
        x1 = int(WIDTH * 0.45 + (WIDTH * 0.25) * offset)
        y1 = int(HEIGHT * 0.4 + (HEIGHT * 0.5) * offset)
        draw.ellipse([x1 - 4, y1 - 2, x1 + 4, y1 + 2], fill=(255, 220, 100))
        # Lane 2 (outbound)
        x2 = int(WIDTH * 0.45 - (WIDTH * 0.25) * offset)
        y2 = int(HEIGHT * 0.4 + (HEIGHT * 0.5) * offset)
        draw.ellipse([x2 - 3, y2 - 2, x2 + 3, y2 + 2], fill=(255, 60, 60))

    # Animated Target Tracking Bounding Box
    box_x = int(WIDTH * 0.42 + 20 * np.sin(t * 2))
    box_y = int(HEIGHT * 0.52 + 10 * np.cos(t * 2))
    box_w, box_h = 70, 40
    # Corner brackets
    draw.line([(box_x, box_y), (box_x + 12, box_y)], fill=(0, 229, 255), width=2)
    draw.line([(box_x, box_y), (box_x, box_y + 12)], fill=(0, 229, 255), width=2)
    draw.line([(box_x + box_w, box_y), (box_x + box_w - 12, box_y)], fill=(0, 229, 255), width=2)
    draw.line([(box_x + box_w, box_y), (box_x + box_w, box_y + 12)], fill=(0, 229, 255), width=2)
    draw.line([(box_x, box_y + box_h), (box_x + 12, box_y + box_h)], fill=(0, 229, 255), width=2)
    draw.line([(box_x, box_y + box_h), (box_x, box_y + box_h - 12)], fill=(0, 229, 255), width=2)
    draw.line([(box_x + box_w, box_y + box_h), (box_x + box_w - 12, box_y + box_h)], fill=(0, 229, 255), width=2)
    draw.line([(box_x + box_w, box_y + box_h), (box_x + box_w, box_y + box_h - 12)], fill=(0, 229, 255), width=2)
    draw.text((box_x, box_y - 14), f"OBJ #482 [TRK {int(94 + 5*np.sin(t*3))}%]", fill=(0, 229, 255), font=font_sm)

    # Static HUD Elements
    # Recording Dot
    dot_color = (255, 50, 50) if (i % 10 < 7) else (80, 20, 20)
    draw.ellipse([20, 20, 32, 32], fill=dot_color)
    draw.text((38, 18), "LIVE REC // CH-04", fill=(255, 255, 255), font=font_lg)
    
    # Real-time counter
    msec = int((i / FPS) * 1000)
    draw.text((WIDTH - 210, 18), f"UTC 2026-11-03 10:00:{i//FPS:02d}.{msec%1000:03d}", fill=(0, 229, 255), font=font_sm)
    
    # Camera telemetry
    draw.text((20, HEIGHT - 32), "CAM: SF-BAY-BRG-N | ELEV: 48M | AZIMUTH: 142.4°", fill=(160, 180, 200), font=font_sm)
    draw.text((WIDTH - 190, HEIGHT - 32), "FPS: 30.0 | RES: 1080p RAW", fill=(160, 180, 200), font=font_sm)

    # Center crosshair
    cx, cy = WIDTH // 2, HEIGHT // 2
    draw.line([(cx - 15, cy), (cx + 15, cy)], fill=(0, 229, 255, 120), width=1)
    draw.line([(cx, cy - 15), (cx, cy + 15)], fill=(0, 229, 255, 120), width=1)

    frames.append(np.array(img))

imageio.mimsave(str(OUTPUT_FILE), frames, fps=FPS)
print(f"[OK] Generated surveillance video: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size / 1024:.1f} KB)")
