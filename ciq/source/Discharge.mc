import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;

// ---------------------------------------------------------------- animation tuning
// Everything the preview needs is a top-level const so ciq/preview.py can parse it and replay
// the SAME frames offline (it mirrors this file's LCG, state machine and geometry exactly).

const FRAME_MS = 100;          // animation tick while awake (Timer minimum is 50 ms)

// Arc channels: the endpoints (ARC_AX/AY/BX/BY) and the dark band the bolts stay inside
// (ARC_Y_MIN/MAX) are GENERATED into Layout.mc - measured once on the tube-tip knobs and mapped
// through the current layout. Channels 0-2 jump knob-to-knob across the three gaps above the
// domes; 3 and 4 discharge from the outer knobs to the screen edge.
// ARC_TUBE_A/B document that wiring. Nothing reads them any more: the tubes' glow stopped pulsing
// per tube, so there is no "a spark touched this tube" state left to flare (user decision, L63).
const ARC_TUBE_A = [0, 1, 2, 0, 3];      // the tube each end touches (-1: the case)
const ARC_TUBE_B = [1, 2, 3, -1, -1];
const ARC_ON_MIN = 1;                    // frames a strike lasts (re-jittered every frame)
const ARC_ON_MAX = 3;
const ARC_OFF_MIN = 4;                   // frames of quiet between strikes
const ARC_OFF_MAX = 24;
const ARC_TENDRILS = 2;                 // forked side branches per strike

// Bolt colours, from the round-6 lightning that passed review (docs: PROJECT_STATUS round 6):
// a white core, a blue-white sheath, a blue bloom. Drawn bloom -> sheath -> core.
const ARC_BLOOM = 0x2F6EA8;
const ARC_SHEATH = 0x7AB6F7;
const ARC_CORE = 0xEAF6FF;

// ---------------------------------------------------------------- side sparks (user request)
// The artwork paints a blue spark beside the outer tubes, and the user asked for it to be ANIMATED:
// "the emitter on the side where the current blue spark emitter is ... fly off into the area above
// the emitter beside the tubes, blue white sparks". So a burst emits from the painted spark's own
// bright core (SPARK_X/SPARK_Y, generated into Layout.mc from the shipping frame) and its filaments
// fan UPWARD beside the tubes, re-jittered every frame while the burst lasts. Same palette as the
// bolts, which is also what the reference's sparks measure (core (149,191,233), tips (11,20,37)).
const SPARK_UP = -90;            // screen degrees: straight up (screen y grows downward)
const SPARK_BIAS = [-13, 13];    // per emitter: tilt slightly outward, away from its own tube
const SPARK_LINES = 10;          // filaments per burst
const SPARK_SPREAD = 32;         // half-angle of the fan, degrees, about straight up
const SPARK_LEN_MIN = 22;        // filament length, screen px - reaches up beside the tube
const SPARK_LEN_MAX = 70;
const SPARK_ON_MIN = 1;          // frames a burst lasts (re-jittered every frame)
const SPARK_ON_MAX = 4;
const SPARK_OFF_MIN = 5;         // frames of quiet between bursts
const SPARK_OFF_MAX = 22;

//! The nixie discharge: arc flicker between the tube tips.
//!
//! Deterministic by design: a 31-bit LCG seeded once, advanced only by step(), so a given frame
//! number always produces the same picture — which is what lets preview.py reproduce it.
//!
//! This class also carried a per-tube GLOW PULSE: the halo rings breathed 35..120 % and flared to
//! 260 % the instant a spark touched a tube, with the hue-preserving cap LESSONS L61 describes. The
//! user removed it — a static bright glow reads cleaner, the flare was never worth the extra state,
//! and the tube glow is now the fixed baseline colour in source/TubeInk.mc.
class Discharge {

    private var _seed as Number;
    private var _timer as Array<Number>;   // frames left in the current on/off phase
    private var _on as Array<Boolean>;
    private var _sparkTimer as Array<Number>;   // the side sparks' own on/off phases
    private var _sparkOn as Array<Boolean>;

