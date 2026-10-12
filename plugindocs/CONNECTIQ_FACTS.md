# Connect IQ — verified facts for a Venu Sq 2 watch face

Compiled from **Garmin's own developer documentation** (`developer.garmin.com/connect-iq/...`) unless a source is
marked *secondary*. Every fact carries the URL it was read from. Anything I could not confirm from a Garmin source is
listed in [§9 Open questions / UNVERIFIED](#9-open-questions--unverified) — **do not invent API names**; the sections
below are quoted verbatim where it matters.

Doc set read (all Garmin, `developer.garmin.com`):

| Page | URL |
|---|---|
| Getting Started | https://developer.garmin.com/connect-iq/connect-iq-basics/getting-started/ |
| Get the SDK | https://developer.garmin.com/connect-iq/sdk/ |
| Monkey C Command Line Setup | https://developer.garmin.com/connect-iq/reference-guides/monkey-c-command-line-setup/ |
| App Types | https://developer.garmin.com/connect-iq/connect-iq-basics/app-types/ |
| Your First App (side loading) | https://developer.garmin.com/connect-iq/connect-iq-basics/your-first-app/ |
| Compatible Devices | https://developer.garmin.com/connect-iq/compatible-devices/ |
| Device Reference — Venu Sq 2 | https://developer.garmin.com/connect-iq/device-reference/venusq2/ |
| Manifest and Permissions | https://developer.garmin.com/connect-iq/core-topics/manifest-and-permissions/ |
| Resources (bitmaps/fonts) | https://developer.garmin.com/connect-iq/core-topics/resources/ |
| Build Configuration | https://developer.garmin.com/connect-iq/core-topics/build-configuration/ |
| Testing and Debugging | https://developer.garmin.com/connect-iq/core-topics/debugging/ |
| Publishing to the Store | https://developer.garmin.com/connect-iq/core-topics/publishing-to-the-store/ |
| App Review Guidelines | https://developer.garmin.com/connect-iq/app-review-guidelines/ |
| FAQ — watch face every second | https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-get-my-watch-face-to-update-every-second/ |
| FAQ — AMOLED watch faces | https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-make-a-watch-face-for-amoled-products/ |
| FAQ — custom fonts | https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-use-custom-fonts/ |
| FAQ — optimize bitmaps | https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-optimize-bitmaps/ |
| API — WatchUi.WatchFace | https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/WatchFace.html |
| API — WatchUi.View | https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/View.html |
| API — WatchUi.WatchFaceDelegate | https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/WatchFaceDelegate.html |
| API — Application.AppBase | https://developer.garmin.com/connect-iq/api-docs/Toybox/Application/AppBase.html |
| API — Graphics | https://developer.garmin.com/connect-iq/api-docs/Toybox/Graphics.html |
| API — Graphics.Dc | https://developer.garmin.com/connect-iq/api-docs/Toybox/Graphics/Dc.html |
| API — System | https://developer.garmin.com/connect-iq/api-docs/Toybox/System.html |
| API — System.ClockTime | https://developer.garmin.com/connect-iq/api-docs/Toybox/System/ClockTime.html |
| API — Time.Gregorian.Info | https://developer.garmin.com/connect-iq/api-docs/Toybox/Time/Gregorian/Info.html |
| API — ActivityMonitor | https://developer.garmin.com/connect-iq/api-docs/Toybox/ActivityMonitor.html |
| API — ActivityMonitor.Info | https://developer.garmin.com/connect-iq/api-docs/Toybox/ActivityMonitor/Info.html |
| API — ActivityMonitor.HeartRateSample | https://developer.garmin.com/connect-iq/api-docs/Toybox/ActivityMonitor/HeartRateSample.html |
| API — Activity.Info | https://developer.garmin.com/connect-iq/api-docs/Toybox/Activity/Info.html |
| API — System.DeviceSettings | https://developer.garmin.com/connect-iq/api-docs/Toybox/System/DeviceSettings.html |

---

## 1. Toolchain and setup (Windows)

**JDK requirement — Oracle Java Runtime Environment, version 11 or higher.**
Quote: *"Before getting started with the installation on Mac or Windows, you'll need version 11 or higher of the Oracle
Java™ Runtime Environment installed."*
— https://developer.garmin.com/connect-iq/reference-guides/monkey-c-command-line-setup/

The VS Code extension page repeats it: *"The Monkey C extension requires Visual Studio Code, version 11 or higher of the
Oracle Java™ Runtime Environment, and Connect IQ SDK version 4.0.6 or higher."* (The "version 11" in that sentence is the
JRE; the SDK-4.0.6 part is the SDK floor.) — https://developer.garmin.com/connect-iq/connect-iq-basics/getting-started/

**SDK version — the current latest is Connect IQ 9.2.0**, page dated *Last Updated: August 25, 2026*.
— https://developer.garmin.com/connect-iq/sdk/
There is **no "9.2.0 for Venu Sq 2"** — one SDK builds for every supported device; the device id selects the target.
The Venu Sq 2 runs **API Level 5.0** (see §2), so any SDK ≥ 5.0 can target it; use 9.2.0 unless you want to support
older devices with a lower `minApiLevel`.

**Exact components to install (Windows):**

