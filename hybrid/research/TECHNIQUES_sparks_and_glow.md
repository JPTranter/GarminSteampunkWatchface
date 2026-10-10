# TECHNIQUES — Electric Sparks, Lightning Arcs & Glow

Scope: what is actually available for electricity/lightning/sparks in **Blender 4.5.10 LTS**,
and which technique is right for *our* deliverable — a **320 × 360 px Garmin Venu Sq 2 watch-face
PNG**, rendered 3D in Blender (Cycles machine layer + controlled data layer), where arcs **render
last** and everything except the digit glyphs must be real geometry (`SPEC.md`,
`PROJECT_STATUS.md` §"3D / Blender phase").

Everything named below has a URL. Anything I could not verify is marked **UNVERIFIED**.

---

## 1. What ships with our Blender install (verified, not from memory)

Inspected the actual install at
`/c/Program Files/Blender Foundation/Blender 4.5/blender.exe` (`--background --python probe.py`)
and the on-disk `scripts/addons_core/` directory.

- **Version:** Blender 4.5.10 LTS (hash `6dc0b208d1b5`, built 2026-05-19).
- **Bundled add-on modules (14 total):** `bl_pkg`, `copy_global_transform`, `cycles`,
  `hydra_storm`, `io_anim_bvh`, `io_curve_svg`, `io_mesh_uv_layout`, `io_scene_fbx`,
  `io_scene_gltf2`, `node_wrangler`, `pose_library`, `rigify`, `ui_translate`,
  `viewport_vr_preview`.
- **Enabled by default:** `bl_pkg`, `cycles`, the importers (`io_*`), `pose_library`.
- **Nothing electrical, lightning, spark, VFX or fracture-related is bundled.** My memory would have
  said "Cell Fracture is bundled" — it is **not**. `addon_utils.check("object_fracture_cell")`
  returns `(False, False)` on this install. Cell Fracture was moved out of the bundle after 4.1
  and now lives on the Extensions platform: <https://extensions.blender.org/add-ons/cell-fracture>
  (Community, v0.2.1, "part of Blender 4.1 bundled add-ons… now offered as is").
- **Extension repositories registered:** the official remote
  `extensions.blender.org` (`https://extensions.blender.org/api/v1/extensions/`) plus the two
  local repos (`User Default`, `System`). The Extensions system is present and usable, but see §2.
- **Bundled geometry-node assets:** only `datafiles/assets/geometry_nodes/procedural_hair_node_assets.blend`.
  There is **no bundled lightning/arc/spark node group**.
- **Geometry Nodes itself is core**, not an add-on — it is always available, including headless.
- **The compositor Glare node is core** (the bloom path in 4.5; see §5).

**Conclusion for §1:** our install gives us *no* off-the-shelf spark/lightning tooling. We start
from core Geometry Nodes + core compositor, or we install/buy something.

---

## 2. Do actual add-ons for electric arcs / lightning / sparks exist?

### 2a. The official Extensions platform — essentially nothing

Searched the live site (`https://extensions.blender.org/search/?q=lightning` →
**3 results**, all irrelevant: *Retro Console Lite*, *Reference Scale*, *Flat UV Mapper*;
`?q=electric` → **4 results**, all irrelevant: *Bonsai*, *Right-Angled Node Connection*,
*Crunchyroll Dark*, *Reflex Potentials*). Queried the JSON API
(`/api/v1/extensions/?q=lightning`, `…?q=electric`, `…?q=spark`) — no matching add-on.

The Extensions platform is free/open-source, Blender-hosted add-ons only. **There is no electric-arc /
lightning / spark add-on on it.** This is the strongest signal: the "official plug-in store" answer is
*no*.

### 2b. Real (paid/free) third-party tools that do exist