    function initialize() {
        _seed = 20261010;
        _timer = [0, 0, 0, 0, 0];
        _on = [false, false, false, false, false];
        // stagger the first strikes so the channels do not fire together on wake
        for (var k = 0; k < ARC_AX.size(); k += 1) {
            _timer[k] = between(1, ARC_OFF_MAX);
        }
        _sparkTimer = [0, 0];
        _sparkOn = [false, false];
        for (var k = 0; k < SPARK_X.size(); k += 1) {
            _sparkTimer[k] = between(1, SPARK_OFF_MAX);
        }
    }

    //! The resting state: no arcs and no sparks. Used whenever the animation is not running, so a
    //! once-a-minute redraw never freezes a half-drawn strike on the screen.
    function reset() as Void {
        for (var k = 0; k < _on.size(); k += 1) {
            _on[k] = false;
        }
        for (var k = 0; k < _sparkOn.size(); k += 1) {
            _sparkOn[k] = false;
        }
    }

    //! 31-bit LCG (the classic ANSI C constants), computed in Long so it cannot overflow.
    private function next() as Number {
        _seed = ((_seed.toLong() * 1103515245l + 12345l) & 0x7FFFFFFFl).toNumber();
        return _seed >> 16;                     // the high 15 bits are the well-mixed ones
    }

    private function between(lo as Number, hi as Number) as Number {
        return lo + next() % (hi - lo + 1);
    }

    //! Advance one frame: the arc and spark state machines.
    function step() as Void {
        for (var k = 0; k < _timer.size(); k += 1) {
            _timer[k] -= 1;
            if (_timer[k] <= 0) {
                _on[k] = !_on[k];
                _timer[k] = _on[k] ? between(ARC_ON_MIN, ARC_ON_MAX)
                                   : between(ARC_OFF_MIN, ARC_OFF_MAX);
            }
        }
        for (var k = 0; k < _sparkTimer.size(); k += 1) {
            _sparkTimer[k] -= 1;
            if (_sparkTimer[k] <= 0) {
                _sparkOn[k] = !_sparkOn[k];
                _sparkTimer[k] = _sparkOn[k] ? between(SPARK_ON_MIN, SPARK_ON_MAX)
                                             : between(SPARK_OFF_MIN, SPARK_OFF_MAX);
            }
        }
    }

    //! Draw every active arc and spark. Each call re-jitters them, so a strike crackles while it lasts.
    function draw(dc as Graphics.Dc) as Void {
        if (dc has :setAntiAlias) {
            dc.setAntiAlias(true);
        }
        for (var k = 0; k < _on.size(); k += 1) {
            if (_on[k]) {
                drawArc(dc, k);
            }
        }
        for (var k = 0; k < _sparkOn.size(); k += 1) {
            if (_sparkOn[k]) {
                drawSpark(dc, k);
            }
        }
        if (dc has :setAntiAlias) {
            dc.setAntiAlias(false);
        }
        dc.setPenWidth(1);
    }

    //! One side spark: SPARK_LINES filaments fanning UP from the painted spark's core, each with a
    //! bend across its own path so it reads as a discharge rather than as a fan of straight lines,
    //! drawn bloom (3 px) -> sheath (2 px) -> core (1 px), plus a small hot head at the emitter.
    private function drawSpark(dc as Graphics.Dc, k as Number) as Void {
        var ox = SPARK_X[k];
        var oy = SPARK_Y[k];
        var pens = [3, 2, 1];
        var inks = [ARC_BLOOM, ARC_SHEATH, ARC_CORE];
        for (var p = 0; p < 3; p += 1) {
            dc.setPenWidth(pens[p]);
            dc.setColor(inks[p], Graphics.COLOR_TRANSPARENT);
            for (var i = 0; i < SPARK_LINES; i += 1) {
                var deg = SPARK_UP + SPARK_BIAS[k]
                          + (between(0, 2000) - 1000) * SPARK_SPREAD / 1000.0;
                var rad = Math.toRadians(deg.toFloat());
                var dx = Math.cos(rad);
                var dy = Math.sin(rad);
                var len = between(SPARK_LEN_MIN, SPARK_LEN_MAX).toFloat();
                var kink = between(-5, 5).toFloat();
                // bend perpendicular to the filament: (-dy, dx)
                var mx = ox + dx * len * 0.55 - dy * kink;
                var my = oy + dy * len * 0.55 + dx * kink;
                var tx = ox + dx * len - dy * kink + between(-4, 4);
                var ty = oy + dy * len + dx * kink;
                dc.drawLine(ox, oy, mx, my);
                dc.drawLine(mx, my, tx, ty);
            }
        }
        dc.setPenWidth(1);
        dc.setColor(ARC_CORE, Graphics.COLOR_TRANSPARENT);
        dc.fillCircle(ox, oy, 2);                    // the head: a bright 2 px pip
        dc.setColor(ARC_BLOOM, Graphics.COLOR_TRANSPARENT);
        dc.drawCircle(ox, oy, 4);
    }