1. **Connect IQ SDK Manager** — the installer *and* the updater. Get it from the "Get the SDK" page, section *Install
   the SDK Manager* → **Accept & Download for Windows**.
   URL: https://developer.garmin.com/connect-iq/sdk/
   Per Getting Started: copy the executable and support files into a new folder, launch it, log in with a **Garmin
   Connect account**, then let it download the SDK and the device library. Click **Yes** when prompted to make the
   downloaded SDK the active one. — https://developer.garmin.com/connect-iq/connect-iq-basics/getting-started/
   `SDK Manager` installs SDKs, the device library, sample code and fonts under
   `%APPDATA%\Garmin\ConnectIQ\` (the active SDK path is recorded in `%APPDATA%\Garmin\ConnectIQ\current-sdk.cfg`).
   — https://developer.garmin.com/connect-iq/reference-guides/monkey-c-command-line-setup/
   *(Note: the SDK page also offers a "direct download" of the SDK which explicitly "does not include the Visual Studio
   Code Monkey C extension". — https://developer.garmin.com/connect-iq/sdk/)*

2. **Visual Studio Code + the "Monkey C" extension from Garmin.** Install from the Extensions Marketplace (search
   "Monkey C"), restart VS Code, then run command palette → **`Monkey C: Verify Installation`**.
   — https://developer.garmin.com/connect-iq/connect-iq-basics/getting-started/

3. **PATH (optional, for command-line builds):**
   ```
   > for /f usebackq %i in (%APPDATA%\Garmin\ConnectIQ\current-sdk.cfg) do set CIQ_HOME=%~pi
   > set PATH=%PATH%;%CIQ_HOME%\bin
   ```
   This exposes three commands: **`connectiq`** (start the simulator), **`monkeyc`** (compiler), **`monkeydo`** (run a
   PRG in the simulator). — https://developer.garmin.com/connect-iq/reference-guides/monkey-c-command-line-setup/

**Developer key — REQUIRED, RSA 4096-bit private key, DER (PKCS#8).**
Quote: *"The Connect IQ compiler requires a developer key to sign apps when they're compiled and packaged. The required
key must be a RSA 4096 bit private key."* and *"If you lose your original signing key you will not be able to update
your app."* — https://developer.garmin.com/connect-iq/connect-iq-basics/getting-started/

GUI route: command palette → **`Monkey C: Generate a Developer Key`**, then set `Monkey C: Developer Key Path` in
Settings. — https://developer.garmin.com/connect-iq/connect-iq-basics/getting-started/

**Exact command-line commands (OpenSSL), quoted from Garmin:**
```
> openssl genrsa -out developer_key.pem 4096
> openssl pkcs8 -topk8 -inform PEM -outform DER -in developer_key.pem -out developer_key.der -nocrypt
```
*"This developer key, developer_key.der, is passed to the compiler using the -y command line option."*
— https://developer.garmin.com/connect-iq/reference-guides/monkey-c-command-line-setup/

---

## 2. Is the Venu Sq 2 supported, and what is its device id?

**Yes.** Confirmed on two Garmin pages.

**Compatible Devices table** (https://developer.garmin.com/connect-iq/compatible-devices/):

| Product | Resolution | Shape | Screen tech | API Level |
|---|---|---|---|---|
| Venu® Sq 2 | **320 x 360** | rectangle | AMOLED | **5.0** |
| Venu® Sq 2 Music | 320 x 360 | rectangle | AMOLED | 5.0 |

**Device Reference page gives the build id** (https://developer.garmin.com/connect-iq/device-reference/venusq2/):

| Attribute | Value |
|---|---|
| **Id** | **`venusq2`** |
| Screen Shape | rectangle |
| Screen Size | **320 x 360** |
| Display Colors | 65536 (i.e. RGB565, 16-bit) |
| Touch | True |
| Buttons | enter, menu, esc |
| Launcher Icon Size | 40 x 40 |
| Part Number | 006-B4115-00 |
| **Watch Face memory limit** | **131072 bytes (128 KB)** |
| Watch App / Widget limit | 786432 (not needed for a watch face) |

**Device id strings:**
- Venu Sq 2 → **`venusq2`** (device-reference path `/connect-iq/device-reference/venusq2/`)
- Venu Sq 2 **Music** → **`venusq2m`** (separate device id, `/connect-iq/device-reference/venusq2m/`)
- Both are listed **separately** in Compatible Devices and Device Reference with identical 320x360/AMOLED/API-5.0
  specs. They are *not* one shared device file: they are two device ids with (per Garmin's tables) identical specs.
  If you want a single PRG that installs on either, list both in `<iq:products>`; otherwise target `venusq2`.

Manifest form:
```xml
<iq:products>
    <iq:product id="venusq2"/>
    <!-- optional: <iq:product id="venusq2m"/> -->
