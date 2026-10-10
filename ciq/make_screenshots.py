"""Regenerate the README and Connect IQ Store images in one go (all rendered 'as seen').

The shipping frame is pre-corrected for the AMOLED panel, so on a normal monitor it looks
yellow-green; every image here goes through device_colour.as_seen() so it looks like the watch
does. They are offline renders from the same constants and resources the watch uses (preview.py),
not photos.

Writes:
    docs/images/face.png           hero, 2x, mid-workout heart rate
    docs/images/states.png         three heart rates side by side (rest / workout / peak)
    docs/images/discharge.gif      arc flicker, glow pulse and a step-belt rollover (1x)
    docs/store/screenshot_N.png    320x360 1x device-size screenshots for the store listing
    docs/store/hero.png            640x720, the face alone
    docs/store/hero_1440x720.png   1440x720 store hero banner (title + tagline + face, OFL fonts)
"""
import os

from PIL import Image, ImageDraw

import device_colour
import preview

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "docs", "images")
STORE = os.path.join(HERE, "..", "docs", "store")


def seen(hr, discharge=None, scale=2):
    c = preview.parse_constants()
    f = device_colour.as_seen(preview.render(consts=c, hr=hr, discharge=discharge))
    return f.resize((320 * scale, 360 * scale), Image.LANCZOS) if scale != 1 else f


def save_under(img, path, max_kb):
    """Save as JPEG at the highest quality (95 down to 60) that fits the store's size limit."""
    for q in range(95, 59, -5):
        img.convert("RGB").save(path, "JPEG", quality=q, optimize=True, progressive=True,
                                subsampling=0 if q >= 90 else 2)
        if os.path.getsize(path) <= max_kb * 1024:
            return q
    raise SystemExit(f"FAIL {path} does not fit {max_kb} KB even at quality 60")


