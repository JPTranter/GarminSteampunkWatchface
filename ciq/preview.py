"""Offline preview of the watch face — composites the face exactly as `onUpdate` draws it.

WHY: every layout tweak on this face cost a `monkeyc` build plus a simulator push. This renders the
same frame in a second: the shipping background, the custom bitmap fonts, and the halo glow, using
the SAME constants the view draws with — `TIME_X`/`TIME_Y`, `INK_*`, `GLOW_RAD*`, `WEEKDAY_Y`, ...
are parsed straight out of `source/SteampunkNixieView.mc`, so the preview cannot quietly drift from
the code. The simulator stays the source of truth (this does not reproduce Garmin's blitter
bit-for-bit); the preview answers "where does the digit land and how big is it" without a build.

Usage:
    python preview.py                      # 320x360 face, mock data, 2x PNG
    python preview.py --now                # the real current time
    python preview.py --sleep              # the low-power burn-in-safe readout
    python preview.py --out face.png --scale 3

Mock data matches the project's fixed set so renders stay comparable (time 10:09, WED 30 SEP,
8,342 steps) - except heart rate, 128 bpm by default (--hr N) so the zone gauge shows a fill
(72, the old mock value, is below zone 1 and lights nothing); the day-of-week/month names are used exactly as Gregorian.info returns them.
"""
import argparse
import datetime
import os
import re

from PIL import Image

import device_colour
import hr_gauge

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "source", "SteampunkNixieView.mc")
FONTS = os.path.join(HERE, "resources", "fonts")
# The SHIPPING bitmap (64-colour, what Rez.Drawables.Background loads). resources/images/ held a
# stale pre-fix copy with a brown watermark patch, and the preview showed that instead.
IMAGE = os.path.join(HERE, "resources", "drawables", "background.png")

W, H = 320, 360


# ---------------------------------------------------------------- the view's own constants
def parse_constants(paths=(SOURCE, os.path.join(HERE, "source", "TubeInk.mc"),
                           os.path.join(HERE, "source", "DateRing.mc"),
                           os.path.join(HERE, "source", "HrGauge.mc"),
                           os.path.join(HERE, "source", "Layout.mc"))):
    """Read every `const NAME = value;` out of the view and the generated/extra .mc files."""
    if isinstance(paths, str):
        paths = (paths,)
    src = "\n".join(open(p, encoding="utf-8").read() for p in paths)
    consts = {}
    for name, value in re.findall(r"^const\s+(\w+)\s*=\s*([^;]+);", src, re.M):
        value = value.split("//")[0].strip()
        if value.startswith("["):
            consts[name] = [int(v.strip(), 0) for v in value.strip("[]").split(",")]
        else:
            consts[name] = int(value, 0)
    return consts


# ---------------------------------------------------------------- BMFont
class Font:
    def __init__(self, name):
        self.name = name
        self.atlas = Image.open(os.path.join(FONTS, name + "_0.png")).convert("L")
        self.glyphs = {}
        for line in open(os.path.join(FONTS, name + ".fnt"), encoding="utf-8"):
            if not line.startswith("common") and not line.startswith("char "):
                continue
            kv = dict(re.findall(r"(\w+)=(-?\d+)", line))
            if line.startswith("common"):
                self.line_height = int(kv["lineHeight"])
                self.base = int(kv["base"])
            else:
                self.glyphs[int(kv["id"])] = (int(kv["x"]), int(kv["y"]), int(kv["width"]),
                                              int(kv["height"]), int(kv["xadvance"]))

    #! dc.getFontHeight(font) for a custom bitmap font is its line height.
    def height(self):
        return self.line_height

    def advance(self, text):
        return sum(self.glyphs[ord(c)][4] for c in text if ord(c) in self.glyphs)


def rgb(colour):
    """0xRRGGBB -> (r, g, b). PIL reads a bare int colour as 0xBBGGRR, which swapped red and blue
    in every earlier preview (the blue glow rendered orange, the ivory text blue)."""
    return ((colour >> 16) & 0xFF, (colour >> 8) & 0xFF, colour & 0xFF)


def draw_text(canvas, font, text, x, y_top, colour):
    """dc.drawText(x, y_top, font, text, TEXT_JUSTIFY_CENTER), blended by glyph coverage.

    Two details that cost build cycles on the device: y is the TOP of the line box (not a middle or
    a baseline), and an anti-aliased custom font's grey atlas is coverage, so the glyph must be
    alpha-composited — pasting the mask opaquely gives the hard stair-stepped edges the resource
    compiler's non-antialiased default would have produced.
    """
    left = x - font.advance(text) // 2
    for ch in text:
        g = font.glyphs.get(ord(ch))
        if g is None:
            continue
        gx, gy, gw, gh, adv = g
        if ch != " ":
            mask = font.atlas.crop((gx, gy, gx + gw, gy + gh))
            canvas.paste(Image.new("RGB", (gw, gh), rgb(colour)), (left, y_top), mask)
        left += adv


