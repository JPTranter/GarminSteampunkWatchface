"""Heart-rate zone gauge, variant B (user-approved: artwork/hr_gauge/_compare.png, row B).

A graduated band round the HR dial face - cold blue -> green -> orange -> red - that is LIT up
to the current heart rate and dim beyond it. Each of the user's five zones gets an equal share
of the arc (as Garmin's own zone gauges do); the zone thresholds come from
UserProfile.getHeartRateZones on the watch, so only the fill position depends on the user.

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

HERE = os.path.dirname(os.path.abspath(__file__))
GEN_MC = os.path.join(HERE, "source", "HrGauge.mc")

HX, HY = 29, 274
R_IN, R_OUT = 34, 42
A0, A1 = -125.0, 125.0          # screen degrees, clockwise
SEGS = 50                       # lit segments: 5 deg each, 10 per zone
GAP_DEG = 1.0                   # trimmed off each side of a zone boundary when lit
DIM = 0.28                      # unlit band brightness (of the corrected colour)
FALLBACK_ZONES = [98, 117, 137, 156, 176, 195]   # only if the watch returns no zones
STOPS = [(0.00, (40, 100, 255)), (0.30, (40, 200, 110)), (0.62, (255, 160, 30)),
         (1.00, (235, 30, 30))]
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
    for z in range(1, 5):
        a = math.radians(A0 + (A1 - A0) * z / 5)
        d.line([((HX + (R_IN - 1) * math.cos(a)) * SS, (HY + (R_IN - 1) * math.sin(a)) * SS),
                ((HX + (R_OUT + 1) * math.cos(a)) * SS, (HY + (R_OUT + 1) * math.sin(a)) * SS)],
               fill=(10, 8, 6, 255), width=SS)
    small = big.resize((W, H), Image.LANCZOS)
    out = img.copy()
    out.paste(small, (0, 0), small)
    return out


def fraction(hr, zones):
    """0..1 along the arc: equal share per zone, piecewise-linear through the six thresholds."""
    if hr is None or hr <= zones[0]:
        return 0.0
    for z in range(5):
        lo, hi = zones[z], zones[z + 1]
        if hr <= hi:
            return (z + (hr - lo) / (hi - lo)) / 5.0
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
        if i % (SEGS // 5) == 0 and i > 0:
            s0 += GAP_DEG
        if (i + 1) % (SEGS // 5) == 0 and i < SEGS - 1 and s1 == A0 + span * (i + 1) / SEGS:
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
const HRG_GAP = {GAP_DEG:g};
const HRG_FALLBACK_ZONES = [{", ".join(str(z) for z in FALLBACK_ZONES)}];
// lit colour per segment, already AMOLED-corrected (device_colour.py)
const HRG_COLOURS = [{table}];
""")
    print(f"wrote {GEN_MC}  ({SEGS} segments)")


if __name__ == "__main__":
    main()
