"""Targeted re-measurement of the two round dials, the counter strip, and the tube interiors.

The eyeball estimate put the right dial's centre at x=810, but the rendered page shows the date
sitting left of centre — so measure it properly. Restricting the scan to a known band (unlike the
whole-image scan) makes "dark run bounded by brass" reliable.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, "BrassBackground.png")).convert("RGB")
W, H = im.size
a = np.asarray(im, dtype=np.float64) / 255.0
lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
DARK = 0.09


def runs_1d(vals, lo, min_len=30):
    m = vals < DARK
    out, start = [], None
    for i, v in enumerate(m):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((lo + start, lo + i))
            start = None
    if start is not None:
        out.append((lo + start, lo + len(m)))
    return [r for r in out if r[1] - r[0] >= min_len]


print(f"image {W}x{H}")
print("\n-- DIALS: horizontal scans (a row through each dial's middle) --")
for label, y, x0, x1 in (("LEFT ", 640, 20, 360), ("RIGHT", 640, 660, 1010),
                         ("LEFT ", 700, 20, 360), ("RIGHT", 700, 660, 1010)):
    rr = runs_1d(lum[y, x0:x1], x0, min_len=60)
    for (rx0, rx1) in rr:
        print(f"  y={y} {label} dark run x {rx0}..{rx1}  centre {(rx0+rx1)//2}  width {rx1-rx0}")

print("\n-- DIALS: vertical scans (a column through each dial's centre) --")
for label, x in (("LEFT ", 200), ("LEFT ", 210), ("RIGHT", 810), ("RIGHT", 830), ("RIGHT", 850)):
    rr = runs_1d(lum[480:820, x], 480, min_len=60)
    for (ry0, ry1) in rr:
        print(f"  x={x} {label} dark run y {ry0}..{ry1}  centre {(ry0+ry1)//2}  height {ry1-ry0}")

print("\n-- COUNTER strip --")
for y in (600, 618, 630):
    rr = runs_1d(lum[y, 320:700], 320, min_len=60)
    print(f"  y={y}: {rr}")
for x in (400, 500, 610):
    rr = runs_1d(lum[500:730, x], 500, min_len=40)
    print(f"  x={x}: vertical {rr}")

print("\n-- TUBE interiors: vertical extent at each tube centre --")
for cx in (272, 439, 591, 747):
    rr = runs_1d(lum[100:430, cx], 100, min_len=40)
    big = max(rr, key=lambda t: t[1] - t[0]) if rr else None
    print(f"  cx={cx}: {rr}   largest {big}")

print("\n-- TUBE interiors: horizontal extent at mid-glass --")
for y in (200, 250, 300):
    rr = runs_1d(lum[y, 150:880], 150, min_len=30)
    print(f"  y={y}: {rr}")
