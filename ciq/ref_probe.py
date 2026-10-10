"""Probe: measure the user's reference (a photo-real nixie render) so the tube glass, the digits and
the side sparks can be derived from numbers instead of eyeballed.

Prints, per tube and pooled: the lit interior's colour, the wall/edge colour, the digit's core /
body / bloom colours and luminance percentiles, and the side sparks' colour, size and position.

Measurement only - writes nothing. Run:  python ref_probe.py <image>
"""
import sys

import numpy as np
from PIL import Image

HSV_W = np.array([0.2126, 0.7152, 0.0722], np.float32)


def hsv(rgb):
    """rgb float 0..1 (...,3) -> hue deg, sat, val."""
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    nz = d > 1e-6
    h = np.where(nz & (mx == r), 60 * (((g - b) / np.maximum(d, 1e-6)) % 6), h)
    h = np.where(nz & (mx == g), 60 * ((b - r) / np.maximum(d, 1e-6) + 2), h)
    h = np.where(nz & (mx == b), 60 * ((r - g) / np.maximum(d, 1e-6) + 4), h)
    return h, np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0), mx


def peaks(profile, n=4, min_sep=None):
    """n strongest well-separated columns of a 1-D profile (greedy)."""
    idx = []
    p = profile.copy()
    step = min_sep or len(p) // (2 * n)
    for _ in range(n):
        i = int(np.argmax(p))
        idx.append(i)
        p[max(0, i - step):i + step] = -1e9
    return sorted(idx)


def med(px, name, extra=""):
    px = np.asarray(px, np.float32).reshape(-1, 3)      # a wall pair arrives as (h, 2, 3)
    if len(px) == 0:
        print(f"    {name:26s}  (none)")
        return None, None
    m = np.median(px, axis=0)
    lum = float(np.median(px @ HSV_W)) / 255
    print(f"    {name:26s}  rgb ({m[0]:5.0f},{m[1]:5.0f},{m[2]:5.0f})  L {lum:.2f}  {extra}")
    return m, lum


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else r"C:/Users/jptra/AppData/Roaming/Hermes/composer-images/image_2ee11f.png"
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, np.float32)
    h, w = a.shape[:2]
    print(f"reference {path}\n  size {w}x{h}")

    lum = a @ HSV_W
    content = lum > 12
    ys, xs = np.where(content)
    print(f"  content box  x {xs.min()}..{xs.max()}  y {ys.min()}..{ys.max()}")

    hue, sat, val = hsv(a / 255.0)
    warm = content & (val > 0.35) & (sat > 0.35) & (hue < 55)
    prof = warm[:, :].sum(0).astype(np.float32)
    # tube centres from the warm content (digit + lit interior), then refine to the envelope walls
    centres = peaks(prof, 4, w // 10)
    print(f"  tube centres (warm-content columns): {centres}")
    widths = [int(np.bincount(np.where(warm[:, max(0, c - w // 12):c + w // 12].any(1))[0]).shape[0]) for c in centres]
    print(f"  warm content spans (rows lit) per tube: {widths}")

    hw = w // 14                                   # tentative tube half-width, refined per tube
    print("\n  per tube (glass + digit):")
    for k, c in enumerate(centres):
        x0, x1 = max(0, c - hw), min(w, c + hw)
        box = a[:, x0:x1]
        bl = box @ HSV_W
        bh, bs, bv = hue[:, x0:x1], sat[:, x0:x1], val[:, x0:x1]
        inside = (bl > 6) & (bl < 235)
        print(f"   tube {k + 1}  x {x0}..{x1}")
        med(box[inside & (bv > 0.85)], "digit core (V>0.85)")
        med(box[inside & (bv > 0.60) & (bv <= 0.85)], "digit body (V .60-.85)")
        med(box[inside & (bv > 0.35) & (bv <= 0.60) & (bs > 0.4) & (bh < 55)], "glow/bloom (V .35-.60)")
        med(box[inside & (bv > 0.12) & (bv <= 0.35) & (bs > 0.25)], "glass interior lit")
        med(box[inside & (bv > 0.05) & (bv <= 0.35) & (bh < 60)], "glass interior (hue<60)")
        # walls: the two brightest gold columns in this tube's span
        colw = (box * HSV_W).sum(0) / max(1, box.shape[0])
        bw = box.shape[1]
        walls = [min(bw - 1, max(0, q)) for q in peaks(colw, 2, max(1, bw // 3))]
        med(box[:, walls], f"wall edges at x {[x0 + q for q in walls]}")

    print("\n  sparks (blue-dominant):")
    blue = a[..., 2] - (a[..., 0] + a[..., 1]) / 2
    m = blue > 15
    print(f"    blue pixels {m.sum()} ({m.mean() * 100:.2f}% of the image)")
    if m.sum():
        bys, bxs = np.where(m)
        print(f"    bbox x {bxs.min()}..{bxs.max()}  y {bys.min()}..{bys.max()}")
        # split left / right half
        for side, sel in (("left", bxs < w // 2), ("right", bxs >= w // 2)):
            if sel.sum() == 0:
                continue
            px = a[bys[sel], bxs[sel]]
            med(px, f"spark {side} (all)", f"{sel.sum()} px")
            top = px[px @ HSV_W >= np.percentile(px @ HSV_W, 80)]
            med(top, f"spark {side} core (top 20%)")
            half = px[px @ HSV_W <= np.percentile(px @ HSV_W, 40)]
            med(half, f"spark {side} tips (low 40%)")
            print(f"      {side}: x {bxs[sel].min()}..{bxs[sel].max()}  y {bys[sel].min()}..{bys[sel].max()}")