| Name | Author | Where | Price | Type | Blender version claims | Maintained? | URL |
|---|---|---|---|---|---|---|---|
| **Electrify – Quick Lightning** | CGI Forge (Robin Pittelkow) | Superhive (ex-Blender Market) | **$14.99** (often $11.99) | **True add-on** (Extension-compatible, GPL) | **2.8 – 5.1** | Published 5+ yrs ago, "free lifelong updates"; 300+ sales, 3 ratings | <https://superhivemarket.com/products/electrify-quick-lightning> |
| **Arc Forge – Procedural Electric Arc Generator** | (Superhive seller) | Superhive | **$4 / $3** | Geometry-Nodes setup (no install) | **4.0 – 5.2** | Published ~3 months ago | <https://superhivemarket.com/products/arc-forge-procedural-electric-arc-generator> |
| **AA LightningGen – Procedural Lightning** | Artem Yakovlev ("AA – Artem Academy") | Superhive | **$5** | Geometry-Nodes project (`no add-on installation required`) | Tested **Blender 5.2** | Recent | <https://superhivemarket.com/products/aa-lightninggen> |
| **Lightning Tools for Blender** | Joey Carlino | Gumroad | **$5+** (name-your-price) | Geometry-Nodes `.blend` (Electricity Arc Gen + Lightning Strike Gen) + old modifier models | Made for 3.1; **tested 4.4** | Updated 2022; 1,503 sales, 4.8★, CC BY 4.0 | <https://joeycarlino.gumroad.com/l/Yrvbg> |
| **Lightning Bolts Generator V4** | Cartesian Caramel | Gumroad | **$0** (free) | Geometry-Nodes modifiers | V4 current (older listing lists 3.2–3.6) | Active creator | <https://bbbn19.gumroad.com/l/jCoDy> |
| **Lightning Toolsuite** | Riley Rivera | Gumroad (via BlendAtlas) | **$10** | Geometry-Nodes generators (surface aura, directed bolts, contact arcs, strikes, drawn splines + spark generator + finalizer) | **UNVERIFIED** version range | Recent | <https://blendatlas.com/products/lightning-toolsuite> → <https://anticode403.gumroad.com/l/lightning_generators> |
| **Lightning Strike Generator** (add-on) | divolgin | GitHub | **Free** (open source) | **True add-on** — generates/animates strikes à la Blender Guru, with branches/levels/flash seeds | Era of Blender Guru 2.9x tutorial; **UNVERIFIED for 4.5** | Repo, no recent activity shown | <https://github.com/divolgin/lightning> |
| **Lightning Strike with Sparks** | Bipro Fx | Blendkit | **Free** (royalty free) | Geometry-Nodes node group incl. impact sparks | **UNVERIFIED** version | — | <https://www.blendkit.com/asset-gallery-detail/f09bed04-bb4a-4e5b-9568-98095ee51177/> |
| **Electricity FX Pack V3** | "AAA" | Superhive | **$15** | Models/assets (not a generator) | 4.3 – 5.0 | ~2 yrs old, 200+ sales | <https://superhivemarket.com/products/electricity-fx-pack-v3> |

Also present in the same category (names verified via BlendAtlas listings): **Pro Thunder** (Cosmo
Mídias, $5, GN) and **Lightning Power FX** — <https://blendatlas.com/products/lightning-toolsuite>.

**Honest read of §2:**

- Almost all of these are **Geometry-Nodes `.blend` setups, not add-ons.** They add a modifier you
  append; they are *content*, not tooling. "Through a Blender plug-in" is therefore already a
  mischaracterisation of what is on offer.
- The only **true add-on** worth the name is **Electrify** ($14.99) — and it is a **generator** (builds
  bezier/simple/branched/random/low-poly lightning objects), 5 years old, not a look/VFX system, and
  it targets the classic tube-and-branch look, not the fine blue-white spidery fork our round-6 faces
  already have. `divolgin/lightning` is a free add-on but is an old struck-bolt generator, unverified on 4.5.
- Nothing here gives us anything we cannot build in ~30 nodes, and all of it introduces version risk
  (a 3.x/4.x `.blend` node group loaded headless in 4.5.10).
- **No add-on on the official Extensions platform. No dedicated "spark add-on" anywhere.** The one
  genuinely useful, category-correct free asset is a **node group** (Cartesian Caramel / Blendkit).

---

## 3. How lightning/arcs are actually done WITHOUT an add-on (the real answer)

Four established techniques. The first is the one the community actually uses.

### 3a. Geometry-Nodes procedural branching (recommended)

The canonical breakdown is Joey Carlino's **"Realistic Lightning with Geometry Nodes"**
(Blender 3.1, still the reference): <https://www.youtube.com/watch?v=r_J8i1eChBs>.
Confirmed node-by-node in the transcript:

