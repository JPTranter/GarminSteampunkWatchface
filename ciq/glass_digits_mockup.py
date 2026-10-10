"""Mockup: clear-glass tube envelopes, and thin nixie-style time digits.

DECISION SUPPORT, not shipping code. Two user requests, rendered on the 5 % zoomed-out layout:
  1. "the nixie tubes look metallic, they should look more like glass" - the AI artwork tints the
     whole envelope gold: the glass walls measure saturation ~120 (of 255) at tube 2's walls
     (x 96 / 156 on screen), which is what reads as polished brass. The treatments act ONLY on
     the glass envelopes (per-tube rectangles on the 1024 grid, down to just above the brass
     collars at source y 335) and leave the collars, the manifold and the dials alone.
  2. "the numbers need to be thinner, like a real glowing nixie display" - real nixie digits
     are thin wire cathodes of even stroke. Candidates are rendered at the shipping ink height
     with the watch's own glow method (solid halo rings 3 px and 1 px out, then the core).

Writes artwork/glass_digits/_glass.png (current vs 3 glass treatments) and _digits.png (current
digits vs 3 thin fonts, on glass B). Fonts in fonts-src/ are SIL OFL (see the OFL.txt files);
Bahnschrift is a Windows system font, shown for comparison only.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import device_colour
import hr_gauge
import prepare_artwork as pa
import preview

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "glass_digits")
os.makedirs(OUT, exist_ok=True)
FONTS = os.path.join(HERE, "fonts-src")

TUBE_X_SRC = [282.3, 439.8, 579.5, 745.9]   # tube centres (POINTS tube1..4)
HALF_W_SRC = 72                             # tube 2's walls measure +-64.5 src; + edge AA
Y0_SRC, Y1_SRC = 55, 335                    # nipple tip .. just above the brass collar
FEATHER = 8

GLASS = {
    "A_clear": dict(chroma=0.25, tint=(1.0, 1.0, 1.0), gamma=1.0),
    "B_clear_cool": dict(chroma=0.10, tint=(0.95, 1.0, 1.07), gamma=1.25),
    "C_smoked": dict(chroma=0.10, tint=(0.97, 1.0, 1.03), gamma=1.55),
}

# The user's reference (a photo-real nixie render) - blue glass lit from inside, bright specular
# streaks, rim light on both walls, a hotspot under the dome. Tube geometry measured on tube 2:
# walls at +-64.5 src about the centre, dome from src y ~124, glass body down to ~335.
WALL_SRC = 64.5
DOME_Y_SRC = 124


def glass_reference(src):
    a = np.asarray(src, np.float32) / 255.0
    h, w = a.shape[:2]
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    base = np.power(np.clip(lum * np.array([0.78, 0.95, 1.22], np.float32), 0, 1), 1.35)
    yy = np.arange(h, dtype=np.float32)[:, None]
    xx = np.arange(w, dtype=np.float32)[None, :]
    spec = np.zeros((h, w), np.float32)      # white-blue additive light
    haze = np.zeros((h, w), np.float32)      # blue glow from the digit, inside the glass
    body = np.clip((yy - DOME_Y_SRC) / 30, 0, 1) * np.clip((Y1_SRC - 12 - yy) / 40, 0, 1)
    for cx in TUBE_X_SRC:
        def g(x0, sx):
            return np.exp(-((xx - x0) ** 2) / (2 * sx * sx))
        spec += 0.62 * g(cx - 0.58 * WALL_SRC, 4.5) * body                    # main streak
        spec += 0.22 * g(cx + 0.62 * WALL_SRC, 3.0) * body                    # faint opposite
        spec += 0.40 * (g(cx - 0.97 * WALL_SRC, 2.2) + g(cx + 0.97 * WALL_SRC, 2.2)) * body   # rims
        spec += 0.75 * np.exp(-(((xx - cx) / 12) ** 2 + ((yy - (DOME_Y_SRC + 8)) / 7) ** 2))  # hotspot
        haze += 0.30 * np.exp(-(((xx - cx) / 48) ** 2 + ((yy - 255) / 85) ** 2))
    m = glass_mask(src.size)
    spec = np.clip(spec, 0, 1) * m
    haze = haze * m
    out = base + haze[..., None] * np.array([0.10, 0.32, 0.62], np.float32)
    light = spec[..., None] * np.array([0.82, 0.92, 1.0], np.float32)
    out = 1 - (1 - np.clip(out, 0, 1)) * (1 - light)                         # screen blend
    res = a * (1 - m[..., None]) + out * m[..., None]
    return Image.fromarray((np.clip(res, 0, 1) * 255).round().astype(np.uint8), "RGB")


def glass_mask(size):
    w, h = size
    m = np.zeros((h, w), np.float32)
    yy = np.arange(h)[:, None].astype(np.float32)
    xx = np.arange(w)[None, :].astype(np.float32)
    vy = np.clip((Y1_SRC - yy) / FEATHER, 0, 1) * np.clip((yy - Y0_SRC + FEATHER) / FEATHER, 0, 1)
    for cx in TUBE_X_SRC:
        vx = np.clip((HALF_W_SRC - np.abs(xx - cx)) / 4, 0, 1)
        m = np.maximum(m, vx * vy)
    return m


def glassify(src, chroma, tint, gamma):
    """Neutralise the envelope's gold: keep luminance, cut chroma, tint faintly cool, and push
    the mid-tones down (gamma) so the dark interior shows through - clear glass, white glints."""
    a = np.asarray(src, np.float32) / 255.0
    lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[..., None]
    out = lum + (a - lum) * chroma
    out = out * np.array(tint, np.float32)
    out = np.power(np.clip(out, 0, 1), gamma)
    m = glass_mask(src.size)[..., None]
    res = a * (1 - m) + out * m
    return Image.fromarray((np.clip(res, 0, 1) * 255).round().astype(np.uint8), "RGB")


def frame(variant=None):
    src = pa.load_clean_source()
    if variant == "D_reference":
        src = glass_reference(src)
    elif variant:
        src = glassify(src, **GLASS[variant])
    f = pa.SHIP.background(src)
    return hr_gauge.bake(device_colour.correct(f))


def digit_run(text, font_path, ink_px, condense, variation=None):
    """Glyph masks for `text` scaled so the digit ink height is ink_px."""
    probe = ImageFont.truetype(font_path, 200)
    if variation:
        probe.set_variation_by_name(variation)
    bb = probe.getbbox("0")
    pt = int(200 * ink_px / (bb[3] - bb[1]))
    f = ImageFont.truetype(font_path, pt)
    if variation:
        f.set_variation_by_name(variation)
    out = []
    for ch in text:
        c = Image.new("L", (pt * 2, pt * 2), 0)
        ImageDraw.Draw(c).text((pt // 2, pt * 3 // 2), ch, font=f, fill=255, anchor="ls")
        g = c.crop(c.getbbox())
        out.append(g.resize((max(1, round(g.width * condense)), g.height), Image.LANCZOS))
    return out


def glow_digits(face, consts, font_path, condense, variation=None, ink_px=71):
    """Draw 1 0 0 9 in the tubes with the watch's glow: ring 3 px, ring 1 px, core."""
    for i, ch in enumerate("1009"):
        g = digit_run(ch, font_path, ink_px, condense, variation)[0]
        x0 = round(consts["TIME_X"][i] - g.width / 2)
        y0 = round(consts["TIME_Y"] - g.height / 2)
        for rad, col in ((3, consts["INK_GLOW2"]), (1, consts["INK_GLOW1"]), (0, consts["INK_TIME"])):
            colour = preview.rgb(col)
            for dx in range(-rad, rad + 1):
                for dy in range(-rad, rad + 1):
                    if rad and max(abs(dx), abs(dy)) != rad:
                        continue
                    face.paste(Image.new("RGB", g.size, colour), (x0 + dx, y0 + dy), g)


