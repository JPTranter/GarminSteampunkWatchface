# Techniques — Nixie glass envelope & brass socket (Blender / Cycles 4.x)

Scope: modelling the glass envelope, glass shading, the emissive plasma discharge, ghost
cathodes, and the brass socket/base. Research-only synthesis for a photoreal nixie watch face.
Every number is cited; anything not found in a written source is marked **UNVERIFIED**.

Reference dimensions used throughout (IN-12 / IN-12B, the tube family the moodboard is closest to):
overall height ≈ 35 mm, body diameter ≈ 30 mm at the widest point, symbol (digit) height ≈ 18–19 mm,
14 pins, pin diameter ≈ 1.02 mm.
Sources: https://docs.omnixie.com/in12.html , http://industrialalchemy.org/articleview.php?item=1010 ,
https://download.mikroe.com/documents/datasheets/Nixie_IN-12B_datasheet.pdf ,
https://shopabunda.com/products/6-pcs-lot-nos-vintage-neon-nixie-tube-in-12-in-12a
(these disagree slightly on total height: 35 mm vs 55 mm depending on whether the pin length is
included — omnixie says 35 mm total, lavky lists "19 × 55 mm" incl. pins).

---

## 1. Modelling the glass envelope

### Recommended approach — profile + lathe (Spin), then Solidify

1. Work from an orthographic reference. Blender Artists/FactoryRestart workaround: import the
   reference photo with `Add > Image > Background`, align view down an orthographic axis
   (`Numpad 3`), snap the 3D cursor to world origin, and "trace" the silhouette.
   https://www.factoryrestart.com/post/series-let-s-build-something-for-the-asset-store-part-3-modeling-the-tube
2. Model **only the outer profile** as a 1D half-silhouette in Edit Mode, then revolve it with the
   **Spin** tool (a lathe). The manual's own worked example is a wine glass and explicitly says:
   "If you are modeling a hollow object, it is a good idea to thicken the outline." Spin rotates
   the selected profile around the 3D cursor about the axis perpendicular to the view; use
   **Angle = 360°** and set **Steps**; then correct the duplicate seam vertices with
   `Merge by Distance` (the manual calls this out as the standard cleanup step).
   https://docs.blender.org/manual/en/latest/modeling/meshes/tools/spin.html
3. Give the tube **real wall thickness** with a **Solidify modifier**, not a modelled double wall.
   Solidify "takes the surface of any mesh and adds depth, thickness to it"; `Thickness` is the
   depth and `Offset` (-1..1) positions the shell inside/outside the original surface (0.0 =
   centred). Two important caveats from the manual: thickness uses **local vertex coordinates**
   (apply/clear object scale first or thickness varies round the tube), and "the final wall
   thickness is not guaranteed and may vary depending on the mesh topology".
   https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/solidify.html
   Typical submitted value for a small object: **0.01–0.02 units**. A hollow object with no
   thickness is treated by Cycles as a *solid block of glass*, which is the classic solid-rod look;
   Solidify is the fix.
   https://housingbasics.com/software-app-operations/general-tech-reference/how-to-make-object-clear-in-blender
   https://blender.stackexchange.com/questions/62330/is-there-a-way-to-make-a-hollow-object-solid
4. **Domed shoulder + drawn-out nipple**: do it in the profile. FactoryRestart's method is a chain
   of repeated `E` (extrude) then `S` (scale) on the top face to "mimic the shape until you reach
   the top" — i.e. build the shoulder and tip as a sequence of profile nodes, then spin. The
   nipple is the profile closing to a near-point; leave one small flat cap.
   https://www.factoryrestart.com/post/series-let-s-build-something-for-the-asset-store-part-3-modeling-the-tube
5. **Avoid the solid-rod look**: keep the wall thickness *small relative to the diameter* (3 mm
   tube → ~0.4–0.7 mm wall would be physical; in Blender use a small Solidify value), keep
   `Roughness ≈ 0` so you actually see feathered refraction, and make sure the *inner* surface
   is visible/closed (Solidify gives you the inner shell automatically). Refraction through two
   close surfaces is what reads as glass; refraction through a single inflated shell reads as a
   solid glass block.
   https://blender.stackexchange.com/questions/62330/is-there-a-way-to-make-a-hollow-object-solid

### Alternative — model the double wall by hand / loft
Duplicate the outer shell, scale it inward, flip the inner normals so they face into the cavity,
then merge the rim. StackExchange presents this as the manual alternative to Solidify.
https://blender.stackexchange.com/questions/62330/is-there-a-way-to-make-a-hollow-object-solid
Curve + bevel is the usual choice for *wire* features (digit electrodes, anode grid), not the
envelope: BlenderArtists' Nixie Tube 2.0 used "curves and plan to bevel them with a 4 vert circle"
for the digits. https://blenderartists.org/t/nixie-tube-2-0/590572

