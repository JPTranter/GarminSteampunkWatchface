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

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "resources", "fonts")
os.makedirs(OUT, exist_ok=True)

SERIF_BD = r"C:\Windows\Fonts\timesbd.ttf"
SERIF = r"C:\Windows\Fonts\georgia.ttf"


def render_glyph(ch, px, condense, source=SERIF_BD):
    """Render one glyph to a tight grayscale mask, condensed horizontally."""
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
    w = max(1, int(round(g.width * condense)))
    return g.resize((w, g.height), Image.LANCZOS)


def build(name, specs, px, condense, source=SERIF_BD, tracking=1):
    """specs: list of (char, codepoint). Packs glyphs left-to-right, wrapping at 512 px."""
    glyphs = []
    for ch, cp in specs:
        g = render_glyph(ch, px, condense, source)
        if g is not None:
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
t_atlas, t_glyphs = build("NixieTime", DIGITS, px=111, condense=0.58)    # ~75 px digits, tubes
# NixieDay: the date dial's day number. The weekday and month moved out to the dial's ring
# (make_date_ring.py), which freed the inner disc for a bigger number: 54 px ink (user-approved,
# artwork/date_ring/_compare.png). Was NixieSmall at px 61 / 42 px ink.
s_atlas, s_glyphs = build("NixieDay", DIGITS + [("-", 45), (" ", 32)],
                          px=78, condense=0.62)                          # ~54 px, day number
# Two more sizes, because a bitmap font cannot be scaled at runtime and the gauges do not want the
# 32 px drum/gauge digit the day number uses:
#   NixieMid  - the heart-rate number, a step below NixieSmall but still a gauge-face reading.
#   NixieStep - the odometer drums, which are only ~28 px of clear dark inside the window, so the
#               32 px digit overflowed onto the brass frame. Shorter is what "fits the drum" means.
m_atlas, m_glyphs = build("NixieMid", DIGITS + [("-", 45), (" ", 32)],
                          px=55, condense=0.62)                          # ~37 px
d_atlas, d_glyphs = build("NixieStep", DIGITS + [("-", 45), (" ", 32)],
                          px=43, condense=0.62)                          # ~29 px
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
