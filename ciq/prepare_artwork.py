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
# Shipping scales. Candidate C was 0.49 / 0.43 with the tube tips on the top edge; the user then
# asked for 5 % less zoom so more of the dials show and the tubes get some room: x0.95, and the
# tips 6 px down. EVERY on-screen position below is derived from these three numbers (see
# geometry() and the generated source/Layout.mc), so a zoom change is a one-line edit here.
ST, SB = 0.49 * 0.95, 0.43 * 0.95
TOP_Y = 6           # screen y of the tube nipples' tips (source y 60)
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
    return glass_tubes(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))


# ---- clear-glass tube envelopes (user-approved "D"; matched to a local-only reference image)
# The AI art tints the whole envelope gold - the glass walls measure saturation ~120/255 - so the
# tubes read as polished brass. Matched to the user's reference render: luminance kept, chroma
# replaced by a cool blue cast, mid-tones pushed down (clear, dark interior), a blue haze where
# the digit lights the glass, and additive white-blue light - a main specular streak, a faint
# opposite one, a rim on both walls and a hotspot under the dome. Acts only inside per-tube
# rectangles on the 1024 grid (walls measured on tube 2: +-64.5 src), down to just above the
# brass collars, so the collars, manifold and dials are untouched.
TUBE_X_SRC = [282.3, 439.8, 579.5, 745.9]
# The haze the digit throws into the glass, and the specular streak. Both follow the discharge's
# colour: the tubes lit BLUE while the digits were blue (the tube_colour target set), so these
# move together with ciq/source/TubeInk.mc - a warm digit inside cool glass clashes visibly.
GLASS_HAZE_RGB = (0.62, 0.26, 0.06)
GLASS_SPEC_RGB = (1.0, 0.94, 0.86)
# The anode grid: real nixie tubes show a hexagonal metal mesh in front of the cathode, and the
# user's reference photo reads as much by its honeycomb as by its colour. 0 = off. Visibility
# follows the digit's own haze (MESH_GAIN), so the mesh lights up with the glow instead of being a
# uniform printed texture.
MESH_ALPHA = 0.55
MESH_RGB = (1.0, 0.72, 0.42)
MESH_R_SRC = 5.35                # hexagon circumradius on the 1024 grid (~14 cells across a tube)
MESH_W_SRC = 0.6                 # wire width, source px (drawn supersampled, see _hex_mesh)
MESH_SS = 6                      # supersampling factor for the mesh mask
MESH_GAIN = 1.6                  # how strongly the local haze brightens the mesh
MESH_BASE = 0.10                 # how visible the mesh is away from the glow
# The wires can be drawn either as light added to the glass (glow, the reference's own look on its
# bright glass) or as an OCCLUDER that darkens the glass behind them. Darkening is what buys digit
# contrast on our near-black glass, so it is the default; MESH_RGB is unused in that mode.
MESH_DARKEN = 1.0
# How much the tube's interior glass is LIT (0 = the current near-black glass). The reference
# photo's tubes are bright amber, interior luminance ~0.33 against a 0.89 digit - which is what
# actually makes that picture read as it does, far more than the mesh.
TUBE_LIFT = 0.0
TUBE_LIFT_RGB = (1.0, 0.62, 0.30)
TUBE_HALF_W_SRC = 72            # +-64.5 walls + edge anti-aliasing
TUBE_WALL_SRC = 64.5
TUBE_Y0_SRC, TUBE_Y1_SRC = 55, 335    # nipple tip .. just above the collar
TUBE_DOME_Y_SRC = 124
TUBE_FEATHER = 8


def _tube_mask(w, h):
    yy = np.arange(h, dtype=np.float32)[:, None]
    xx = np.arange(w, dtype=np.float32)[None, :]
    vy = (np.clip((TUBE_Y1_SRC - yy) / TUBE_FEATHER, 0, 1)
          * np.clip((yy - TUBE_Y0_SRC + TUBE_FEATHER) / TUBE_FEATHER, 0, 1))
    m = np.zeros((h, w), np.float32)
    for cx in TUBE_X_SRC:
        m = np.maximum(m, np.clip((TUBE_HALF_W_SRC - np.abs(xx - cx)) / 4, 0, 1) * vy)
    return m


