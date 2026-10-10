"""Mockup: how orange the time digits should be. Decision support.

The user, looking at the watch: "The time display is not orange enough. It should be like the
reference." The shipped core (252,196,96) was deliberately one step HOTTER than the reference's own
core (245,155,30, hue 35 deg / L 0.63) to buy contrast (7.5:1 vs 6.2:1). The device is the judge, so
this renders the ladder from the shipped row to a saturated orange and measures each row's actual
ink colour as seen, beside the reference's own numbers.

Writes artwork/ink_orange.png (reference band + four rows, amber glass, SHIPPING background).
"""
import os

import numpy as np
from PIL import Image

import amber_candidates as ac
import device_colour

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "ink_orange.png")

# name -> (core, ring), AS SEEN (before the AMOLED pre-correction)
INK = [
    ("1  SHIPPED  core FC C460 / ring D6 781E", (252, 196, 96), (214, 120, 30)),
    ("2  REFERENCE MATCH  core F5 9B1E / ring B6 6616", (245, 155, 30), (182, 102, 22)),
    ("3  REF core + shipped ring  F5 9B1E / D6 781E", (245, 155, 30), (214, 120, 30)),
    ("4  DEEP ORANGE  core F2 8C14 / ring C0 6010", (242, 140, 20), (192, 96, 16)),
]


def core_colour(bg, ink):
    """Median sRGB of the digit's own ink as the panel shows it, off the eroded glyph core."""
    import cv2
    with_d = device_colour.as_seen(ac.render(bg, ink))
    without = device_colour.as_seen(ac.render(bg, ink, hide_digits=True))
    a = np.asarray(with_d, np.float32)
    b = np.asarray(without, np.float32)
    mask = ((np.abs(a - b).sum(2) > 24).astype(np.uint8)) * 255
    mask = cv2.erode(mask, np.ones((3, 3), np.uint8))
    px = a[mask > 0]
    return np.median(px, axis=0), len(px)


if __name__ == "__main__":
    glass = dict(zip(("cast", "gamma", "lift"), ac.GLASS[1][1:]))          # B amber = shipping
    bg = ac.build(glass["cast"], glass["gamma"], glass["lift"])
    rows = []
    print(f"{'row':50s} {'ink as seen':22s} {'hue/sat':12s} core-vs-glass  stroke")
    for name, core, ring in INK:
        face = device_colour.as_seen(ac.render(bg, (core, ring)))
        med, n = core_colour(bg, (core, ring))
        ratio, stroke = ac.legibility(bg, (core, ring))
        mx, mn = max(med), min(med)
        sat = (mx - mn) / max(mx, 1)
        # hue of the ink as seen (r/g/b 0-255)
        r, g, bl = med
        hue = 60 * (((g - bl) / max(1.0, r - min(g, bl))) % 6) if r >= g >= bl else float("nan")
        print(f"{name:50s} ({med[0]:4.0f},{med[1]:4.0f},{med[2]:4.0f})   "
              f"{hue:4.0f} deg / {sat:.2f}   {ratio:5.1f}:1   {stroke:.0f} px")
        rows.append((f"{name}   ink ({med[0]:.0f},{med[1]:.0f},{med[2]:.0f})"
                     f"  {ratio:.1f}:1", face))
    print("\nreference (measured off the user's AI render): core (245,155,30) hue 35 / L 0.63, "
          "stroke body (182,102,22) hue 30 / L 0.44")
    ac.sheet(rows, OUT, True)