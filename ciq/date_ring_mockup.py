"""Mockup: weekday and month set one letter per segment in the date dial's outer ring, rotated.

DECISION SUPPORT, not shipping code. Writes artwork/date_ring/_compare.png:
    current | ring letters + day at 42 px | ring letters + day at 52 px

Geometry, measured on the source art (1024 grid) and mapped through the bottom band:
- dial centre (810, 658) -> screen (288.1, 283.9)
- ring band: r 87..121 src (inner-disc edge 85, outer edge 123) -> letters centred on r 104 src
  = 44.7 px on screen, band depth ~15 px
- the 12 segment dividers, read off a polar unwrap of the dial (0 deg = 3 o'clock, clockwise,
  screen y down): 25, 58, 90, 122, 152.5, 179, 205, 241, 270, 299, 331, 357. They are hand-drawn
  (25-36 deg apart), so each letter sits on ITS segment's measured centre, not on a 30 deg grid.
- dividers fall exactly on 12 and 6 o'clock, so a 3-letter word cannot be centred on the vertical;
  the segments right of 12/6 o'clock also run off the screen edge (x > 315). Both words therefore
  lean LEFT, mirrored about the horizontal: weekday in the segments centred 223 / 255.5 / 284.5,
  month in 137 / 106 / 74 (read left to right).
- top letters stand with their tops pointing OUTWARD (read clockwise); bottom letters with their
  tops pointing INWARD, the way a coin's lower legend reads upright.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

import preview

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "date_ring")
os.makedirs(OUT, exist_ok=True)

CX, CY = 288.1, 283.9
R_TEXT = 44.7
DIVIDERS = [25, 58, 90, 122, 152.5, 179, 205, 241, 270, 299, 331, 357]
TOP_SEGS = [223.0, 255.5, 284.5]      # weekday, left -> right
BOT_SEGS = [137.0, 106.0, 74.0]       # month, left -> right
GEORGIA = r"C:\Windows\Fonts\georgia.ttf"
TIMES_BD = r"C:\Windows\Fonts\timesbd.ttf"
INK_DIM = (0xFF, 0xD8, 0xA0)
INK_IVORY = (0xFF, 0xF3, 0xD8)
SS = 6                                 # supersampling for clean rotation


def letter(ch, cap_px):
    """A glyph mask whose cap height is cap_px on screen, rendered at SS x and tightly cropped."""
    f = ImageFont.truetype(GEORGIA, int(cap_px * SS / 0.70))   # Georgia cap height ~0.70 em
    c = Image.new("L", (cap_px * SS * 3, cap_px * SS * 3), 0)
    ImageDraw.Draw(c).text((cap_px * SS, cap_px * SS * 2), ch, font=f, fill=255, anchor="ls")
    return c.crop(c.getbbox())


def place(face, ch, theta_deg, outward, cap_px, colour):
    """Paste `ch` centred on the ring at theta, rotated so its top points out (or in)."""
    t = math.radians(theta_deg)
    x, y = CX + R_TEXT * math.cos(t), CY + R_TEXT * math.sin(t)
    # PIL rotates counter-clockwise. A glyph's 'up' is screen -y; it must point along the outward
    # normal (cos t, sin t) for the top legend, or the inward one for the bottom legend.
    up = (math.cos(t), math.sin(t)) if outward else (-math.cos(t), -math.sin(t))
    cw = math.degrees(math.atan2(up[0], -up[1]))            # clockwise rotation from upright
    g = letter(ch, cap_px).rotate(-cw, resample=Image.BICUBIC, expand=True)
    g = g.resize((max(1, round(g.width / SS)), max(1, round(g.height / SS))), Image.LANCZOS)
    face.paste(Image.new("RGB", g.size, colour), (round(x - g.width / 2), round(y - g.height / 2)), g)


def day_number(face, text, ink_px):
    """Day number in the inner disc, condensed Times Bold like NixieSmall, at a chosen ink height."""
    f = ImageFont.truetype(TIMES_BD, int(ink_px * SS / 0.66))
    glyphs = []
    for ch in text:
        c = Image.new("L", (ink_px * SS * 3, ink_px * SS * 3), 0)
        ImageDraw.Draw(c).text((ink_px * SS // 2, ink_px * SS * 2), ch, font=f, fill=255, anchor="ls")
        g = c.crop(c.getbbox())
        g = g.resize((max(1, round(g.width * 0.62 / SS)), round(g.height / SS)), Image.LANCZOS)
        glyphs.append(g)
    w = sum(g.width for g in glyphs) + (len(glyphs) - 1)
    h = max(g.height for g in glyphs)
    x = round(CX - w / 2)
    for g in glyphs:
        face.paste(Image.new("RGB", g.size, INK_IVORY), (x, round(CY - h / 2) + h - g.height), g)
        x += g.width + 1
    return h


def ring_face(day_px, weekday="WED", month="SEP", day="30", cap_px=11):
    c = preview.parse_constants()
    for k in ("WEEKDAY_Y", "MONTH_Y", "DAY_Y"):
        c[k] = -500                                        # suppress the current date lines
    face = preview.render(consts=c)
    for ch, th in zip(weekday, TOP_SEGS):
        place(face, ch, th, True, cap_px, INK_DIM)
    for ch, th in zip(month, BOT_SEGS):
        place(face, ch, th, False, cap_px, INK_DIM)
    h = day_number(face, day, day_px)
    return face, h


if __name__ == "__main__":
    current = preview.render()
    a, ha = ring_face(42)
    b, hb = ring_face(52)
    panels = [("CURRENT", current), (f"RING + day {ha}px", a), (f"RING + day {hb}px", b)]
    # full faces at 2x, plus the dial region at 4x underneath
    sheet = Image.new("RGB", (3 * 640 + 4 * 16, 720 + 16 + 4 * 150 + 40), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (lab, im) in enumerate(panels):
        x = 16 + i * (640 + 16)
        d.text((x, 4), lab, fill=(255, 220, 120))
        sheet.paste(im.resize((640, 720), Image.LANCZOS), (x, 20))
        crop = im.crop((210, 215, 320, 355)).resize((440, 560), Image.LANCZOS)
        sheet.paste(crop, (x + 100, 20 + 720 + 16))
    p = os.path.join(OUT, "_compare.png")
    sheet.save(p)
    for name, im in (("ring_day42", a), ("ring_day52", b)):
        im.save(os.path.join(OUT, name + ".png"))
    print("wrote", p)
