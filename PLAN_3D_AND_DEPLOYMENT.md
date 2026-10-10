# Steampunk Watch Face: 3D Render & Garmin Venu Sq 2 Deployment Plan

This document outlines the complete plan to produce the 3D-rendered steampunk components from the reference image ([`reference/nixie_moodboard_arcs.png`](reference/nixie_moodboard_arcs.png)) and deploy them as a fully functional watch face on a physical Garmin Venu Sq 2 device.

---

## Part 1: 3D Asset Creation Plan (Blender Pipeline)

### 1. Component Hierarchy & Breakdown
Excluding the watch body and exterior bezel, the steampunk assembly consists of four modular sub-assemblies:

```
[ Steampunk Assembly ]
├── 1. Nixie Tubes Rack (Upper Half)
│   ├── Outer glass envelopes (domed cylinder with tip pinched off, physical wall thickness)
│   ├── Internal cathode wire grids & digit filaments (0-9 wire meshes)
│   ├── Anode honey-comb/mesh backplate
│   ├── Blue ionization glow / plasma sparks emitter
│   └── Turned brass sockets / collars with knurling and bolt flanges
│
├── 2. Central Structural Manifold & Chassis
│   ├── Horizontal cast-brass / bronze manifold beam (rounded brackets, seams, hex bolts)
│   ├── Indicator lamps (recessed jewel lenses with blue backlight)
│   └── Central horizontal hinge / rod mechanism
│
├── 3. Sub-Dials & Gauges (Lower Half)
│   ├── Left Gauge (Heart Rate):
│   │   ├── Stepped brass bezel with screw mounts
│   │   ├── Dark brushed dial face with luminous radial arc and markings
│   │   └── Red enameled heart centerpiece + dual-ended pointer needle
│   ├── Center Odometer / Mechanical Counter (Steps):
│   │   ├── Recessed chamfered housing frame
│   │   └── Rolling numbered cylindrical drums (white numerals on stamped dark metal)
│   ├── Right Dial (Date / Calendar / Time):
│   │   ├── Antiqued brass outer ring with engraved numerals / Roman marks
│   │   ├── Recessed circular date aperture window showing "24"
│   │   └── Skeletonized brass hands with circular counterbalance
│
└── 4. Under-chassis Exposed Gear Train (Bottom)
    ├── Intermeshing brass spur gears with cutouts
    ├── Screwed pivot pins and mounting plates
    └── Weathered dark iron backplate with subtle grime and patina
```

---

### 2. Modeling & Texturing Steps (Blender Cycles)

#### Step 1: Camera & Scene Calibration
- **Camera**: Orthographic or 85–100mm telephoto perspective camera positioned straight-on.
- **Canvas / Safe Area**: Render canvas matching the 320 × 360 px aspect ratio (working at high-res 4x: 1280 × 1440 px). Set guides for the Garmin safe area (292 × 332 px, >= 14 px margin on all sides).

#### Step 2: Hard-Surface Modeling
- **Nixie Tubes**:
  - Model glass dome with a `Solidify` modifier (vital for realistic index of refraction: IOR ~ 1.50–1.52).
  - Model internal wire cage and curved digit filaments (0–9) using beveled 3D curves.
- **Gears**:
  - Generate parametric gears using Blender's built-in `Extra Objects` add-on (`Add -> Mesh -> Gears -> Gear`).
- **Gauges & Chassis**:
  - Extrude and bevel the manifold beam, adding hex bolts, knurled collars, and rivet arrays.

#### Step 3: PBR Materials & Shading
- **Aged Brass / Bronze**:
  - Base Color: `#B8860B` to `#8B6914` (Metallic: 1.0, Roughness: 0.25–0.45).
  - Procedural weathering: Use `Geometry -> Pointiness` or `Ambient Occlusion` mixed with `Noise Texture` to place shiny gold on exposed edges and dark verdigris (`#40826D`) in recesses.
- **Nixie Plasma Glow**:
  - `Emission` shader (Cyan/Electric Blue: `#38B6FF` to `#7DF9FF`, strength 20–30).
  - Compositor: Glare node set to `Fog Glow` and `Streaks` for bloom and arc streaks.

---

### 3. Layered Export Strategy for Connect IQ
To keep the watch face dynamic and within Garmin memory limits, render the scene as isolated 2D sprite layers:

1. **`bg_base.png` (320 × 360 px)**: Static background containing the chassis, unlit empty Nixie tubes, gauge backplates, odometer window frame, and bottom gears.
2. **`nixie_digits_0_9.png` (Sprite strip or isolated files)**: Individual glowing digits (0 through 9) with alpha channels to composite over the tubes.
3. **`needle_hr.png`**: Isolated red pointer needle with centered pivot point.
4. **`hands_clock.png` / `date_ring.png`**: Isolated hands or date indicator.
5. **`odometer_digits.png`**: Digits 0–9 for the 5-wheel step counter.
6. **`glass_reflection_overlay.png` (Optional)**: Top-layer subtle specular reflections to place over the active digits.

---

## Part 2: Garmin Venu Sq 2 Technical Constraints

The **Garmin Venu Sq 2** runs Garmin Connect IQ (Monkey C) on a **1.41" AMOLED (320 × 360 px)** display.

