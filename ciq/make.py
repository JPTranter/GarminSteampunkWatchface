"""One entry point for the watch-face pipeline - short, quiet output.

    python make.py assets            artwork -> resources, in dependency order (below)
    python make.py build             compile for every product; one line each: size + sha256
    python make.py preview [--hr N] [--anim N]     offline render (artwork/face_preview.png)
    python make.py push              build venusq2m, sideload to the watch, verify the copy
    python make.py all               assets + build + preview + push
    python make.py screenshots       README + store images, rendered 'as seen' on the watch
    python make.py release [--publish]
                                     signed release build: per-product .prg + store .iq +
                                     SHA256SUMS + notes in ../release/; --publish also tags
                                     v<version> and creates the GitHub release (gh CLI)

Releases are built HERE, not in CI: the Connect IQ SDK is only downloadable through Garmin's
login-gated SDK Manager, and the signing key (ciq/keys/, never committed) must not leave this
machine. The version comes from manifest.xml (iq:application version=...).

Run it with the Python that has numpy/opencv/PIL (C:/Python314/python.exe here; the bare `python`
shim on PATH is broken - LESSONS). Each step prints one line; full output is printed only when a
step fails, so a routine change costs a few lines of output rather than pages.

Asset order matters - each step reads the previous one's output:
  1. prepare_artwork.py    reference art -> artwork/cand_split.png (split-scale fit, clean-up)
  2. prepare_resources.py  -> drawables/background.png (AMOLED correction + baked HR band)
  3. hr_gauge.py           -> source/HrGauge.mc (geometry + corrected lit-colour table)
  4. make_date_ring.py     -> drawables/ring/*.png + source/DateRing.mc (crops the background)
  5. make_fonts.py         -> resources/fonts/*
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRODUCTS = ["venusq2m", "venusq2"]      # venusq2m = the user's watch (006-B4116-00)
WATCH = "venusq2m"
ASSETS = ["prepare_artwork.py", "prepare_resources.py", "hr_gauge.py", "make_date_ring.py",
          "make_fonts.py"]


def sdk_bin():
    cfg = os.path.join(os.environ["APPDATA"], "Garmin", "ConnectIQ", "current-sdk.cfg")
    return os.path.join(open(cfg).read().strip().rstrip("\\/"), "bin")


def run(cmd, label):
    r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode != 0:
        print(f"FAIL {label}\n{out}")
        sys.exit(1)
    return out


def assets():
    for s in ASSETS:
        out = run([sys.executable, s], s)
        print(f"ok   {s:22s} {out.splitlines()[-1][:90] if out else ''}")


def build(products=PRODUCTS):
    mc = os.path.join(sdk_bin(), "monkeyc.bat")
    for p in products:
        prg = os.path.join(HERE, "SteampunkNixie.prg" if p == WATCH else f"SteampunkNixie_{p}.prg")
        out = run([mc, "-d", p, "-f", "monkey.jungle", "-o", prg, "-y",
                   os.path.join("keys", "developer_key.der")], f"build {p}")
        warns = [l for l in out.splitlines() if "WARNING" in l.upper()]
        if "BUILD SUCCESSFUL" not in out:
            print(f"FAIL build {p}\n{out}")
            sys.exit(1)
        sha = hashlib.sha256(open(prg, "rb").read()).hexdigest()[:16]
        note = f"  ({len(warns)} warnings)" if warns else ""
        print(f"ok   build {p:9s} {os.path.getsize(prg):7d} B  sha256 {sha}{note}")
        for w in warns[:5]:
            print("     " + w.strip())


def preview(extra):
    out = run([sys.executable, "preview.py"] + extra, "preview")
    print(f"ok   preview {out.splitlines()[0]}")


def push():
    build([WATCH])
    out = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
               "push_watch.ps1"], "push")
    tail = [l for l in out.splitlines() if l.startswith(("VERIFIED", "MISMATCH", "PUSH", "device"))]
    print("ok   push " + (tail[-1] if tail else out.splitlines()[-1]))
    if not any(l.startswith("VERIFIED") for l in tail):
        print(out)
        sys.exit(1)


def version():
    m = re.search(r'<iq:application[^>]*\sversion="([^"]+)"',
                  open(os.path.join(HERE, "manifest.xml"), encoding="utf-8").read(), re.S)
    if not m:
        sys.exit("FAIL no version= on iq:application in manifest.xml")
    return m.group(1)


def git(*args):
    return subprocess.run(["git", *args], cwd=HERE, capture_output=True, text=True).stdout.strip()


def release(publish):
    ver = version()
    tag = f"v{ver}"
    if git("status", "--porcelain"):
        sys.exit("FAIL working tree not clean - commit first, so the release matches a commit")
    if publish and git("tag", "-l", tag):
        sys.exit(f"FAIL tag {tag} already exists - bump version= in manifest.xml")
    out_dir = os.path.join(HERE, "..", "release")
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)
    mc = os.path.join(sdk_bin(), "monkeyc.bat")
    key = os.path.join("keys", "developer_key.der")
    assets_ = []
    for p in PRODUCTS:          # -r: strip debug info (release build)
        prg = os.path.join(out_dir, f"SteampunkNixie-{tag}-{p}.prg")
        run([mc, "-r", "-d", p, "-f", "monkey.jungle", "-o", prg, "-y", key], f"release {p}")
        assets_.append(prg)
    iq = os.path.join(out_dir, f"SteampunkNixie-{tag}.iq")     # -e: store package, all products
    run([mc, "-e", "-r", "-f", "monkey.jungle", "-o", iq, "-y", key], "release .iq")
    assets_.append(iq)
    sums = os.path.join(out_dir, "SHA256SUMS.txt")
    with open(sums, "w", newline="\n") as f:
        for a_ in assets_:
            f.write(f"{hashlib.sha256(open(a_, 'rb').read()).hexdigest()}  {os.path.basename(a_)}\n")
    prev = git("describe", "--tags", "--abbrev=0", "HEAD^") if git("tag") else ""
    log = git("log", "--format=- %s", f"{prev}..HEAD" if prev else "HEAD")
    notes = os.path.join(out_dir, "NOTES.md")
    with open(notes, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"""## Steampunk Nixie {tag}