### Inner dark sleeve
Real nixies are not "dark inside"; the dark thing you see is the **stacked electrode assembly and
mica/ceramic spacers**, plus a **wire-mesh/perforated anode** that wraps the digits. Model a
thin dark cylinder/mesh (nickel, roughness ~0.4, dark base colour) slightly inside the glass and
give it the anode-mesh treatment below. Sources:
https://grokipedia.com/page/Nixie_tube
https://www.factoryrestart.com/post/series-let-s-build-something-for-the-asset-store-part-4-modeling-the-characters
**UNVERIFIED**: no source gives a specific colour or thickness for this inner sleeve.

### Pitfall
- Don't leave the envelope a single-sided open shell and then apply a plain glass shader — Cycles
  treats the enclosed volume as solid glass (solid-rod/plastic look). Solidify (or a modelled
  double wall) is mandatory.
- Don't skip `Apply Scale` before Solidify — non-uniform scale makes wall thickness vary.
- Spin leaves a duplicate seam; if you don't `Merge by Distance` you get z-fighting along one line
  of the tube.
- Don't over-subdivide the profile: the spine of the silhouette (shoulder/nipple) should be
  smooth-shaded; a faceted shoulder is the giveaway of a low-poly lathe.

### Minimum viable recipe
Ortho reference image → cylinder or half-profile in Edit Mode → `E`/`S` chain for barrel +
shoulder + nipple → Spin 360° → `Merge by Distance` → **Solidify, Thickness ≈ small (0.01–0.02 in
a unit-scale scene), Offset = -1 or 0** → Shade Smooth + Auto Smooth on the shoulder.

---

## 2. Glass material in Cycles 4.x

### Recommended approach — clean Principled BSDF + the shadow-ray trick

Principled BSDF inputs that matter (Blender manual confirms the semantics):
- **Base Color**: pure/near-white. Any grey "can make the glass look dirty or overly dense".
  https://cookstation.blog/how-to-make-glass-blender
- **Transmission Weight = 1.0** — "Mix between fully opaque surface at zero and fully transmissive
  at one." https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html
- **IOR = 1.45–1.50** for generic glass; the manual notes the default 1.5 "is a good approximation
  for glass". For **borosilicate** use **1.47** (Schott 8347 datasheet: 1.473 @ 587.6 nm;
  a PBR material spec lists refractive_index 1.47). Note the PBR recipe still writes IOR 1.50 in
  code while declaring 1.47 in metadata — pick 1.47 for accuracy.
  https://www.lookpolymers.com/pdf/Schott-Glass-8347-Borosilicate-Glass.pdf
  https://renato.design/formatter-app/materials/glass/mat_borosilicate_glass.html
- **Roughness = 0.0–0.05**; a tested value in a glass-comparison thread was **0.027**.
  https://blenderartists.org/t/glass-in-cycles-what-is-your-best-approach-to-glass-material/1243845
  https://cookstation.blog/make-glass-principled-shader-blender
- **Metallic = 0**.
- **Coat Weight**: leave **0** for clean glass. The manual says coat weight "typically should be
  zero or one for physically-based materials"; a small coat (0.1–0.3 with low roughness) is the
  standard way to add a polish layer on thick decorative glass, but a nixie envelope is bare glass.
  https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html
- **Thin Film**: do **not** enable. It models interference (oil films, soap bubbles); the effect is
  visible only for thickness ≈ **100–1000 nm** and vanishes at film IOR 1.0 or equal to the base
  IOR. A nixie envelope has no film.
  https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html
- **Thin Wall checkbox**: for single-surface sheets. Not needed if you Solidified.

**Shadow problem & the fix.** With pure transmission glass, Cycles produces a black/no-light
shadow because it is trying to compute caustics. The industry fix is a **Mix Shader: Principled
BSDF ↔ Transparent BSDF, Factor = Light Path > Is Shadow Ray**. Glass is then refractive to the
camera/reflections but transparent to shadows — "a standard industry practice for architectural
visualization where render speed and clarity are prioritized". A MixRGB/curve on the factor lets
you restore a chosen amount of shadow darkness.
https://cookstation.blog/how-to-make-glass-blender
https://blenderartists.org/t/shadow-from-glass-material/1369658
https://blender.stackexchange.com/questions/188168/why-does-my-light-source-not-pass-through-my-glass

