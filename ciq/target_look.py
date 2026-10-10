"""Mockup: the TARGET LOOK in one image - amber glass + reference-matched digits + live side sparks -
shown beside the user's reference. Decision support; writes artwork/target_look.png only.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import amber_candidates as ac
import device_colour
import preview
import spark_mockup as sm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artwork", "target_look.png")


def label_font(size):
    for p in (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


if __name__ == "__main__":
    glass = dict(zip(("cast", "gamma", "lift"), ac.GLASS[1][1:]))    # B amber
    bg = ac.build(glass["cast"], glass["gamma"], glass["lift"])
    ink = ac.INK[2][1:]                                              # 3 ref hot core
    ratio, stroke = ac.legibility(bg, ink)
    frames = []
    sp = sm.Sparks()
    for n in range(24):
        sp.step()
        face = ac.render(bg, ink)
        sp.draw(face)
        frames.append(device_colour.as_seen(face))
    b, dk = ac.measure(frames[8])

    ref = Image.open(ac.REF).convert("RGB").crop((44, 20, 1013, 430))
    face = frames[8].resize((640, 720), Image.LANCZOS)
    band = face.crop((0, 0, 640, 400))
    w = 640
    refb = ref.resize((w, round(ref.height * w / ref.width)), Image.LANCZOS)
    s = Image.new("RGB", (2 * w + 36, 30 + refb.height + 30 + 400 + 12 + 360 + 12), (26, 24, 22))
    d = ImageDraw.Draw(s)
    f = label_font(22)
    d.text((12, 8), "REFERENCE (the user's AI render, tube band)", fill=(240, 215, 165), font=f)
    d.text((16 + w, 8), "PROPOSED: amber glass + reference-matched digits + live side sparks",
           fill=(240, 215, 165), font=f)
    s.paste(refb, (12, 30))
    s.paste(band, (16 + w, 30))
    y = 30 + max(refb.height, 400) + 12
    d.text((12, y), f"lit glass ({b[0]:.0f},{b[1]:.0f},{b[2]:.0f})   dark glass "
                    f"({dk[0]:.0f},{dk[1]:.0f},{dk[2]:.0f})   digit core-vs-glass {ratio:.1f}:1   "
                    f"stroke {stroke:.0f} px   emitter origins (16,126) / (304,126)",
           fill=(240, 215, 165), font=f)
    s.paste(face.resize((320, 360), Image.LANCZOS), (16 + w, y + 26))
    s.paste(frames[8].resize((640, 720), Image.LANCZOS).crop((0, 0, 640, 380)), (12, y + 26))
    s.save(OUT)
    print("wrote", OUT, s.size)
    print(f"amber glass lit ({b[0]:.0f},{b[1]:.0f},{b[2]:.0f}); digit core-vs-glass {ratio:.1f}:1,"
          f" stroke {stroke:.0f} px")