1. **Base curve** — a straight 2-point bezier with **vector handles** (V) so it stays straight; or draw
   a guide curve in Edit Mode (T = draw panel). The guide defines where the strike goes.
2. **Resample Curve** set to **Length** (not Count), step ≈ 0.01 m — you need resolution before noise.
3. **Distort** — `Set Position` offset by a **Noise Texture**: noise colour → Vector Math (Scale) for
   strength; a second Vector Math **Subtract 0.5** so the curve does not drift; and **capture the
   Spline Parameter / Factor *before* the trim** (`Capture Attribute`) so the endpoints are pinned
   (factor multiplied into the offset; a **Float Curve** pins both ends to zero). Noise scale ~1–4,
   **detail ~10** for the jagged read; 4D + W offset varies the shape per seed.
4. **Trim Curve** — the growth animation is a single "End" slider. Because the factor was captured
   pre-trim, branches stay anchored.
5. **Taper / thickness hierarchy** — `Set Curve Radius` driven by **Spline Length** (via Map Range,
   unclamped): the main bolt is thickest, branches progressively thinner, tips near zero. This is what
   makes a fork read as a fork rather than a uniform tube.
6. **Curve to Mesh** with a tiny circle profile (resolution 3 → basically a triangular cross-section,
   radius ~0.01) — cheap geometry.
7. **Branches** — instance trimmed copies of the bolt onto sample points along the parent, then feed the
   whole thing back into the group for **2–4 levels** (a group + a Switch for depth). Each level uses
   its own float curve, noise seed and Map Range so levels don't look alike. The "flash" is a Switch
   when the bolt is at max length → bright emission burst → fade.

**How to get the fork/spider look rather than a smooth tube** (community consensus, cross-checked on
Blender Artists <https://blenderartists.org/t/procedural-lightning/1580821> — whose author lays the
process out as: line → bends → large branches in the bolt's direction → smaller branches → more curve
→ small noise → convert to mesh *keeping the main bolt largest and thus brightest*):

- **Multiple discrete branch levels** (2–4), each shorter and thinner, oriented along a perturbed copy
  of the parent direction — not one noisy tube.
- **Aggressive taper:** main bolt thick, each fork roughly half again as thin, tips → ~0.
- **High noise detail (≈10) with low scale**, applied *after* resampling, so you get angular kinks, not
  a sine wave. Vector/extrapolated handles and flat shading help the spiky look.
- **Branch density high enough to overlap**, so the silhouette is a web of tips — exactly the "4–10
  branch tips per side, 5–6 fork points" property our round-6 bolts already scored.
- Keep the **main bolt's radius/brightness greatest**; the eye reads hierarchy from thickness+glow.

### 3b. Modifier method (no Geometry Nodes)

Blender Guru's **"How to Make Lightning, The Procedural Way"** (2.90):
<https://www.youtube.com/watch?v=LB0dphDcC7g> — full transcript summarised at
<https://videodb.org/how-to-make-lightning-the-procedural-way-blender-290/dblHLxyE7BU>.

Recipe: a single edge (plane → M collapse → extrude 10 m → 7 loop cuts) → stack **Displace** modifiers
with a **Cloud texture** on X, then Y, then Z (size ~1–1.5, depth controls noisiness, Z weaker) using an
**empty** as the *Object* texture coordinate so you can art-direct the shape → **Skin** modifier *after*
the displaces for thickness → **Subdivision Surface** → a **vertex group on the tip vertex** ("focus",
weight 1, inverted on each Displace) to pin the strike point → proportional-edit scale of the tip to 0 for
taper. Extrude extra points in Edit Mode for branches and scale *those* tips to zero. Parent the empties
to a control circle so the whole bolt is poseable. This gives **smooth local curvature + jitter** well, but
**true recursive forks are manual** — hence it is a fallback, not the primary.

### 3c. Curve + noise displacement + bevel

Simplest variant: a bezier path, `Bevel` depth for a tube, a `Displace` modifier with noise for jitter.
Fine for a single smooth arc; no branching. Mentioned only for completeness.

### 3d. Grease Pencil

