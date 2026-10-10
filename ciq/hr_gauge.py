"""Heart-rate zone gauge, variant B (user-approved: artwork/hr_gauge/_compare.png, row B).

A graduated band round the HR dial face - cold blue -> green -> orange -> red - that is LIT up
to the current heart rate and dim beyond it. The arc has SEVEN equal parts:
    40..60 bpm cold blue | 60 bpm..zone 1 green (a normal resting rate) | zones 1..5
so GREEN STARTS AT 60 BPM for everyone (user request), and the five zones run green -> yellow ->
orange -> red above it (as Garmin's own zone gauges do). The first version had only the five
zones, so a resting rate - below zone 1 - lit nothing, and the gauge looked broken on the watch.
Zone thresholds come from UserProfile.getHeartRateZones; 40 and 60 bpm are fixed.

Split between build time and run time, so the watch draws as little as possible:
  * bake(img)  - paints the DIM band and the four zone gaps into the background (called by
                 prepare_resources.py AFTER the AMOLED correction, so it is never corrected twice);
  * main()     - writes source/HrGauge.mc: the geometry and a SEGS-entry colour table for the lit
                 segments. The table is put through device_colour.correct() too, so the lit
                 colours land on the panel the same way as the baked dim ones.

Geometry (screen): dial centre (29, 274) - the dark face spans y 227..320 down the dial's
centre column - band r 34..42, inside the face and clear of a 3-digit number (corners r ~27).
The centre is 29 px from the screen edge, so the arc opens LEFT (off-screen): it runs clockwise
from -125 deg (upper-left) over the top to +125 deg (lower-left), in screen degrees (0 = 3
o'clock, clockwise). Garmin's drawArc counts counter-clockwise, so HrGauge.mc stores both.
"""
import math
import os

from PIL import Image, ImageDraw

import device_colour
import prepare_artwork

HERE = os.path.dirname(os.path.abspath(__file__))
GEN_MC = os.path.join(HERE, "source", "HrGauge.mc")

_G = prepare_artwork.geometry()          # follows the layout's zoom
HX, HY = round(_G["HR_CENTRE"][0]), round(_G["HR_CENTRE"][1])
R_IN, R_OUT = round(_G["HR_BAND"][0]), round(_G["HR_BAND"][1])
A0, A1 = -125.0, 125.0          # screen degrees, clockwise
PARTS = 7                       # 40-60 | 60-zone 1 | zones 1..5, equal shares of the arc
SEGS = 70                       # lit segments: ~3.6 deg each, 10 per part
FLOOR_BPM = 40                  # the start of the arc
GREEN_BPM = 60                  # where green begins (user request)
GAP_DEG = 1.0                   # trimmed off each side of a zone boundary when lit
DIM = 0.28                      # unlit band brightness (of the corrected colour)
FALLBACK_ZONES = [98, 117, 137, 156, 176, 195]   # only if the watch returns no zones
# colour stops along the arc (fractions of 7 parts): deep -> light cold blue below 60 bpm, a step
# to GREEN exactly at 60, then green -> yellow -> orange -> red through the zones
STOPS = [(0.00, (30, 55, 190)), (1 / 7 - 0.001, (50, 120, 255)), (1 / 7, (40, 200, 110)),
         (2 / 7, (90, 210, 80)), (3 / 7, (220, 215, 40)), (4 / 7, (255, 165, 30)),
         (5 / 7, (250, 100, 30)), (1.00, (235, 30, 30))]
SS = 4


def raw_colour(f):
    for (f0, c0), (f1, c1) in zip(STOPS, STOPS[1:]):
        if f <= f1:
            t = (f - f0) / (f1 - f0)
            return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def corrected(colours):
    """Run a list of RGB tuples through the AMOLED pre-correction (as one image row)."""
    row = Image.new("RGB", (len(colours), 1))
    row.putdata(colours)
    out = device_colour.correct(row)
    return [out.getpixel((i, 0)) for i in range(out.width)]


def seg_colours():
    return corrected([raw_colour((i + 0.5) / SEGS) for i in range(SEGS)])


