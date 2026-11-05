"""Finds which source seconds the owner's finished edit uses. Writes owner-cuts.json (src_s, src_e, out_s).
Run: tools/fx-venv/bin/python projects/2026-11-day0-welcome/align_owner_edit.py"""
import json, subprocess, numpy as np
W, H, F = 96, 54, 10
def load(p):
    b = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", p, "-vf", f"fps={F},scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(-1, H, W).astype(np.float32)
    return a
ed = load("raw-footage/day0-owner-edit/edit.mp4"); so = load("raw-footage/day0-welcome/source.mp4")
m = np.ones((H, W), bool); m[:12, :26] = False   # ignore the burned-in logo
def norm(a):
    v = a[:, m]; v = v - v.mean(1, keepdims=True); return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-6)
ne, ns = norm(ed), norm(so)
print("frames", len(ne), len(ns))
best = []; score = []
for i in range(len(ne)):
    c = ns @ ne[i]; j = int(c.argmax()); best.append(j); score.append(float(c[j]))
best = np.array(best); score = np.array(score)
d = best - np.arange(len(best))            # constant inside a cut
cuts = []; i = 0
while i < len(d):
    if score[i] < .9: i += 1; continue
    j = i + 1
    while j < len(d) and (abs(d[j] - d[i]) <= 1 or score[j] < .9): j += 1
    if j - i >= 5: cuts.append((i / F, j / F, float(np.median(d[i:j])) / F))
    i = j
out = []
for a, b, off in cuts:
    if out and abs(out[-1]["off"] - off) < .15: out[-1]["out_e"] = b
    else: out.append({"out_s": a, "out_e": b, "off": off})
for c in out: print(f'{c["out_s"]:7.1f} {c["out_e"]:7.1f}  src {c["out_s"] + c["off"]:7.1f} off {c["off"]:6.1f}')
json.dump(out, open("projects/2026-11-day0-welcome/owner-cuts.json", "w"), indent=0)
