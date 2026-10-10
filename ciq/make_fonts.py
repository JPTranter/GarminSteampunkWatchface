"""Generate Garmin custom bitmap fonts (BMFont .fnt + grayscale atlas) for the nixie face.

WHY: measured on the real Venu Sq 2 Music, the SMALLEST built-in font is 39 px tall
(FONT_XTINY), and FONT_NUMBER_MILD is 82 px. This design needs ~54 px tube digits, ~34 px drum
digits, ~30 px gauge numbers and ~11 px unit labels, so no built-in font fits. Garmin custom fonts
are single-channel GRAYSCALE masks drawn in one colour — which suits glowing nixie numerals.

The "tall and thin" look from the HTML model (scaleX .72 / scaleY 1.34) is baked into the glyphs
here by condensing horizontally, since a bitmap font cannot be scaled at runtime.

Outputs, per font: <name>.fnt (BMFont text) + <name>_0.png (grayscale atlas), written to
ciq/resources/fonts/. Also writes a preview sheet so the result can be judged before building.
"""
import os

import prepare_artwork

# Sizes were tuned on layout C (0.49 / 0.43); they follow any later zoom by the band's factor.
_G = prepare_artwork.geometry()
TOP_K, BOT_K = _G["TOP_K"], _G["BOT_K"]

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "resources", "fonts")
os.makedirs(OUT, exist_ok=True)

SERIF_BD = r"C:\Windows\Fonts\timesbd.ttf"
SERIF = r"C:\Windows\Fonts\georgia.ttf"


def render_glyph(ch, px, condense, source=SERIF_BD, thin=0, thick=0):
    """Render one glyph to a tight grayscale mask, condensed horizontally.

    `thin` erodes the stroke by that many px on each side and `thick` dilates it by that many:
    Nixie One's natural weight is the middle of that range. The tube digits shipped THIN (1 px off
    each side) to match a reference photograph of a wire cathode, and the user then reported them
    "really hard to read on the device" - at 74 px ink on a 320 px screen the eroded stroke is ~3 px,
    which the AMOLED plus the panel's own small-pixel behaviour washes out. `thin=0` restores the
    natural weight (~6 px, twice the stroke) and `thick` goes past it.
    """
    f = ImageFont.truetype(source, px)
    pad = 6
    canvas = Image.new("L", (px * 3, px * 3), 0)
    d = ImageDraw.Draw(canvas)
    # anchor "ls" = left-BASELINE, so the baseline must sit BELOW the glyph body or the whole
    # glyph is drawn above the origin and clipped (first attempt produced 6 px-tall slivers).
    d.text((pad, pad + px), ch, font=f, fill=255, anchor="ls")
    bbox = canvas.getbbox()
    if bbox is None:
        return None
    g = canvas.crop(bbox)
    if thin > 0:
        g = g.filter(ImageFilter.MinFilter(2 * thin + 1)).filter(ImageFilter.GaussianBlur(0.5))
    elif thick > 0:
        g = g.filter(ImageFilter.MaxFilter(2 * thick + 1)).filter(ImageFilter.GaussianBlur(0.5))
    w = max(1, int(round(g.width * condense)))
    return g.resize((w, g.height), Image.LANCZOS)


def halo_mask(g, d0, d1, pad, curve="log"):
    """The glyph's OUTER fade as an 8-bit coverage mask: alpha 1 at d0 px from the stroke, falling
    linearly to 0 at d1, and 0 inside d0, on a canvas padded by `pad` so the fade is not clipped.
    Padding every glyph by the same amount keeps this font's advances and line height in step with the
    wire font it overlays - the ink sits `pad` px in, so it lands exactly where the wire does.

    This is how a text element gets a real alpha fade on the device: drawText has no alpha parameter,
    but an antialiased custom font's grey coverage IS blended over the background, so encoding the fade
    in the coverage gives a per-glyph falloff that follows whatever glyphs are drawn - which a baked
    blob cannot do, and four more solid bands would cost 8r glyph blits each per digit per frame.
    """
    import cv2
    import numpy as np
    # > 0, not > 127: the glyph's anti-aliased skirt is part of the stroke as the eye sees it, and
    # binarising at the midpoint measures every distance ~1 px too far out.
    a = (np.asarray(g, np.uint8) > 0).astype(np.uint8) * 255
    d = cv2.distanceTransform(255 - a, cv2.DIST_L2, 5)       # px from the stroke edge
    t = np.clip((d - d0) / float(d1 - d0), 0, 1)             # 0 at the edge, 1 at the end of the fade
    if curve == "log":
        # logarithmic: alpha = 1 - log(1 + k t) / log(1 + k), so it drops fast just outside the wire
        # and then lingers - 1.00 / 0.49 / 0.26 / 0.06 / 0.00 at t = 0, .25, .5, .75, 1 against the
        # linear ramp's 1.00 / 0.75 / 0.50 / 0.25 / 0.00. User request ("make the alpha falloff
        # logarithmically, not linear").
        k = 9.0
        alpha = 1.0 - np.log1p(k * t) / float(np.log1p(k))
    elif curve == "exp":
        alpha = np.power(0.5, t / 0.25)                      # halving every quarter of the fade
    else:
        alpha = 1.0 - t
    alpha[d < d0] = 0
    m = Image.fromarray((alpha * 255).astype(np.uint8), "L")
    big = Image.new("L", (m.width + 2 * pad, m.height + 2 * pad), 0)
    big.paste(m, (pad, pad))
    return big


