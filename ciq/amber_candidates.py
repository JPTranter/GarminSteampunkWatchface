"""Mockup: amber tube glass and orange digits, measured off the user's two references.

DECISION SUPPORT, not shipping code. The user supplied a photo-real nixie render and then an AI face
render ("it should look a bit like the top of this"): warm amber envelopes, saturated orange wire
digits, dark background, blue sparks at the sides. Measured off the AI render (ciq/ref_probe.py):

    digit core (V>0.85)   (245, 155, 30)   hue 35 deg, L 0.63   -> the glyph core, INK_TIME
    digit body (V .60-.85)(182, 102, 22)   hue 30 deg, L 0.44   -> the 1 px ring, INK_GLOW1
    glow/bloom            (117,  61, 11)   hue 28 deg, L 0.27   -> the haze already baked in the glass
    glass interior lit     (53,  25,  6)   L 0.11               -> the base cast's hue

The glass axes are the cast (`GLASS_CAST_RGB`), its gamma and the interior field lift (`TUBE_LIFT`) -
all module constants in prepare_artwork.py, overridden here IN MEMORY, so nothing on disk moves.
Ink candidates run through `tube_colour.corrected()` exactly like the shipping constants, because a
live colour must be pre-corrected the same way as the baked art.

Writes artwork/amber_glass.png (4 glass rows, current ink) and artwork/amber_ink.png (3 ink rows, on
amber glass), each with the reference's tube band above for comparison.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import device_colour
import hr_gauge
import prepare_artwork as pa
import preview
import tube_colour

HERE = os.path.dirname(os.path.abspath(__file__))
# Reference images are user-supplied and stay out of git (see .gitignore): ciq/refs/.
# GARMIN_REFS moves them, for a machine where they live elsewhere.
REFS = os.environ.get("GARMIN_REFS") or os.path.join(HERE, "refs")
REF = os.path.join(REFS, "Copilot_20261010_221001_82b632.png")

# name -> (cast, gamma, interior lift)
GLASS = [
    ("A  CURRENT  blue x1.22",        (0.78, 0.95, 1.22), 1.35, 0.00),
    ("B  AMBER  ref hue 28-35 deg",   (1.30, 0.74, 0.26), 1.35, 0.00),
    ("C  AMBER, warmer/deeper",       (1.45, 0.68, 0.20), 1.30, 0.00),
    ("D  AMBER + interior lift .10",  (1.30, 0.74, 0.26), 1.35, 0.10),
]

# name -> (core, ring)  AS SEEN (before the AMOLED pre-correction)
INK = [
    ("1  CURRENT  core FC E296 / ring FF 4E16", (252, 226, 150), (255, 78, 22)),
    ("2  REF-MATCHED  core F5 9B1E / ring B6 6616", (245, 155, 30), (182, 102, 22)),
    ("3  REF hot core  FC C460 / ring D6 781E", (252, 196, 96), (214, 120, 30)),
]

W, H = 320, 360


def build(cast, gamma, lift):
    """The shipping frame for one glass variant, through the same chain make.py uses."""
    old = (pa.GLASS_CAST_RGB, pa.GLASS_GAMMA, pa.TUBE_LIFT)
    pa.GLASS_CAST_RGB, pa.GLASS_GAMMA, pa.TUBE_LIFT = cast, gamma, lift
    try:
        frame = pa.SHIP.background(pa.load_clean_source())
    finally:
        pa.GLASS_CAST_RGB, pa.GLASS_GAMMA, pa.TUBE_LIFT = old
    return hr_gauge.bake(device_colour.correct(frame))


def render(bg, ink, hide_digits=False):
    """Preview the face with one ink candidate: the constants are the shipping ones with the three
    INK_* values replaced by corrected(candidate), exactly as tube_colour.py writes them.
    `hide_digits` pushes the time row off-frame, so the frame differs from the real one ONLY in the
    time digits - that diff is the ink mask used to measure core contrast."""
    c = dict(preview.parse_constants())
    core, ring = ink
    c["INK_TIME"] = int.from_bytes(bytes(tube_colour.corrected(core)), "big")
    c["INK_GLOW1"] = int.from_bytes(bytes(tube_colour.corrected(ring)), "big")
    c["INK_GLOW2"] = c["INK_GLOW1"]
    if hide_digits:
        c["TIME_Y"] = -500
    return preview.render(consts=c, hr=128, background=bg)


def legibility(bg, ink):
    """(core-vs-glass contrast, stroke px) for one ink candidate, measured on the ERODED glyph core.

    The ink mask is the pixels the digits changed (render with and without them), eroded 1 px so the
    halo ring and the anti-aliased skirt - which outnumber the stroke pixels - cannot decide the
    number. Stroke is the median longest lit run per row of that same mask.
    """
    import cv2
    with_d = device_colour.as_seen(render(bg, ink))
    without = device_colour.as_seen(render(bg, ink, hide_digits=True))
    a = np.asarray(with_d, np.float32)
    b = np.asarray(without, np.float32)
    core = np.asarray(with_d.convert("L"), np.float32)
    back = np.asarray(without.convert("L"), np.float32)
    mask = ((np.abs(a - b).sum(2) > 24).astype(np.uint8)) * 255
    mask = cv2.erode(mask, np.ones((3, 3), np.uint8))
    sel = mask > 0
    if not sel.any():
        return 0.0, 0.0
    ratio = float(np.median(core[sel]) / max(1.0, np.median(back[sel])))
    runs = []
    for row in mask:
        lit = np.where(row > 0)[0]
        if len(lit) == 0:
            continue
        d = np.diff(lit)
        runs.append(max(np.split(lit, np.where(d > 1)[0] + 1), key=len).size)
    return ratio, float(np.median(runs)) if runs else 0.0


def measure(face):
    """Median sRGB of the lit glass (top 30 % of the tube walls) and of the digit ink area."""
    img = np.asarray(face, np.float32)
    band = []
    for cx in preview.parse_constants()["TIME_X"]:
        band.append(img[15:150, cx - 30:cx - 24].reshape(-1, 3))
        band.append(img[15:150, cx + 24:cx + 30].reshape(-1, 3))
    band = np.concatenate(band)
    lum = band @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hi, lo = np.percentile(lum, (70, 30))
    return np.median(band[lum >= hi], axis=0), np.median(band[lum <= lo], axis=0)


def label_font(size):
    for p in (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def ref_band(width):
    """The reference's tube band, scaled to `width`: everything above its brass collars."""
    im = Image.open(REF).convert("RGB")
    band = im.crop((44, 20, 1013, 430))
    return band.resize((width, round(band.height * width / band.width)), Image.LANCZOS)


