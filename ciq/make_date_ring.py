"""Generate the date-ring resources: the weekday and month set one letter per segment of the date
dial's outer ring, rotated to the ring (user-approved: artwork/date_ring/_compare.png, the 54 px
ring version).

The device cannot rotate text (drawText has no angle; drawRadialText needs vector fonts, which
this watch is not confirmed to have), so every word is PRE-RENDERED here:

    resources/drawables/ring/wd1..wd7.png   SUN..SAT  (Gregorian day_of_week 1 = Sunday)
    resources/drawables/ring/mo1..mo12.png  JAN..DEC
    resources/drawables/ring/ring.xml       their <bitmap> declarations
    source/DateRing.mc                      generated: patch offsets + resource-id lookups

Each word is an OPAQUE patch: a crop of the shipping background (already AMOLED-corrected) with
the rotated letters blended in, so it needs no bitmap alpha and is pixel-identical to the face
around it. All patches in a group share one rectangle (the union of every word's ink), so the
view blits them at one constant offset. They compile 16-bit (automaticPalette="false") like the
background, so no palette edge can show.

Geometry - measured on the source art and mapped through the bottom band (see the constants):
dial centre (810, 658) src -> (288.1, 283.9); letters on r 104 src (the ring band 87..121) ->
44.7 px; the 12 hand-drawn dividers read off a polar unwrap at 25, 58, 90, 122, 152.5, 179,
205, 241, 270, 299, 331, 357 deg (0 = 3 o'clock, clockwise). Dividers fall exactly on 12 and
6 o'clock, and the segments right of them run off the screen, so both words lean left, mirrored:
weekday in the segments centred 223 / 255.5 / 284.5 (tops out, read clockwise), month in
137 / 106 / 74 (tops in, read left to right like a coin's lower legend).

Usage:  python make_date_ring.py      (after prepare_resources.py, which writes the background)
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "resources", "drawables", "background.png")
RING = os.path.join(HERE, "resources", "drawables", "ring")
GEN_MC = os.path.join(HERE, "source", "DateRing.mc")

import prepare_artwork  # noqa: E402  (geometry follows the layout's scales)

_G = prepare_artwork.geometry()
CX, CY = _G["DATE_CENTRE"]
R_TEXT = _G["RING_R"]
TOP_SEGS = [223.0, 255.5, 284.5]      # weekday, left -> right
BOT_SEGS = [137.0, 106.0, 74.0]       # month, left -> right
CAP_PX = round(_G["RING_CAP"])        # cap height; ~11 px at layout C (band ~15 px deep)
GEORGIA = r"C:\Windows\Fonts\georgia.ttf"
INK_DIM = (0xFF, 0xD8, 0xA0)           # the view's INK_DIM, as the labels used before
SS = 6                                 # supersampling for clean rotation

WEEKDAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]      # day_of_week 1..7
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def letter(ch, cap_px=CAP_PX):
    """A glyph mask whose cap height is cap_px, rendered at SS x and tightly cropped."""
    f = ImageFont.truetype(GEORGIA, int(cap_px * SS / 0.70))   # Georgia cap height ~0.70 em
    c = Image.new("L", (cap_px * SS * 3, cap_px * SS * 3), 0)
    ImageDraw.Draw(c).text((cap_px * SS, cap_px * SS * 2), ch, font=f, fill=255, anchor="ls")
    return c.crop(c.getbbox())


def letter_mask(ch, theta_deg, outward, size, cap_px=CAP_PX):
    """Full-screen coverage mask of `ch` on the ring at theta, its top pointing out (or in)."""
    t = math.radians(theta_deg)
    x, y = CX + R_TEXT * math.cos(t), CY + R_TEXT * math.sin(t)
    up = (math.cos(t), math.sin(t)) if outward else (-math.cos(t), -math.sin(t))
    cw = math.degrees(math.atan2(up[0], -up[1]))            # clockwise rotation from upright
    g = letter(ch, cap_px).rotate(-cw, resample=Image.BICUBIC, expand=True)   # PIL: CCW
    g = g.resize((max(1, round(g.width / SS)), max(1, round(g.height / SS))), Image.LANCZOS)
    m = Image.new("L", size, 0)
    m.paste(g, (round(x - g.width / 2), round(y - g.height / 2)))
    return m


def word_mask(word, segs, outward, size):
    acc = np.zeros((size[1], size[0]), np.float32)
    for ch, th in zip(word, segs):
        acc = np.maximum(acc, np.asarray(letter_mask(ch, th, outward, size), np.float32))
    return Image.fromarray(acc.astype(np.uint8), "L")


def union_box(masks, pad=1):
    boxes = [m.getbbox() for m in masks]
    x0 = min(b[0] for b in boxes) - pad
    y0 = min(b[1] for b in boxes) - pad
    x1 = max(b[2] for b in boxes) + pad
    y1 = max(b[3] for b in boxes) + pad
    return x0, y0, x1, y1


def patches(bg, words, segs, outward, prefix, first_index):
    masks = [word_mask(w, segs, outward, bg.size) for w in words]
    box = union_box(masks)
    ink = Image.new("RGB", bg.size, INK_DIM)
    names = []
    for i, m in enumerate(masks):
        frame = Image.composite(ink, bg, m)
        name = f"{prefix}{first_index + i}"
        frame.crop(box).save(os.path.join(RING, name + ".png"), optimize=True)
        names.append(name)
    return box, names


if __name__ == "__main__":
    os.makedirs(RING, exist_ok=True)
    bg = Image.open(BG).convert("RGB")
    top_box, wd = patches(bg, WEEKDAYS, TOP_SEGS, True, "wd", 1)
    bot_box, mo = patches(bg, MONTHS, BOT_SEGS, False, "mo", 1)

    with open(os.path.join(RING, "ring.xml"), "w", newline="\n") as f:
        f.write("<resources>\n  <drawables>\n"
                "    <!-- generated by ciq/make_date_ring.py: opaque date-ring patches, 16-bit like\n"
                "         the background so no palette edge shows (see that script) -->\n")
        for n in wd + mo:
            f.write(f'    <bitmap id="Ring_{n}" filename="{n}.png" automaticPalette="false" />\n')
        f.write("  </drawables>\n</resources>\n")

    def ids(names):
        return ",\n        ".join(f"Rez.Drawables.Ring_{n}" for n in names)

    with open(GEN_MC, "w", newline="\n") as f:
        f.write(f"""// GENERATED by ciq/make_date_ring.py - do not edit; re-run the script instead.
import Toybox.Lang;

// Top-left of the weekday / month patches (each group shares one rectangle).
const RING_TOP_X = {top_box[0]};
const RING_TOP_Y = {top_box[1]};
const RING_BOT_X = {bot_box[0]};
const RING_BOT_Y = {bot_box[1]};

//! Resource id of the weekday patch for Gregorian day_of_week (1 = Sunday .. 7 = Saturday).
function ringWeekday(dow as Number) as ResourceId {{
    var ids = [
        {ids(wd)}
    ] as Array<ResourceId>;
    return ids[(dow - 1) % 7];
}}

//! Resource id of the month patch for Gregorian month (1 = January .. 12 = December).
function ringMonth(month as Number) as ResourceId {{
    var ids = [
        {ids(mo)}
    ] as Array<ResourceId>;
    return ids[(month - 1) % 12];
}}
""")
    print(f"weekday patches {top_box}  ({top_box[2]-top_box[0]}x{top_box[3]-top_box[1]})")
    print(f"month   patches {bot_box}  ({bot_box[2]-bot_box[0]}x{bot_box[3]-bot_box[1]})")
    print(f"wrote {len(wd) + len(mo)} patches, ring.xml, {GEN_MC}")