    //! One bolt: 3 levels of midpoint displacement (9 points) perpendicular to the chord, plus
    //! ARC_TENDRILS forked tendrils, drawn as bloom (4 px) -> sheath (2 px) -> core (1 px).
    private function drawArc(dc as Graphics.Dc, k as Number) as Void {
        var xs = [ARC_AX[k].toFloat()] as Array<Float>;
        var ys = [ARC_AY[k].toFloat()] as Array<Float>;
        xs.add(ARC_BX[k].toFloat());
        ys.add(ARC_BY[k].toFloat());
        var dx = xs[1] - xs[0];
        var dy = ys[1] - ys[0];
        var len = Math.sqrt(dx * dx + dy * dy).toFloat();
        var nx = -dy / len;
        var ny = dx / len;
        var amp = len * 0.22;
        for (var level = 0; level < 3; level += 1) {
            var nxs = [xs[0]] as Array<Float>;
            var nys = [ys[0]] as Array<Float>;
            for (var i = 0; i < xs.size() - 1; i += 1) {
                var off = (between(0, 2000) - 1000) * amp / 1000.0;
                nxs.add((xs[i] + xs[i + 1]) / 2.0 + nx * off);
                nys.add(clampY((ys[i] + ys[i + 1]) / 2.0 + ny * off));
                nxs.add(xs[i + 1]);
                nys.add(ys[i + 1]);
            }
            xs = nxs;
            ys = nys;
            amp = amp / 2.0;
        }
        // two tendrils: from inner points, out along the normal (either side), each with a kink
        var tx = [] as Array<Float>;
        var ty = [] as Array<Float>;
        for (var t = 0; t < ARC_TENDRILS; t += 1) {
            var j = between(2, 6);
            var side = (between(0, 1) == 0) ? -1.0 : 1.0;
            var tl = between(5, 11).toFloat();
            var kx = xs[j] + nx * side * tl * 0.5 + (between(0, 6) - 3);
            var ky = clampY(ys[j] + ny * side * tl * 0.5);
            tx.addAll([xs[j], kx, kx + nx * side * tl * 0.5 + (between(0, 6) - 3)]);
            ty.addAll([ys[j], ky, clampY(ky + ny * side * tl * 0.5)]);
        }

        var pens = [4, 2, 1];
        var inks = [ARC_BLOOM, ARC_SHEATH, ARC_CORE];
        for (var p = 0; p < 3; p += 1) {
            dc.setPenWidth(pens[p]);
            dc.setColor(inks[p], Graphics.COLOR_TRANSPARENT);
            for (var i = 0; i < xs.size() - 1; i += 1) {
                dc.drawLine(xs[i], ys[i], xs[i + 1], ys[i + 1]);
            }
            if (p > 0) {        // tendrils are thinner: no bloom pass
                for (var t = 0; t < tx.size(); t += 3) {
                    dc.drawLine(tx[t], ty[t], tx[t + 1], ty[t + 1]);
                    dc.drawLine(tx[t + 1], ty[t + 1], tx[t + 2], ty[t + 2]);
                }
            }
        }
    }

    private function clampY(y as Float) as Float {
        if (y < ARC_Y_MIN) {
            return ARC_Y_MIN.toFloat();
        }
        if (y > ARC_Y_MAX) {
            return ARC_Y_MAX.toFloat();
        }
        return y;
    }
}