def build(name, specs, px, condense, source=SERIF_BD, tracking=1, thin=0, thick=0, erode=0,
          halo=None):
    """specs: list of (char, codepoint). Packs glyphs left-to-right, wrapping at 512 px.

    `erode` (after the crop) thins the SAME glyphs without touching their box, so a font built with it
    has identical metrics to the one it is derived from and lands concentrically on it — that is what
    draws the wire's cream core inside the yellow body (NixieTimeHot). `thin` cannot do this job: it
    re-crops to the smaller bbox, so the two fonts' line heights and advances would differ and the core
    would drift off centre.

    `halo` = (d0, d1, pad) turns the glyph into its own outer fade instead (see halo_mask).
    """
    glyphs = []
    for ch, cp in specs:
        g = render_glyph(ch, px, condense, source, thin, thick)
        if g is not None:
            if erode > 0:
                g = g.filter(ImageFilter.MinFilter(2 * erode + 1)).filter(ImageFilter.GaussianBlur(0.5))
            if halo is not None:
                g = halo_mask(g, halo[0], halo[1], halo[2])
            glyphs.append((ch, cp, g))
    if not glyphs:
        raise SystemExit(f"{name}: no glyphs rendered")

    MAXW = 512
    x = y = 0
    row_h = 0
    placed = []
    for ch, cp, g in glyphs:
        if x + g.width + tracking > MAXW:
            x = 0
            y += row_h + 1
            row_h = 0
        placed.append((ch, cp, g, x, y))
        x += g.width + tracking
        row_h = max(row_h, g.height)
    atlas_h = y + row_h

    atlas = Image.new("L", (MAXW, atlas_h), 0)
    for ch, cp, g, gx, gy in placed:
        atlas.paste(g, (gx, gy))

    cap = px  # nominal point size for this font
    max_h = max(g.height for _, _, g, _, _ in placed)
    # BMFont metrics: `base` is the distance from the LINE TOP down to the BASELINE, and a glyph's
    # `yoffset` is measured DOWN from the line top. The first version wrote yoffset=-height, which
    # puts every glyph ABOVE the line box — the text loads and then draws nothing visible.
    lines = [
        f'info face="{name}" size={cap} bold=0 italic=0 charset="" unicode=1 stretchH=100 '
        f'smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline=0',
        f'common lineHeight={max_h + 2} base={max_h} scaleW={MAXW} scaleH={atlas_h} pages=1 '
        f'packed=0 alphaChnl=1 redChnl=0 greenChnl=0 blueChnl=0',
        f'page id=0 file="{name}_0.png"',
        f'chars count={len(placed)}',
    ]
    for ch, cp, g, gx, gy in placed:
        lines.append(f'char id={cp} x={gx} y={gy} width={g.width} height={g.height} '
                     f'xoffset=0 yoffset=0 xadvance={g.width + tracking} page=0 chnl=15')
    open(os.path.join(OUT, name + ".fnt"), "w", newline="\n").write("\n".join(lines) + "\n")
    atlas.save(os.path.join(OUT, name + "_0.png"))
    print(f"  {name:12s} {len(placed):3d} glyphs  atlas {MAXW}x{atlas_h}  nominal {cap}px")
    return atlas, placed


DIGITS = [(str(i), 48 + i) for i in range(10)]

# Target DIGIT heights come from the measured layout (ciq/LAYOUT.md). A serif digit's ink height is
# ~0.66x the point size, so the point sizes below are chosen to hit those targets.
#
# SPLIT-SCALE LAYOUT (prepare_artwork.py): the art is now drawn at 0.49 (tubes) and 0.43 (dials,
# counter) instead of the old uniform 0.3365, so every size is the old one times its band's factor:
# top x1.456 (76 -> 111) and bottom x1.278 (48 -> 61, 43 -> 55, 34 -> 43, 16 -> 20).
# NixieTime: Nixie One (SIL OFL, fonts-src/), user-chosen for thin, even-stroke digits like a
# real tube's wire cathodes (mockups: artwork/glass_digits/_digits.png). Sized by INK height so
# the digit fills the tube as the old Times Bold one did (75 px at layout C, scaled by TOP_K).
NIXIE_ONE = os.path.join(HERE, "fonts-src", "nixieone_NixieOne-Regular.ttf")


