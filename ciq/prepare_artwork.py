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
# The tube digits sit 2 SCREEN px higher than measured (user request): the digit centre is stored on
# the source grid, so the nudge is 2 / ST = 4.3 source px and survives any later zoom. The separator
# (SEP_Y) is derived from TIME_Y, so it lifts with them.
_TUBE_Y_SRC = 255.6 - 2 / ST
# The digits are centred on the ELECTRODE STEM under each tube - the artwork feature that actually
# marks a tube's axis - rather than on the original centre measurement, which the user could see was
# wrong ("the 2nd '0' should center on the stem below it"). Measured on the frame as the bright cap's
# centre just below each digit (narrow band y 149..161): tube 1 stem 55 (digit was 53), tube 2 128.8
# (digit 129), tube 3 196-197 (digit 191), tube 4 268 (digit 269). So tubes 1 and 3 move; 2 and 4 are
# already within a pixel. Stored on the source grid, so the nudges survive any later zoom.
_TUBE_X_SRC = {1: 282.3 + 2 / ST, 2: 439.8 + 3 / ST, 3: 579.5 + 5 / ST, 4: 745.9}
POINTS = {
    "tube1": (_TUBE_X_SRC[1], _TUBE_Y_SRC, "top"), "tube2": (_TUBE_X_SRC[2], _TUBE_Y_SRC, "top"),
    "tube3": (_TUBE_X_SRC[3], _TUBE_Y_SRC, "top"), "tube4": (_TUBE_X_SRC[4], _TUBE_Y_SRC, "top"),
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
# ---- the digits' haze: the baked half of the glow
# The user: "It does not have a glowing orange effect like in the sample image." Measured off the
# reference (ciq/ref_glow.py) in distance bands from the lit ink, converted to our pixels (its tube is
# ~164 px across against our 60): 0.5 px out the glass sits at L111 - the wire's own halo - then L32
# at 1.2 px, L21 at 2.3, L15 at 4.0, L11 at 6.8 and L3 at 11.4. The OLD haze (sigma 48 x 85 source px,
# i.e. 22 x 40 screen px) holds L17-23 all the way out to 11 px: a broad wash that fills the tube
# instead of a bloom around the wire, which is the opposite of the reference and is most of why the
# digits do not read as glowing. A tight haze plus one painted outer ring (the view's GLOW_RAD2)
# reproduces the measured falloff; the ring is live because it has to hug whatever glyphs are shown.
GLASS_HAZE_RGB = (0.62, 0.26, 0.06)
GLASS_SPEC_RGB = (1.0, 0.94, 0.86)
GLASS_HAZE_AMP = 0.30           # peak of the digit's haze in the glass
GLASS_HAZE_SIGMA = (20, 60)     # source px, x and y: tight around the digit, still taller than wide
# ---- what the digit's glow has to read against
# The user: "there is obviously no glow at the bottom of the digit / you haven't taken the glow size
# into account". Measured on the frame: beside the wire the glass falls 79 -> 10 over 6 px, but BELOW
# it the frame sits flat at L 30-48 and ABOVE it starts at 76 - because the artwork paints a bright
# amber ELECTRODE STEM immediately under each digit and the tube's shoulder highlight just above it.
# The glow is drawn there (bands 2 px, halo 4 px, symmetric - verified on black), it simply has no
# dark glass to fade into. So the artwork is dimmed in a band around the digit's ink, outside it, and
# only inside the tubes: below by GLOW_DIM_BELOW, above by GLOW_DIM_ABOVE, fading out over ~30 src px.
GLOW_DIM_BELOW = 0.65
GLOW_DIM_ABOVE = 0.45
GLOW_DIM_SIGMA = 30.0            # source px
DIGIT_INK_HALF_SRC = 75.5        # half the tube digit's ink height, in source px (70 px screen ink
                                 # after the user's 5 % reduction, / ST), so the dim band follows it


def _dim_field(h, w):
    """The darkening applied above and below the digits (see GLOW_DIM_*), as an (h, w) field.

    Two things it has to get right, both found by measuring the result rather than the code:

    - it is applied to the COMPOSITE, not to the glass inside the tube mask: the mask stops a few
      source px below the digit, and the stem that swallows the glow sits outside it;
    - it is limited to each tube's own columns, because a per-row field would darken the whole width
      of the face at those rows, the manifold between the tubes included.
    """
    yy = np.arange(h, dtype=np.float32)[:, None]
    xx = np.arange(w, dtype=np.float32)[None, :]
    y0 = _TUBE_Y_SRC + DIGIT_INK_HALF_SRC          # just below the ink
    y1 = _TUBE_Y_SRC - DIGIT_INK_HALF_SRC          # just above it
    below = np.where(yy > y0, np.exp(-(((yy - y0) / GLOW_DIM_SIGMA) ** 2)), 0.0)
    above = np.where(yy < y1, np.exp(-(((y1 - yy) / GLOW_DIM_SIGMA) ** 2)), 0.0)
    cols = np.zeros((1, w), np.float32)
    for cx in TUBE_X_SRC:
        cols = np.maximum(cols, np.clip((TUBE_HALF_W_SRC + 6 - np.abs(xx - cx)) / 6.0, 0.0, 1.0))
    return np.clip(1.0 - (GLOW_DIM_BELOW * below + GLOW_DIM_ABOVE * above) * cols, 0.0, 1.0)


GLASS_HAZE_Y_SRC = _TUBE_Y_SRC  # the digit centre the haze is centred on: it follows the wire's
                                # 2 px lift above, so the baked tint moves with the ink that lights it
# The envelope's own CAST: a per-channel gain applied to the artwork's luminance. It replaced the AI
# art's gold with a cool blue cast, and the user's reference (a warm amber tube render) then asked for
# the opposite: the base chroma is what the PANEL re-lights, and the baked haze cannot re-tint the
# envelope on its own, so "the glass should be amber" is a change to THIS constant. Measured off the
# reference: lit interior (53,25,6), hue 27-35 deg, against the blue build's (81,91,112) - the amber
# values below land the lit glass at (116,81,54), hue 26 deg, at the same luminance and darkness.
GLASS_CAST_RGB = (1.30, 0.74, 0.26)
GLASS_GAMMA = 1.35               # mid-tone push-down; higher = darker, clearer tube interior
# The anode grid: real nixie tubes show a hexagonal metal mesh in front of the cathode, and the
# user's reference photo reads as much by its honeycomb as by its colour. 0 = off. Visibility
# follows the digit's own haze (MESH_GAIN), so the mesh lights up with the glow instead of being a
# uniform printed texture.
# The user asked for the mesh to read as a LIGHTER RED behind the digits: d05227. That is the mesh
# drawn as coloured light (MESH_DARKEN = 0) with MESH_RGB set to that colour in as-seen space - the
# baked art is pre-corrected on the way out, so the panel shows the requested colour. Measured on the
# rendered frame, the wires ADD (105,43,22) at their peaks against 0.6 px wires: about half the
# requested colour, because a 0.6 source-px wire only part-covers a pixel. The cost is legibility,
# measured on the eroded glyph core: the darkening mesh held 11.5:1, this holds 6.6:1 at
# MESH_ALPHA 1.5 (and 5.8:1 at 2.0, below this project's bar). Widening MESH_W_SRC is the other way
# to deepen the colour, at a similar contrast price.
MESH_ALPHA = 1.5
MESH_RGB = (0.816, 0.322, 0.153)   # (208, 82, 39) = d05227
MESH_R_SRC = 5.35                # hexagon circumradius on the 1024 grid (~14 cells across a tube)
MESH_W_SRC = 0.6                 # wire width, source px (drawn supersampled, see _hex_mesh)
MESH_SS = 6                      # supersampling factor for the mesh mask
MESH_GAIN = 1.6                  # how strongly the local haze brightens the mesh
MESH_BASE = 0.10                 # how visible the mesh is away from the glow
# 1.0 = the wires occlude (darken) the glass, 0 = they are drawn as coloured light. The occluder
# polarity is what buys digit contrast on a near-black field; the user's request for a lighter red
# mesh is the coloured-light polarity, so this ships as 0 and MESH_RGB is live.
MESH_DARKEN = 0.0
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


# ---- the digits' glow is NOT baked as a second layer
# It was tried: a union of all ten glyphs at the shipping size, blurred, added to the glass. Measured,
# it floods the digit BOX rather than hugging the glyphs - the ten digits overlap so heavily that the
# union is a filled blob, and its profile held L61 at 2 px against the reference's L32, L21 at 2.3 and
# L3 at 11. A bloom has to follow the strokes that are actually lit, and the strokes change every
# minute, so the tight half of the glow is painted LIVE (the view's GLOW_RAD2 ring) and only the
# broader haze above is baked.


def glass_tubes(src):
    a = np.asarray(src, np.float32) / 255.0
    h, w = a.shape[:2]
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    base = np.power(np.clip(lum * np.array(GLASS_CAST_RGB, np.float32), 0, 1), GLASS_GAMMA)
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
        haze += GLASS_HAZE_AMP * np.exp(
            -(((xx - cx) / GLASS_HAZE_SIGMA[0]) ** 2
              + ((yy - GLASS_HAZE_Y_SRC) / GLASS_HAZE_SIGMA[1]) ** 2))
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
    # dim just above and below each digit so the wire's glow has dark glass to fall into: the
    # artwork's electrode stem below and shoulder highlight above otherwise swallow it whole.
    # Applied to the COMPOSITE, not to the masked glass - the tube mask stops a few source px below
    # the digit and the stem sits outside it (dimming only the glass changed 3,626 px above the digits
    # and left the region below them untouched).
    res = res * _dim_field(h, w)[..., None]
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


# The arc channels and the side-spark emitters that used to be generated here are gone with
# source/Discharge.mc (user request: "remove the sparks at the side and lightning above the tubes").
# The baked artwork still carries its own painted blue sparks and the lamp glows - removal of those is
# an ARTWORK change (an inpaint), not a code one.
# The hours/minutes separator's x: measured on the shipping frame as the centre of the gap between the
# two tubes' WALLS (their rims bracket screen x 148..168), at digit height.
SEP_POINT = _src_from_screen(160, 95, "top")
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
    hx, hy = lay.map(*HR_DIAL_SRC, "bot")
    g["HR_CENTRE"] = (hx, hy)
    g["HR_BAND"] = (HR_BAND_SRC[0] * lay.sb, HR_BAND_SRC[1] * lay.sb)
    g["DATE_CENTRE"] = lay.map(*DATE_DIAL_SRC, "bot")
    g["RING_R"] = RING_R_SRC * lay.sb
    g["RING_CAP"] = RING_CAP_SRC * lay.sb
    g["TOP_K"] = lay.st / 0.49          # font scale vs the layout the font sizes were tuned on
    g["BOT_K"] = lay.sb / 0.43
    # Hours/minutes separator: the colon sits in the tube 2 / tube 3 gap at digit height. Its x is its
    # OWN measured point (the centre of the gap between the two tubes' walls), not the midpoint of the
    # digit centres: the digits are placed on their stems now, and a stem-centred digit is not
    # necessarily the geometric centre of the gap - deriving the dots from the digits would drag them
    # off the gap every time a digit is nudged.
    sx, _sy = lay.map(*SEP_POINT, "top")
    g["SEP_X"] = round(sx)
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