def bake(img):
    """Paint the dim band + zone gaps onto an (already corrected) background. Returns a copy."""
    W, H = img.size
    fine = 250
    cols = corrected([raw_colour((i + 0.5) / fine) for i in range(fine)])
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    box = [(HX - R_OUT) * SS, (HY - R_OUT) * SS, (HX + R_OUT) * SS, (HY + R_OUT) * SS]
    for i, c in enumerate(cols):
        a0 = A0 + (A1 - A0) * i / fine
        a1 = A0 + (A1 - A0) * (i + 1) / fine + 0.3
        d.arc(box, a0, a1, fill=tuple(round(v * DIM) for v in c) + (255,),
              width=(R_OUT - R_IN) * SS)
    for z in range(1, PARTS):
        a = math.radians(A0 + (A1 - A0) * z / PARTS)
        d.line([((HX + (R_IN - 1) * math.cos(a)) * SS, (HY + (R_IN - 1) * math.sin(a)) * SS),
                ((HX + (R_OUT + 1) * math.cos(a)) * SS, (HY + (R_OUT + 1) * math.sin(a)) * SS)],
               fill=(10, 8, 6, 255), width=SS)
    small = big.resize((W, H), Image.LANCZOS)
    out = img.copy()
    out.paste(small, (0, 0), small)
    return out


def fraction(hr, zones):
    """0..1 along the arc: seven equal parts, piecewise-linear through 40, 60 and the six zone
    thresholds (zone 1 min is held at least 5 bpm above 60). The view applies the same rule."""
    pts = [FLOOR_BPM, GREEN_BPM, max(zones[0], GREEN_BPM + 5)] + list(zones[1:])
    if hr is None or hr <= pts[0]:
        return 0.0
    for z in range(PARTS):
        lo, hi = pts[z], pts[z + 1]
        if hr <= hi:
            return (z + (hr - lo) / (hi - lo)) / PARTS
    return 1.0


def lit_segments(frac):
    """(screen_start_deg, screen_end_deg, colour_index) for every lit piece - the same rule the
    watch applies, so the preview draws exactly what the view draws."""
    out = []
    span = A1 - A0
    end = A0 + span * frac
    for i in range(SEGS):
        s0 = A0 + span * i / SEGS
        s1 = A0 + span * (i + 1) / SEGS
        if s0 >= end:
            break
        s1 = min(s1, end)
        if i % (SEGS // PARTS) == 0 and i > 0:
            s0 += GAP_DEG
        if (i + 1) % (SEGS // PARTS) == 0 and i < SEGS - 1 and s1 == A0 + span * (i + 1) / SEGS:
            s1 -= GAP_DEG
        if s1 > s0:
            out.append((s0, s1, i))
    return out


def draw_lit(img, frac):
    """Preview mirror of the view's live drawing (drawArc, pen R_OUT-R_IN, anti-aliased)."""
    W, H = img.size
    cols = seg_colours()
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    r = (R_IN + R_OUT) / 2
    w = R_OUT - R_IN
    box = [(HX - r - w / 2) * SS, (HY - r - w / 2) * SS, (HX + r + w / 2) * SS, (HY + r + w / 2) * SS]
    for s0, s1, i in lit_segments(frac):
        d.arc(box, s0, s1, fill=cols[i] + (255,), width=w * SS)
    small = big.resize((W, H), Image.LANCZOS)
    img.paste(small, (0, 0), small)


def main():
    cols = seg_colours()
    table = ", ".join(f"0x{r:02X}{g:02X}{b:02X}" for r, g, b in cols)
    with open(GEN_MC, "w", newline="\n") as f:
        f.write(f"""// GENERATED by ciq/hr_gauge.py - do not edit; re-run `python make.py assets`.
import Toybox.Lang;

// Heart-rate zone gauge (variant B): the dim band is baked into the background; the view draws
// the lit part live as up to HRG_SEGS arcs. Screen degrees run clockwise from 3 o'clock;
// Garmin's drawArc counts counter-clockwise, so the view negates them.
const HRG_X = {HX};
const HRG_Y = {HY};
const HRG_R = {(R_IN + R_OUT) // 2};
const HRG_PEN = {R_OUT - R_IN};
const HRG_A0 = {int(A0)};
const HRG_A1 = {int(A1)};
const HRG_SEGS = {SEGS};
const HRG_PARTS = {PARTS};       // 40-60 | 60-zone 1 | zones 1..5
const HRG_FLOOR = {FLOOR_BPM};
const HRG_GREEN = {GREEN_BPM};
const HRG_GAP = {GAP_DEG:g};
const HRG_FALLBACK_ZONES = [{", ".join(str(z) for z in FALLBACK_ZONES)}];
// lit colour per segment, already AMOLED-corrected (device_colour.py)
const HRG_COLOURS = [{table}];
""")
    print(f"wrote {GEN_MC}  ({SEGS} segments)")


if __name__ == "__main__":
    main()
