"""Measure the data windows in the brass background by ENCLOSURE, not by darkness.

The whole image is mostly black, so "dark" alone also finds the gaps between brass parts. What
distinguishes a data window is that it is ENCLOSED by brass. So:

  1. dark mask (lum < thresh)
  2. flood-fill the dark from the image border -> that is the OUTSIDE
  3. whatever dark remains is enclosed -> the windows
  4. label those remaining blobs (PIL flood-fill per blob, in C, so it is fast)

Out: measure_report.txt + measure_overlay.png (boxes on a copy, to be verified by eye)
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "BrassBackground.png")
DARK_THRESH = 0.085
MIN_AREA = 1500

im = Image.open(SRC).convert("RGB")
W, H = im.size
a = np.asarray(im, dtype=np.float64) / 255.0
lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]

# 1-2. dark, then erase everything reachable from the border (the outside)
m = Image.fromarray(((lum < DARK_THRESH) * 255).astype(np.uint8), "L")
for seed in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)]:
    ImageDraw.floodfill(m, seed, 0)
m = Image.fromarray(((np.asarray(m) == 255) * 255).astype(np.uint8), "L")

# 3-4. label the enclosed blobs
work = m.copy()
blobs = []
while True:
    arr = np.asarray(work)
    idx = np.argwhere(arr == 255)
    if not len(idx):
        break
    y0, x0 = int(idx[0][0]), int(idx[0][1])
    ImageDraw.floodfill(work, (x0, y0), 64)
    a2 = np.asarray(work)
    ys, xs = np.where(a2 == 64)
    blobs.append(dict(x0=int(xs.min()), y0=int(ys.min()), x1=int(xs.max()), y1=int(ys.max()),
                      area=int(len(xs)), cx=int(xs.mean()), cy=int(ys.mean())))
    work = Image.fromarray(np.where(a2 == 64, 0, a2).astype(np.uint8), "L")

blobs = [b for b in blobs if b["area"] >= MIN_AREA]
blobs.sort(key=lambda b: (b["y0"] // 120, b["x0"]))

lines = [f"image {W}x{H}  dark<{DARK_THRESH}  min_area={MIN_AREA}",
         f"enclosed blobs: {len(blobs)}", "",
         f"{'#':>3} {'x0':>5} {'y0':>5} {'x1':>5} {'y1':>5} {'w':>5} {'h':>5} {'area':>8}  c(x,y)"]
for i, b in enumerate(blobs):
    lines.append(f"{i:>3} {b['x0']:>5} {b['y0']:>5} {b['x1']:>5} {b['y1']:>5} "
                 f"{b['x1']-b['x0']:>5} {b['y1']-b['y0']:>5} {b['area']:>8}  {b['cx']},{b['cy']}")
report = "\n".join(lines)
open(os.path.join(HERE, "measure_report.txt"), "w").write(report + "\n")
print(report)

ov = im.copy()
d = ImageDraw.Draw(ov)
for i, b in enumerate(blobs):
    d.rectangle([b["x0"], b["y0"], b["x1"], b["y1"]], outline=(0, 255, 90), width=2)
    d.text((b["x0"] + 3, b["y0"] + 3), str(i), fill=(0, 255, 90))
ov.save(os.path.join(HERE, "measure_overlay.png"))
print("\nwrote measure_report.txt and measure_overlay.png")