def _hex_mesh(w, h):
    """An alpha mask of a flat-top honeycomb (the nixie anode grid), or None when MESH_ALPHA is 0.

    Drawn supersampled (MESH_SS) and downsampled, because a mesh fine enough to read as the
    reference photograph's texture is 1-2 source px per wire - drawn at 1:1 it either vanishes or
    turns into stair-steps. Only the columns that can land inside a tube are visited.
    """
    if MESH_ALPHA <= 0:
        return None
    import math

    from PIL import ImageDraw
    ss = MESH_SS
    W, H = w * ss, h * ss
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    r = MESH_R_SRC * ss
    dy = math.sqrt(3.0) * r
    wdt = max(1, round(MESH_W_SRC * ss))
    for col in range(-2, int(W / (1.5 * r)) + 2):
        cx = 1.5 * r * col
        # skip columns that cannot reach any tube (the mask is only used inside the tubes)
        if not any(abs(cx / ss - t) < TUBE_HALF_W_SRC + 2 * MESH_R_SRC for t in TUBE_X_SRC):
            continue
        for row in range(-2, int(H / dy) + 2):
            cy = dy * (row + 0.5 * (col % 2))
            pts = [(cx + r * math.cos(math.radians(60 * k)),
                    cy + r * math.sin(math.radians(60 * k))) for k in range(6)]
            for k in range(6):
                d.line([pts[k], pts[(k + 1) % 6]], fill=255, width=wdt)
    mask = mask.resize((w, h), Image.LANCZOS)
    return np.asarray(mask, np.float32) / 255.0


def glass_tubes(src):
    a = np.asarray(src, np.float32) / 255.0
    h, w = a.shape[:2]
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    base = np.power(np.clip(lum * np.array([0.78, 0.95, 1.22], np.float32), 0, 1), 1.35)
    yy = np.arange(h, dtype=np.float32)[:, None]
    xx = np.arange(w, dtype=np.float32)[None, :]
    spec = np.zeros((h, w), np.float32)
    haze = np.zeros((h, w), np.float32)
    body = (np.clip((yy - TUBE_DOME_Y_SRC) / 30, 0, 1)
            * np.clip((TUBE_Y1_SRC - 12 - yy) / 40, 0, 1))

    def g(x0, sx):
        return np.exp(-((xx - x0) ** 2) / (2 * sx * sx))
    for cx in TUBE_X_SRC:
        spec += 0.62 * g(cx - 0.58 * TUBE_WALL_SRC, 4.5) * body                  # main streak
        spec += 0.22 * g(cx + 0.62 * TUBE_WALL_SRC, 3.0) * body                  # faint opposite
        spec += 0.40 * (g(cx - 0.97 * TUBE_WALL_SRC, 2.2)
                        + g(cx + 0.97 * TUBE_WALL_SRC, 2.2)) * body              # rims
        spec += 0.75 * np.exp(-(((xx - cx) / 12) ** 2
                                + ((yy - (TUBE_DOME_Y_SRC + 8)) / 7) ** 2))      # dome hotspot
        haze += 0.30 * np.exp(-(((xx - cx) / 48) ** 2 + ((yy - 255) / 85) ** 2))
    m = _tube_mask(w, h)
    out = base + (haze * m)[..., None] * np.array(GLASS_HAZE_RGB, np.float32)
    if TUBE_LIFT > 0:
        out = np.clip(out + (body * m * TUBE_LIFT)[..., None] * np.array(TUBE_LIFT_RGB, np.float32),
                      0, 1)
    mesh = _hex_mesh(w, h)
    if mesh is not None:
        gain = MESH_BASE + MESH_GAIN * np.clip(haze * 2.4, 0, 1)
        wires = mesh * m * gain * MESH_ALPHA           # never shadow `a` (the source image)
        if MESH_DARKEN > 0:
            out = out * (1.0 - np.clip(wires * MESH_DARKEN, 0, 1))[..., None]   # wires occlude
        else:
            out = np.clip(out + wires[..., None] * np.array(MESH_RGB, np.float32), 0, 1)
    light = (np.clip(spec, 0, 1) * m)[..., None] * np.array(GLASS_SPEC_RGB, np.float32)
    out = 1 - (1 - np.clip(out, 0, 1)) * (1 - light)                             # screen blend
    res = a * (1 - m[..., None]) + out * m[..., None]
    return Image.fromarray((np.clip(res, 0, 1) * 255).round().astype(np.uint8), "RGB")


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