def shot(bg, consts, hr=70, digits=None):
    c = dict(consts)
    if digits:
        c["TIME_Y"] = -500
    f = preview.render(consts=c, hr=hr, background=bg)
    if digits:
        glow_digits(f, consts, *digits)
    return device_colour.as_seen(f)


def sheet(panels, path):
    pad = 14
    s = Image.new("RGB", (pad + len(panels) * (640 + pad), 30 + 720 + pad), (30, 28, 26))
    d = ImageDraw.Draw(s)
    for i, (lab, im) in enumerate(panels):
        x = pad + i * (640 + pad)
        d.text((x + 4, 8), lab, fill=(240, 215, 165))
        s.paste(im.resize((640, 720), Image.LANCZOS), (x, 28))
    s.save(path)
    print("wrote", path)


if __name__ == "__main__":
    import sys
    c = preview.parse_constants()
    if "--reference" in sys.argv:
        # the user's reference vs the procedural glass, with two thin digit candidates
        ref = Image.open(sys.argv[sys.argv.index("--reference") + 1]).convert("RGB")
        bg = frame("D_reference")
        nix = (os.path.join(FONTS, "nixieone_NixieOne-Regular.ttf"), 0.80)
        osw = (os.path.join(FONTS, "oswald_Oswald[wght].ttf"), 1.0, "Light")
        a, b = shot(bg, c, digits=nix), shot(bg, c, digits=osw)
        top = [im.crop((0, 0, 320, 160)).resize((640, 320), Image.LANCZOS) for im in (a, b)]
        rw = 640 * 2 + 14
        refr = ref.resize((rw, round(ref.height * rw / ref.width)), Image.LANCZOS)
        s = Image.new("RGB", (rw + 28, 30 + refr.height + 30 + 320 + 30 + 720 + 14), (30, 28, 26))
        d = ImageDraw.Draw(s)
        d.text((18, 8), "REFERENCE (user)", fill=(240, 215, 165))
        s.paste(refr, (14, 28))
        y = 28 + refr.height + 8
        d.text((18, y), "D: procedural reference glass  -  left: Nixie One   right: Oswald Light",
               fill=(240, 215, 165))
        s.paste(top[0], (14, y + 20)); s.paste(top[1], (14 + 654, y + 20))
        y += 20 + 320 + 10
        s.paste(a.resize((640, 720), Image.LANCZOS), (14, y))
        s.paste(b.resize((640, 720), Image.LANCZOS), (14 + 654, y))
        p = os.path.join(OUT, "_reference_glass.png")
        s.save(p)
        print("wrote", p)
        raise SystemExit(0)
    sheet([("CURRENT (gold-tinted envelopes)", shot(frame(), c))] +
          [(v.replace("_", " "), shot(frame(v), c)) for v in GLASS],
          os.path.join(OUT, "_glass.png"))
    bg = frame("B_clear_cool")
    sheet([("CURRENT digits (Times Bold, condensed)", shot(bg, c)),
           ("Nixie One (OFL)", shot(bg, c, digits=(os.path.join(FONTS, "nixieone_NixieOne-Regular.ttf"), 0.80))),
           ("Oswald ExtraLight (OFL)", shot(bg, c, digits=(os.path.join(FONTS, "oswald_Oswald[wght].ttf"), 0.85, "ExtraLight"))),
           ("Bahnschrift Light Condensed (Windows, comparison)",
            shot(bg, c, digits=(r"C:\Windows\Fonts\bahnschrift.ttf", 1.0, "Light Condensed")))],
          os.path.join(OUT, "_digits.png"))
