"""Probe: how the reference's orange GLOW falls off around a lit digit.

"The digits do not have a glowing orange effect" is a question about the bloom, not the ink colour -
so measure the reference's radial profile: for each distance band from the digit's bright ink, the
median colour and luminance of the glass it lights. That gives the amplitude and the width a baked
glow (or an extra halo ring) has to reproduce.

Measurement only. Run: python ref_glow.py [image]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
W = np.array([0.2126, 0.7152, 0.0722], np.float32)
BANDS = [(1, 2), (3, 4), (5, 8), (9, 14), (15, 24), (25, 40), (41, 70)]


def band_masks(mask, size):
    """Ring masks at the given distances from `mask`, by successive elliptical dilations."""
    out, prev = [], np.zeros_like(mask)
    for lo, hi in BANDS:
        d = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * hi + 1,) * 2))
        ring = (d > 0) & (prev == 0)
        out.append((lo, hi, ring))
        prev = d
    return out


if __name__ == "__main__":
    refs = os.environ.get("GARMIN_REFS") or os.path.join(HERE, "refs")
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        refs, "Copilot_20261010_221001_82b632.png")
    a = np.asarray(Image.open(path).convert("RGB"), np.float32)
    h, w = a.shape[:2]
    # the tube band only: above the manifold, so the brass never contaminates the profile
    a = a[: int(h * 0.42)]

    mx, mn = a.max(-1), a.min(-1)
    val = mx / 255.0
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    hue = np.zeros_like(mx)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = mx - mn
    nz = d > 1
    hue = np.where(nz & (mx == r), 60 * (((g - b) / np.maximum(d, 1)) % 6), hue)
    hue = np.where(nz & (mx == b), 60 * ((r - g) / np.maximum(d, 1) + 4), hue)

    ink = ((val > 0.75) & (sat > 0.5) & (hue < 55)).astype(np.uint8) * 255
    print(f"reference {path}: ink mask {int((ink > 0).sum())} px (bright saturated core)")
    lum = a @ W
    print(f"  ink luminance  median {np.median(lum[ink > 0]):6.1f}  "
          f"p90 {np.percentile(lum[ink > 0], 90):6.1f}")
    print(f"\n  {'distance':>10s}  {'median rgb':>18s}  {'median L':>8s}  {'vs ink':>7s}")
    inkL = np.median(lum[ink > 0])
    for lo, hi, ring in band_masks(ink, a.shape[:2]):
        px = a[ring]
        if len(px) == 0:
            continue
        med = np.median(px, axis=0)
        L = np.median(lum[ring])
        print(f"  {lo:4d}-{hi:3d} px  ({med[0]:5.0f},{med[1]:5.0f},{med[2]:5.0f})  "
              f"{L:8.1f}  {L / inkL:.3f}")