# Points MEASURED on the layout-C screen (0.49 / 0.43, tips at y 0), converted once to the 1024
# grid so they follow any later zoom. Measured: the tube-tip knobs the arcs jump between, the
# dark band above the domes the arcs stay inside, and the HR dial face (centre and the gauge band
# radii). The date dial centre and ring radius were measured on the source directly.
_C = Layout("C", 0.49, 0.43, 0)


def _src_from_screen(sx, sy, band, lay=SHIP):
    """Inverse of Layout.map for a point measured ON THE SHIPPING FRAME. `_unmap` below inverts
    layout C instead - right for the constants that were measured there, wrong (by the 0.95 zoom)
    for anything read off the current screen."""
    if band == "top":
        return (sx - 160) / lay.st + CX, (sy - lay.oy) / lay.st
    return (sx - 160) / lay.sb + CX, (sy - lay.seam_y) / lay.sb + SEAM


def _unmap(sx, sy, band, lay=_C):
    if band == "top":
        return (sx - 160) / lay.st + CX, (sy - lay.oy) / lay.st
    return (sx - 160) / lay.sb + CX, (sy - lay.seam_y) / lay.sb + SEAM


ARC_A_SRC = [_unmap(x, y, "top") for x, y in ((54, 7), (129, 7), (200, 7), (43, 7), (275, 7))]
ARC_B_SRC = [_unmap(x, y, "top") for x, y in ((119, 7), (189, 7), (264, 7), (0, 15), (319, 15))]
ARC_B_EDGE = [None, None, None, 0, 319]           # channels 3, 4 end ON the screen edge
ARC_Y_SRC = (_unmap(0, 1, "top")[1], _unmap(0, 21, "top")[1])
HR_DIAL_SRC = _unmap(29, 274, "bot")              # HR dial face centre
HR_BAND_SRC = (34 / 0.43, 42 / 0.43)              # gauge band radii, in source px
DATE_DIAL_SRC = (810, 658)                        # date dial centre (polar-unwrap fit)
# The step counter's FIVE drum windows (the face used to fill only the right four, so 12,345
# showed as 2345). Measured on the 0.4655 / 0.4085 frame: dividers at screen x 99 / 122 / 144 /
# 167 / 190 / 214, clear window y 229..267 (frame at 222 and 268), converted to the 1024 grid.
DRUM_DIV_SRC = [362.67, 418.98, 472.83, 529.14, 585.44, 644.19]
DRUM_Y_SRC = (543.67, 636.69)
BELT_PITCH_SRC = 32 / 0.4085     # digit spacing on the belt. Was 30 px, which left only ~2 px of
                                 # clear space between the 28 px digits and showed a fat sliver of the
                                 # next/previous numeral at the window's edges; the user asked for at
                                 # least one more px of separation, so 32 px (a 4 px gap).
RING_R_SRC = 104                                  # ring band centre radius
RING_CAP_SRC = 11 / 0.43                          # ring letter cap height, in source px


def geometry(lay=SHIP):
    """Every derived on-screen position/size, for the generators and Layout.mc."""
    g = {}
    c = {k: lay.map(x, y, b) for k, (x, y, b) in POINTS.items()}
    g["TIME_X"] = [round(c[f"tube{i}"][0]) for i in range(1, 5)]
    g["TIME_Y"] = round(c["tube1"][1])
    dx = [lay.map(x, 600, "bot")[0] for x in DRUM_DIV_SRC]
    dy = [lay.map(512, y, "bot")[1] for y in DRUM_Y_SRC]
    g["DRUM_X0"] = [round(x) + 1 for x in dx[:-1]]          # clear interior, inside the dividers
    g["DRUM_X1"] = [round(x) for x in dx[1:]]
    g["DRUM_Y0"], g["DRUM_Y1"] = round(dy[0]), round(dy[1])
    g["STEP_X"] = [round((a + b) / 2) for a, b in zip(dx[:-1], dx[1:])]
    g["STEP_Y"] = round((dy[0] + dy[1]) / 2)
    g["BELT_PITCH"] = round(BELT_PITCH_SRC * lay.sb)
    ax = [lay.map(x, y, "top") for x, y in ARC_A_SRC]
    bx = [lay.map(x, y, "top") for x, y in ARC_B_SRC]
    g["ARC_AX"] = [round(p[0]) for p in ax]
    g["ARC_AY"] = [round(p[1]) for p in ax]
    g["ARC_BX"] = [e if e is not None else round(p[0]) for p, e in zip(bx, ARC_B_EDGE)]
    g["ARC_BY"] = [round(p[1]) for p in bx]
    g["ARC_Y_MIN"] = max(0, round(ARC_Y_SRC[0] * lay.st + lay.oy))
    g["ARC_Y_MAX"] = round(ARC_Y_SRC[1] * lay.st + lay.oy)
    hx, hy = lay.map(*HR_DIAL_SRC, "bot")
    g["HR_CENTRE"] = (hx, hy)
    g["HR_BAND"] = (HR_BAND_SRC[0] * lay.sb, HR_BAND_SRC[1] * lay.sb)
    g["DATE_CENTRE"] = lay.map(*DATE_DIAL_SRC, "bot")
    g["RING_R"] = RING_R_SRC * lay.sb
    g["RING_CAP"] = RING_CAP_SRC * lay.sb
    g["TOP_K"] = lay.st / 0.49          # font scale vs the layout the font sizes were tuned on
    g["BOT_K"] = lay.sb / 0.43
    # Hours/minutes separator: the colon sits in the tube 2 / tube 3 gap (the hour|minute
    # boundary), exactly midway between their digit centres, at digit height.
    g["SEP_X"] = (g["TIME_X"][1] + g["TIME_X"][2]) / 2.0
    g["SEP_Y"] = g["TIME_Y"]
    g["SEP_DY"] = 7
    g["SEP_R"] = 2
    return g


