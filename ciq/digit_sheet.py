"""Diagnostic: all ten digits on black, from the SHIPPING draw path, layer by layer.

The user asked for "a collection of 0 to 9 digits on a black background so I can confirm the issue"
("there is obviously no glow at the bottom of the digit"). Three rows, so the cause is visible rather
than inferred:

  1. the halo font ALONE (its glyph coverage IS the alpha ramp) - does the mask fade downward?
  2. the bands + wire + core (no halo)                  - is the solid rim even all round?
  3. everything, as the watch draws it                  - what the eye actually gets.

It also prints, per digit, the halo's own contribution above vs below the ink, measured as the
difference between row 3 and row 2.

Writes artwork/digit_sheet.png. Diagnostic, not shipping code.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import preview

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "digit_sheet.png")
DIGITS = [str(i) for i in range(10)]
CELL_W, CELL_H, ZOOM = 64, 96, 4


def cell(fonts, colour_only=None, halo=True):
    """One digit drawn by the shipping path (or one layer of it) on black, cropped to a cell."""
    c = preview.parse_constants()
    wire = preview.Font("NixieTime")
    hot = preview.Font("NixieTimeHot")
    halo_f = preview.Font("NixieTimeHalo")
    out = []
    for d in DIGITS:
        img = Image.new("RGB", (CELL_W, CELL_H), (0, 0, 0))
        x, y = CELL_W // 2, CELL_H // 2
        if colour_only is not None:                     # the halo mask alone, in its own colour
            preview.centred(img, c, halo_f, d, x, y, colour_only)
        elif halo:                                      # the shipping path
            preview.glowing(img, c, wire, d, x, y, hot, halo_f)
        else:                                           # the same without the halo pass
            preview.glowing(img, c, wire, d, x, y, hot, None)
        out.append(img)
    return out


def diff_above_below(a_imgs, b_imgs):
    """Per digit: the (a - b) contribution above vs below the digit's own ink."""
    res = []
    for a, b in zip(a_imgs, b_imgs):
        d = np.abs(np.asarray(a, np.int32) - np.asarray(b, np.int32)).sum(2)
        lum = np.asarray(a, np.int32) @ np.array([0.2126, 0.7152, 0.0722])
        ink = lum > 90
        ys = np.where(ink.any(1))[0]
        top, bot = ys.min(), ys.max()
        above = d[max(0, top - 6):top].sum()
        below = d[bot + 1:bot + 7].sum()
        res.append((above, below))
    return res


if __name__ == "__main__":
    all_layer = cell(None, halo=True)
    no_halo = cell(None, halo=False)
    halo_only = cell(None, colour_only=preview.parse_constants()["INK_GLOW3"])

    rows = [("1. the halo mask alone (its coverage IS the ramp)", halo_only),
            ("2. bands + wire + core (no halo)", no_halo),
            ("3. shipping: all three passes", all_layer)]
    pad, head = 8, 26
    W = pad + len(DIGITS) * (CELL_W * ZOOM + pad)
    H = pad + len(rows) * (head + CELL_H * ZOOM + pad)
    s = Image.new("RGB", (W, H), (10, 10, 10))
    d = ImageDraw.Draw(s)
    f = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 17)
    for r, (label, imgs) in enumerate(rows):
        y = pad + r * (head + CELL_H * ZOOM + pad)
        d.text((pad, y), label, fill=(230, 210, 165), font=f)
        for i, im in enumerate(imgs):
            x = pad + i * (CELL_W * ZOOM + pad)
            s.paste(im.resize((CELL_W * ZOOM, CELL_H * ZOOM), Image.NEAREST), (x, y + head))
    s.save(OUT)

    print("halo's contribution above / below each digit's ink (sum of |diff| over 6 rows):")
    for dig, (a_, b_) in zip(DIGITS, diff_above_below(all_layer, no_halo)):
        flag = "  <-- asymmetric" if b_ < a_ / 3 else ""
        print(f"   {dig}:  above {a_:6d}   below {b_:6d}{flag}")
    print("wrote", OUT, s.size)