def centred(canvas, consts, font, text, x, y, colour):
    """The view's `centred()`: x,y is the glyph's centre, so shift up by half the font height."""
    draw_text(canvas, font, text, x, y - font.height() // 2, colour)


def ring(canvas, consts, font, text, x, y, radius, colour):
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if -radius < dx < radius and -radius < dy < radius:
                continue
            centred(canvas, consts, font, text, x + dx, y + dy, colour)


def glowing(canvas, consts, font, text, x, y, hot=None, halo=None):
    """Mirror of the view's glowing(): the static halo rings (outer first) under the core. The rings
    no longer pulse - the glow is a fixed bright baseline. Radius 3 is the outermost step of the
    hand-painted bloom (drawText has no alpha, so a soft falloff can only be stepped bands); a radius
    equal to the next one inward is skipped, exactly as the view skips it."""
    if halo is not None:                      # the 4 px fade, alpha-blended by the font's coverage
        centred(canvas, consts, halo, text, x, y, consts["INK_GLOW3"])
    if consts["GLOW_RAD2"] != consts["GLOW_RAD1"]:
        ring(canvas, consts, font, text, x, y, consts["GLOW_RAD2"], consts["INK_GLOW2"])
    ring(canvas, consts, font, text, x, y, consts["GLOW_RAD1"], consts["INK_GLOW1"])
    centred(canvas, consts, font, text, x, y, consts["INK_WIRE"])         # the wire: full weight
    centred(canvas, consts, hot or font, text, x, y, consts["INK_TIME"])  # its cream core, eroded


# ---------------------------------------------------------------- the frame
def belt_text(steps):
    """The view's 5-drum text: right-aligned, leading zeros blank, last five digits."""
    return (str(steps).rjust(5))[-5:]


def belt_digits(face, consts, font, frm, to, phase):
    """Mirror of SteampunkNixieView.drawSteps: each drum clipped to its window, the digit with
    its belt neighbours, and a changed digit rolled down by the same ease-out offset."""
    p, F = consts["BELT_PITCH"], consts["BELT_FRAMES"]
    off = (p * (F * F - (F - phase) ** 2)) // (F * F) if phase > 0 else 0
    nxt = lambda c: str((int(c) + 1) % 10) if c.isdigit() else " "
    prv = lambda c: str((int(c) + 9) % 10) if c.isdigit() else " "
    y = consts["STEP_Y"]
    for i in range(5):
        x0, x1 = consts["DRUM_X0"][i], consts["DRUM_X1"][i]
        y0, y1 = consts["DRUM_Y0"], consts["DRUM_Y1"]
        win = face.crop((x0, y0, x1, y1))
        layer = face.copy()
        if phase > 0 and frm[i] != to[i]:
            seq = [(nxt(to[i]), y + off - 2 * p), (to[i], y + off - p), (frm[i], y + off),
                   (prv(frm[i]), y + off + p)]
        else:
            seq = [(nxt(to[i]), y - p), (to[i], y), (prv(to[i]), y + p)]
        for ch, cy in seq:
            if ch != " ":
                centred(layer, consts, font, ch, consts["STEP_X"][i], cy, consts["INK_IVORY"])
        face.paste(layer.crop((x0, y0, x1, y1)), (x0, y0))      # the clip
        del win


def separator(canvas, consts):
    """Mirror of SteampunkNixieView.drawSeparator/litDot: two solid dots in the colour the digits
    READ as - their ring, INK_GLOW1 - not the yellow of their hot core. No glow ring."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(canvas)
    r = consts["SEP_R"]
    for dy in (-consts["SEP_DY"], consts["SEP_DY"]):
        y = consts["SEP_Y"] + dy
        d.ellipse([consts["SEP_X"] - r, y - r, consts["SEP_X"] + r, y + r],
                  fill=rgb(consts["INK_GLOW1"]))


def render(mock=True, sleep=False, consts=None, hr=None, background=None,
           belt=None):
    consts = consts or parse_constants()
    f_time, f_day = Font("NixieTime"), Font("NixieDay")
    f_hot = Font("NixieTimeHot")
    f_halo = Font("NixieTimeHalo")
    f_mid, f_step = Font("NixieMid"), Font("NixieStep")

    face = (background.copy() if background is not None
            else Image.open(IMAGE).convert("RGB"))   # background=: mockups of a changed frame
    assert face.size == (W, H), face.size

    if mock:
        hh, mm = 10, 9
        steps = "8342"
        weekday, day, month = "WED", "30", "SEP"
    else:
        now = datetime.datetime.now()
        hh, mm = now.hour, now.minute
        steps = "8342"
        weekday, day, month = now.strftime("%a").upper(), now.strftime("%d"), now.strftime("%b").upper()

    hr = str(hr if hr is not None else 128)   # 128 bpm (zone 2-3) so the gauge shows a fill
    if sleep:
        centred(face, consts, f_time, "%02d:%02d" % (hh, mm), 160, 175, consts["INK_SLEEP"])
        return face

    for i, d in enumerate("%02d%02d" % (hh, mm)):
        # The glow is painted back-to-front: far ring, near ring, then the core glyph on top.
        glowing(face, consts, f_time, d, consts["TIME_X"][i], consts["TIME_Y"], f_hot, f_halo)
    separator(face, consts)                     # the hours/minutes colon, as the view draws it

    frm, to, phase = belt if belt else (belt_text(steps), belt_text(steps), 0)
    belt_digits(face, consts, f_step, frm, to, phase)

    # the zone gauge (variant B): the dim band is in the background; light it up to the rate,
    # through the same segment rule the view uses (example zones - the watch reads the user's)
    hr_gauge.draw_lit(face, hr_gauge.fraction(int(hr), consts["HRG_FALLBACK_ZONES"]))
    centred(face, consts, f_mid, hr, consts["HRG_X"], consts["HR_Y"], consts["INK_IVORY"])
    # the date ring: the same pre-rendered patches the view blits (make_date_ring.py), at the
    # offsets in the generated DateRing.mc
    ring = os.path.join(HERE, "resources", "drawables", "ring")
    names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    face.paste(Image.open(os.path.join(ring, f"wd{names.index(weekday) + 1}.png")).convert("RGB"),
               (consts["RING_TOP_X"], consts["RING_TOP_Y"]))
    face.paste(Image.open(os.path.join(ring, f"mo{months.index(month) + 1}.png")).convert("RGB"),
               (consts["RING_BOT_X"], consts["RING_BOT_Y"]))
    centred(face, consts, f_day, day, consts["DAY_X"], consts["DAY_Y"], consts["INK_IVORY"])
    return face


DEFAULT_OUT = os.path.join(HERE, "artwork", "face_preview.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--now", action="store_true", help="real clock instead of the fixed mock time")
    ap.add_argument("--sleep", action="store_true", help="the low-power readout")
    ap.add_argument("--hr", type=int, default=None, help="heart rate to show (default 128)")
    ap.add_argument("--as-seen", action="store_true",
                    help="undo the AMOLED pre-correction: how the face looks ON the watch, for "
                         "screenshots (the shipping frame itself looks yellow-green on a monitor)")
    ap.add_argument("--anim", type=int, metavar="FRAMES", default=0,
                    help="replay the arc flicker + glow pulse: write an animated GIF and a sheet")
    args = ap.parse_args()

    consts = parse_constants()
    if args.anim:
        frames = []
        # the step belts: a rollover 8399 -> 8400 a second in, so several drums roll at once
        frm, to, phase = belt_text(8399), belt_text(8399), 0
        for n in range(args.anim):
            if phase > 0:
                phase = phase + 1 if phase < consts["BELT_FRAMES"] else 0
            if n == 10:
                frm, to, phase = to, belt_text(8400), 1
            f = render(mock=not args.now, consts=consts, hr=args.hr, belt=(frm, to, phase))
            f = device_colour.as_seen(f) if args.as_seen else f
            frames.append(f.resize((W * args.scale, H * args.scale), Image.LANCZOS))
        gif = os.path.join(HERE, "artwork", "anim_preview.gif")
        # The odometer is the only thing that animates now (the arcs and side sparks were removed), so
        # both outputs crop ITS band - the tubes above it are static. A full-face 80-frame GIF at 2x was
        # 28 MB, hence a band.
        band = [fr.crop((0, 190 * args.scale, W * args.scale, 290 * args.scale)) for fr in frames]
        band[0].save(gif, save_all=True, append_images=band[1:], duration=consts["FRAME_MS"],
                     loop=0, optimize=True)
        # contact sheet of the same band, 8 frames per row, at the requested scale
        crop = [fr.crop((0, 190 * args.scale, W * args.scale, 290 * args.scale)) for fr in frames[:24]]
        cw, ch = crop[0].size
        sheet = Image.new("RGB", (cw * 4, ch * ((len(crop) + 3) // 4)))
        for n, im in enumerate(crop):
            sheet.paste(im, ((n % 4) * cw, (n // 4) * ch))
        sheet_p = os.path.join(HERE, "artwork", "anim_sheet.png")
        sheet.save(sheet_p)
        print(f"{gif}  {len(frames)} frames @ {consts['FRAME_MS']} ms;  sheet {sheet_p}")
        raise SystemExit(0)
    face = render(mock=not args.now, sleep=args.sleep, consts=consts, hr=args.hr)
    face = device_colour.as_seen(face) if args.as_seen else face

    if args.scale > 1:
        face = face.resize((W * args.scale, H * args.scale), Image.LANCZOS)
    face.save(args.out)

    print(f"{args.out}  {face.size[0]}x{face.size[1]}")
    for name, font, y, cols in (("time", "NixieTime", consts["TIME_Y"], 4),
                                ("heart rate", "NixieMid", consts["HR_Y"], 2),
                                ("steps", "NixieStep", consts["STEP_Y"], 4),
                                ("day number", "NixieDay", consts["DAY_Y"], 2),
):
        f = Font(font)
        print(f"  {name:11s} {font:11s} ink {f.base:2d} px  centred y {y}  "
              f"box {y - f.height() // 2}..{y - f.height() // 2 + f.height()}")