def write_layout_mc(g, path=os.path.join(HERE, "source", "Layout.mc")):
    def lst(v):
        return "[" + ", ".join(str(x) for x in v) + "]"
    hx, hy = g["HR_CENTRE"]
    dx, dy = g["DATE_CENTRE"]
    with open(path, "w", newline="\n") as f:
        f.write(f"""// GENERATED by ciq/prepare_artwork.py from ST={ST:.4f} SB={SB:.4f} TOP_Y={TOP_Y} -
// do not edit; change the layout there and run `python make.py assets`.
import Toybox.Lang;

// Tube digit centres (the drawers centre each glyph on these).
const TIME_X = {lst(g["TIME_X"])};
const TIME_Y = {g["TIME_Y"]};

// The five step drums: digit centres, each window's clear interior (the belt is clipped to it),
// and the belt's digit spacing.
const STEP_X = {lst(g["STEP_X"])};
const STEP_Y = {g["STEP_Y"]};
const DRUM_X0 = {lst(g["DRUM_X0"])};
const DRUM_X1 = {lst(g["DRUM_X1"])};
const DRUM_Y0 = {g["DRUM_Y0"]};
const DRUM_Y1 = {g["DRUM_Y1"]};
const BELT_PITCH = {g["BELT_PITCH"]};

// The heart-rate number sits on the HR dial's centre, the day number on the date dial's centre.
// Both fonts put their ink centre 0.5 px above the y passed to centred(), hence the +0.5.
const HR_Y = {round(hy + 0.5)};
const DAY_X = {round(dx)};
const DAY_Y = {round(dy + 0.5)};

// The hours/minutes separator (two lit dots in the tube 2 / tube 3 gap).
const SEP_X = {round(g["SEP_X"])};
const SEP_Y = {g["SEP_Y"]};
const SEP_DY = {g["SEP_DY"]};
const SEP_R = {g["SEP_R"]};

// Arc channels (Discharge.mc): tube-tip knobs, and the dark band the bolts must stay inside.
const ARC_AX = {lst(g["ARC_AX"])};
const ARC_AY = {lst(g["ARC_AY"])};
const ARC_BX = {lst(g["ARC_BX"])};
const ARC_BY = {lst(g["ARC_BY"])};
const ARC_Y_MIN = {g["ARC_Y_MIN"]};
const ARC_Y_MAX = {g["ARC_Y_MAX"]};
""")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    frame = SHIP.background(load_clean_source())
    p = os.path.join(OUT, "cand_split.png")
    frame.save(p)
    print(f"wrote {p}  top x{ST} bottom x{SB}  seam at screen y {SHIP.seam_y:.0f}")
    g = geometry()
    write_layout_mc(g)
    print(f"wrote source/Layout.mc  time x {g['TIME_X']} y {g['TIME_Y']}  "
          f"HR dial ({g['HR_CENTRE'][0]:.1f}, {g['HR_CENTRE'][1]:.1f})  "
          f"date dial ({g['DATE_CENTRE'][0]:.1f}, {g['DATE_CENTRE'][1]:.1f})")
