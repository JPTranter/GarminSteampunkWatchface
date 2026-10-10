# Connect IQ Store submission

Everything needed to publish **Steampunk Nixie** in the Garmin Connect IQ Store. The upload
needs **your** Garmin developer account, so it's done by hand. These steps reflect Garmin's
developer portal at the time of writing. If a screen differs, follow the portal; the inputs
below don't change.

## What you upload

| Item | File | Notes |
|---|---|---|
| App package | `release/SteampunkNixie-vX.Y.Z.iq` | From `python ciq/make.py release`. One signed `.iq` holds both Venu Sq 2 builds. |
| **Cover image** | `docs/store/upload/cover_640x720.jpg` | 640×720, ~210 KB (limit 300 KB): the face alone. |
| **Screenshots** | `docs/store/upload/screenshot_1..3_320x360.jpg` | 320×360, the device's own resolution, ~88 KB each (limit 150 KB): resting, workout, peak heart rate. |
| Full-quality PNGs | `docs/store/*.png` | The same images lossless, for anywhere without a size limit. |
| **Hero image** | `docs/store/upload/hero_1440x720.jpg` (~232 KB; PNG: `docs/store/hero_1440x720.png`) | 1440×720, the size the store's app upload asks for: title + tagline + the face mid-strike. (`hero.png`, 640×720, is the face alone.) |
| App icon | built into the `.iq` | `ciq/resources/drawables/launcher_icon.png` (40×40). |
| Listing text | [LISTING.md](LISTING.md) | Title, short and long description, permission note. |

Regenerate the images any time with `python ciq/make.py screenshots`. They're rendered as the
face looks on the watch, because the raw frame is pre-corrected for the AMOLED and looks
yellow-green on a monitor.

## Before the first upload

1. **Back up the signing key** (`ciq/keys/developer_key.der` and `.pem`) somewhere safe. Every
   future update of this store listing must be signed with the same key.
2. Make sure `version="X.Y.Z"` in `ciq/manifest.xml` is the version you mean to publish.
   Store updates need a higher version each time.
3. Build the package from a clean, committed tree: `python ciq/make.py release` (or
   `--publish` to also create the GitHub release).

## Upload

1. Sign in at <https://apps.garmin.com/developer/> with your Garmin account. The first time,
   accept the Connect IQ developer agreement.
2. Choose **Upload an App**, then select `release/SteampunkNixie-vX.Y.Z.iq`. The portal reads the
   app type (watch face), the supported devices (Venu Sq 2, Venu Sq 2 Music) and the
   permissions from the package.
3. Fill in the listing from [LISTING.md](LISTING.md): title, descriptions, category **Watch
   Faces**, and price **free**.
4. Add the three screenshots and the hero image from `docs/store/`.
5. On the permissions step, the package requests **UserProfile**. Use the justification in
   LISTING.md.
6. Submit for review. Garmin reviews new apps before they appear, usually within a few days;
   you'll get an email either way.

## Updating later

Bump the version in `ciq/manifest.xml`, commit, run `python ciq/make.py release --publish`, then
in the developer portal open the app and **Upload a new version** with the new `.iq`, signed
with the **same** key.