def px_for_ink(source, ink):
    probe = ImageFont.truetype(source, 200)
    bb = probe.getbbox("0")
    return round(200 * ink / (bb[3] - bb[1]))


# NixieTime weight: NATURAL (thin=0). It shipped eroded by 1 px per side to match a reference photo
# of a wire cathode, and the user reported the result "really hard to read on the device" - the
# eroded stroke is ~3 px at 74 px ink and the panel washes it out. `thick=1` dilates if it is ever
# wanted heavier than the typeface's own weight.
t_atlas, t_glyphs = build("NixieTime", DIGITS, px=px_for_ink(NIXIE_ONE, 75 * TOP_K),
                          condense=0.80, source=NIXIE_ONE)          # ~75 px digits, tubes
# NixieTimeHot: the same glyphs eroded 1 px per side, drawn as the wire's CREAM CORE over the yellow
# glyph (the user's zoom specifies exactly that: f8f7d4 core, f5e67d body). Erosion happens after the
# crop, so both fonts share metrics and the core sits concentrically inside the wire.
h_atlas, h_glyphs = build("NixieTimeHot", DIGITS, px=px_for_ink(NIXIE_ONE, 75 * TOP_K),
                          condense=0.80, source=NIXIE_ONE, erode=1)
# NixieTimeHalo: the wire's OUTER fade, drawn in the last glow colour (INK_GLOW3). Its glyphs ARE the
# alpha ramp - full brightness at the stroke's edge, LOGARITHMICALLY down to nothing 4 px out - so the
# falloff follows whatever digits are shown and alpha-blends over the background. The user asked for
# exactly that: "the last colour ... alpha blend over the background for 4 pixels out to nothing",
# then "make the alpha falloff logarithmically, not linear". The pad is 5 px so the 4 px fade and its
# anti-aliased tail both fit inside the glyph box.
hl_atlas, hl_glyphs = build("NixieTimeHalo", DIGITS, px=px_for_ink(NIXIE_ONE, 75 * TOP_K),
                            condense=0.80, source=NIXIE_ONE, halo=(0.5, 4.5, 5, "log"))
# NixieDay: the date dial's day number. The weekday and month moved out to the dial's ring
# (make_date_ring.py), which freed the inner disc for a bigger number: 54 px ink (user-approved,
# artwork/date_ring/_compare.png). Was NixieSmall at px 61 / 42 px ink.
s_atlas, s_glyphs = build("NixieDay", DIGITS + [("-", 45), (" ", 32)],
                          px=round(78 * BOT_K), condense=0.62)                          # ~54 px, day number
# Two more sizes, because a bitmap font cannot be scaled at runtime and the gauges do not want the
# 32 px drum/gauge digit the day number uses:
#   NixieMid  - the heart-rate number, a step below NixieSmall but still a gauge-face reading.
#   NixieStep - the odometer drums, which are only ~28 px of clear dark inside the window, so the
#               32 px digit overflowed onto the brass frame. Shorter is what "fits the drum" means.
m_atlas, m_glyphs = build("NixieMid", DIGITS + [("-", 45), (" ", 32)],
                          px=round(55 * BOT_K), condense=0.62)                          # ~37 px
d_atlas, d_glyphs = build("NixieStep", DIGITS + [("-", 45), (" ", 32)],
                          px=round(43 * BOT_K), condense=0.62)                          # ~29 px
# (NixieLabel - BPM / weekday / month - retired: the date moved into the dial's ring as
# pre-rendered patches, and BPM went with the heart-rate zone gauge.)

# ---- preview sheet: the glyphs at actual size, on a dark background like the watch
prev_w = 320
prev_h = 190
prev = Image.new("RGB", (prev_w, prev_h), (12, 10, 8))
d = ImageDraw.Draw(prev)
y = 8
d.text((6, y), "NixieTime 54px (tube digits)", fill=(120, 120, 120))
y += 14
x = 6
for ch, cp, g, gx, gy in t_glyphs:
    prev.paste(Image.new("RGB", (g.width, g.height), (235, 244, 255)),
               (x, y), g)
    x += g.width + 3
y += 60
d.text((6, y), "NixieDay (day number)", fill=(120, 120, 120))
y += 14
x = 6
for ch, cp, g, gx, gy in s_glyphs:
    prev.paste(Image.new("RGB", (g.width, g.height), (255, 243, 216)), (x, y), g)
    x += g.width + 3
y += 42
prev.resize((prev_w * 2, prev_h * 2), Image.NEAREST).save(
    os.path.join(HERE, "artwork", "_fonts_preview.png"))
print("wrote artwork/_fonts_preview.png")