**`Is Camera Ray` tricks.** Use Light Path > `Is Camera Ray` to swap behaviour between camera and
everything else (e.g. keep an emissive surface visible to the camera but suppress its contribution
elsewhere, or make a glass object invisible to camera but still refract). The manual lists
`Is Camera Ray`, `Is Shadow Ray`, `Is Diffuse Ray`, `Is Glossy Ray` (1.0/0.0 flags) as
"particularly useful for non-physically-based tricks".
https://docs.blender.org/manual/en/latest/render/shader_nodes/input/light_path.html
Note the known limitation: Light Path node ray flags are unreliable for **emission** shaders (the
Devs state the info isn't available without evaluating the shader multiple times).
https://blenderartists.org/t/cycles-light-path-diffuse-ray-doesnt-work-with-emission-shaders/1287929

**Volume Absorption inside the wall.** Connect a Volume Absorption node to the Material Output
*Volume* socket to tint thick regions (the classic green/teal glass edge): cyan absorption colour
with **Anisotropy = 1** is the iMeshh recipe.
https://blog.imeshh.com/index.php/2022/05/19/glass-in-blender-3-0  (page was re-skinned and the
glass article body is no longer retrievable — treat that specific node value as **UNVERIFIED**)
Density is an **attenuation coefficient with units of 1/scene-unit** (1/m if 1 unit = 1 m):
transmitted intensity ≈ `exp(-length · density · (1-color))`. This is critical at nixie scale —
a fog density of 0.015 that works for a room-scale world is far too low for a 3 cm tube.
https://devtalk.blender.org/t/physical-units-on-volume-scatter-and-volume-absorption/28572
https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/volume_absorption.html

**Render-time controls**
- **Bounces**: raise Total/Glossy/Transmission to at least **12–16**; low bounces make glass
  render black. https://cookstation.blog/how-to-make-glass-blender
- **Filter Glossy**: 0.2 or higher (manual says "1.0 is a good starting value to tweak") blurs
  glossy bounces to reduce caustic noise. https://docs.blender.org/manual/en/latest/render/cycles/render_settings/light_paths.html
- **Clamp Indirect** (default 10) keeps fireflies down; clamping was how one artist avoided
  fireflies from an over-bright glass colour. https://blenderartists.org/t/glass-in-cycles-what-is-your-best-approach-to-glass-material/1243845
- **Caustics**: leave reflective/refractive caustics OFF for speed; if you want real shadow
  caustics use **MNEE shadow caustics** — tick Shadow Caustics on the light, **Cast Shadow
  Caustics** on the glass, **Receive Shadow Caustics** on the floor/socket, and give the glass
  **smooth normals**. Documented limits: only *refractive caustics inside shadows* are handled;
  max 6 caustic-caster surfaces per path; Filter Glossy is ignored under MNEE; results are
  approximate. https://docs.blender.org/manual/en/latest/render/cycles/object_settings/object_data.html
  https://blender.stackexchange.com/questions/272147/how-can-i-render-caustic-using-only-the-cycles-render-engine

### Alternative — "fake glass" (Glossy + Transparent mix)
Skip refraction entirely: mix a Glossy BSDF with a Transparent BSDF. It renders dramatically faster
and was recommended for a light-bulb envelope specifically because the inner glass "if it stays as
a glass shader, is nearly black". The refraction is lost but for a small tube seen at a soft angle
it can be invisible.
https://blender.stackexchange.com/questions/56647/glass-render-problem
Also common: per-object **Object Properties > Visibility > Ray Visibility**, untick **Shadow**
(and Diffuse) on the glass instead of using the node trick — simpler, but no control over shadow
density. https://blog.imeshh.com/index.php/2022/05/19/glass-in-blender-3-0

### Pitfall
- Pure transmission + caustics is slow and dark; don't chase physically-correct caustics unless
  you enable MNEE shadow caustics with the right flags *and* smooth normals.
- Adding a Volume Absorption with room-scale density inside a 3 cm tube does nothing visible;
  density must scale with the object (**UNVERIFIED** exact value — derive from the 1/unit relation:
  for a ~3 cm path you need density on the order of **20–100** to get an O(1) effect).
- Non-uniform object scale breaks both Solidify and IOR/absorption scaling.
- Don't enable Thin Film or Coat on the clean envelope — it reads as plastic/coated glass.

### Minimum viable recipe
Principled: Base Color white, Metallic 0, **Transmission Weight 1.0**, **Roughness 0.02–0.05**,
**IOR 1.47**. Mix with Transparent BSDF via **Is Shadow Ray**. Total/Glossy/Transmission bounces
≥ 12. Filter Glossy 0.5, Clamp Indirect 10, caustics off. Optionally add Volume Absorption with a
high density for a faint teal edge.

---

## 3. The glowing cathode / plasma discharge

### Recommended approach — emissive geometry + glow, with tone-mapping control

- **Emission node semantics**: strength 1.0 makes the surface "shadeless" (exactly its colour);
  materials measure emission in **W/m²**. Blender's own example shows strength 1.0 vs 3.0.
  https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/emission.html