</iq:products>
```
(`<iq:products>` syntax from https://developer.garmin.com/connect-iq/core-topics/manifest-and-permissions/)

---

## 3. Watch face fundamentals — class and method signatures

**Manifest app type:** `type="watchface"`.
*"The type field specifies what kind of application you are developing. Currently, Connect IQ supports five types of
apps: watchface, datafield, widget, watch-app, audio-content-provider-app."*
— https://developer.garmin.com/connect-iq/core-topics/manifest-and-permissions/

**The entry class derives from `Application.AppBase`; the initial view derives from `WatchUi.WatchFace`.**
*"The initial view of a watch face application `must` extend WatchFace."*
— https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/WatchFace.html

`WatchFace extends Toybox.WatchUi.View` — so `onLayout/onShow/onUpdate/onHide` are **inherited from `View`**, and
`WatchFace` itself only adds the power-state hooks. — https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/View.html

**Exact signatures (from Garmin's API docs):**

From `Toybox.WatchUi.View` — https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/View.html
```
onLayout(dc as Graphics.Dc) as Void      // "The entry point for the View."
onShow() as Void                          // view brought into foreground; load resources here
onUpdate(dc as Graphics.Dc) as Void       // all drawing
onHide() as Void                          // view backgrounded
```
Life-cycle order for watch faces as Garmin states it: `onLayout() → onShow() → onUpdate()`.

From `Toybox.WatchUi.WatchFace` — https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/WatchFace.html
```
initialize()                                  // constructor
onEnterSleep() as Void                        // device entering low power mode
onExitSleep() as Void                         // device exiting low power mode
onPartialUpdate(dc as Graphics.Dc) as Void    // API level 2.3.0
```

**`getInitialView()` — the app entry point.** On `Application.AppBase`:
```
getInitialView() as [ WatchUi.Views ] or [ WatchUi.Views, WatchUi.InputDelegates ]
```
*"An Application.AppBase object should override AppBase.getInitialView() to provide the view object to initially push.
An array must be returned with either a view and a delegate, or just a one element array with the WatchUi.View object:
`return [ new MyView(), new MyDelegate() ];`"*
— https://developer.garmin.com/connect-iq/core-topics/manifest-and-permissions/ and
https://developer.garmin.com/connect-iq/api-docs/Toybox/Application/AppBase.html

For a watch face the delegate should be a `WatchUi.WatchFaceDelegate` (https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/WatchFaceDelegate.html).
Also on AppBase: `onStart()` and `onStop(state)` order is `onStart() → getInitialView() → onStop()`.

**What `onUpdate` receives and when it fires.** `dc` is a `Graphics.Dc` device context.
Garmin's exact wording (View page):
- *"Once per minute in Watch Faces when in low power mode"*
- *"Once per second in Watch Faces when in high power mode"*
- *"More than one call to onUpdate() may occur during View transitions"*
Also from the WatchFace page: high power mode lasts *"typically about ten seconds"*, then `onEnterSleep()`; during low
power *"the system will call onUpdate() at the top of every minute"*, and `onPartialUpdate()` *"will be called for the
first 59 seconds of every minute"* if supported.

**Rules about drawing outside `onUpdate`:**
- **All drawing happens in `onUpdate(dc)`** (and, for AOD, in `onPartialUpdate(dc)`).
- `onLayout(dc)` is *"Once after init, when screen size is known … Don't draw — `dc.getWidth/Height` are valid here."*
  (secondary restatement of the official `View.onLayout` doc.)
- `onShow()` is where *"Resources should be loaded into system memory"* — and the Resources page is explicit:
  *"Loading a resource can be an expensive operation, so do not load resources when handling screen updates."*
  — https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/View.html and
  https://developer.garmin.com/connect-iq/core-topics/resources/
- **Timers/animations are only legal in high power mode:** *"The application will not have access to timers or
  animations while in low power mode."* — https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/WatchFace.html

`onPartialUpdate` constraints (verbatim): *"This method is called each second as long as the device power budget is not
exceeded… the application must set the clipping region for the Graphics.Dc object using the setClip() method. Calls to
System.println() and System.print() will not execute on devices when this function is being invoked, but can be used in
the device simulator. If the call to this method exceeds the power budget of the device, the partial update will not
draw and a call to onPowerBudgetExceeded() is made"* — the delegate method is
`WatchFaceDelegate.onPowerBudgetExceeded(powerInfo as WatchUi.WatchFacePowerInfo) as Void`.

---

## 4. Live data inside a watch face

### (a) Time — `System.getClockTime()`
```
System.getClockTime() as System.ClockTime
```
— https://developer.garmin.com/connect-iq/api-docs/Toybox/System.html

`System.ClockTime` members (all `Lang.Number`, API 1.0.0):
`hour` (24-hour), `min`, `sec`, `dst`, `timeZoneOffset` — https://developer.garmin.com/connect-iq/api-docs/Toybox/System/ClockTime.html
Garmin's own example: `var myTime = System.getClockTime(); myTime.hour.format("%02d") + ":" + myTime.min.format("%02d")`.
There is **no date on `ClockTime`** — for the date use Gregorian (below).

### (b) Heart rate — two different APIs, and only one of them is listed as available to a watch face
Garmin's **App Types** table (the VM's allow-list; *"A Toybox module requested for your app type that is outside this
list will result in a Symbol Not Found error"*) has these rows:

| Module | Data Field | **Watch Face** | Widget | App | Audio |
|---|---|---|---|---|---|
| `Toybox.Activity` | ✓ | **(blank)** | (blank) | ✓ | ✓ |
| `Toybox.ActivityMonitor` | ✓ | **✓** | ✓ | ✓ | ✓ |
| `Toybox.Sensor` | (blank) | **(blank)** | ✓ | ✓ | ✓ |
| `Toybox.SensorHistory` | ✓ | **✓** | ✓ | ✓ | ✓ |
— https://developer.garmin.com/connect-iq/connect-iq-basics/app-types/ (read from the live HTML table, cell by cell)

The prose on the same page: watch faces *"have access to graphics, bitmaps, fonts, current activity tracker status,
current battery status, and the user's activity profile. They cannot access the compass, GPS, or other sensors."*
`Toybox.Sensor` is also confirmed unavailable to watch faces by its own API page (its "App Types and Runtime Contexts"
list is: Audio Content Provider, Background, Data Field, Glance, Watch App, Widget — **no Watch Face**).
— https://developer.garmin.com/connect-iq/api-docs/Toybox/Sensor.html

**`Activity.getActivityInfo().currentHeartRate`**
```
Activity.getActivityInfo() as Toybox.Activity.Info
Activity.Info.currentHeartRate as Lang.Number or Null   // bpm, API 1.0.0
```
— https://developer.garmin.com/connect-iq/api-docs/Toybox/Activity/Info.html
It is a **property, not a method** (`currentHeartRate`, no parentheses). On the device this value updates "very often"
(near-real-time). **It is `null` when the sensor is off / the watch is not being worn**, and in the simulator it is
`null` unless you play back a FIT/GPX file or start Data Simulation.
— *Secondary:* Garmin forum threads (moderator "jim_m_58"): https://forums.garmin.com/developer/connect-iq/f/discussion/212496/getting-per-second-heart-rate-on-a-watch-face ,
https://forums.garmin.com/developer/connect-iq/f/discussion/400174/wrist-removal-detection ,
https://forums.garmin.com/developer/connect-iq/f/discussion/5977/how-to-get-current-hearth-rate-on-watch-faces
⚠ **CONTRADICTION — see §9.** The App Types table marks `Toybox.Activity` as *not* available to watch faces, yet the
forum practice (and the Stack Overflow answer below) is to call exactly this from a watch face. This is the single
biggest risk item in the plan.

**`ActivityMonitor.getHeartRateHistory()` — the officially watch-face-available HR path**
```
ActivityMonitor.getHeartRateHistory(period as Time.Duration or Lang.Number or Null,
                                    newestFirst as Lang.Boolean) as ActivityMonitor.HeartRateIterator
```
- `period == null` → entire available history; `Duration` → that window; `Number` → last N entries.
- **`ActivityMonitor.INVALID_HR_SAMPLE` == 255** — *"Indicates that the given heart rate sample is invalid."*
— https://developer.garmin.com/connect-iq/api-docs/Toybox/ActivityMonitor.html

```
HeartRateIterator.next() -> ActivityMonitor.HeartRateSample
HeartRateSample.heartRate as Lang.Number or Null   // "Before using heart rate information, check for INVALID_HR_SAMPLE"
HeartRateSample.when as Time.Moment or Null
```
— https://developer.garmin.com/connect-iq/api-docs/Toybox/ActivityMonitor/HeartRateSample.html

Garmin's own example (verbatim), `ActivityMonitor.getHeartRateHistory(null,false)`, then per sample
`sample.heartRate != ActivityMonitor.INVALID_HR_SAMPLE`. In the simulator the HR history is **canned** (community
reports a constant 80 and no update from a played-back FIT); it only changes every minute or two on real hardware.

**`ActivityMonitor.getInfo()` → `ActivityMonitor.Info`** — used for steps, below. Note `Info` has **no HR field**
(verified: the string `currentHeartRate` does not appear anywhere on the `ActivityMonitor.Info` or `ActivityMonitor`
pages). HR comes only from `getHeartRateHistory()` or `Activity.Info.currentHeartRate`.

**Recommended null-handling chain** (community consensus, matches the documented nullability of each API):
1. try `Activity.getActivityInfo()` → if non-null and `currentHeartRate != null` and not `0` / not `255`, use it;
2. else `ActivityMonitor.getHeartRateHistory(null, true).next()` → accept `heartRate` only if it is neither `null` nor
   `ActivityMonitor.INVALID_HR_SAMPLE` (255);
3. else display `"--"` (do not display a bogus number).
Guard belt-and-braces: `if (ActivityMonitor has :getHeartRateHistory) { … }` — the method is API 1.2.1 and may be
missing on very old devices. *Secondary:* https://stackoverflow.com/questions/56990405/garmin-watchface-how-to-show-heartrate

### (c) Steps — `ActivityMonitor.getInfo()`
```
ActivityMonitor.getInfo() as ActivityMonitor.Info
ActivityMonitor.Info.steps as Lang.Number or Null    // "step count since midnight … in number of steps", API 1.0.0
ActivityMonitor.Info.stepGoal as Lang.Number or Null
```
— https://developer.garmin.com/connect-iq/api-docs/Toybox/ActivityMonitor/Info.html
Same page: *"The fields in this class may return null. It is recommended to null check a value before using it. If the
value is not available, an error indicating that the symbol was not found will be thrown."* — so **always null-check
`steps` before formatting**. Garmin's example: `var steps = info.steps;`
Other useful `Info` fields: `calories`, `distance` (cm), `floorsClimbed`, `activeMinutesDay`, `moveBarLevel`,
`stressScore`, `respirationRate`, `timeToRecovery` (all nullable).

### (d) Date / weekday — `Time.Gregorian.info()`
```
Time.Gregorian.info(moment as Time.Moment, format as Time.Format) as Time.Gregorian.Info
```
`Gregorian.Info` members — https://developer.garmin.com/connect-iq/api-docs/Toybox/Time/Gregorian/Info.html
| Member | Type | Meaning |
|---|---|---|
| `day` | Lang.Number | day of the month |
| `day_of_week` | Lang.Number **or** Lang.String | depends on format (below) |
| `month` | Lang.Number **or** Lang.String | depends on format (below) |
| `year` | Lang.Number | year |
| `hour`, `min`, `sec` | Lang.Number | also available here |

Format behaviour, quoted:
- `FORMAT_SHORT` → **Number**: `day_of_week` 1–7 with **1 = Sunday, 2 = Monday, …, 7 = Saturday**; `month` 1–12 (1 = January).
- `FORMAT_MEDIUM` → **String**: `day_of_week` "Sun", "Mon", …, "Sat"; `month` "Jan", "Feb", …, "Dec".
- `FORMAT_LONG` → *"Currently the same as FORMAT_MEDIUM"*.
- *"The String values returned are language and device dependent."* — so a further `Lang.String` post-processing is not needed, but the abbreviations are locale-dependent.

So for **weekday + day-of-month + month** on the four-tube face: call
`Time.Gregorian.info(Time.now(), Time.FORMAT_MEDIUM)` and read `.day_of_week`, `.day`, `.month`.

---

## 5. Permissions

**Syntax** (verbatim from Garmin):
```xml
<iq:permissions>
    <iq:uses-permission id="Sensor"/>