| Constraint | Limit / Requirement | Consequence & Strategy |
| :--- | :--- | :--- |
| **Graphics Pool RAM** | **~90 KB – 120 KB** available | Uncompressed 320×360 at 16-bit color takes ~230 KB. Cannot store multiple full-screen bitmaps in memory. Use 8-bit indexed palettes and compressed resources. |
| **AMOLED Burn-in Rule** | Max **10% pixel luminance** in sleep mode | In Always-On Display (AOD), the full brass background must be turned off. Only render minimal, dimmed time digits on pure black (`#000000`). |
| **Burn-in Shift Rule** | Pixels cannot remain static forever | In AOD mode, shift the rendering origin by 1–2 pixels periodically. |
| **CPU / Battery Budget** | `onUpdate` budget: < 30ms/frame | In low-power mode, the screen updates only once per minute. Avoid complex math or per-frame resource loading. |

---

## Part 3: Garmin Connect IQ Implementation Plan

### 1. Prerequisites & Environment Setup
1. **Garmin Connect IQ SDK**: Install the Connect IQ SDK Manager and download the latest SDK (v7.x+) and the **Venu Sq 2 device profile**.
2. **IDE**: VS Code with the **Monkey C** extension.
3. **Java Runtime**: JDK 11 or higher.
4. **Developer Key**: Generate a 4096-bit RSA key (`developer_key.der`) via the Monkey C extension command palette.

### 2. Project Structure
Create a Connect IQ Watch Face project:
```
GarminSteampunkWatch/
├── manifest.xml
├── monkey.jungle
└── resources/
    ├── drawables/
    │   └── drawables.xml
    └── images/
        ├── bg_base.png
        ├── digits/
        └── needles/
└── source/
    ├── SteampunkApp.mc
    └── SteampunkView.mc
```

### 3. Resource Definitions (`resources/drawables/drawables.xml`)
```xml
<drawables>
    <bitmap id="BgBase" filename="../images/bg_base.png" />
    <bitmap id="NeedleHR" filename="../images/needles/needle_hr.png" />
    <!-- Nixie digit bitmaps or custom bitmap font -->
    <bitmap id="Nixie0" filename="../images/digits/digit_0.png" />
    <bitmap id="Nixie1" filename="../images/digits/digit_1.png" />
    <!-- ... digits 2-9 ... -->
</drawables>
```

### 4. Core Logic (`source/SteampunkView.mc`)

```monkeyc
import Toybox.Graphics;
import Toybox.WatchUi;
import Toybox.System;
import Toybox.ActivityMonitor;
import Toybox.Time;

class SteampunkView extends WatchUi.WatchFace {
    private var _isLowPower as Boolean = false;
    private var _bgBitmap as BitmapResource?;
    private var _hrNeedle as BitmapResource?;
    private var _nixieDigits as Array<BitmapResource> = [];

    function initialize() {
        WatchFace.initialize();
    }

    function onLayout(dc as Dc) as Void {
        // Load bitmaps ONCE to prevent memory churn
        _bgBitmap = WatchUi.loadResource(Rez.Drawables.BgBase) as BitmapResource;
        _hrNeedle = WatchUi.loadResource(Rez.Drawables.NeedleHR) as BitmapResource;
        
        // Cache digit resources
        _nixieDigits = [
            WatchUi.loadResource(Rez.Drawables.Nixie0) as BitmapResource,
            WatchUi.loadResource(Rez.Drawables.Nixie1) as BitmapResource
            // ... load remaining digits
        ];
    }

    function onUpdate(dc as Dc) as Void {
        if (_isLowPower) {
            // AMOLED AOD Protection: Pure black background, <10% illuminated pixels
            dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
            dc.clear();
            drawLowPowerTime(dc);
            return;
        }

        // 1. Draw static background brass chassis
        if (_bgBitmap != null) {
            dc.drawBitmap(0, 0, _bgBitmap);
        }

        // 2. Fetch Time & Draw Nixie Tubes
        var clockTime = System.getClockTime();
        drawNixieTime(dc, clockTime.hour, clockTime.min);

        // 3. Fetch Activity Data (HR & Steps)
        var hr = ActivityMonitor.getHeartRateHistory(1, true).next().heartRate;
        var info = ActivityMonitor.getInfo();
        var steps = info.steps != null ? info.steps : 0;

        // 4. Draw Sub-Dials
        drawHeartRateGauge(dc, hr);
        drawOdometerSteps(dc, steps);
    }

    function onEnterSleep() as Void {
        _isLowPower = true;
        WatchUi.requestUpdate();
    }

    function onExitSleep() as Void {
        _isLowPower = false;
        WatchUi.requestUpdate();
    }
}
```

---

## Part 4: Testing & Deployment to Hardware

### Step 1: Simulator Verification
1. Open the project in VS Code and press `F5` targeting `venu_sq_2`.
2. Open **File -> View Memory** and verify:
   - Total memory does not exceed device limit (~90–120 KB graphics heap).
3. Open **Settings -> Toggle Low Power Mode**:
   - Check the console for any `Burn-in Protection Violation` or exceeding the 10% pixel luminance threshold.

### Step 2: Build Device Binary (`.prg`)
Execute via the VS Code Command Palette:
> `Monkey C: Export Project by Device` -> Select `venu_sq_2` -> Select export directory.
This outputs `GarminSteampunkWatch.prg`.

### Step 3: Physical Device Sideloading
1. Connect the **Garmin Venu Sq 2** to your PC using the Garmin USB charging cable.
2. In Windows File Explorer, open the mounted storage device:
   ```
   This PC\Venu Sq 2\Primary\GARMIN\APPS\
   ```
3. Copy `GarminSteampunkWatch.prg` into the `GARMIN\APPS\` folder.
4. Safely disconnect / unplug the watch.
5. On the Venu Sq 2, press and hold the bottom button -> **Watch Face** -> scroll to and select your custom steampunk watch face.