def sheet(rows, path, ref_first):
    """rows: (name, face_2x). Reference band across the top, then one row per candidate: the 2x tube
    band above the 1x face."""
    cw, ch, zh, pad, head = 520, 585, 325, 12, 40
    rb = ref_band(len(rows) * (cw + pad) - pad)
    top = 30 + rb.height + 10
    Ws = pad + len(rows) * (cw + pad)
    Hs = top + head + zh + 8 + H + pad
    s = Image.new("RGB", (Ws, Hs), (26, 24, 22))
    d = ImageDraw.Draw(s)
    f = label_font(22)
    if ref_first:
        d.text((pad + 4, 8), "REFERENCE (top of the AI render, scaled) - warm amber glass, "
                             "saturated orange digits, blue side sparks", fill=(240, 215, 165), font=f)
        s.paste(rb, (pad, 30))
    y0 = 30 + rb.height + 20
    for i, (name, face) in enumerate(rows):
        x = pad + i * (cw + pad)
        bright, dark = measure(face)
        d.text((x + 4, y0), f"{name}   lit glass ({bright[0]:.0f},{bright[1]:.0f},{bright[2]:.0f})"
                            f"  B-R {bright[2] - bright[0]:+.0f}", fill=(240, 215, 165), font=f)
        two = face.resize((cw, ch), Image.LANCZOS)
        s.paste(two.crop((0, 0, cw, zh)), (x, y0 + head))
        s.paste(two.resize((W, H), Image.LANCZOS), (x, y0 + head + zh + 8))
    s.save(path)
    print("wrote", path, s.size)


if __name__ == "__main__":
    print(f"{'row':44s} {'lit glass':22s} B-R   {'dark glass':22s} B-R")
    bg = {}
    for name, cast, gamma, lift in GLASS:
        bg[name] = build(cast, gamma, lift)
        face = device_colour.as_seen(render(bg[name], INK[0][1:]))
        b, dk = measure(face)
        fmt = lambda v: f"({v[0]:4.0f},{v[1]:4.0f},{v[2]:4.0f})"
        print(f"{name:44s} {fmt(b):22s} {b[2] - b[0]:+5.0f}  {fmt(dk):22s} {dk[2] - dk[0]:+5.0f}")

    amber = GLASS[1][0]
    print()
    rows_ink = []
    legs = {}
    for name, core, ring in INK:
        face = device_colour.as_seen(render(bg[amber], (core, ring)))
        legs[name] = legibility(bg[amber], (core, ring))
        b, dk = measure(face)
        print(f"{name:52s} lit glass ({b[0]:.0f},{b[1]:.0f},{b[2]:.0f})   "
              f"core-vs-glass {legs[name][0]:.1f}:1   stroke {legs[name][1]:.0f} px")
        rows_ink.append((f"{name}   core-vs-glass {legs[name][0]:.1f}:1  "
                         f"stroke {legs[name][1]:.0f} px", face))

    sheet([(n, device_colour.as_seen(render(bg[n], INK[0][1:]))) for n, *_ in GLASS],
          os.path.join(HERE, "artwork", "amber_glass.png"), True)
    sheet(rows_ink, os.path.join(HERE, "artwork", "amber_ink.png"), True)