- **Nixie colour**: neon/argon Penning discharge → **orange-red**; later mercury-doped tubes add a
  **blue/purple tinge near the electrodes**. So the "blue-white core with an orange halo" is not
  wrong — the *core* of the discharge is the overexposed hot part (clips toward white/blue-white)
  and the *halo* is the orange neon scatter/glare.
  https://en.wikipedia.org/wiki/Nixie_tube
  https://jlcpcb.com/blog/how-nixie-tubes-work
- **The white-blob problem is tone mapping.** In Cycles, a very bright coloured emission gets
  clamped toward white. A well-documented answer: emission **Strength = 100** (hue-preserved by
  Filmic/AgX with the **Look** set to High Contrast) and volume scatter density **0.015** (world
  scale) produced a coloured glow rather than a flat white blob — and the note explicitly warns:
  "you will probably also have to turn the density of your volume scattering way, way down."
  https://blender.stackexchange.com/questions/168662/emission-red-glow-while-the-object-itself-is-white
- **Numeral = emissive geometry, not a textured plane** at this scale. Two proven methods:
  - Text object → set **Extrude = 0.005**, **Bevel Depth = 0.003** → `Object > Convert to > Mesh`
    (FactoryRestart; they also note the default font is "fat" and recommend a nixie-style face such
    as *Nixie One*). https://www.factoryrestart.com/post/series-let-s-build-something-for-the-asset-store-part-4-modeling-the-characters
  - **Curve + bevel with a 4-vertex circle** for bent-wire digit cathodes (BlenderArtists).
    https://blenderartists.org/t/nixie-tube-2-0/590572
- **Glow bloom**: Cycles has **no** Bloom. Add a **Compositor > Filter > Glare node** (type
  **Fog Glow**, threshold ~1.0; Mix from 0 to 1) between Render Layers and Composite.
  https://brandon3d.com/blender-add-bloom-glow-effect-eevee-and-cycles/
  https://blenderartists.org/t/ ... (stackexchange answer: https://blender.stackexchange.com/questions/304140/how-can-i-achive-glow-effect-as-show-in-reference-image)
- **Volume Scatter inside the tube** (the gas glow): enclose the interior in a mesh (a capsule or
  the tube's inner volume), give it a Volume Scatter (+ Absorption, combined with an **Add Shader**
  — the official Cycles Encyclopedia excerpt says to combine them with add, not mix), and use a
  **density gradient that is thickest in the middle and fades to zero at the edges** (Object
  coordinates → Length → ColorRamp → Density). That reddit-tip setup exists precisely because
  scene-wide fog is "holy shit that's slow" and you want the glow confined to the bulb.
  https://www.reddit.com/r/blender/comments/76hz6g/
  https://download.blender.org/institute/ExcerptCyclesEncyclopedia.Volume.Scatter.pdf
  https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/volume_scatter.html