</iq:permissions>
```
— https://developer.garmin.com/connect-iq/core-topics/manifest-and-permissions/

**Relevant rows of the official permission table** (columns: Watch Face / Data Field / Widget / App / Audio):

| Permission | Module(s) | API Level | Watch Face |
|---|---|---|---|
| `Sensor` | `Toybox.Sensor` | 1.0.0 | *(blank — not grantable)* |
| `SensorHistory` | `Toybox.SensorHistory` | 2.1.0 | *(blank in the permission table; `✓` in the App Types module table — see §9)* |
| `UserProfile` | `Toybox.UserProfile` | 1.0.0 | ✓ |
| `Background` | `Toybox.Background` | 2.3.0 | ✓ |
| `ComplicationSubscriber` | `Toybox.Complications` | 4.1.0 | ✓ |
| `Communications` | `Toybox.Communications`, `Toybox.Authentication` | 1.0.0 | ✓ |
— https://developer.garmin.com/connect-iq/core-topics/manifest-and-permissions/

**`ActivityMonitor` is NOT in the permission list at all** — the string "ActivityMonitor" does not occur anywhere on
the Manifest-and-Permissions page. So **steps + `getHeartRateHistory()` need no `<iq:uses-permission>` entry**.
(An older community manifest example shows `<iq:uses-permission id="ActivityMonitor"/>`; that id is not in the current
official list, and requesting an unknown id is the kind of thing that produces a manifest validation error.)

**Practical permission block for this project (recommended):**
```xml
<iq:permissions>
    <iq:uses-permission id="UserProfile"/>   <!-- only if you use Toybox.UserProfile (e.g. HR zones, resting HR) -->
    <!-- SensorHistory only if you use Toybox.SensorHistory -->
</iq:permissions>
```
**Store-review implications:** permissions are surfaced to the user **at install time** — Garmin's support page lists
them under names the user sees, e.g. *"Heart Rate, Barometer, Temperature and Altitude History"* (SensorHistory) and
*"Sensor Data (i.e., ANT+, Heart Rate, Compass)"* (Sensor). Requesting the minimum set is the right call; every
permission you request is displayed on the store listing.
— https://support.garmin.com/en-US?faq=Z8zVsJfH3v1KAhrFTNmZi8 *(secondary — Garmin Customer Support, not developer docs)*
Also from App Review Guidelines: apps must not *"override information previously synced to their Connect account"* and
must not drain battery — a watch face that grabs extra sensors for no reason is exactly the pattern they call out.
— https://developer.garmin.com/connect-iq/app-review-guidelines/

---

## 6. Drawing the artwork plus text

### Loading and drawing a bitmap
```
WatchUi.loadResource(resource as Lang.ResourceId) as WatchUi.Resource      // API 1.0.0
Application.loadResource(resource as Lang.ResourceId) as Application.Resource // API 3.1.0
Dc.drawBitmap(x as Lang.Numeric, y as Lang.Numeric, bitmap as Graphics.BitmapType) as Void
Dc.drawBitmap2(x, y, bitmap, options as { :bitmapX, :bitmapY, :bitmapWidth, :bitmapHeight, :tintColor,
                                          :filterMode, :transform }) as Void
