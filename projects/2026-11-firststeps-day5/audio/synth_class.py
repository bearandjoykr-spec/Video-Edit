"""Class-video music bed + SFX (original, synthesised). Calmer than the Reels beat: softer drums, no open hats.

Usage: python3 synth_class.py OUT_DIR TIMELINE_JSON
Reuses the instruments in projects/2026-11-confidence/audio/synth_lofi.py; adds a very soft 'tap' for stress pulses.
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../2026-11-confidence/audio"))
import synth_lofi as L

# softer drums: scale the kit down before the loop is built
_k, _s, _h = L.kick, L.snare, L.hat
L.kick = lambda: _k() * 0.55
L.snare = lambda: L.band(_s(), 300, 6000) * 0.35
L.hat = lambda open_=False: _h(False) * 0.45


def tap():
    t = L.t_(0.08)
    return np.sin(2 * np.pi * 1100 * t) * np.exp(-t * 70) * 0.6


if __name__ == "__main__":
    out, tl = sys.argv[1], json.load(open(sys.argv[2]))
    os.makedirs(out, exist_ok=True)
    m = tl.get("music", {})
    bed = L.lofi(tl["duration"], m.get("dropouts", []), m.get("drops", []))
    # "musicOn": [[s, e, gain], ...] — the bed plays only there (Mark's section already carries its own music)
    if tl.get("musicOn"):
        tt = np.arange(len(bed)) / L.SR; env = np.zeros(len(bed))
        for s, e, g in tl["musicOn"]:
            env = np.maximum(env, g * np.clip((tt - s) / 1.5, 0, 1) * np.clip((e - tt) / 2.0, 0, 1))
        bed = bed * env[:, None]
    L.write(f"{out}/music.wav", bed, peak_db=-1.0 if not tl.get("musicOn") else -1.0 + 20 * np.log10(max(1e-3, max(g for _, _, g in tl["musicOn"]))))
    for name, fn in [("pop", L.pop), ("whoosh", L.whoosh), ("sparkle", L.sparkle), ("boing", L.boing), ("chime", L.chime), ("tap", tap)]:
        L.write(f"{out}/sfx_{name}.wav", fn())
    print("class bed + sfx written for", tl["duration"], "s")