Martin Klekner's **"Animated Lightning in Blender"**: <https://www.youtube.com/watch?v=oE-vT1ekvrs> —
draw strokes, Thickness + Opacity modifiers, the **Glow** visual effect
(<https://docs.blender.org/manual/en/latest/grease_pencil/visual_effects/glow.html>), compositing.
2D strokes, not real geometry — **conflicts with our "real geometry, no overlays" rule**, so reject for us.

### 3e. Ready-made free/cheap GN node groups (shortcut)

Same URLs as §2b: Cartesian Caramel **Lightning Bolts Generator V4 (free)**, Blendkit **Lightning Strike
with Sparks (free)**, Arc Forge **$3–4**, AA LightningGen **$5**, Joey Carlino **$5+**. Useful as a
**reference to read** or a time-boxed shortcut; you inherit their look and their version compatibility.

---

## 4. Spark showers (particles flying off a contact point)

Standard approach, confirmed from Blender Guru's **"How to Make Sparks"**
(<https://blenderguru.com/tutorials/how-to-make-sparks>) and the community walkthrough
(<https://youtube.com/watch?v=8XFz-wqv3Kc>), plus the API sketch at
<https://shreyakapoor18.github.io/posts/2026-06-14-blender-python-vfx>:

1. **Emitter**: a point, or a small sphere / the tip of the arc curve. Particle system, type **Emitter**.
   Emit from faces/volume; `use_emit_random`; frame Start/End matched to the strike; **lifetime** ~30
   with **lifetime_random ~0.3–0.5** so sparks die at different times.
2. **Tiny emissive geometry, not halos**: Render as **Object** → a small **Icosphere** (scale ~0.04–0.2)
   with an **Emission** material. Emission **Strength ≈ 15–40** (community sweet spot ~25) so it blooms in
   the compositor and, in Cycles, spills real light onto the surrounding brass. Halos/billboards work but
   look flatter.
3. **Motion**: `normal_factor` (initial outward velocity, ~2.5–4), `factor_random` (~1.0–1.2) so they
   aren't a uniform spray, `drag_factor` (small, so they decelerate like debris), and **gravity** (a
   Gravity force field, or the particle Newtonian physics). A **collision plane** with Damping and
   Stickiness ~0.2 makes sparks bounce and "stick" like real metal spatter.
4. **Size variation**: `size` + `size_random ~0.5`; use a **Particle Info → Lifetime** factor through a
   **Color Ramp** to shrink/brighten the spark over its life (this was the breakthrough in Blender Guru's
   tutorial — before the Particle Info node you could not fade sparks).
5. **Motion blur**: enable render **Motion Blur** with a shutter; this turns each tiny sphere into the
   characteristic **streak/trail** and is what actually sells sparks. It is a *render* setting, so it must
   be on in the final frame — Blender Guru explicitly closes his sparks tutorial with "Using Motion Blur".
6. **Bloom**: last, in the compositor (§5) — never bake a glow sprite into the spark material.
7. **Cheap alternative**: instead of a sim, instance a handful of short tapered curve slivers with random
   directions and a **frame-locked seed** — for a still watch face this is just as readable and has zero
   simulation cost.

**Settings that matter most, in order:** lifetime + lifetime_random (spread of deaths), normal/factor_random
(the spray cone), gravity + drag (the arc of the shower), emission strength (whether it blooms), and motion
blur shutter (the streak). Particle count matters least.

---

## 5. Compositing the glow — the Glare node in Blender 4.5

Authoritative: **Blender 4.5 LTS Manual — Glare Node**
<https://docs.blender.org/manual/en/4.5/compositing/types/filter/glare.html>; API
<https://docs.blender.org/api/4.5/bpy.types.CompositorNodeGlare.html>. Note the 4.5 manual's
EEVEE "Bloom" panel page **does not exist** (`/render/eevee/render_settings/bloom.html` → 404): EEVEE
Next (4.2+) removed the legacy bloom checkbox, so **the compositor Glare node is now the glow path for
*both* Cycles and EEVEE.** Do not plan on an EEVEE bloom toggle.

`glare_type` ∈ `BLOOM`, `GHOSTS`, `STREAKS`, `FOG_GLOW`, `SIMPLE_STAR`.

| Type | What it does | Cost | Notes for a small bright source |
|---|---|---|---|
| **BLOOM** | Soft glow around bright areas (eye/lens scattering). | Cheapest | In 4.5 energy-conserving and better-ranged; **Size still limited to discrete steps**, unlike Fog Glow. Fine default. |
| **FOG_GLOW** | "More physically accurate version of Bloom" — softer, more realistic halo. | Slow (iterative) | **Continuous Size** in 4.5 (linear 0–1, relative to image). **Best for a small hot source.** |
| **STREAKS** | Bright streaks radiating from highlights = lens flare / anamorphic spikes. | Medium | `Streaks` count, `Streaks Angle`, `Fade`, `Iterations`. Reads as *camera/lens*, not as the light itself — use sparingly, if at all, on a watch face. |
| **GHOSTS** | Overlapping lens-reflection artefacts / hazy glow. | Medium | `Iterations` = ghosts; `Color Modulation` for chromatic dispersion. |
| **SIMPLE_STAR** | Star-shaped streaks. | Cheap | `Fade`, `Diagonal`. Decorative; not physical. |

**Parameters that matter (4.5):**

- **Highlights → Threshold**: minimum luminance to contribute. *This is the single most important knob:*
  set it just below the arc's emissive peak so the **arc core blooms but the brass, enamel and digits do
  not**. Lower = more of the image glows (mushy); higher = only the hottest pixels.
- **Highlights → Smoothness**: how gradually pixels enter the effect (avoids a hard cut-out edge).
- **Highlights → Clamp / Maximum**: caps highlight intensity — keeps bloom consistent when luminance
  varies; useful to stop one blown pixel dominating.
- **Adjust → Strength**: replaces the old **Mix**. `>1` boosts the glare, `<1` blends it back; this is how
  you dial the glow without extra nodes. (In pre-4.5 the Mix scale was `-1 … 1`; if you follow an old
  tutorial, the numbers have been re-versioned and are *not* 1:1 — see the 4.5 render-compositor
  change notes at <https://devtalk.blender.org/t/improved-render-compositor-feedback-and-discussion/33377/62>).
- **Adjust → Saturation / Tint**: colour the glow; a slightly cool tint on a white-hot core reads as
  electric, and matches our round-6 white-core/blue-sheath measurement.
- **Glare → Size**: now **0–1 linear, relative to image size** (1 = covers the whole frame). At
  **320 × 360** this is the pixel-budget control: keep it small (~0.05–0.15) so the halo is a few pixels
  and never washes the plate.
- **Quality**: High / Medium / Low — lower runs on a reduced-resolution copy (faster, but the glow
  *spreads differently*, so lock it to **High** for finals).
- **Outputs**: `Image` (composited), **`Glare`** (the glow alone), **`Highlights`** (the extracted bright
  pixels). The separate `Glare` output lets you grade the glow independently and **Add** it back over the
  clamped plate — the manual notes a plain Add is usually physically correct because light adds.

**Making the glow physical, not painted** (community consensus, e.g.
<https://artisticrender.com/how-to-use-bloom-with-cycles-in-blender/>,
<https://brandon3d.com/blender-add-bloom-glow-effect-eevee-and-cycles/>):

- The Glare node is a **post-process on real luminance** — it only blooms pixels that are actually
  brighter than Threshold. So the physical part is **emissive geometry at real strength (15–40)** plus, in
  Cycles, the **light that geometry spills onto neighbouring metal**.
- **Don't paint a halo** into the material and don't use a glow sprite: it reads as a sticker. Let the
  emission overshoot white and let Glare — and Cycles' GI — do the bloom.
- **Order:** render → Glare (Fog Glow, Quality High) → optionally split `Glare` output to a separate
  grade / mask → Composite. Keep the arcs and sparks on their **own render layer/pass** (the Blender Guru
  glow method relies on isolating the lightning in its own layer) so the threshold can be tuned without
  touching the machine layer or the digits.

**Recommendation for our case:** **FOG_GLOW, Quality High, Size small (≈0.05–0.12), Threshold set just
under the arc core's value, Strength ~1–4, slight cool Tint**, glow added over the machine layer, and
arcs/sparks isolated on their own layer so the data layer's contrast is bit-identical to the approved
round-6 faces.

---

## Recommendation table

| Technique | What it gives | Cost / complexity | Verdict for our case |
|---|---|---|---|
| **Purpose-built Geometry-Nodes branching group** (base curve → resample → noise `Set Position` → `Trim Curve` → radius taper by spline length → `Curve to Mesh` → recursive branch levels) | Exact control of fork count, taper, spikiness, seed and pixel budget; deterministic; headless-safe; free | Medium (≈30 nodes, one group, reusable across components) | **BUILD THIS — primary path** for the arcs |
| **Free/cheap GN node groups** (Cartesian Caramel $0, Blendkit free, Arc Forge $3–4, AA LightningGen $5, Joey Carlino $5+) | Instant lightning/arcs/sparks without authoring nodes | Low money, high look-risk; version risk loading into 4.5.10 | **Reference / fallback** if time-boxed — read them, don't depend on them |
| **Modifier method** (edge + stacked Displace cloud textures X/Y/Z + Skin + Subsurf + tip vertex group) | Smooth tube with controllable jitter | Low; no GN knowledge | **Fallback** — weak on true recursive forks |
| **Particle sparks** (point emitter, object-rendered tiny emissive Icosphere, gravity + drag + randomness, Particle-Info fade, motion blur) | A real spark shower off a contact point | Low–medium; needs motion blur + a sim cache | **USE for the spark showers** (or the frame-locked curve-sliver variant for a still) |
| **Grease Pencil + Glow VFX** | 2D drawn lightning, fast | Low | **Reject** — not real geometry; violates our no-overlay rule |
| **True add-on install** (Electrify $14.99; divolgin/lightning free) | A one-click lightning *generator* | ~$15 or a legacy install; version risk | **Not worth it** — see verdict |
| **Glare node (FOG_GLOW) + emissive geometry** | Physical bloom on the real arc/spark luminance | Trivial | **DO THIS** — the glow step, both engines, Blender 4.5 |

---

## Sources

- Blender 4.5 Glare Node manual — <https://docs.blender.org/manual/en/4.5/compositing/types/filter/glare.html>
- Glare API (`glare_type`, deprecated Mix/size) — <https://docs.blender.org/api/4.5/bpy.types.CompositorNodeGlare.html>
- 4.5 render-compositor Glare changes (Strength replaces Mix; Size 0–1) — <https://devtalk.blender.org/t/improved-render-compositor-feedback-and-discussion/33377/62>
- Cycles bloom via Glare — <https://artisticrender.com/how-to-use-bloom-with-cycles-in-blender/> · <https://brandon3d.com/blender-add-bloom-glow-effect-eevee-and-cycles/>
- Cell Fracture on the Extensions platform (was bundled ≤4.1) — <https://extensions.blender.org/add-ons/cell-fracture>
- Extensions platform — <https://extensions.blender.org/> · search "lightning" — <https://extensions.blender.org/search/?q=lightning> · "electric" — <https://extensions.blender.org/search/?q=electric>
- EEVEE Next 4.2 rewrite (no legacy bloom panel) — <https://developer.blender.org/docs/release_notes/4.2/eevee/>
- GN lightning, node-by-node — <https://www.youtube.com/watch?v=r_J8i1eChBs>
- Blender Artists procedural lightning build order — <https://blenderartists.org/t/procedural-lightning/1580821>
- Modifier-method lightning (Blender Guru 2.90), transcript — <https://videodb.org/how-to-make-lightning-the-procedural-way-blender-290/dblHLxyE7BU>
- Sparks tutorial (Particle Info fade, motion blur) — <https://blenderguru.com/tutorials/how-to-make-sparks> · <https://youtube.com/watch?v=8XFz-wqv3Kc>
- Grease Pencil lightning + Glow VFX — <https://www.youtube.com/watch?v=oE-vT1ekvrs> · <https://docs.blender.org/manual/en/latest/grease_pencil/visual_effects/glow.html>
- Candidates: Electrify — <https://superhivemarket.com/products/electrify-quick-lightning> · Arc Forge — <https://superhivemarket.com/products/arc-forge-procedural-electric-arc-generator> · AA LightningGen — <https://superhivemarket.com/products/aa-lightninggen> · Joey Carlino — <https://joeycarlino.gumroad.com/l/Yrvbg> · Cartesian Caramel V4 — <https://bbbn19.gumroad.com/l/jCoDy> · Lightning Toolsuite — <https://blendatlas.com/products/lightning-toolsuite> · divolgin add-on — <https://github.com/divolgin/lightning> · Blendkit node group — <https://www.blendkit.com/asset-gallery-detail/f09bed04-bb4a-4e5b-9568-98095ee51177/>