Dc.drawScaledBitmap(x, y, width, height, bitmap) as Void
```
— https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi.html (loadResource),
https://developer.garmin.com/connect-iq/api-docs/Toybox/Graphics/Dc.html (draw calls)

Garmin's own example (verbatim from the Resources page):
```mc
image = Application.loadResource( Rez.Drawables.bitmap_id ) as BitmapResource;
dc.drawBitmap( 50, 50, image );
```
and the warning *"Loading a resource can be an expensive operation, so do not load resources when handling screen
updates."* — https://developer.garmin.com/connect-iq/core-topics/resources/

⚠ **`Graphics.createBitmap` does NOT exist** — I searched the Graphics module page and there is no `createBitmap`.
The creation APIs are `Graphics.createBufferedBitmap(options)` (options: `:width`, `:height`, `:palette`,
`:colorDepth`, `:bitmapResource`, `:alphaBlending`, `:scale`, …) and the resource compiler's `Rez.Drawables.*`.
— https://developer.garmin.com/connect-iq/api-docs/Toybox/Graphics.html

Declaring the resource:
```xml
<bitmap id="bg" filename="images/background.png" scaleX="..." scaleY="..." scaleRelativeTo="screen"/>
```
Useful `<bitmap>` attributes (Garmin's table): `dithering` (`floyd_steinberg`|`none`, default floyd_steinberg),
`compress` (true/false), `automaticPalette` (auto-reduce colour palette; on 16-bit devices limited to 256 colours),
`packingFormat` (`default`|`png`|`jpg`|`yuv`, only some on certain devices), `scaleX`/`scaleY` (pixels or %, default
100%), `scaleRelativeTo` (`screen` default | `image`) — **`scaleRelativeTo="screen"` re-scales the image at compile
time for the product it is built for**, which is how you take a single 1024×1024 master and get a 320×360-target fit.
— https://developer.garmin.com/connect-iq/core-topics/resources/

### Bitmap constraints for a 320×360 / 16-bit device
- Resource compiler accepts **JPG/JPEG, BMP/WBMP, GIF, SVG and PNG**. — Resources page (above)
- Supported bit depths: **1, 2, 4, 8, 16 BPP**. Loaded-size cost for a 100×100 image, per Garmin:
  1 BPP = 1.22 KB, 2 BPP = 2.44 KB, 4 BPP = 4.88 KB, 8 BPP = 9.77 KB, 16 BPP = 19.53 KB.
  → scale linearly: a full-screen 320×360 16 BPP image ≈ **225 KB of graphics memory**. A 8 BPP (256-colour) version
  ≈ **112 KB**. The Venu Sq 2 is RGB565/65536 colours = **16 BPP** internally.
  — https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-optimize-bitmaps/
- **Watch Face runtime memory limit = 131072 bytes (128 KB)**, from the device reference
  (https://developer.garmin.com/connect-iq/device-reference/venusq2/). A full-screen 16-BPP bitmap is bigger than that
  budget on its own — **reduce the palette** (`<palette>`, `automaticPalette`) and/or split the artwork, and load
  nothing you do not draw.
- **Max image pixel dimensions / per-image byte cap: NOT documented on the device page — see §9 (UNVERIFIED).**

### One background image vs procedural drawing
Garmin does not state a preference. The relevant documented constraints point one way:
- A single full-screen background **blows the 128 KB watch-face memory budget at 16 BPP** and is re-drawn in full on
  every `onUpdate` (once per second in high power).
- For AMOLED always-on you must be able to render a **< 10 % luminance** low-power variant anyway
  (§8), which a full-colour brass artwork cannot supply by itself.
- Compromise Garmin *does* document: build the complex artwork once into a **`BufferedBitmap`** during `onUpdate`
  (which is *"not subject to the execution time limits"*), then blit the single object in `onPartialUpdate`.
  — https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-get-my-watch-face-to-update-every-second/
Suggestion (engineering judgement, not a Garmin rule): ship the brass frame/background as one palette-reduced
(≤256-colour) PNG, and draw the four nixie glass tubes + text procedurally or as small per-digit bitmaps so the live
digits can be redrawn inside a tight `setClip()` region.

### Text
```
Dc.drawText(x as Lang.Numeric, y as Lang.Numeric,
            font as Graphics.FontType,
            text as Lang.Object or Null,
            justification as Graphics.TextJustification or Lang.Number) as Void
