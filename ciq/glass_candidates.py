"""Mockup: how blue the nixie tube envelopes should be.

DECISION SUPPORT, not shipping code. The user: "the nixie tubes look wrong at the moment with so
much blue - can they look more like glass". The blue is one knob: `GLASS_CAST_RGB` in
prepare_artwork.py, a per-channel gain on the artwork's luminance (blue x1.22, red x0.78) that
replaced the AI art's gold. This renders the ladder from that blue cast to neutral and warm through
the SHIPPING chain (glass_tubes -> SHIP.background -> device_colour.correct -> hr_gauge.bake ->
preview.render -> as_seen) and measures the glass itself.

MEASUREMENT REGIONS, both haze-free (the digit's warm haze is centred on the tube at
src y 255 +-85 = screen y 96 +-40, and the dome hotspot sits at screen y 39):
  shoulder  screen y 6..34  - the dome/shoulder glass, no haze at all
  wall      screen x +-22..30, y 45..150 - the envelope's side walls, no digit
Writes artwork/glass_candidates.png (all five: tube band 2x + full face) and
artwork/glass_zoom.png (one tube at 4x, A / C / E).
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import device_colour
import hr_gauge
import prepare_artwork as pa
import preview

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "glass_candidates.png")
ZOOM = os.path.join(HERE, "artwork", "glass_zoom.png")

# name -> (cast, gamma)
CANDIDATES = [
    ("A  CURRENT  blue x1.22",        (0.78, 0.95, 1.22), 1.35),
    ("B  HALF-BLUE  x1.11",           (0.87, 0.97, 1.12), 1.35),
    ("C  NEUTRAL  no cast",           (1.00, 1.00, 1.00), 1.35),
    ("D  NEUTRAL, lighter interior",  (1.00, 1.00, 1.00), 1.15),
    ("E  WARM-NEUTRAL  x0.97 blue",   (1.05, 1.00, 0.97), 1.25),
]


def build(cast, gamma):
    """The shipping frame for one cast, through the same chain make.py uses."""
    old = (pa.GLASS_CAST_RGB, pa.GLASS_GAMMA)
    pa.GLASS_CAST_RGB, pa.GLASS_GAMMA = cast, gamma
    try:
        frame = pa.SHIP.background(pa.load_clean_source())
    finally:
        pa.GLASS_CAST_RGB, pa.GLASS_GAMMA = old
    bg = hr_gauge.bake(device_colour.correct(frame))
    return preview.render(consts=preview.parse_constants(), hr=128, background=bg)


def measure(face, cx):
    """Two medians off the tube's side WALLS (x +-24..30: no digit, no halo, no bloom).

    `bright` is the top 30 % of the wall by luminance - the lit glass streaks, which is where the
    cast shows most (at lum 0.5 the blue gain alone shifts B-R by ~+60/255), and `dark` the bottom
    30 %, the clear glass. Reporting both stops a metric dominated by the near-black interior."""
    img = np.asarray(face, np.float32)
    band = []
    for c in (preview.parse_constants()["TIME_X"] if cx is None else [cx]):
        band.append(img[15:150, c - 30:c - 24].reshape(-1, 3))
        band.append(img[15:150, c + 24:c + 30].reshape(-1, 3))
    band = np.concatenate(band)
    lum = band @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hi, lo = np.percentile(lum, (70, 30))
    return np.median(band[lum >= hi], axis=0), np.median(band[lum <= lo], axis=0)


def label_font(size):
    for p in (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


if __name__ == "__main__":
    c = preview.parse_constants()
    cx = None                                 # all four tubes
    faces = {}
    fmt = lambda v: f"({v[0]:4.0f},{v[1]:4.0f},{v[2]:4.0f})"
    print(f"{'candidate':32s} {'bright wall':20s} B-R   {'dark wall':20s} B-R")
    for name, cast, gamma in CANDIDATES:
        faces[name] = device_colour.as_seen(build(cast, gamma))
        s, w = measure(faces[name], cx)
        print(f"{name:32s} {fmt(s):20s} {s[2] - s[0]:+5.0f}  {fmt(w):20s} {w[2] - w[0]:+5.0f}")

    # ---- sheet 1: all five, tube band at 2x above the whole face
    cw, ch, zoom_h, pad, head = 640, 720, 400, 12, 44
    W, H = pad + len(CANDIDATES) * (cw + pad), head + zoom_h + 8 + 360 + pad
    sheet = Image.new("RGB", (W, H), (26, 24, 22))
    d = ImageDraw.Draw(sheet)
    f = label_font(24)
    for i, name in enumerate(faces):
        s, w = measure(faces[name], cx)
        x = pad + i * (cw + pad)
        two = faces[name].resize((cw, ch), Image.LANCZOS)
        d.text((x + 6, 12),
               f"{name}   bright wall B-R {s[2] - s[0]:+.0f}  dark wall B-R {w[2] - w[0]:+.0f}",
               fill=(240, 215, 165), font=f)
        sheet.paste(two.crop((0, 0, cw, zoom_h)), (x, head))
        sheet.paste(two.resize((320, 360), Image.LANCZOS), (x, head + zoom_h + 8))
    sheet.save(OUT)

    # ---- sheet 2: one tube at 4x, A / C / E side by side, for the actual pick
    pick = [n for n in faces if n[0] in "ACDE"]
    zs = 3
    box = ((c["TIME_X"][1] - 46) * 2, 0, (c["TIME_X"][1] + 46) * 2, 175 * 2)
    cells = [faces[n].resize((cw, ch), Image.LANCZOS).crop(box)
             .resize(((box[2] - box[0]) // 2 * zs, (box[3] - box[1]) // 2 * zs), Image.LANCZOS)
             for n in pick]
    zw, zh = cells[0].size
    zsheet = Image.new("RGB", (len(cells) * (zw + pad) + pad, zh + head + 2 * pad), (26, 24, 22))
    dz = ImageDraw.Draw(zsheet)
    for i, (n, cell) in enumerate(zip(pick, cells)):
        s, w = measure(faces[n], cx)
        x = pad + i * (zw + pad)
        dz.text((x + 6, pad + 6), f"{n}   bright wall B-R {s[2] - s[0]:+.0f}",
                fill=(240, 215, 165), font=f)
        zsheet.paste(cell, (x, pad + head))
    zsheet.save(ZOOM)
    print("wrote", OUT, sheet.size, "and", ZOOM, zsheet.size)