def hero_banner(c):
    """1440x720 Connect IQ Store hero: the face (as seen, mid-strike) on the right, the title and
    a tagline on the left over a soft blue glow. Text uses the OFL fonts in fonts-src/ only."""
    import numpy as np
    from PIL import ImageFilter, ImageFont
    W_, H_ = 1440, 720
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    glow = np.exp(-(((xx - 1040) / 520) ** 2 + ((yy - 300) / 340) ** 2))
    bg = np.stack([8 + 10 * glow, 10 + 26 * glow, 16 + 52 * glow], -1)
    img = Image.fromarray(bg.clip(0, 255).astype(np.uint8), "RGB")

    dis = preview.Discharge(c)
    for _ in range(9):                      # a frame with an arc striking (same seed as the watch)
        dis.step()
    face = device_colour.as_seen(preview.render(consts=c, hr=150, discharge=dis))
    face = face.resize((640, 720), Image.LANCZOS)
    x0 = 760
    # feather the face's left/right edges into the background (its own surround is black, so a
    # hard paste leaves a visible panel edge against the blue gradient)
    fm = np.ones((720, 640), np.float32)
    ramp = np.linspace(0, 1, 40, dtype=np.float32)
    fm[:, :40] *= ramp[None, :]          # 40 px: wider fades the HR dial's first digit
    fm[:, -40:] *= ramp[::-1][None, :]
    fmask = Image.fromarray((fm * 255).astype(np.uint8), "L")
    halo = Image.new("L", (W_, H_), 0)      # soft shadow so the face lifts off the background
    ImageDraw.Draw(halo).rectangle((x0 + 40, 14, x0 + 620, 706), fill=150)
    halo = halo.filter(ImageFilter.GaussianBlur(28))
    img = Image.composite(Image.new("RGB", (W_, H_), (0, 0, 0)), img, halo)
    img.paste(face, (x0, 0), fmask)

    fonts = os.path.join(HERE, "fonts-src")
    title_f = ImageFont.truetype(os.path.join(fonts, "nixieone_NixieOne-Regular.ttf"), 112)
    body_f = ImageFont.truetype(os.path.join(fonts, "oswald_Oswald[wght].ttf"), 34)
    body_f.set_variation_by_name("Light")
    small_f = ImageFont.truetype(os.path.join(fonts, "oswald_Oswald[wght].ttf"), 26)
    small_f.set_variation_by_name("Light")

    # title with the face's own nixie glow: blurred blue under a near-white core
    t = Image.new("L", (W_, H_), 0)
    td = ImageDraw.Draw(t)
    td.text((70, 150), "Steampunk", font=title_f, fill=255)
    td.text((70, 272), "Nixie", font=title_f, fill=255)
    for radius, colour in ((18, (40, 110, 200)), (6, (90, 170, 255))):
        img = Image.composite(Image.new("RGB", (W_, H_), colour), img,
                              t.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: min(255, v * 2)))
    img = Image.composite(Image.new("RGB", (W_, H_), (234, 246, 255)), img, t)

    d = ImageDraw.Draw(img)
    d.text((74, 430), "Glowing nixie tubes on a brass machine.", font=body_f, fill=(235, 214, 170))
    d.text((74, 476), "Arcs crackle every time you raise your wrist.", font=body_f, fill=(235, 214, 170))
    d.text((74, 560), "Heart-rate zone gauge  ·  rolling step counter  ·  calendar dial",
           font=small_f, fill=(170, 160, 140))
    d.text((74, 600), "Venu Sq 2  ·  Venu Sq 2 Music", font=small_f, fill=(130, 125, 115))
    return img


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(STORE, exist_ok=True)

    seen(150).save(os.path.join(IMG, "face.png"))
    seen(150).save(os.path.join(STORE, "hero.png"))

    states = [(62, "Resting - below zone 1"), (150, "Workout - zone 3"), (186, "Peak - zone 5")]
    pad, lab = 16, 26
    sheet = Image.new("RGB", (pad + 3 * (640 + pad), lab + 720 + pad), (24, 22, 20))
    d = ImageDraw.Draw(sheet)
    for i, (hr, text) in enumerate(states):
        x = pad + i * (640 + pad)
        d.text((x + 4, 6), f"{hr} bpm  -  {text}", fill=(235, 210, 160))
        sheet.paste(seen(hr), (x, lab))
        seen(hr, scale=1).save(os.path.join(STORE, f"screenshot_{i + 1}.png"))
    sheet.save(os.path.join(IMG, "states.png"))

    c = preview.parse_constants()
    dis = preview.Discharge(c)
    frames = []
    # arcs + glow pulse, and a step rollover (8,399 -> 8,400) a second in, so the belts roll too
    frm, to, phase = preview.belt_text(8399), preview.belt_text(8399), 0
    for n in range(40):
        dis.step()
        if phase > 0:
            phase = phase + 1 if phase < c["BELT_FRAMES"] else 0
        if n == 10:
            frm, to, phase = to, preview.belt_text(8400), 1
        f = device_colour.as_seen(preview.render(consts=c, hr=150, discharge=dis,
                                                 belt=(frm, to, phase)))
        frames.append(f.crop((0, 0, 320, 280)))
    frames[0].save(os.path.join(IMG, "discharge.gif"), save_all=True, append_images=frames[1:],
                   duration=c["FRAME_MS"], loop=0, optimize=True)

    hero = hero_banner(c)
    hero.save(os.path.join(STORE, "hero_1440x720.png"))

    # ---- the size-limited set the Connect IQ app upload accepts: cover < 300 KB, screenshots
    # < 150 KB. JPEG at the best quality that fits (the PNGs above are 190-800 KB).
    up = os.path.join(STORE, "upload")
    os.makedirs(up, exist_ok=True)
    report = []
    q = save_under(seen(150), os.path.join(up, "cover_640x720.jpg"), 290)
    report.append(("cover_640x720.jpg", q))
    q = save_under(hero, os.path.join(up, "hero_1440x720.jpg"), 290)
    report.append(("hero_1440x720.jpg", q))
    for i, (hr, _) in enumerate(states):
        name = f"screenshot_{i + 1}_320x360.jpg"
        report.append((name, save_under(seen(hr, scale=1), os.path.join(up, name), 140)))
    for name, q in report:
        print(f"  upload/{name:28s} {os.path.getsize(os.path.join(up, name)) // 1024:4d} KB  q{q}")
    for n in sorted(os.listdir(IMG)) + [f"store/{n}" for n in sorted(os.listdir(STORE))]:
        p = os.path.join(IMG, n) if not n.startswith("store/") else os.path.join(STORE, n[6:])
        print(f"  {n:24s} {os.path.getsize(p) // 1024:5d} KB")
