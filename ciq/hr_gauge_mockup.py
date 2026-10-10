"""Mockup: the heart-rate dial as a zone gauge - a graduated band (cold blue -> green -> orange ->
red) round the dial face, BPM label removed, the number alone on the dial centre.

DECISION SUPPORT, not shipping code. Writes artwork/hr_gauge/_compare.png: two variants
(A: full band + bright marker at the current HR; B: band lit only up to the current HR, the rest
dimmed) at three heart rates, on the approved 54 px ring-date face.

Geometry (screen, measured in the split frame): HR dial centre (29, 275), dark face y 227..320
(r ~46). The band sits at r 34..42 inside the face, clear of the number (corners at r ~27).
The dial centre is only 29 px from the screen edge, so the arc OPENS to the left (off-screen):
it runs clockwise from -125 deg (upper-left) over the top to +125 deg (lower-left), 250 deg.

Scale: each zone gets an EQUAL share of the arc (as Garmin's own zone gauges do), so the
colour band is the same for every user and can be baked into the background; only the marker
position depends on the user's zones (UserProfile.getHeartRateZones: [z1 min, z1..z5 max]).
Below zone 1 the marker rests at the start; above zone 5 max it pins at the end.
"""
import math
import os

from PIL import Image, ImageDraw

import date_ring_mockup as ring
import preview

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "hr_gauge")
os.makedirs(OUT, exist_ok=True)

HX, HY = 29.0, 275.0
R_IN, R_OUT = 34.0, 42.0
A0, A1 = -125.0, 125.0                    # degrees, 0 = 3 o'clock, clockwise (screen y down)
ZONES = [98, 117, 137, 156, 176, 195]     # example thresholds; the watch reads the user's own
# colour stops along the arc (fraction, RGB): cold blue -> green -> orange -> red
STOPS = [(0.00, (40, 100, 255)), (0.30, (40, 200, 110)), (0.62, (255, 160, 30)),
         (1.00, (235, 30, 30))]
SS = 4


def colour_at(f):
    for (f0, c0), (f1, c1) in zip(STOPS, STOPS[1:]):
        if f <= f1:
            t = (f - f0) / (f1 - f0)
            return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def hr_fraction(hr):
    """Equal arc per zone: piecewise-linear through the six thresholds."""
    if hr <= ZONES[0]:
        return 0.0
    for z in range(5):
        lo, hi = ZONES[z], ZONES[z + 1]
        if hr <= hi:
            return (z + (hr - lo) / (hi - lo)) / 5.0
    return 1.0


def band(face, lit_to=None, dim=0.28):
    """Paint the graduated band (supersampled), optionally dimming beyond fraction lit_to."""
    W, H = face.size
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    steps = 250
    for i in range(steps):
        f0, f1 = i / steps, (i + 1) / steps
        c = colour_at((f0 + f1) / 2)
        if lit_to is not None and f0 >= lit_to:
            c = tuple(round(v * dim) for v in c)
        a0 = A0 + (A1 - A0) * f0
        a1 = A0 + (A1 - A0) * f1 + 0.3
        bbox = [(HX - R_OUT) * SS, (HY - R_OUT) * SS, (HX + R_OUT) * SS, (HY + R_OUT) * SS]
        d.arc(bbox, a0, a1, fill=c + (255,), width=int((R_OUT - R_IN) * SS))
    # zone ticks: thin dark gaps at the 4 inner zone boundaries
    for z in range(1, 5):
        a = math.radians(A0 + (A1 - A0) * z / 5)
        d.line([((HX + (R_IN - 1) * math.cos(a)) * SS, (HY + (R_IN - 1) * math.sin(a)) * SS),
                ((HX + (R_OUT + 1) * math.cos(a)) * SS, (HY + (R_OUT + 1) * math.sin(a)) * SS)],
               fill=(10, 8, 6, 255), width=SS)
    small = big.resize((W, H), Image.LANCZOS)
    face.paste(small, (0, 0), small)


def marker(face, f):
    """A bright ivory pointer tick across the band at fraction f, with a dark outline."""
    a = math.radians(A0 + (A1 - A0) * f)
    W, H = face.size
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    p0 = ((HX + (R_IN - 3) * math.cos(a)) * SS, (HY + (R_IN - 3) * math.sin(a)) * SS)
    p1 = ((HX + (R_OUT + 3) * math.cos(a)) * SS, (HY + (R_OUT + 3) * math.sin(a)) * SS)
    d.line([p0, p1], fill=(0, 0, 0, 255), width=5 * SS)
    d.line([p0, p1], fill=(255, 243, 216, 255), width=3 * SS)
    small = big.resize((W, H), Image.LANCZOS)
    face.paste(small, (0, 0), small)


def face_for(hr, variant):
    c = preview.parse_constants()
    for k in ("WEEKDAY_Y", "MONTH_Y", "DAY_Y", "HR_Y", "HR_UNIT_Y"):
        c[k] = -500
    face = preview.render(consts=c)
    for ch, th in zip("WED", ring.TOP_SEGS):
        ring.place(face, ch, th, True, 11, ring.INK_DIM)
    for ch, th in zip("SEP", ring.BOT_SEGS):
        ring.place(face, ch, th, False, 11, ring.INK_DIM)
    ring.day_number(face, "30", 52)
    f = hr_fraction(hr)
    if variant == "A":
        band(face)
        marker(face, f)
    else:
        band(face, lit_to=f)
    preview.centred(face, c, preview.Font("NixieMid"), str(hr), int(HX), int(HY), c["INK_IVORY"])
    return face


if __name__ == "__main__":
    hrs = [72, 128, 168]
    pad = 14
    tile_w, tile_h = 4 * 110, 4 * 120              # the HR dial region at 4x
    sheet = Image.new("RGB", (pad + 3 * (tile_w + pad), 40 + 2 * (tile_h + 34) + 760),
                      (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    full = None
    for r, (variant, label) in enumerate((("A", "A: full band + marker"),
                                          ("B", "B: lit up to current HR"))):
        y = 10 + r * (tile_h + 34)
        d.text((pad, y), label, fill=(255, 220, 120))
        for i, hr in enumerate(hrs):
            fc = face_for(hr, variant)
            if variant == "A" and hr == 128:
                full = fc
            fc.save(os.path.join(OUT, f"{variant}_{hr}.png"))
            crop = fc.crop((0, 215, 110, 335)).resize((tile_w, tile_h), Image.LANCZOS)
            x = pad + i * (tile_w + pad)
            sheet.paste(crop, (x, y + 18))
            d.text((x + 4, y + 22), f"{hr} bpm  (zone fraction {hr_fraction(hr):.2f})",
                   fill=(255, 255, 255))
    yb = 10 + 2 * (tile_h + 34)
    d.text((pad, yb), "A at 128 bpm, full face (2x)", fill=(255, 220, 120))
    sheet.paste(full.resize((640, 720), Image.LANCZOS), (pad, yb + 18))
    p = os.path.join(OUT, "_compare.png")
    sheet.save(p)
    print("wrote", p)