Dc.getTextDimensions(text as Lang.String, font as Graphics.FontType) as [ Lang.Number, Lang.Number ]
Dc.getTextWidthInPixels(text as Lang.String, font as Graphics.FontType) as Lang.Number
Dc.getFontHeight(font as Graphics.FontType) as Lang.Number
```
Justification constants (`Graphics.TextJustification`):
`TEXT_JUSTIFY_LEFT` = 2, `TEXT_JUSTIFY_CENTER` = 1, `TEXT_JUSTIFY_RIGHT` = 0, **`TEXT_JUSTIFY_VCENTER` = 4** (can be
bitwise-OR'd with a horizontal one — e.g. `TEXT_JUSTIFY_CENTER | TEXT_JUSTIFY_VCENTER`); `x,y` is the anchor point.
Garmin's own example uses `dc.drawText(dc.getWidth()/2, dc.getHeight()/2, Graphics.FONT_LARGE, "Hello World", Graphics.TEXT_JUSTIFY_CENTER)`.
— https://developer.garmin.com/connect-iq/api-docs/Toybox/Graphics/Dc.html and
https://developer.garmin.com/connect-iq/api-docs/Toybox/Graphics.html

Built-in fonts (`Graphics.FontDefinition`, API 1.0.0): `FONT_XTINY`, `FONT_TINY`, `FONT_SMALL`, `FONT_MEDIUM`,
`FONT_LARGE`, `FONT_NUMBER_MILD`, `FONT_NUMBER_MEDIUM`, `FONT_NUMBER_HOT`, `FONT_NUMBER_THAI_HOT`, plus
`FONT_SYSTEM_*` (1.3.0), `FONT_GLANCE*` (3.1.8) and `FONT_AUX1..9` (4.2.x).
For the Venu Sq 2 the numeric faces are big: **`FONT_NUMBER_HOT` is Yantramanav at 119 px**
(`006B411500_YANTRAMANAV_NUMBER_LARGE`) — good for the nixie digits without writing any font work at all.
— https://developer.garmin.com/connect-iq/device-reference/venusq2/ (Fonts table)

### Custom bitmap fonts
- Resource compiler reads fonts in **TXT or PNG** format; use **BMFont** (http://www.angelcode.com/products/bmfont/)
  to produce a compatible `.fnt` (+ `.png`), setting **Unicode** as the character set on export.
- Declare: `<font id="font_id" filename="roboto.fnt" antialias="true" />`
- *"Since bitmap fonts can take a lot of runtime memory, the font converter defaults to non-anti-aliased 1-bit fonts
  to save memory."*
- **`filter`** restricts which glyphs are imported — Garmin's example for a big numeric watch-face font:
  `<font id="font_id" filename="big_font.fnt" filter="[PHONE]:"/>` and the advice *"If you use custom fonts for
  numeric display, use the filter option to only load the critical glyphs. This will save memory."*
- Load with `WatchUi.loadResource(Rez.Fonts.<id>)`; colour with `dc.setColor(fg, Gfx.COLOR_TRANSPARENT)` before
  `drawText` so the glyph background is transparent (this is how Garmin's custom-font FAQ overlays text on artwork).
— https://developer.garmin.com/connect-iq/core-topics/resources/ ,
https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-use-custom-fonts/ ,
https://developer.garmin.com/connect-iq/connect-iq-basics/app-types/

---

## 7. Building, simulating, sideloading, publishing

### Build (command line)
```
connectiq                                                        # start the simulator first
monkeyc -d venusq2 -f monkey.jungle -o SteampunkNixie.prg -y developer_key.der
monkeydo SteampunkNixie.prg venusq2
```
`monkeyc` arguments, quoted: `-d <arg>` Target device · `-f <arg>` Jungle files · `-o <arg>` Output file to create ·
`-y <arg>` Private key to sign builds with. `monkeydo` args: `executable`, `device_id` (e.g. `"fenix5plus"` — ours is
`venusq2`), `-n` (native sensor pairing mode), `-t` (Run No Evil unit tests).
— https://developer.garmin.com/connect-iq/reference-guides/monkey-c-command-line-setup/
Output is a single **`.prg`** (a *"Connect IQ executable"*). In VS Code the equivalent is **Run > Run Without
Debugging** (picks the product) / command palette **`Monkey C: Build for Device`** (picks product + output folder).
— https://developer.garmin.com/connect-iq/connect-iq-basics/your-first-app/

**Project layout** (VS Code "New Project"): `resources/` (layouts, images, fonts, strings), `source/` (`.mc` files,
split into App and View), `manifest.xml`; the extension also generates the **`monkey.jungle`** build file. Jungle is
Garmin's build framework (`-f`); see https://developer.garmin.com/connect-iq/reference-guides/jungle-reference/
— https://developer.garmin.com/connect-iq/connect-iq-basics/your-first-app/

### Testing in the Connect IQ Simulator
- Start with `connectiq` (or via VS Code); run the app with `monkeydo <prg> venusq2` (or Run > Run Without Debugging).
- **Simulated HR/steps:** simulator menu **Simulation → Activity Data**, then either **"Data Simulation"** (random
  canned sensor data) or **"FIT/GPX Playable File"** and pick a `.fit`/`.gpx` *with* HR data. You must press the
  play/start button in the bottom-left of the timer controls for data to flow. In the sim, `ActivityMonitor`
  `getHeartRateHistory()` returns **canned data that never changes** (commonly 80), so to see the HR change you must
  drive it with a FIT/GPX file. *(Secondary — Garmin forum threads:*
  https://forums.garmin.com/developer/connect-iq/f/discussion/367539/data-simulation-from-fit-or-gpx-file-in-garmin-simulator-in-watchface ,
  https://forums.garmin.com/developer/connect-iq/f/discussion/406064/how-to-simulate-heart-rate-data-in-the-simulator-version-8-1 *)*
  ⚠ I could not find a Garmin *developer-docs* page describing the Simulation menu, only forum threads — see §9.
- **AMOLED-specific:** `File → View Screen Heat Map` opens the **"Screen Burn-in Simulation"** dialog — press Start to
  simulate a 24-hour run in minutes. *"The menu option is only enabled when simulating a WatchFace on a device that
  supports screen protection."* — https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-make-a-watch-face-for-amoled-products/
- `System.println()` output goes to the VS Code console; **on a real device it writes to
  `/GARMIN/APPS/LOGS/<PRGNAME>.TXT`, which you must create yourself and name after the PRG** (e.g. `/GARMIN/APPS/MYAPP.PRG`
  → create `/GARMIN/APPS/LOGS/MYAPP.TXT`). — https://developer.garmin.com/connect-iq/core-topics/debugging/
- Command-line debugger: `mdd` (gdb-like) after starting the simulator.
  — https://developer.garmin.com/connect-iq/core-topics/debugging/

### Sideloading onto the real Venu Sq 2
Garmin's official instructions (verbatim steps):
1. Plug your device into your computer.
2. Command palette → **`Monkey C: Build for Device`**, select the product (Venu Sq 2), choose an output folder.
3. *"Copy the generated PRG files to your device's **GARMIN/APPS** directory."*
4. Unplug; the app appears in the watch's Connect IQ apps / watch-face list.
— https://developer.garmin.com/connect-iq/connect-iq-basics/your-first-app/

*Secondary corroboration of the exact path and that watch faces specifically live there:* the watch's own
`GARMIN/GARMINDEVICE.XML` declares
`<Name>IQWatchFaces</Name> … <Path>GARMIN/APPS</Path> … <FileExtension>PRG</FileExtension>`, i.e. **watch faces (and
watch apps) are stored in `GARMIN/APPS`**, while widgets/data fields go to `GARMIN/APPS/MEDIA`. Multiple forum posts and
downstream projects describe copying the `.prg` to `\GARMIN\APPS` over USB mass-storage/MTP, and note it then behaves
like any installed app (deletable via the Connect IQ app on the phone or Garmin Express). *The watch may rename the file
to an 8-character hex name (visible in `GARMINDEVICE.XML`).*
— https://forums.garmin.com/developer/connect-iq/f/discussion/333043/can-i-sideload-a-data-field-from-my-venue-to-my-fr-965/1616496
and https://github.com/missing-foss/trobar-garmin
**"Does it survive a sync?"** — no Garmin doc says a sideloaded PRG is removed by a Garmin Connect sync; the community
consensus is that it stays installed as a normal app. **Marked UNVERIFIED** (see §9). The one real risk is that a
firmware update can wipe side-loaded apps; re-copying the PRG is the fix.

### Publishing to the Connect IQ Store
1. Manifest must list all supported products.
2. **`Monkey C: Export Project`** → generates a **`.iq`** file containing binaries for each supported device.
3. Upload at the developer site's **Submit an App** page (developer account required; you sign in with a Garmin Connect
   account).
4. Review: *"reviews are completed within 72 hours"*; +48 h if you declare ANT+ profiles. Until approved the app is
   visible only to you for testing. Rejections come by email with reasons and can be fixed and resubmitted.
5. You must sign with the **same developer key** for updates — losing it means you cannot update the listing.
— https://developer.garmin.com/connect-iq/core-topics/publishing-to-the-store/ and
https://developer.garmin.com/connect-iq/connect-iq-basics/getting-started/

---

## 8. Gotchas specific to watch faces

1. **Update cadence is not yours to choose.** High power: `onUpdate()` **once per second**; low power (AOD): `onUpdate()`
   **once per minute at the top of the minute**, plus `onPartialUpdate()` each second *only if the device supports it*.
   *"The application will not have access to timers or animations while in low power mode."*
   — https://developer.garmin.com/connect-iq/api-docs/Toybox/WatchUi/WatchFace.html
2. **`onPartialUpdate` must clip.** You must call `dc.setClip(x, y, w, h)` first, and update as few pixels as possible.
   Exceeding the power budget → `WatchFaceDelegate.onPowerBudgetExceeded(powerInfo)`, and per the FAQ *"partial updates
   will stop executing for the remainder of the app life-cycle."* (the WatchFace page's phrasing is that the partial
   update simply does not draw). Do not rely on it for the whole first minute.
   — https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-get-my-watch-face-to-update-every-second/
3. **AMOLED burn-in protection is the dominant constraint on the Venu Sq 2.** Official rules: burn-in protection
   activates when the watch face is in the foreground and the system enters sleep mode; *"if more than 10% of the screen
   pixels are on or any pixel is on for longer than 3 minutes, the system will shut off the screen."* *"Since the Venu®
   2, the rule for always-on is to use less than 10% of the screen's luminance."* Detect with
   `System.DeviceSettings.requiresBurnInProtection` (`as Lang.Boolean`) and branch on
   `System.getDisplayMode()` → `System.DISPLAY_MODE_HIGH_POWER` / `DISPLAY_MODE_LOW_POWER` / `DISPLAY_MODE_OFF`.
   *"Most of the existing Connect IQ watch faces will trip the burn-in protector."* — a full-screen brass artwork with
   lit nixie tubes will absolutely trip it, and the screen will shut off in AOD after 3 minutes.
   — https://developer.garmin.com/connect-iq/connect-iq-faq/how-do-i-make-a-watch-face-for-amoled-products/
   (API confirmations: `System.getDisplayMode() as System.DisplayMode` — "only available in devices with AMOLED or LCD
   screens" — and `DeviceSettings.requiresBurnInProtection as Lang.Boolean`,
   `DeviceSettings.screenWidth/screenHeight as Lang.Number`.)
   — https://developer.garmin.com/connect-iq/api-docs/Toybox/System.html ,
   https://developer.garmin.com/connect-iq/api-docs/Toybox/DeviceSettings.html → see
   https://developer.garmin.com/connect-iq/api-docs/Toybox/System/DeviceSettings.html
4. **Watch faces get the smallest API surface and the smallest memory budget.** *"watch faces have the least access to
   APIs in the system … They cannot access the compass, GPS, or other sensors."* Watch Face memory limit on this device:
   **131072 bytes**. — app-types page + device reference (URLs above).
5. **Requests outside the allow-list fail at runtime, not compile time in a friendly way:**
   *"A Toybox module requested for your app type that is outside this list will result in a Symbol Not Found error."*
   — https://developer.garmin.com/connect-iq/connect-iq-basics/app-types/
6. **Load resources once, in `onShow()`/`initialize()` — never in `onUpdate`.** *"Loading a resource can be an
   expensive operation, so do not load resources when handling screen updates."* — Resources page.
7. **Trim custom fonts with `filter=`** — *"If you use custom fonts for numeric display, use the filter option to only
   load the critical glyphs."* — app-types page.
8. **Performance is a review criterion, not a nicety.** App Review Guidelines: *"Apps should not cause Garmin's products
   to no longer meet their expected battery life"*, and *"By the time you submit, your app should be fully completed,
   tested, and ready for use."* — https://developer.garmin.com/connect-iq/app-review-guidelines/
9. **The same signing key is required forever** for store updates; there is no recovery. And **sideloaded builds are
   signed too** — `-y` is required by `monkeyc`, so an unsigned PRG is not an option.
   — Getting Started + command-line setup pages.
10. **Do not display seconds full-time** — there is no legal way to update every second except `onPartialUpdate`, and
    that only works in low power on devices that support partial updates, and only within the power budget.

---

## 9. Open questions / UNVERIFIED

1. **⚠ CONTRADICTION (highest risk): is `Toybox.Activity` usable from a watch face?**
   - Garmin's **App Types** table marks `Toybox.Activity` as available to *Data Field / App / Audio Content Provider*
     and **blank under Watch Face** — read cell-by-cell from the live HTML:
     https://developer.garmin.com/connect-iq/connect-iq-basics/app-types/
   - Yet the same page's Watch Faces prose says watch faces have access to *"current activity tracker status"* (which is
     `ActivityMonitor`), and Garmin's own `Toybox.Sensor` page confirms `Sensor` is *not* available to watch faces.
   - Meanwhile Garmin-forum moderator "jim_m_58" and many third-party watch faces use
     `Activity.getActivityInfo().currentHeartRate` **inside watch faces** and report it working (secondary sources):
     https://forums.garmin.com/developer/connect-iq/f/discussion/212496/getting-per-second-heart-rate-on-a-watch-face ,
     https://forums.garmin.com/developer/connect-iq/f/discussion/400174/wrist-removal-detection ,
     https://stackoverflow.com/questions/56990405/garmin-watchface-how-to-show-heartrate
   **Resolution I could not reach:** compile-test both. Safe design: use
   `ActivityMonitor.getHeartRateHistory()` as the guaranteed path and treat `Activity.getActivityInfo()` as an
   optional enhancement, guarded (`if (Activity has :getActivityInfo) { … }`) and never the sole source of HR.
2. **`SensorHistory` permission vs module availability disagree.** The App Types module table says
   `Toybox.SensorHistory` ✓ for Watch Face; the Manifest-and-Permissions table leaves the Watch Face column blank for
   the `SensorHistory` permission. Both are on Garmin's site:
   https://developer.garmin.com/connect-iq/connect-iq-basics/app-types/ vs
   https://developer.garmin.com/connect-iq/core-topics/manifest-and-permissions/ — **do not rely on SensorHistory in
   the watch face** without testing; `ActivityMonitor` covers the stated needs (steps + HR) with no permission at all.
3. **Max bitmap pixel dimensions and any per-image byte cap for the Venu Sq 2: UNVERIFIED.** The device reference page
   for `venusq2` gives screen size, colour depth, app memory limits, field layouts, part number, languages and fonts —
   **no image-dimension or per-image-size limit table**. The only documented image costs are the bit-depth KB/100×100
   figures (FAQ) and the 131072-byte watch-face memory limit (device page). Assume a 1024×1024 source PNG must be
   down-scaled/palette-reduced at compile time (`scaleX/scaleY/scaleRelativeTo="screen"`, `<palette>`), and verify by
   building.
4. **Connect IQ Store upload size limit for the `.iq` file: UNVERIFIED** — I found no Garmin developer-docs statement of
   a maximum `.iq`/PRG upload size, nor a per-app on-device size limit. Garmin's customer-support page
   *"Connect IQ App Limits on a Garmin Device"* exists but concerns the number/space of apps, not build size.
5. **Does a sideloaded PRG survive a Garmin Connect / Garmin Express sync? UNVERIFIED by Garmin docs.** Community
   consensus is yes (it is a normal installed app; remove it via the Connect IQ phone app or Garmin Express). Firmware
   updates are the known eraser.
6. **No Garmin developer-docs page found for the Simulator's Simulation menu** (Data Simulation / FIT-GPX Playable
   File / burn-in heat map). The burn-in heat-map menu *is* documented on the AMOLED FAQ page; the HR/steps data
   simulation workflow is only described in forum threads (linked in §7). Treat the exact menu labels as
   version-dependent between simulator releases.
7. **`Venu Sq 2` vs `Venu Sq 2 Music` device-file sharing:** Garmin lists them as two ids (`venusq2`, `venusq2m`) with
   identical documented specs. Whether the SDK ships literally one shared device definition behind those two ids is not
   stated. Listing both `<iq:product>` ids is the safe route if both must be supported.
8. **Watch-face battery/update-interval numbers are qualitative in the docs** — there is no published "minimum update
   interval" or numeric power-budget figure; the budget is enforced at runtime per device via
   `onPowerBudgetExceeded()`. The only hard numbers are the AMOLED rules (>10 % pixels on, or any pixel on >3 min → the
   system shuts the screen off; 10 % luminance rule since Venu 2).
9. **`Application.loadResource` vs `WatchUi.loadResource`:** both exist (API 3.1.0 and 1.0.0 respectively); Garmin's
   Resources page uses both in different examples. Not a contradiction, but pick one consistently.

---

## 10. Facts CONFIRMED BY COMPILING (the research above, corrected where it was wrong)

These were found by actually running `monkeyc` — each one is a compile error that the docs alone
did not prevent:

1. **`minApiLevel` needs THREE components.** `minApiLevel="5.0"` is rejected:
   `cvc-pattern-valid: Value '5.0' is not facet-valid with respect to pattern
   '[0-9]+\.[0-9]+\.[0-9]+(\.[0-9a-zA-Z_]+)?'`. Use **`5.0.0`**.

2. **A device must be listed in `<iq:products>` to be a build target**, even with `-d`:
   `ERROR: Target device id 'venux1' is not enabled in the application manifest file.`

3. **`WatchFacePowerInfo` members are PROPERTIES, not methods.** `powerInfo.getExecutionTimeAverage()`
   fails with `Undefined symbol ':getExecutionTimeAverage'`. The real members are
   **`executionTimeAverage`** and **`executionTimeLimit`** (both `-var` in the docs).

4. **A loaded bitmap is NOT `Graphics.Bitmap`.** `WatchUi.loadResource()` returns
   `WatchUi.Resource`, and `Dc.drawBitmap` accepts
   `BitmapReference or BufferedBitmap or BufferedBitmapReference or WatchUi.BitmapResource`.
   Assigning `as Graphics.Bitmap` fails with *"Cannot assign value '$.Toybox.Graphics.Bitmap' to
   member ':_bg'"*. The correct named type is **`Graphics.BitmapType`**:
   ```monkeyc
   private var _bg as Graphics.BitmapType or Null;
   _bg = WatchUi.loadResource(Rez.Drawables.Background) as Graphics.BitmapType;
   ```

5. **Declare drawable ids explicitly.** A `resources/drawables/drawables.xml` with
   `<bitmap id="Background" filename="background.png"/>` guarantees `Rez.Drawables.Background`
   instead of relying on filename inference.

### Working build command (verified)
```bash
"$APPDATA/Garmin/ConnectIQ/Sdks/connectiq-sdk-win-9.2.0-2026-06-09-92a1605b2/bin/monkeyc.bat" \
  -d <deviceId> -f monkey.jungle -o SteampunkNixie.prg -y keys/developer_key.der
