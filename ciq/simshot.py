"""Build the face, run it in the Connect IQ simulator, and save a screenshot of the simulator window.

WHY: showing the face as the device renders it used to be four manual steps (build, start the
simulator, push, screenshot) plus a guess at where the display sits inside the window. This does the
whole loop in one command.

Two things about capturing the simulator window, both learned the hard way:

- **Screen grabs are useless here.** `ImageGrab` only sees what is on top of a screen rectangle, and
  `SetForegroundWindow` is refused for a background process, so the first attempt captured a web
  browser that happened to sit over the simulator's rectangle. `PrintWindow` asks the window to draw
  itself into a memory DC instead — no focus, no z-order — which is what this uses.
- **The device screen cannot be found in the capture by brightness.** The watch case's black bezel,
  the artwork's own black bands, the simulator's dark toolbar and status bar, and the window's black
  non-client regions are all `rgb(0,0,0)`; three automatic calibrations (dark-region bbox, brass
  silhouette matching, warm-row band) each returned a wrong rectangle, because warm/black heuristics
  latch onto window chrome. So the crop is explicit: pass `--crop x0,y0,x1,y1`, reading the numbers
  off the saved window image. A silently wrong crop is worse than no crop — it looks like a
  rendering bug.

Usage:
    python simshot.py                     # build, push, save artwork/face_sim_window.png
    python simshot.py --no-build          # reuse the existing .prg
    python simshot.py --no-push           # just capture what the simulator is already showing
    python simshot.py --crop 62,240,556,740     # also cut the face out and scale it 2x
    python simshot.py --device venusq2m

The simulator must be running (`<sdk>/bin/connectiq.bat`); the script starts it if it is not, and
waits for the window. On the simulator, Simulation -> Activity Data feeds heart rate and steps —
without it those two readouts keep whatever the simulator last held.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import time

from PIL import Image, ImageChops, ImageGrab, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
SDK = os.environ.get("CIQ_SDK") or os.path.join(
    os.environ.get("APPDATA", ""), "Garmin", "ConnectIQ", "Sdks",
    "connectiq-sdk-win-9.2.0-2026-06-09-92a1605b2")
WINDOW_TITLE = "CIQ Simulator"
DEVICE_SCREEN = (320, 360)   # Venu Sq 2 display; the --crop path scales to it (was never defined,
                             # so every --crop run crashed after saving the window capture)

u32 = ctypes.windll.user32
u32.SetProcessDPIAware()


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG),
                ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD)]


def grab_window(h, box):
    """Capture a window's own pixels via PrintWindow — no focus, no z-order, no screen overlap.

    ImageGrab can only see what is on top of a screen rectangle, and the simulator would not always
    come to the front (SetForegroundWindow is refused for background processes), which produced a
    capture of a web browser instead of the watch. PrintWindow asks the window to draw itself into a
    memory DC, so it works regardless. PW_RENDERFULLCONTENT (2) is needed for composited windows.
    """
    gdi32 = ctypes.windll.gdi32
    left, top, right, bottom = box
    w, hh = right - left, bottom - top
    src = u32.GetWindowDC(h)
    mem = gdi32.CreateCompatibleDC(src)
    bmp = gdi32.CreateCompatibleBitmap(src, w, hh)
    gdi32.SelectObject(mem, bmp)
    ok = u32.PrintWindow(h, mem, 2)
    info = BITMAPINFOHEADER()
    info.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    info.biWidth, info.biHeight = w, -hh          # negative = top-down rows
    info.biPlanes, info.biBitCount = 1, 32
    info.biCompression = 0                        # BI_RGB
    buf = ctypes.create_string_buffer(w * hh * 4)
    lines = gdi32.GetDIBits(mem, bmp, 0, hh, buf, ctypes.byref(info), 0)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mem)
    u32.ReleaseDC(h, src)
    if not ok or lines == 0:
        return None
    return Image.frombuffer("RGB", (w, hh), buf, "raw", "BGRX", 0, 1)


def content_bbox(img, threshold=12):
    """Trim the black padding a window capture can carry (DWM frame vs client-area mismatch)."""
    r, g, b = img.convert("RGB").split()
    lit = ImageChops.lighter(ImageChops.lighter(r, g), b).point(
        lambda v: 255 if v > threshold else 0).convert("1")
    box = lit.getbbox()
    return img.crop(box) if box else img


def windows(title_sub):
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(h, _):
        if u32.IsWindowVisible(h):
            n = u32.GetWindowTextLengthW(h)
            if n:
                b = ctypes.create_unicode_buffer(n + 1)
                u32.GetWindowTextW(h, b, n + 1)
                if title_sub.lower() in b.value.lower():
                    r = wt.RECT()
                    u32.GetWindowRect(h, ctypes.byref(r))
                    found.append((h, b.value, (r.left, r.top, r.right, r.bottom)))
        return True

    u32.EnumWindows(cb, 0)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="venusq2m")
    ap.add_argument("--out", default=os.path.join(HERE, "artwork", "face_sim_window.png"))
    ap.add_argument("--crop", help="x0,y0,x1,y1 of the device screen inside the capture; also "
                                   "writes <out>_face.png and <out>_face_<scale>x.png")
    ap.add_argument("--scale", type=int, default=2, help="scale of the cropped face image")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--no-push", action="store_true", help="capture what the simulator already shows")
    ap.add_argument("--push-timeout", type=float, default=360.0,
                    help="guard against a wedged monkeydo only; a push normally takes ~50 s but has "
                         "been seen to run for minutes")
    ap.add_argument("--settle", type=float, default=8.0, help="seconds to wait after the push")
    args = ap.parse_args()

    if not args.no_build:
        print("building…")
        subprocess.run([os.path.join(SDK, "bin", "monkeyc.bat"), "-d", args.device,
                        "-f", "monkey.jungle", "-o", "SteampunkNixie.prg",
                        "-y", "keys/developer_key.der"], cwd=HERE, check=True)

    if not windows(WINDOW_TITLE):
        print("simulator not running — starting it")
        subprocess.Popen([os.path.join(SDK, "bin", "connectiq.bat")])
        for _ in range(60):
            if windows(WINDOW_TITLE):
                break
            time.sleep(1)
        else:
            raise SystemExit("simulator window never appeared")

    if not args.no_push:
        print("pushing…")
        # A push takes ~50 s and can run for minutes while it waits on the simulator, but it does
        # return 0. The timeout is only a guard against a genuinely wedged process, so it is generous:
        # a short one discards a push that was about to succeed.
        try:
            subprocess.run([os.path.join(SDK, "bin", "monkeydo.bat"), "SteampunkNixie.prg",
                            args.device], cwd=HERE, check=True, timeout=args.push_timeout)
        except subprocess.TimeoutExpired:
            print(f"warning: monkeydo did not return within {args.push_timeout:.0f}s "
                  f"(the app may still have been pushed); carrying on to the capture")
    time.sleep(args.settle)

    h, title, box = windows(WINDOW_TITLE)[0]
    shot = grab_window(h, box)
    if shot is None or not shot.getbbox():
        print("PrintWindow returned nothing; falling back to a screen grab (the window must be on top)")
        fg = u32.GetForegroundWindow()
        other = u32.GetWindowThreadProcessId(fg, None)
        mine = ctypes.windll.kernel32.GetCurrentThreadId()
        if other != mine:
            u32.AttachThreadInput(other, mine, True)
        u32.ShowWindow(h, 9)                       # SW_RESTORE
        u32.SetForegroundWindow(h)
        u32.BringWindowToTop(h)
        if other != mine:
            u32.AttachThreadInput(other, mine, False)
        time.sleep(0.7)
        if u32.GetForegroundWindow() != h:
            raise SystemExit("the simulator window will not come to the front and PrintWindow failed "
                             "— move other windows off it, or run this from an interactive shell")
        shot = ImageGrab.grab(bbox=box, all_screens=True)
    shot = content_bbox(shot)
    shot.save(args.out)
    print(f"{args.out}  {shot.size}  ({title})")

    if args.crop:
        x0, y0, x1, y1 = (int(v) for v in args.crop.split(","))
        face = shot.crop((x0, y0, x1, y1))
        stem = os.path.splitext(args.out)[0]
        face.save(stem + "_face.png")
        face.resize((DEVICE_SCREEN[0] * args.scale, DEVICE_SCREEN[1] * args.scale),
                    Image.LANCZOS).save(stem + f"_face_{args.scale}x.png")
        print(f"face crop {x1-x0}x{y1-y0} → {stem}_face_{args.scale}x.png "
              f"({DEVICE_SCREEN[0]*args.scale}x{DEVICE_SCREEN[1]*args.scale})")
        aspect = (x1 - x0) / (y1 - y0)
        want = DEVICE_SCREEN[0] / DEVICE_SCREEN[1]
        if abs(aspect - want) / want > 0.05:
            print(f"warning: crop aspect {aspect:.3f} is not the screen's {want:.3f} — "
                  f"check the rectangle against the saved window image")


if __name__ == "__main__":
    sys.exit(main())