Sideload: download the `.prg` for your watch (`venusq2m` = Venu Sq 2 **Music**, `venusq2` = Venu Sq 2),
plug the watch in over USB and copy it into `GARMIN/APPS` - see
[docs/USER_MANUAL.md](https://github.com/JPTranter/GarminSteampunkWatchface/blob/main/docs/USER_MANUAL.md).
The `.iq` is the Connect IQ Store package. Verify downloads against `SHA256SUMS.txt`.

### Changes{" since " + prev if prev else ""}
{log}
""")
    assets_ += [sums]
    for a_ in assets_:
        print(f"ok   {os.path.basename(a_):40s} {os.path.getsize(a_):7d} B")
    if publish:
        run(["git", "tag", "-a", tag, "-m", f"Steampunk Nixie {tag}"], "tag")
        run(["git", "push", "origin", tag], "push tag")
        run(["gh", "release", "create", tag, *assets_, "--title", f"Steampunk Nixie {tag}",
             "--notes-file", notes], "gh release")
        print(f"ok   published {tag}: " + git("remote", "get-url", "origin").removesuffix(".git")
              + f"/releases/tag/{tag}")
    else:
        print(f"     (dry run - `make.py release --publish` tags {tag} and creates the release)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("step", choices=["assets", "build", "preview", "push", "all", "screenshots",
                                     "release"])
    ap.add_argument("--publish", action="store_true", help="release: tag + GitHub release")
    ap.add_argument("--hr", type=int, help="preview: heart rate to show")
    ap.add_argument("--anim", type=int, help="preview: frames of arc/pulse animation (GIF)")
    a = ap.parse_args()
    extra = (["--hr", str(a.hr)] if a.hr else []) + (["--anim", str(a.anim), "--scale", "1"]
                                                     if a.anim else [])
    if a.step in ("assets", "all"):
        assets()
    if a.step in ("build", "all"):
        build()
    if a.step in ("preview", "all"):
        preview(extra)
    if a.step in ("push", "all"):
        push()
    if a.step == "screenshots":
        out = run([sys.executable, "make_screenshots.py"], "screenshots")
        print("ok   screenshots\n" + out)
    if a.step == "release":
        release(a.publish)