### Alternative — composited glow / additive fake
1. Emissive geometry set to a modest strength plus a **thicker emissive+transparent half-cylinder
   over the digit** to fake the cloudy gas glow (the BlendSwap Nixie 3.0 approach: "make the line
   thicker and to TRY and simulate the cloudy glow i used a half-cylinder and an emission/transparent
   material — not the best"). https://blendswap.com/blend/10631
2. Stack **multiple Glare nodes** with different blur radii in the compositor for a soft coloured
   bloom without any volumetrics. https://brandon3d.com/blender-add-bloom-glow-effect-eevee-and-cycles/

### Pitfall
- Cranking emission strength too hard shifts the colour to **yellow** — reported directly in the
  Nixie 2.0 thread ("if I bump that up much higher it changes the color to yellow"), which is why
  that artist composited the glow instead.
  https://blenderartists.org/t/nixie-tube-2-0/590572
- A flat displacement/emission plane behind the digits gives a flat white blob; use 3D emissive
  geometry so the glow falls off in depth and the anode/digit edges read.
- Don't use Volume Scatter alone for colour — the scatter colour appears as its *complement* where
  it isn't directly lit; combine with Volume Absorption (Add Shader) or use an emissive volume.
  https://download.blender.org/institute/ExcerptCyclesEncyclopedia.Volume.Scatter.pdf

### Minimum viable recipe
Convert the lit digit to emissive geometry (Extrude 0.005 / Bevel 0.003). Emission colour =
saturated neon orange-red, **Strength ≈ 10–100** (start 30; raise until the core clips white but
the halo stays orange, with AgX/Filmic High Contrast). Confine a Volume Scatter mesh to the tube
interior with a centre-weighted gradient density. Add a compositor **Glare / Fog Glow** node,
threshold 1.0.

---

## 4. Which digit is lit, and the ghosting

### Recommended approach — one mesh + one material per digit, "on"/"off" variants
- Build all ten digits, then **separate them into individual meshes** (`P > Selection`) so each can
  carry its own material. FactoryRestart does exactly this because the asset switches which digit
  lights up. https://www.factoryrestart.com/post/series-let-s-build-something-for-the-asset-store-part-4-modeling-the-characters
- The BlendSwap nixie exposes the switch as: select the active curve, set its material to an
  **"off"** material; select the digit to show, set it to **"on"**.
  https://blendswap.com/blend/10631
- **"off"** = dull nickel/dark metal (Metallic ~1.0, Roughness ~0.4, dark base colour). The ghost
  you see in a real tube is the unlit cathode seen *through* the glass and through the lit digit's
  glow — so part of the ghosting is a **rendering artefact you get for free** once refraction and
  the glow exist; you don't necessarily need to add fake emissiveness.
  https://www.ioccc.org/2025/endoh1/README.md ("Note how the numbers 0 and 6 appear at the
  back/front of the tube respectively due to the digit stacking") — https://nixlabs.com.au/nixie
- If the ghosts are too faint, the standard trick is **stacked emissive layers with different
  strengths**: lit digit emission e.g. 30, inactive digits a very low emission
  (**≈ 0.02–0.1**) so they read as dim shapes. **UNVERIFIED** — no source publishes a specific
  ghost emission strength; this range is inferred from the "flat white vs halo" tone-mapping answer.
- **Stacking order** (front→back) for realism: **6, 7, 5, 8, 4, 3, 9, 2, 0, 1**, offset slightly to
  produce depth and reduce obscuring. https://grokipedia.com/page/Nixie_tube

### Alternative — alpha-mapped planes
Use a transparent-over-matte grid texture as a mask for the anode mesh and/or thin alpha planes for
the faint digits — cheap and controllable. BlendSwap's nixie uses "a transparent over matte with
the texture as a mask" for the grid anode. https://blendswap.com/blend/10631
Thin alpha-mapped planes are also the game-engine approach for foliage-style fakes.
https://blenderartists.org/t/nixie-tube-2-0/590572

### The anode mesh (this is what makes the tube read)
Model it as a hollow-square grid: plane → Inset → delete inner face → **Array modifier** on X, then
again on Y/Z → Extrude for depth → join four sides into a wrap. FactoryRestart walks through it
step by step. https://www.factoryrestart.com/post/series-let-s-build-something-for-the-asset-store-part-4-modeling-the-characters

### Pitfall
- If every digit shares one material, you can't switch the lit one without per-frame node edits.
  Separate meshes + on/off materials is the proven pattern.
- Ghost digits with too-high emission look like *two* lit numbers, not one faint one.
- Don't forget the anode mesh; without it the interior looks like loose floating digits.

### Minimum viable recipe
Ten digit meshes (Extrude 0.005 / Bevel 0.003), each own material. "on" = emission strength ~30,
neon orange; "off" = dark nickel metal, optionally emission 0.03. Slight Z offsets; order 6,7,5,8,
4,3,9,2,0,1. Add the arrayed hollow-square anode mesh wrapping them.

---

## 5. The brass socket / base

### Recommended approach — procedural brass, Metallic 1.0, tuned colour + anisotropic turned finish

- **Metallic = 1.0** (physical metals are metallic or not; values 0.2–0.8 read "plasticky").
  Roughness controls polish. Base Color tints the specular reflection.
  https://blender-cg.net/principled-bsdf-every-parameter-explained-real-materials
- **Base colour values that read as real brass, not orange.** Blender's own Metallic-BSDF example
  table gives measured conductor colours: **Copper = (0.972, 0.694, 0.486)**, **Gold = (1.000,
  0.735, 0.353)** (F82-Tint base colours). Brass sits between copper and gold/zinc — pick around
  **(0.93, 0.72, 0.42)** (**derived**, not published). Independent recipes: polished copper
  (0.926, 0.721, 0.504); copper hex **#B87333**; gold hex **#FFD700**; weathered copper #F2A35E.
  https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/metallic.html
  https://tomevault.io/tome/RobLe3/cc-blender-skill/blender-materials
  https://thecraftsandkitchen.com/how-to-make-metal-in-blender-procedural-texture-and-material
  https://varsitytutors.com/practice/subjects/blender/lessons/use-principled-bsdf-inputs-base-color-metallic-roughness-normal
- **Roughness ranges**: polished **0.05**, brushed/satin **0.3–0.5**, aged **0.6+**. For a turned
  brass socket, aim satin: **0.3–0.4**.
  https://tomevault.io/tome/RobLe3/cc-blender-skill/blender-materials
  https://salivity.github.io/blender/article/create-anisotropic-brushed-metal-in-blender
- **Anisotropy for a turned/lathed finish.** Principled **Anisotropic** is Cycles-only: higher
  values elongate highlights along the tangent, negative perpendicular. Use a **Tangent node set to
  Radial, axis = the lathe axis**, which is documented as exactly the tool for "brushed, machined or
  lathed metals". A worked radial-brushed-metal recipe uses **Anisotropic ≈ 0.7–1.0, Rotation ≈ 0.0**;
  a satin (polished-away) finish can skip rotation variation.
  https://docs.blender.org/manual/en/latest/render/shader_nodes/input/tangent.html
  https://odederell3d.blog/2018/06/09/cycles-tangent-node-anisotropic-reflection/
  https://blender-cg.net/principled-bsdf-every-parameter-explained-real-materials
  https://blenderartists.org/t/brushed-steel-texture-help/1556190
  Anisotropic reflections need **some** roughness to become visible (0.3–0.4).
  https://salivity.github.io/blender/article/create-anisotropic-brushed-metal-in-blender

### Modelling the socket features

- **Stepped collar / socket body / lip**: same lathe workflow as the glass — spin a stepped profile.
  A valve/socket lip is a flared profile node at the top of the spin; if you'd rather not spin, a
  stack of cylinders with beveled edges reads fine at watch scale (**UNVERIFIED** — no single source,
  it's standard practice).
- **Pin ring**: a cylinder for the ring plus small cylinders (pin diameter ≈ **1.02 mm** for IN-12)
  arranged by an **Array modifier** around a circle, or a circle curve with a bevel.
  Pin geometry from https://docs.omnixie.com/in12.html ; 14 pins per the IN-12 datasheet.
  https://download.mikroe.com/documents/datasheets/Nixie_IN-12B_datasheet.pdf
- **Knurled band — documented mesh method (loop cuts + un-subdivide):**
  1. Add cylinder, **radius 1, depth 2, 60 vertices, no cap fill**.
  2. `Ctrl-R` → **24 loop cuts**.
  3. Face mode (`3`), Select All, right-click → **Un-subdivide**, set **iterations = 1**
     (this turns the ring-segments into the diamond/rhombus layout).
  4. `Alt-E` → **Individual Faces** → extrude outward; set transform pivot to **Individual Origins**
     → `S` to shrink, making the knurl points.
  5. To set knurl depth, switch pivot to **Median** and `S` then `Shift-Z` (Z-locked scale).
  https://simmer3d.com/2020/07/23/knurl-mesh-in-blender/
- **Knurled band — geometry nodes alternative**: triangulate the band in a **checkerboard/alternating
  pattern** to get rhombuses, then move the vertices at the **centres of the diamonds along their
  normal** (a small group; StackExchange provides the node tree and a .blend).
  https://blender.stackexchange.com/questions/294248/creating-knurl-on-certain-faces-using-geometry-nodes
  (There is also a Blender.fi geometry-nodes knurling walkthrough, but the page is behind a bot
  wall — https://blender.fi/2025/11/26/make-knurling-with-geonodes-easy/ **UNVERIFIED** content.)

### Pitfall
- The known failure of procedural brass: a **bright orange-yellow highlight that can dominate the
  image in Cycles** at certain angles ("in Cycles it can grow to dominate the image if the angle is
  just right"). The OP could not fully diagnose it; the working advice in the thread was that
  anisotropy needs proper tangents (radial vs UV) and roughness. If your socket glows orange, raise
  roughness slightly and desaturate the base colour rather than adding emission.
  https://blenderartists.org/t/anisotropic-brass/1453500
- UV-driven tangents break across UV seams; **radial tangent** is safer for a lathed part.
  https://blenderartists.org/t/brushed-steel-texture-help/1556190
- 24 loop cuts + un-subdivide is geometry-heavy; if the socket is only a few cm on screen, a
  **normal/bump map or geometry-nodes knob** may be cheaper.

### Minimum viable recipe
Principled: **Metallic 1.0**, Base Color ≈ (0.93, 0.72, 0.42), **Roughness 0.35**, **Anisotropic
0.7** with a **Tangent node (Radial, Z)**. Socket = spun stepped profile; pin ring = cylinder +
Array of 1 mm pins; knurl band = cylinder/60 verts → 24 loop cuts → un-subdivide 1 → individual-face
extrude → individual-origin shrink.

---

## 6. Volumetrics for a glowing gas at cm scale

### Recommended approach — Volume Scatter + Volume Absorption (Add Shader), confined, gradient density

- **Node semantics**: Volume Scatter `Density` = "density of the scatter effect"; `Color` = per-
  channel scattering coefficients; `Anisotropy` controls forward/backward scatter (Henyey-Greenstein
  by default). Volume Absorption absorbs; classic use is "water and colored glass". Combine Scatter
  and Absorption with an **Add Shader** — the official Cycles Encyclopedia excerpt says combining
  them with add gives the natural result (the shadow goes grey because all colour is either
  scattered or absorbed).
  https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/volume_scatter.html
  https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/volume_absorption.html
  https://download.blender.org/institute/ExcerptCyclesEncyclopedia.Volume.Scatter.pdf
- **Density ballpark**: published test values in a controlled scatter study were **1, 10, 25, 50,
  500**, with anisotropy **-1 … 1** (-1 back-scatter, +1 forward-scatter, 0 random).
  https://blenderdiplom.com/en/tutorials/all-tutorials/582-cycles-volume-scatter.html
  A world-scale glow example used **density 0.015** — but that is for a whole room, and the source
  warns you must turn volume density "way, way down" as emission goes up.
  https://blender.stackexchange.com/questions/168662/emission-red-glow-while-the-object-itself-is-white
- **Scale matters.** Blender's density is an **attenuation coefficient per scene unit** (1/m when
  1 unit = 1 m): transmission ≈ `exp(-length · density)`. A 3 cm tube in a metre-scale scene has a
  path length ~0.03, so to get a visible glow you need density roughly **k/0.03 ≈ 30–100** for
  k ≈ 1–3. **This is derived from the units source, not a published nixie value — treat the exact
  number as UNVERIFIED and tune from ~30 upward.**
  https://devtalk.blender.org/t/physical-units-on-volume-scatter-and-volume-absorption/28572
- **Avoid washing out what's behind it**:
  - Confine the volume to a **mesh inside the tube** (capsule/cylinder), never the world — a scene-
    wide volume is both slow and fogs everything.
    https://www.reddit.com/r/blender/comments/76hz6g/
  - Use a **centre-weighted density gradient** so the glow is bright in the middle and fades to 0
    at the glass: Object coords → Vector Math Length → ColorRamp → Density.
    https://www.reddit.com/r/blender/comments/76hz6g/
    https://blenderartists.org/t/how-can-i-create-volume-density-based-on-the-thickness-of-the-object/1280435
  - Keep **anisotropy near 0** for a soft uniform glow; positive values push light forward and can
    look like a beam.
  - Prefer **emissive volume** (Principled Volume / Emission into the Volume socket) for the colour
    and let Scatter supply only the soft haze — scatter-only colour shows as its complement where
    unlit. https://download.blender.org/institute/ExcerptCyclesEncyclopedia.Volume.Scatter.pdf
  - Raise **Volume bounces** and enable **denoising**; volumetrics are noisy.

### Alternative — Principled Volume
The Principled Volume shader bundles Density + Emission + Blackbody (useful for a hot-gas look) and
is the one-node option. Manual inputs could **not** be extracted this session (403), so exact socket
names/units are **UNVERIFIED**; the canonical page is
https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/volume_principled.html

### Pitfall
- A world/box volume at room density in a small object either looks like nothing or washes out the
  whole scene. Keep it local.
- Scatter colour alone gives a complementary-colour cast in shadowed regions; pair it with
  Absorption or use emission for the hue.
- Very high density (100s) can look like solid diffuse material — the study notes "a volume scatter
  material with a high density looks fairly similar to the diffuse shader".
  https://blenderdiplom.com/en/tutorials/all-tutorials/582-cycles-volume-scatter.html
- Volume noise + caustics + glass = the slowest possible render. Denoise and clamp.

### Minimum viable recipe
Capsule mesh inside the tube → Volume Scatter (colour = neon orange) **Add** Volume Absorption →
Object-coords gradient **ColorRamp → Density**, start density ≈ 30, anisotropy 0. Alternatively one
Principled Volume node. Keep it inside the tube, raise Volume bounces, enable denoising.

---

## Cross-cutting render settings that make the six areas work together
- Total/Glossy/Transmission bounces **≥ 12**, Volume bounces raised, Transparent bounces raised.
- **Filter Glossy** 0.5, **Clamp Indirect** ~10 (or 0 if you want physical values and accept fireflies).
- Reflective/Refractive caustics **off** unless using MNEE shadow caustics (then: light + cast +
  receive flags, smooth normals).
- Colour management: **AgX or Filmic, Look = High Contrast** — keeps the emissive core from
  becoming a flat white blob.
- Compositor: **Glare / Fog Glow** (threshold 1) after the Render Layers node; Cycles has no bloom.
- Reference render already produced by the project sits at `z_tube.png`; moodboard is
  `reference/nixie_moodboard_arcs.png`.

## Source index
- Blender manual — Principled BSDF: https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html
- Blender manual — Metallic BSDF (conductor colour table): https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/metallic.html
- Blender manual — Emission: https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/emission.html
- Blender manual — Volume Scatter: https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/volume_scatter.html
- Blender manual — Volume Absorption: https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/volume_absorption.html
- Blender manual — Principled Volume: https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/volume_principled.html
- Blender manual — Light Path node: https://docs.blender.org/manual/en/latest/render/shader_nodes/input/light_path.html
- Blender manual — Light Paths (render settings): https://docs.blender.org/manual/en/latest/render/cycles/render_settings/light_paths.html
- Blender manual — Object ray visibility & MNEE shadow caustics: https://docs.blender.org/manual/en/latest/render/cycles/object_settings/object_data.html
- Blender manual — Solidify modifier: https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/solidify.html
- Blender manual — Spin tool: https://docs.blender.org/manual/en/latest/modeling/meshes/tools/spin.html
- Blender manual — Tangent node: https://docs.blender.org/manual/en/latest/render/shader_nodes/input/tangent.html
- devtalk — volume/absorption physical units: https://devtalk.blender.org/t/physical-units-on-volume-scatter-and-volume-absorption/28572
- Cycles Encyclopedia excerpt — Volume Scatter (PDF): https://download.blender.org/institute/ExcerptCyclesEncyclopedia.Volume.Scatter.pdf
- BlenderDiplom — Volume Scatter values: https://blenderdiplom.com/en/tutorials/all-tutorials/582-cycles-volume-scatter.html
- Cookstation — glass in Cycles (shadow trick, bounces): https://cookstation.blog/how-to-make-glass-blender
- iMeshh — advanced glass (volume absorption, ray visibility): https://blog.imeshh.com/index.php/2022/05/19/glass-in-blender-3-0
- StackExchange — glass render problem / fake glass: https://blender.stackexchange.com/questions/56647/glass-render-problem
- StackExchange — hollow vs solid glass, Solidify: https://blender.stackexchange.com/questions/62330/is-there-a-way-to-make-a-hollow-object-solid
- StackExchange — emission colour vs tone mapping: https://blender.stackexchange.com/questions/168662/emission-red-glow-while-the-object-itself-is-white
- StackExchange — knurl via geometry nodes: https://blender.stackexchange.com/questions/294248/creating-knurl-on-certain-faces-using-geometry-nodes
- StackExchange — shadow caustics: https://blender.stackexchange.com/questions/272147/how-can-i-render-caustic-using-only-the-cycles-render-engine
- BlenderArtists — yellow shift on over-bright emission: https://blenderartists.org/t/nixie-tube-2-0/590572
- BlenderArtists — anisotropic brass orange highlight: https://blenderartists.org/t/anisotropic-brass/1453500
- BlenderArtists — brushed steel / lathed tangents: https://blenderartists.org/t/brushed-steel-texture-help/1556190
- BlenderArtists — glass approaches thread: https://blenderartists.org/t/glass-in-cycles-what-is-your-best-approach-to-glass-material/1243845
- FactoryRestart — modelling the tube: https://www.factoryrestart.com/post/series-let-s-build-something-for-the-asset-store-part-3-modeling-the-tube
- FactoryRestart — modelling the guts: https://www.factoryrestart.com/post/series-let-s-build-something-for-the-asset-store-part-4-modeling-the-characters
- Simmer3D — knurl mesh (loop cuts + un-subdivide): https://simmer3d.com/2020/07/23/knurl-mesh-in-blender/
- Oded Erell — Tangent node & anisotropic reflection: https://odederell3d.blog/2018/06/09/cycles-tangent-node-anisotropic-reflection/
- BlendSwap — Nixie Tube 3.0 (on/off materials, fake glow): https://blendswap.com/blend/10631
- Wikipedia — Nixie tube (orange glow, mercury blue tinge): https://en.wikipedia.org/wiki/Nixie_tube
- Grokipedia — Nixie tube (stack order, anode mesh): https://grokipedia.com/page/Nixie_tube
- OmniXie — IN-12 reference (35 mm, 18 mm symbols, 1.02 mm pins): https://docs.omnixie.com/in12.html
- Schott 8347 borosilicate (n = 1.473): https://www.lookpolymers.com/pdf/Schott-Glass-8347-Borosilicate-Glass.pdf
- ForMatter borosilicate glass spec (IOR 1.47): https://renato.design/formatter-app/materials/glass/mat_borosilicate_glass.html
- Reddit — confined volume glow with gradient density: https://www.reddit.com/r/blender/comments/76hz6g/
- Brandon3D — Glare/Fog Glow in Cycles: https://brandon3d.com/blender-add-bloom-glow-effect-eevee-and-cycles/
- blender-cg.net — Principled parameter ranges: https://blender-cg.net/principled-bsdf-every-parameter-explained-real-materials
- Salivity — anisotropic brushed metal roughness 0.3–0.4: https://salivity.github.io/blender/article/create-anisotropic-brushed-metal-in-blender