```
Output `BUILD SUCCESSFUL` and a ~217 KB PRG.

### BLOCKER: the venusq2 device definition is not installed
`%APPDATA%\Garmin\ConnectIQ\Devices\` holds **38 devices, none of them venu
Sq 2** (it has venux1, venu441mm, venu445mm — but the current-generation models only). The SDK
Manager *knows* the device (`sdkmanager-config.ini` has `venusq2-first-seen=…` among 173 catalogue
entries) but never downloaded its definition, so `-d venusq2` fails with
`Invalid device id specified: 'venusq2'`. Fix: open the SDK Manager and add the Venu Sq 2 device.

---

## 11. Facts confirmed by RUNNING it on the venusq2m device profile

Verified in the CIQ Simulator against the real device definition (screen reports **320x360**):

### Text transparency — the one that looked like a rendering bug
`dc.drawText` **fills the text's bounding box with the background colour** passed to `setColor`.
Passing `Graphics.COLOR_BLACK` therefore paints an opaque rectangle over the artwork. It is
invisible where the text sits over dark areas (the tubes, the counter) and glaring over the brass
gauges — so it looks like a partial bug.

**Fix: `dc.setColor(colour, Graphics.COLOR_TRANSPARENT)`** (`COLOR_TRANSPARENT` = -1). Garmin's own
custom-font guide does exactly this: *"you specify a transparent background color for the font and
finally draw the time on top of the skyline"*.

### Built-in font heights on the Venu Sq 2 Music (measured with `dc.getFontHeight`)
| Font | px |
|---|---|
| FONT_XTINY | 39 |
| FONT_TINY | 44 |
| FONT_SMALL | 51 |
| FONT_MEDIUM | 59 |
| FONT_LARGE | 68 |
| FONT_NUMBER_MILD | 82 |
| FONT_NUMBER_MEDIUM | 105 |
| FONT_NUMBER_HOT | 155 |

**The smallest built-in font is 39 px**, so a dense layout needing ~53 px tube digits, ~32 px
drum/gauge digits and ~11 px unit labels CANNOT use built-in fonts. Custom fonts are mandatory, not
a refinement. (The device definition carries no font-size table — measure at runtime.)

### Generating custom fonts without BMFont
`ciq/make_fonts.py` writes the BMFont `.fnt` + grayscale atlas directly with PIL. Three gotchas:
1. **A glyph's `yoffset` is measured DOWN from the line top.** Writing `yoffset=-height` puts every
   glyph ABOVE the line box: the font loads fine and then draws **nothing**, with no error.
2. **`base` = distance from the line top down to the baseline**; for glyphs sitting on the baseline,
   `base` = the tallest glyph height, `lineHeight` = that + 2.
3. **Ink height is not a linear function of the point size at these sizes, so MEASURE the size
   rather than solving for it.** A serif face ran ~0.66x (76 pt -> 53 px digits), but on the
   rasteriser's hinted small sizes the ink jumps 2-5 px between adjacent point sizes: Courier Prime
   Bold's tallest digit measured 25 px at 44 pt and 30 px at 47 pt, so a computed correction
   oscillates between them (44 -> 49 -> 44). `px_for_ink_max()` scans the candidate sizes and takes
   the closest, preferring the smaller digit on a tie. `d.text(..., anchor="ls")`
   needs the baseline y BELOW the glyph body or the glyph is clipped to slivers.

Condensing horizontally (`condense=0.58`) is how the "tall and thin" look survives — a bitmap font
cannot be scaled at runtime, so the proportions must be baked into the glyphs.

### Layout consequence
The text centre points derived from the artwork were spaced for the HTML model's metrics. With real
font metrics the line boxes collide, so readouts inside a gauge must be spaced by their actual
heights (the date dial needed SAT/03/OCT at y 216/248/282 inside a dial face spanning y 206-298).

### Sideload (not yet done — needs the watch on USB)
Copy the built PRG to the watch's `GARMIN/APPS` directory, then unplug. The device may rename it to
an 8-character hex name. Garmin's wording: *"Copy the generated PRG files to your device's
GARMIN/APPS directory"*.
