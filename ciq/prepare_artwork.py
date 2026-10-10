"""Fit the 1024x1024 artwork to the Venu Sq 2's 320x360 screen, and derive the text coordinates.

Shipping layout: SPLIT SCALE — candidate C in artwork/zoom/_zoom_compare.png, chosen by the user
over the earlier uniform width-fit (scale 0.3365, artwork/cand_width.png; that script is in git
history), which kept the whole device on screen and left every readout small.

Why split: the device art is landscape, the screen portrait, and the dial CENTRES sit near the
art's outer edges (x 207 / 813 on the 1024 grid). Any single scale large enough for the tubes to
fill the width pushes a dial's readout off the screen. So the halves are scaled independently:

  * TOP band (tubes + manifold), scale ST — the tubes fill the full 320 px width.
  * BOTTOM band (dials + counter + gears), scale SB — the dials run off both sides, but their
    centres, and so their readouts, stay on screen.

They join at source y = SEAM, the dark gap under the manifold, with an 8 px feather.

Source clean-up before scaling: the "Made with AI" watermark is filled with PURE black (a sampled
field colour showed as a brown rectangle), and the heart-rate dial's winged pointer and boss are
inpainted out of the dial face (user request).

Outputs: artwork/cand_split.png (full colour; the input to prepare_resources.py) and the text
coordinate table for SteampunkNixieView.mc.
"""
import os

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "reference", "BrassBackground.png")
OUT = os.path.join(HERE, "artwork")
W, H = 320, 360

CX = 512            # horizontal centre of the device on the 1024 grid
SEAM = 506          # source y of the join: the dark gap between the manifold and the dial tops
ST, SB = 0.49, 0.43  # shipping scales (candidate C)
TOP_Y = 0           # screen y of the tube nipples' tips (source y 60)
OLD_SCALE = 0.3365  # the previous uniform fit; the fonts scale by ST/OLD_SCALE and SB/OLD_SCALE

# Text centre points ON THE 1024 GRID, with the band each belongs to. These are the coordinates
# that shipped under the old 0.3365 transform — including every hand nudge recorded in the view —
# mapped back to the source, so the nudges survive the change of scale.
POINTS = {
    "tube1": (282.3, 255.6, "top"), "tube2": (439.8, 255.6, "top"),
    "tube3": (579.5, 255.6, "top"), "tube4": (745.9, 255.6, "top"),
    "steps1": (445.8, 600.3, "bot"), "steps2": (505.2, 591.4, "bot"),
    "steps3": (561.7, 591.4, "bot"), "steps4": (618.1, 591.4, "bot"),
}
# The gauges are NOT placed from this table any more: the HR number and its zone band are centred
# on the HR dial by hr_gauge.py (HRG_X/HRG_Y), and the day number plus the ring weekday/month by
# make_date_ring.py (dial centre 810,658 src). The note below records how the gauges were first
# re-centred after the split-scale change.
# The gauge points above were re-centred AFTER the split-scale change, on the dial centres measured
# in the new frame (HoughCircles on cand_split.png, agreeing within 2 px with the transformed
# 1024-grid centres): HR dial (29, 275), date dial (288, 282). The heart-rate number had sat 22 px
# above centre — it was kept clear of the winged pointer, which is now removed. The HR GROUP
# (number + BPM, ink 246..302) is centred on the dial's dark face, measured as y 227..320 down the
# dial's centre column (centre 273.5) — centring the number alone left the group 11.5 px low. The
# day number is on the date dial's centre with the weekday and month at the same spacing as before.


def load_clean_source():
    """The artwork with the watermark and the heart-rate needle removed (RGB, full res)."""
    im = cv2.imread(SRC)
    im[0:63, 820:1024] = 0
    # Heart-rate pointer: bright brass inside the dark dial face. Mask by luminance, restricted to
    # the face circle (centre 207,628, r 104) so the brass ring is never touched, dilate to take
    # the boss's shadow and anti-aliased edge, then inpaint from the surrounding face.
    x0, y0, x1, y1 = 135, 660, 305, 730
    lum = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    inside = ((xx - 207) ** 2 + (yy - 628) ** 2) < 104 ** 2
    m = ((lum > 45) & inside).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    m[~inside] = 0
    mask = np.zeros(im.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = m
    im = cv2.inpaint(im, mask, 9, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))


class Layout:
    """Top band: screen = (src_x - CX)*st + 160, src_y*st + oy. The bottom band continues from
    the seam at its own scale, so the two meet exactly at SEAM."""

    def __init__(self, name, st, sb, top_y=0):
        self.name, self.st, self.sb = name, st, sb
        self.oy = top_y - 60 * st            # source y 60 = tip of the tube nipples
        self.seam_y = SEAM * st + self.oy

    def map(self, x, y, band):
        if band == "top":
            return (x - CX) * self.st + 160, y * self.st + self.oy
        return (x - CX) * self.sb + 160, (y - SEAM) * self.sb + self.seam_y

    def background(self, src):
        sw, sh = src.size
        layers = {}
        for band, s in (("bot", self.sb), ("top", self.st)):
            big = src.resize((round(sw * s), round(sh * s)), Image.LANCZOS)
            ox, oy = self.map(0, 0, band)
            layer = Image.new("RGB", (W, H), (0, 0, 0))
            layer.paste(big, (round(ox), round(oy)))
            layers[band] = layer
        # top band over the bottom: opaque above the seam, 8 px linear feather across it
        seam = round(self.seam_y)
        m = np.zeros((H, W), np.float32)
        m[:max(0, seam - 4)] = 1.0
        for i in range(8):
            r = seam - 4 + i
            if 0 <= r < H:
                m[r] = 1.0 - (i + 1) / 9
        mask = Image.fromarray((m * 255).astype(np.uint8), "L")
        return Image.composite(layers["top"], layers["bot"], mask)

    def coords(self):
        return {k: tuple(round(v) for v in self.map(x, y, b)) for k, (x, y, b) in POINTS.items()}


SHIP = Layout("split", ST, SB, TOP_Y)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    frame = SHIP.background(load_clean_source())
    p = os.path.join(OUT, "cand_split.png")
    frame.save(p)
    print(f"wrote {p}  top x{ST} bottom x{SB}  seam at screen y {SHIP.seam_y:.0f}")
    print(f"font scale vs the old fit: top x{ST / OLD_SCALE:.3f}  bottom x{SB / OLD_SCALE:.3f}")
    for k, (x, y) in SHIP.coords().items():
        print(f"  {k:8s} {x:4d}, {y:4d}")
