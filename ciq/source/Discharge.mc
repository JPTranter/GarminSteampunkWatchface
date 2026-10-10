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

// Glow pulse: the halo rings of each tube breathe between PULSE_MIN..PULSE_MAX % of their
// static brightness — each tube holds a target for PULSE_HOLD_MIN..MAX frames and eases toward
// it (1/4 per frame), so it reads as a gas glow breathing rather than per-frame noise — and
// FLASH to PULSE_FLARE the instant an arc touches that tube, then fade back. The first range
// (78..100 %, flare 140 %, re-drawn every frame) was invisible on the watch: the rings are dark
// blues, so a +-20 % swing moved them by a few levels. Only the HALO moves — the core glyph stays fixed so the time keeps
// its contrast (LESSONS L37: the halo carries the colour; the core carries the contrast).
const PULSE_MIN = 35;
const PULSE_MAX = 120;
const PULSE_FLARE = 260;
const PULSE_HOLD_MIN = 3;
const PULSE_HOLD_MAX = 8;

//! The nixie discharge: arc flicker between the tube tips plus the per-tube glow pulse.
//!
//! Deterministic by design: a 31-bit LCG seeded once, advanced only by step(), so a given frame
//! number always produces the same picture — which is what lets preview.py reproduce it.
class Discharge {

    private var _seed as Number;
    private var _timer as Array<Number>;   // frames left in the current on/off phase
    private var _on as Array<Boolean>;
    private var _pulse as Array<Number>;   // per-tube halo brightness, %
    private var _target as Array<Number>;  // the level each tube is easing toward
    private var _hold as Array<Number>;    // frames before that tube picks a new target

    function initialize() {
        _seed = 20261010;
        _timer = [0, 0, 0, 0, 0];
        _on = [false, false, false, false, false];
        _pulse = [100, 100, 100, 100];
        _target = [100, 100, 100, 100];
        _hold = [0, 0, 0, 0];
        // stagger the first strikes so the channels do not fire together on wake
        for (var k = 0; k < ARC_AX.size(); k += 1) {
            _timer[k] = between(1, ARC_OFF_MAX);
        }
    }

    //! The resting state: no arcs, halos at 100 %. Used whenever the animation is not running,
    //! so a once-a-minute redraw never freezes a half-drawn strike on the screen.
    function reset() as Void {
        for (var k = 0; k < _on.size(); k += 1) {
            _on[k] = false;
        }
        for (var i = 0; i < _pulse.size(); i += 1) {
            _pulse[i] = 100;
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

    //! Advance one frame: the arc state machines, then the pulse.
    function step() as Void {
        for (var k = 0; k < _timer.size(); k += 1) {
            _timer[k] -= 1;
            if (_timer[k] <= 0) {
                _on[k] = !_on[k];
                _timer[k] = _on[k] ? between(ARC_ON_MIN, ARC_ON_MAX)
                                   : between(ARC_OFF_MIN, ARC_OFF_MAX);
            }
        }
        for (var i = 0; i < _pulse.size(); i += 1) {
            _hold[i] -= 1;
            if (_hold[i] <= 0) {
                _target[i] = between(PULSE_MIN, PULSE_MAX);
                _hold[i] = between(PULSE_HOLD_MIN, PULSE_HOLD_MAX);
            }
            if (touched(i)) {
                _pulse[i] = PULSE_FLARE;                         // instant flash ...
            } else {
                _pulse[i] = (_pulse[i] * 3 + _target[i]) / 4;    // ... then ease back
            }
        }
    }

    private function touched(tube as Number) as Boolean {
        for (var k = 0; k < _on.size(); k += 1) {
            if (_on[k] && (ARC_TUBE_A[k] == tube || ARC_TUBE_B[k] == tube)) {
                return true;
            }
        }
        return false;
    }

    //! A halo colour scaled by this tube's current pulse.
    //!
    //! The scale is CAPPED at the value that just reaches 255 in the colour's brightest channel.
    //! Multiplying the channels and clamping them instead (the first version) shifts the HUE: a
    //! saturated orange like 0xFF7626 clipped its red and green to 255 when the glow flared, so the
    //! digit's glow turned yellow exactly when it got boldest (user: "when the number becomes more
    //! bold, its colour should only change slightly - now it becomes too yellow"). Capping the
    //! multiplier means the pulse changes brightness only, and the hue cannot drift.
    function haloColour(tube as Number, colour as Number) as Number {
        var p = _pulse[tube];
        var r = (colour >> 16) & 0xFF;
        var g = (colour >> 8) & 0xFF;
        var b = colour & 0xFF;
        var mx = (r > g) ? ((r > b) ? r : b) : ((g > b) ? g : b);
        if (mx > 0) {
            var cap = (255 * 100) / mx;          // % that lands exactly on 255
            if (p > cap) {
                p = cap;
            }
        }
        r = (r * p) / 100;
        g = (g * p) / 100;
        b = (b * p) / 100;
        r = (r > 255) ? 255 : r;
        g = (g > 255) ? 255 : g;
        b = (b > 255) ? 255 : b;
        return (r << 16) | (g << 8) | b;
    }

    //! Draw every active arc. Each call re-jitters the bolt, so a strike crackles while it lasts.
    function draw(dc as Graphics.Dc) as Void {
        if (dc has :setAntiAlias) {
            dc.setAntiAlias(true);
        }
        for (var k = 0; k < _on.size(); k += 1) {
            if (_on[k]) {
                drawArc(dc, k);
            }
        }
        if (dc has :setAntiAlias) {
            dc.setAntiAlias(false);
        }
        dc.setPenWidth(1);
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
