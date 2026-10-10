"""Measure the brass background's data windows by 4-way ENCLOSURE (pure numpy, no flood fill).

The image is mostly black, so "dark" alone also matches the gaps between brass parts. A data window
is dark AND bounded by non-dark on all four sides. So for every pixel compute whether a non-dark
pixel exists to its left / right / up / down (cumulative maximum), and keep dark pixels that have all
four. Label the survivors with a small BFS.

Out: measure_report.txt + measure_overlay.png
"""
import os
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "BrassBackground.png")
DARK_THRESH = 0.09
MIN_AREA = 1200

im = Image.open(SRC).convert("RGB")
W, H = im.size
a = np.asarray(im, dtype=np.float64) / 255.0
lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
dark = lum < DARK_THRESH
nd = ~dark

left = np.zeros_like(dark)
left[:, 1:] = np.maximum.accumulate(nd, axis=1)[:, :-1]
right = np.zeros_like(dark)
right[:, :-1] = np.maximum.accumulate(nd[:, ::-1], axis=1)[:, ::-1][:, 1:]
up = np.zeros_like(dark)
up[1:, :] = np.maximum.accumulate(nd, axis=0)[:-1, :]
down = np.zeros_like(dark)
down[:-1, :] = np.maximum.accumulate(nd[::-1, :], axis=0)[::-1, :][1:, :]

win = dark & left & right & up & down

# label with BFS (window pixels are a small fraction of the image)
lab = np.zeros((H, W), dtype=np.int32)
blobs, nid = [], 0
ys_all, xs_all = np.where(win)
for sy, sx in zip(ys_all, xs_all):
    if lab[sy, sx]:
        continue
    nid += 1
    q = deque([(sy, sx)])
    lab[sy, sx] = nid
    pix = []
    while q:
        y, x = q.popleft()
        pix.append((y, x))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and win[ny, nx] and not lab[ny, nx]:
                lab[ny, nx] = nid
                q.append((ny, nx))
    arr = np.array(pix)
    blobs.append(dict(x0=int(arr[:, 1].min()), y0=int(arr[:, 0].min()),
                      x1=int(arr[:, 1].max()), y1=int(arr[:, 0].max()),
                      area=len(pix), cx=int(arr[:, 1].mean()), cy=int(arr[:, 0].mean())))

blobs = [b for b in blobs if b["area"] >= MIN_AREA]
blobs.sort(key=lambda b: (b["y0"] // 120, b["x0"]))

lines = [f"image {W}x{H}  dark<{DARK_THRESH}  min_area={MIN_AREA}",
         f"enclosed windows: {len(blobs)}", "",
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
    d.rectangle([b["cx"] - 3, b["cy"] - 3, b["cx"] + 3, b["cy"] + 3], fill=(255, 60, 60))
    d.text((b["x0"] + 4, b["y0"] + 4), str(i), fill=(0, 255, 90))
ov.save(os.path.join(HERE, "measure_overlay.png"))
print("\nwrote measure_report.txt + measure_overlay.png")
