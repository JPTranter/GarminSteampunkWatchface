# SPIKE 001 — Blender/Cycles photoreal watch face

**Question.** Can a real raytracer give us the photorealism the procedural PIL pipeline could
not (PBR brass, glass refraction, volumetric glow, physical bloom, depth of field) *without*
breaking the frozen readability bar (digit ink heights, and contrast ≥12:1 at a 16 px ring)?

**Answer: PARTIAL.** The materials are a decisive upgrade. The **data does not survive**, and
the reason is physics, not a bug — so the correct build is a hybrid, not a rewrite.

---

## Environment (verified on this machine)

| Item | Result |
|---|---|
| Blender | 4.5.10 LTS, installed via `winget install --id BlenderFoundation.Blender.LTS.4.5` |
| Renderer | Cycles, CPU. Also exposes a **HIP** device (Radeon 890M) — unused, not needed |
| Speed | 1280×1440 @48 samples + denoise ≈ **37-50 s**; 640×720 @64 ≈ 6 s |
| Stage | Orthographic camera, `ortho_scale=3.2`, so **1 px = 0.01 world units** exactly, letting
the Blender scene share the 2D layouts' coordinates. Rendered at 4× and LANCZOS-downsampled. |

## What was tried, and what each attempt proved

| Ver | Change | Result |
|---|---|---|
| v1 `scene.py` | First scene | **Broken.** Two geometry bugs (below). Produced a grey slab. |
| v2 `scene_v2.py` | Hollow tubes, corrected layers, AgX tonemap | Structure correct: glass tubes, brass, bolts, haze all render. **Digits smeared into vertical blobs** — no readable numerals. 16 px-ring contrast ≈ **3.0:1**. |
| v3 `scene_v3.py` | Cathode moved to the front glass wall; Standard tonemap; hotter emission; haze confined to the gutters | Digits **clipped to pure white and flooded by their own bloom**; the centre of the face blew out. Contrast ≈ **2.6:1**. |
| v4 `scene_v4.py` | Data as **matte paint lit from inside each tube** (emission 0), so it never enters the bloom pass; AgX restored | Best exposure of the four, materials excellent. **Still not readable**: numerals refracted into vertical smears, 16 px-ring contrast ≈ **2.9:1**; `8,342` measured essentially zero ink. |

### Measured (v4, tight boxes around each datum, on the 320×360 result)

| region | ink height | contrast @2 px | @6 px | @16 px |
|---|---|---|---|---|
| tube digit `1` | 58 px | 1.70 | 2.76 | **2.98** |
| tube digit `0` | 58 px | 1.62 | 2.43 | 2.89 |
| heart rate `72` | 38 px | 1.52 | 2.57 | 3.77 |
| steps `8,342` | **2 px** | 1.62 | 2.12 | 3.07 |
| date `30` | 38 px | 1.54 | 2.36 | 3.93 |

Frozen bar: time ≥44 px ink at ≥12:1 @16 px, date ≥16, HR ≥16, steps ≥18. **Nothing passes on
contrast**; the best is 3.9:1 against a 12:1 requirement.

## Verdict: PARTIAL

### What worked
- **Brass and copper are now real metal.** PBR metallic/roughness with a directional key light
  gives specular highlights the procedural pipeline could never fake.
- **Glass is genuinely glass**: IOR 1.44, transmission, refraction, real edge highlights.
- **Bloom is physical**, not painted — the electric bolts are emissive geometry and the Glare
  node blooms them with correct falloff.
- **Volumetric haze** exists in-engine, confined to the gutters.
- Headless, scriptable, fast: ~40 s per 4× frame on CPU, no GPU required.

### What didn't
- **Self-luminous data cannot hold a contrast bar in this environment.** Two opposite failures:
  AgX tonemapping compresses emissive digits to pale grey; Standard tonemapping clips them to
  white where their own bloom then floods the face.
- **Glass refraction destroys a numeral behind it.** A 51 px glyph sitting mid-depth in a
  cylindrical tube is smeared into a vertical streak by the curved wall acting as a lens —
  moving the cathode to the front wall reduced but did not remove it.
- Making the data a *lit surface* rather than a light source (v4) fixed the blowout but not the
  legibility: it is still refracted, and it is now lit through the same glass.

### Surprises (the reusable part)
1. **`--background` loads Blender's default startup scene** (Cube + Camera + Light). The default
   Cube enclosed the whole test scene and rendered as a flat grey slab. Call
   `bpy.ops.wm.read_factory_settings(use_empty=True)` first, always.
2. **Blender resolves a relative render filepath against its own CWD**, not the script's — it
   wrote to `C:\probe_out.png` and failed with "Permission denied". Use absolute paths.
3. **Axis mistaken for depth.** The camera looks down **+Y**, so the screen vertical is **Z**,
   and view depth is **Y**. Rotating a cylinder 90° about X to "lay it down" makes its length run
   *into* the screen: a 150 px deep solid glass rod that swallowed the digits. Tubes take the
   default Z axis; only camera-facing discs take `axis='Y'`.
4. **Smaller y is nearer the camera.** Emissive digits placed at y=+0.06 sat *inside* the solid
   box of the plate meant to carry them, so the plate occluded its own data.
5. **A nixie tube must be a shell.** A solid glass cylinder embeds the cathode in glass; use an
   open cylinder + Solidify for wall thickness.
6. **Tone mapping is a legibility decision, not a look.** AgX/Filmic roll off highlights (good
   for metal, fatal for data); Standard keeps data white but clips it. Neither is right when the
   data is the light source.
7. **Measure the datum, not its container.** Boxes spanning a whole tube returned `ink_height=145`
   for a 51 px digit — the mask was catching the bright glass wall. Tight boxes around the glyph
   are mandatory, or every number is meaningless.
8. **Bloom thresholds and emission strengths are coupled.** Raise emission and the data enters
   the bloom pass; lower the threshold and the machine blooms too. There is no single setting
   that keeps a light-emitting datum crisp *and* a glowing tube atmospheric.

## Recommendation for the real build — hybrid, not a rewrite

The spike invalidates "render everything in Blender", not "use Blender". The machine and the
data have opposing optical requirements, so **split them**:

1. **Cycles renders the MACHINE ONLY** — brass, copper, glass tubes, arcs, bloom, volumetric
   haze, lighting, depth of field. No data objects in the scene at all. This is where every
   realism gain lives, and nothing about it needs to be legible.
2. **Data is composited in a controlled pass** — the numerals drawn (procedurally or as a second
   render with no bloom and a flat render pass, e.g. Cycles' Emission-only pass) and placed on
   the machine layer at known ink heights.
3. **The existing verification harness gates the composite** — ink heights, contrast at the
   2/6/16 px rings, clearance, safe area. It already catches exactly what a photoreal render
   silently ruins, and this spike is the proof: it reported 2.9:1 where the eye guessed "fine".
4. **Optionally** add a bloom-masked pass so the glow spills around the data rather than over it
   (bloom the machine layer, then composite the data on top).

Estimated effort: the Blender scene is already written and fast; the remaining work is the
compositing pass and a re-run of the loop against the existing rubric. Expect a large realism
gain over the procedural faces at **no cost to the readability bar**.
