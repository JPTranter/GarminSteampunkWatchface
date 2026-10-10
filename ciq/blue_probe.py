"""Probe: where is the BLUE on the current face? Prints the blue-excess (B - (R+G)/2 > 12) pixel
clusters with their bounding boxes and mean colour, so a "the tubes are too blue" complaint can be
attributed to an element instead of a guess. Reads the as-seen frame of the current candidate.

Not shipping code - a measurement. Run:  python blue_probe.py
"""
import os
import sys

import numpy as np
from PIL import Image

import device_colour
import glass_candidates as gc

HERE = os.path.dirname(os.path.abspath(__file__))


def clusters(exc, rgb, thr=12.0, min_px=40):
    """Simple flood fill over the thresholded blue-excess mask (4-connectivity, iterative).
    Reports each cluster's OWN mean colour (a bounding-box mean is misleading - the box of an arc
    that runs beside a digit averages the digit's orange in)."""
    m = exc > thr
    h, w = m.shape
    seen = np.zeros_like(m, bool)
    out = []
    for y0 in range(h):
        for x0 in range(w):
            if not m[y0, x0] or seen[y0, x0]:
                continue
            stack, pix = [(y0, x0)], []
            seen[y0, x0] = True
            while stack:
                y, x = stack.pop()
                pix.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
            if len(pix) >= min_px:
                ys = [p[0] for p in pix]
                xs = [p[1] for p in pix]
                sel = rgb[np.array(ys), np.array(xs)]
                out.append((len(pix), (min(xs), min(ys), max(xs), max(ys)),
                            np.mean([exc[p] for p in pix]), sel.mean(axis=0)))
    return sorted(out, reverse=True)


if __name__ == "__main__":
    name, cast, gamma = gc.CANDIDATES[0]                 # A = current
    if len(sys.argv) > 1:                                # or the candidate letter given
        for c in gc.CANDIDATES:
            if c[0].startswith(sys.argv[1]):
                name, cast, gamma = c
    face = device_colour.as_seen(gc.build(cast, gamma))
    a = np.asarray(face, np.float32)
    exc = a[..., 2] - (a[..., 0] + a[..., 1]) / 2.0
    print(f"{name}:  blue pixels (B-R > 12 and B-G > 12) = {(exc > 12).mean() * 100:.2f}% of the face")
    for n, box, e, mean in clusters(exc, a)[:14]:
        x0, y0, x1, y1 = box
        band = "TUBE BAND" if y1 < 170 else ("manifold" if y1 < 215 else "dials")
        print(f"  {n:6d} px  x {x0:3d}-{x1:3d}  y {y0:3d}-{y1:3d}  ({band:9s})  "
              f"mean rgb ({mean[0]:5.0f},{mean[1]:5.0f},{mean[2]:5.0f})  excess {e:5.1f}")