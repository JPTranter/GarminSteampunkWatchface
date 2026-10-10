"""Regenerate the README and Connect IQ Store images in one go (all rendered 'as seen').

The shipping frame is pre-corrected for the AMOLED panel, so on a normal monitor it looks
yellow-green; every image here goes through device_colour.as_seen() so it looks like the watch
does. They are offline renders from the same constants and resources the watch uses (preview.py),
not photos.

Writes:
    docs/images/face.png           hero, 2x, mid-workout heart rate
    docs/images/states.png         three heart rates side by side (rest / workout / peak)
    docs/images/discharge.gif      the arc flicker + glow pulse (tube band, 1x)
    docs/store/screenshot_N.png    320x360 1x device-size screenshots for the store listing
    docs/store/hero.png            640x720 store hero image
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
    for _ in range(40):
        dis.step()
        f = device_colour.as_seen(preview.render(consts=c, hr=150, discharge=dis))
        frames.append(f.crop((0, 0, 320, 150)))
    frames[0].save(os.path.join(IMG, "discharge.gif"), save_all=True, append_images=frames[1:],
                   duration=c["FRAME_MS"], loop=0, optimize=True)
    for n in sorted(os.listdir(IMG)) + [f"store/{n}" for n in sorted(os.listdir(STORE))]:
        p = os.path.join(IMG, n) if not n.startswith("store/") else os.path.join(STORE, n[6:])
        print(f"  {n:24s} {os.path.getsize(p) // 1024:5d} KB")
