"""Mockup: the blue side sparks, ANIMATED - the effect rendered offline before any device code.

DECISION SUPPORT, not shipping code. The user's reference (the AI face render) carries blue
star-crackle at the outer sides of tubes 1 and 4 at mid-tube height, and asks for the face's own
side sparks to be animated. On this face those sparks are BAKED into the artwork (measured: blue
clusters at screen x 0..18 y 106..147 and x 304..319 y 111..148). This renders the live version -
the same LCG, state machine and pass structure `source/Discharge.mc` uses, so porting is mechanical -
as a GIF (the wrist-raise loop) plus a contact sheet of one burst's life.

Palette is the shipped bolt palette (measured off the reference's sparks: core (149,191,233),
tips (11,20,37) - ARC_SHEATH 0x7AB6F7 and ARC_BLOOM 0x2F6EA8 sit right there).

Writes artwork/spark_anim.gif (tube band, 2x) and artwork/spark_sheet.png (8 frames of one burst).
"""
import os

import numpy as np
from PIL import Image, ImageDraw

import device_colour
import preview

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork")

# ---------------------------------------------------------------- tuning (the device's numbers)
FRAME_MS = 100
# Emitter origins: the bright core of the spark CURRENTLY baked in the artwork (user: "the emitter on
# the side where the current blue spark emitter is"). Measured off the shipping background - the
# top-15 % blue-excess centroid in each side margin is (10, 138) left and (306, 135) right; the
# surrounding baked glow spans y 6..238 (left) / 7..148 (right), i.e. up the tubes' own sides.
SPARK_X = [10, 306]
SPARK_Y = [138, 135]
SPARK_UP = -90.0                 # the filaments FLY UP from the emitter (screen degrees)
SPARK_BIAS = [-13.0, 13.0]       # each emitter tilts slightly outward, away from its tube
SPARK_LINES = 10                 # radiating filaments per burst
SPARK_SPREAD = 32.0              # half-angle of the fan, degrees, about straight up
SPARK_LEN = (22, 70)             # filament length, screen px - reaches up beside the tube
SPARK_ON_MIN, SPARK_ON_MAX = 1, 4
SPARK_OFF_MIN, SPARK_OFF_MAX = 5, 22
SPARK_BLOOM = 0x2F6EA8
SPARK_SHEATH = 0x7AB6F7
SPARK_CORE = 0xEAF6FF


class Sparks:
    """Two side emitters, sparks flying UP beside the tubes. Same 31-bit LCG and on/off state
    machine as Discharge, one extra axis: while a burst is ON it is re-jittered every frame, which
    is what makes it crackle."""

    def __init__(self):
        self.seed = 20261010
        n = len(SPARK_X)
        self.timer = [self.between(1, SPARK_OFF_MAX) for _ in range(n)]
        self.on = [False] * n

    def next(self):
        self.seed = (self.seed * 0x41C64E6D + 12345) & 0x7FFFFFFF
        return self.seed >> 16

    def between(self, lo, hi):
        return lo + self.next() % (hi - lo + 1)

    def step(self):
        for k in range(len(self.timer)):
            self.timer[k] -= 1
            if self.timer[k] <= 0:
                self.on[k] = not self.on[k]
                self.timer[k] = (self.between(SPARK_ON_MIN, SPARK_ON_MAX) if self.on[k]
                                 else self.between(SPARK_OFF_MIN, SPARK_OFF_MAX))

    def filaments(self, k):
        """One frame's filaments for emitter k: a fan about straight up, each with a kink so the
        crackle reads as electric rather than as a fan of straight lines."""
        import math
        ox, oy = SPARK_X[k], SPARK_Y[k]
        out = []
        for _ in range(SPARK_LINES):
            a = math.radians(SPARK_UP + SPARK_BIAS[k]
                             + (self.between(0, 2000) - 1000) * SPARK_SPREAD / 1000.0)
            ln = float(self.between(*SPARK_LEN))
            dx, dy = math.cos(a), math.sin(a)
            # bend across the filament (perpendicular), so the path zigzags like a discharge
            px, py = -dy, dx
            kink = self.between(-5, 5)
            mx = ox + dx * ln * 0.55 + px * kink
            my = oy + dy * ln * 0.55 + py * kink
            tx = ox + dx * ln + px * kink + (self.between(-4, 4))
            ty = oy + dy * ln + py * kink
            out.append([(ox, oy), (mx, my), (tx, ty)])
        return out

    def draw(self, canvas):
        d = ImageDraw.Draw(canvas)
        for k in range(len(self.on)):
            if not self.on[k]:
                continue
            fils = self.filaments(k)
            for pen, ink in ((3, SPARK_BLOOM), (2, SPARK_SHEATH), (1, SPARK_CORE)):
                col = preview.rgb(ink)
                for f in fils:
                    d.line(f, fill=col, width=pen, joint="curve")
            # a hot head where the burst leaves the tube: bright, small
            r = 2
            d.ellipse([SPARK_X[k] - r, SPARK_Y[k] - r, SPARK_X[k] + r, SPARK_Y[k] + r],
                      fill=preview.rgb(SPARK_CORE))
            r = 4
            d.ellipse([SPARK_X[k] - r, SPARK_Y[k] - r, SPARK_X[k] + r, SPARK_Y[k] + r],
                      outline=preview.rgb(SPARK_BLOOM))


if __name__ == "__main__":
    consts = preview.parse_constants()
    bg = Image.open(os.path.join(HERE, "resources", "drawables", "background.png")).convert("RGB")
    sp = Sparks()
    frames = []
    for n in range(32):
        sp.step()
        face = preview.render(consts=consts, hr=128, background=bg)
        sp.draw(face)
        face = device_colour.as_seen(face)
        frames.append(face)

    band = [f.crop((0, 0, 320, 185)).resize((640, 370), Image.LANCZOS) for f in frames]
    gif = os.path.join(OUT, "spark_anim.gif")
    band[0].save(gif, save_all=True, append_images=band[1:], duration=FRAME_MS, loop=0, optimize=True)

    # contact sheet: one burst's life (frames 0..15) at 1x, so the flicker reads
    cw, ch = 320, 185
    sheet = Image.new("RGB", (cw * 4, ch * 4), (20, 18, 16))
    for i in range(16):
        sheet.paste(frames[i].crop((0, 0, cw, ch)), ((i % 4) * cw, (i // 4) * ch))
    sheet = sheet.resize((cw * 4 * 2, ch * 4 * 2), Image.LANCZOS)
    sheet_p = os.path.join(OUT, "spark_sheet.png")
    sheet.save(sheet_p)
    print(f"{gif}  {len(frames)} frames @ {FRAME_MS} ms;  sheet {sheet_p}")
    print("emitter origins (screen):", list(zip(SPARK_X, SPARK_Y)))
