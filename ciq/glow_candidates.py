"""Mockup: the digits' GLOW - the tight bloom, measured against the reference's falloff.

Decision support. The reference's profile was measured off its own pixels (ciq/ref_glow.py) and
converted to OUR screen px by the digit/tube size ratio (~0.35):

    0.5 px out   L111   the wire's own halo (our live 1 px ring measures L134 for the same band)
    1.2 px       L 32
    2.3 px       L 21
    4.0 px       L 15
    6.8 px       L 11
   11.4 px       L  3   the glass away from the wire is nearly black

The shipped glass holds L17-23 out to 11 px: a broad wash (haze sigma 22x40 screen px) with no tight
component - which is why the digits do not read as glowing. Rows below vary the two levers that fix
it: the baked haze's width, and the live ring steps (drawText has no alpha, so a soft falloff can only
be hand-painted as stepped bands, at 8r glyph blits per digit per frame).

Writes artwork/glow_candidates.png.
"""
import os

import cv2
import numpy as np
from PIL import Image

import device_colour
import hr_gauge
import prepare_artwork as pa
import preview

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "glow_candidates.png")
WL = np.array([0.2126, 0.7152, 0.0722], np.float32)
DISTANCES = [1, 2, 3, 4, 5, 7, 11]

# name -> (haze sigma src, haze amp, ring steps {radius: as-seen colour})
ROWS = [
    ("1  SHIPPED NOW  haze 48x85, no bloom", (48, 85), 0.30, {}),
    ("3  TIGHT HAZE 13x42 + RING2", (13, 42), 0.30, {2: (85, 22, 6)}),
    ("4  TIGHT HAZE 13x42 + RING2 + RING3", (13, 42), 0.30,
     {2: (85, 22, 6), 3: (40, 11, 4)}),
    ("6  MID HAZE 20x60 + RING2 + RING3", (20, 60), 0.30,
     {2: (85, 22, 6), 3: (40, 11, 4)}),
    ("7  TIGHT HAZE 13x42 amp .38 + RING2 + RING3", (13, 42), 0.38,
     {2: (85, 22, 6), 3: (40, 11, 4)}),
]
REFERENCE = [(1.2, 32), (2.3, 21), (4.0, 15), (6.8, 11), (11.4, 3)]


def build(sigma, amp):
    old = (pa.GLASS_HAZE_SIGMA, pa.GLASS_HAZE_AMP)
    pa.GLASS_HAZE_SIGMA, pa.GLASS_HAZE_AMP = sigma, amp
    try:
        return hr_gauge.bake(device_colour.correct(pa.SHIP.background(pa.load_clean_source())))
    finally:
        pa.GLASS_HAZE_SIGMA, pa.GLASS_HAZE_AMP = old


def _corr(rgb):
    return device_colour.correct(Image.new("RGB", (1, 1), tuple(rgb))).getpixel((0, 0))


def render(bg, steps):
    """Render with the candidate ring steps: corrected(ink) exactly as tube_colour.py writes them."""
    c = dict(preview.parse_constants())
    c["GLOW_RAD3"] = 0
    if steps:
        c["GLOW_RAD2"] = max(steps)
        c["INK_GLOW2"] = int.from_bytes(bytes(_corr(steps[max(steps)])), "big")
        if len(steps) > 1:
            c["GLOW_RAD2"], c["GLOW_RAD3"] = 2, 3
            c["INK_GLOW2"] = int.from_bytes(bytes(_corr(steps[2])), "big")
            c["INK_GLOW3"] = int.from_bytes(bytes(_corr(steps[3])), "big")
    return preview.render(consts=c, hr=128, background=bg)


def ink_mask(face):
    a = np.asarray(face, np.float32)
    c = preview.parse_constants()
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    box = np.zeros(a.shape[:2], bool)
    for cx in c["TIME_X"]:
        box[max(0, c["TIME_Y"] - 48):c["TIME_Y"] + 48, cx - 26:cx + 26] = True
    return ((mx / 255.0 > 0.75) & (sat > 0.5) & box).astype(np.uint8) * 255


def profile(face):
    a = np.asarray(face, np.float32)
    lum = a @ WL
    m = ink_mask(face)
    out, prev = [], np.zeros_like(m)
    for d in DISTANCES:
        cur = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * d + 1,) * 2))
        ring = (cur > 0) & (prev == 0)
        prev = cur
        if ring.any():
            out.append((d, tuple(np.median(a[ring], axis=0)), float(np.median(lum[ring]))))
    return out


if __name__ == "__main__":
    print("reference in our px: " + "  ".join(f"{d}px L{L}" for d, L in REFERENCE))
    print()
    rows = []
    for name, sigma, amp, steps in ROWS:
        face = device_colour.as_seen(render(build(sigma, amp), steps))
        prof = profile(face)
        print(f"{name:46s} " + "  ".join(f"{d}px L{L:3.0f}" for d, _, L in prof))
        rows.append((name + "   " + " ".join(f"{d}:L{L:.0f}" for d, _, L in prof), face))
    from amber_candidates import sheet
    sheet(rows, OUT, True)

    # one tube of the mid-haze row at 4x: a stepped bloom must not read as a blocky outline
    from PIL import Image
    name, sigma, amp, steps = ROWS[3]
    face = device_colour.as_seen(render(build(sigma, amp), steps)).resize((640, 720), Image.LANCZOS)
    cx = preview.parse_constants()["TIME_X"][1]
    z = face.crop(((cx - 46) * 2, 0, (cx + 46) * 2, 350)).resize((552, 1050), Image.LANCZOS)
    z.save(os.path.join(HERE, "artwork", "glow_zoom.png"))
    print("wrote artwork/glow_zoom.png", z.size, "for", name)