"""Measure the data windows in the supplied brass background so text can be placed on them.

Method: the device is brass (bright + warm) against a black field, so a data window is a run of
NOT-brass pixels enclosed by brass. Scan 1-D lines through each window's middle and take the dark
runs — precise, and cheap to verify by drawing the results back onto a copy.

Out: measure_report.txt + measure_overlay.png (boxes drawn on a copy, for visual verification)
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "BrassBackground.png")
OUT_OVERLAY = os.path.join(HERE, "measure_overlay.png")
OUT_TXT = os.path.join(HERE, "measure_report.txt")

im = Image.open(SRC).convert("RGB")
W, H = im.size
a = np.asarray(im, dtype=np.float64) / 255.0
lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
# brass = lit and warmer than it is blue
brass = (lum > 0.16) & (a[..., 0] >= a[..., 2] * 1.15)

lines = []
lines.append(f"image {W}x{H}")


def dark_runs(line, lo, hi, min_len=12, max_len=None):
    """Contiguous runs along a 1-D brass line where the pixel is NOT brass."""
    seg = brass[line[0], lo:hi] if line[0] == line[0] else None
    seg = brass[line[0], lo:hi]
    runs, start = [], None
    for i, v in enumerate(seg):
        if not v and start is None:
            start = i
        elif v and start is not None:
            runs.append((lo + start, lo + i))
            start = None
    if start is not None:
        runs.append((lo + start, hi))
    out = [r for r in runs if r[1] - r[0] >= min_len]
    if max_len:
        out = [r for r in out if r[1] - r[0] <= max_len]
    return out


def col_dark_runs(x, lo, hi, min_len=12):
    seg = brass[lo:hi, x]
    runs, start = [], None
    for i, v in enumerate(seg):
        if not v and start is None:
            start = i
        elif v and start is not None:
            runs.append((lo + start, lo + i))
            start = None
    if start is not None:
        runs.append((lo + start, hi))
    return [r for r in runs if r[1] - r[0] >= min_len]


boxes = []

# ---- 1. the four tube interiors: scan a row through the tube bodies
for y in (190, 210, 230):
    r = dark_runs((y,), 150, 880, min_len=40, max_len=200)
    lines.append(f"row y={y}: dark runs {r}")
TUBE_ROW_Y = 210
tubes = dark_runs((TUBE_ROW_Y,), 150, 880, min_len=40, max_len=200)
for i, (x0, x1) in enumerate(tubes):
    cx = (x0 + x1) // 2
    vruns = col_dark_runs(cx, 40, 430, min_len=60)
    lines.append(f"  tube{i}: x {x0}-{x1} (cx={cx})  vertical dark runs {vruns}")
    if vruns:
        y0, y1 = max(vruns, key=lambda t: t[1] - t[0])
        boxes.append((f"tube{i}", x0, y0, x1, y1))

# ---- 2. gauge / counter band: scan rows to find the three instrument openings
for y in (560, 600, 620, 640, 680):
    r = dark_runs((y,), 20, 1010, min_len=40, max_len=420)
    lines.append(f"row y={y}: dark runs {r}")

# left gauge: column through its centre
for x in (150, 190, 230):
    r = col_dark_runs(x, 470, 800, min_len=40)
    lines.append(f"col x={x}: dark runs {r}")

# ---- 3. counter windows: scan the middle of the counter
CNT_Y = 615
cnt = dark_runs((CNT_Y,), 330, 700, min_len=20, max_len=340)
lines.append(f"counter row y={CNT_Y}: {cnt}")
if cnt:
    x0, x1 = max(cnt, key=lambda t: t[1] - t[0])
    vruns = col_dark_runs((x0 + x1) // 2, 520, 720, min_len=30)
    lines.append(f"  counter vertical {vruns}")
    if vruns:
        y0, y1 = max(vruns, key=lambda t: t[1] - t[0])
        boxes.append(("counter", x0, y0, x1, y1))

with open(OUT_TXT, "w") as f:
    f.write("\n".join(lines) + "\n")

ov = im.copy()
d = ImageDraw.Draw(ov)
for name, x0, y0, x1, y1 in boxes:
    d.rectangle([x0, y0, x1, y1], outline=(0, 255, 80), width=3)
    d.text((x0 + 4, y0 + 4), name, fill=(0, 255, 80))
for i, (x0, x1) in enumerate(tubes):
    d.line([x0, 0, x0, H], fill=(255, 60, 60), width=1)
    d.line([x1, 0, x1, H], fill=(255, 60, 60), width=1)
d.line([0, TUBE_ROW_Y, W, TUBE_ROW_Y], fill=(255, 200, 0), width=1)
d.line([0, CNT_Y, W, CNT_Y], fill=(255, 200, 0), width=1)
ov.save(OUT_OVERLAY)

print("\n".join(lines))
print(f"\nwrote {OUT_TXT} and {OUT_OVERLAY}")
for b in boxes:
    print("box:", b)
