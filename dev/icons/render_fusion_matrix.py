"""Renders fusion matrix icon candidates as a lit 3D cube, in the manner of Space Exploration's item icons.

Usage: python3 render_fusion_matrix.py OUTPUT_DIR [seed ...]\nEach seed gives a different fracture pattern; a steel-caged variant is rendered as well.
The cube is viewed orthographically from the same angle as SE's naquium cube.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

S, K = 512, 8.0                       # supersampled canvas, scale from 64 px
C = np.array([27.5, 30.0]) * K        # near corner of the cube on screen
AX = np.array([-20.0, -16.0]) * K     # screen direction of the cube's x axis (up-left)
AY = np.array([29.0, -13.0]) * K      # y axis (up-right)
AZ = np.array([0.5, 31.0]) * K        # z axis (down)
YY, XX = np.mgrid[0:S, 0:S].astype(float) + 0.5
LIGHT = np.array([-0.30, -0.58, -1.0]); LIGHT /= np.linalg.norm(LIGHT)
VIEW = np.array([-1.0, -1.0, -1.0]); VIEW /= np.linalg.norm(VIEW)
HALF = LIGHT + VIEW; HALF /= np.linalg.norm(HALF)
MAGENTA = np.array([1.0, 0.10, 0.56]); HOT = np.array([1.0, 0.86, 0.96])
GLOWING, DARK = 4, 6                  # number of lit and unlit fracture planes

def face_uv(e1, e2):
    det = e1[0] * e2[1] - e1[1] * e2[0]
    px, py = XX - C[0], YY - C[1]
    return (px * e2[1] - py * e2[0]) / det, (e1[0] * py - e1[1] * px) / det

def noise(rng, cells, lo=0.0, hi=1.0):
    small = (rng.random((cells, cells)) * 255).astype(np.uint8)
    big = np.array(Image.fromarray(small).resize((S, S), Image.BICUBIC)).astype(float) / 255
    return lo + (hi - lo) * big

# name, screen edges, 3D point from (u, v), outward normal
FACES = [
    ("top",   AX, AY, lambda u, v: (u, v, 0 * u), np.array([0.0, 0.0, -1.0])),
    ("left",  AX, AZ, lambda u, v: (u, 0 * u, v), np.array([0.0, -1.0, 0.0])),
    ("right", AY, AZ, lambda u, v: (0 * u, u, v), np.array([-1.0, 0.0, 0.0])),
]

def shade(albedo, normal, gloss, spec_strength):
    diff = np.clip(np.tensordot(normal, LIGHT, axes=([-1], [0])), 0, 1)
    spec = np.clip(np.tensordot(normal, HALF, axes=([-1], [0])), 0, 1) ** gloss
    return albedo * (0.16 + 0.95 * diff)[..., None] + spec_strength * spec[..., None]

def render(style, seed):
    rng = np.random.default_rng(seed)
    rgb = np.zeros((S, S, 3)); alpha = np.zeros((S, S)); emit = np.zeros((S, S, 3))
    grain = noise(rng, 180, -1, 1); cloud = noise(rng, 9, -1, 1); mottle = noise(rng, 28, 0, 1)
    # Fracture planes through the cube. Later planes stop at an earlier one, giving T-junctions.
    planes = []
    # The first GLOWING planes are lit from within; the rest are plain dark fractures like the naquium cube's.
    for i in range(GLOWING + DARK):
        n = rng.normal(size=3); n /= np.linalg.norm(n)
        p0 = np.array([rng.uniform(0.05, 0.75), rng.uniform(0.05, 0.75), rng.uniform(0.05, 0.75)])
        stop = None if i < 2 else (int(rng.integers(0, i)), rng.choice([-1.0, 1.0]))
        planes.append((n, float(n @ p0), stop))
    cell_shade = rng.uniform(-1, 1, size=4096); cell_tilt = rng.normal(size=(4096, 3))

    for name, e1, e2, to3d, nrm in FACES:
        u, v = face_uv(e1, e2)
        m = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
        x, y, z = to3d(u, v)
        P = np.stack([x, y, z], -1)
        edge = np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v))          # 0 at the face border
        depth = np.clip((x + y + z) / 2.0, 0, 1)                                # 0 at the near corner
        if style == "cracks":
            sides = [np.sign(P @ n - d) for n, d, _ in planes]
            dist = np.full((S, S), 9.0); dark = np.full((S, S), 9.0); cell = np.zeros((S, S), int)
            for i, (n, d, stop) in enumerate(planes):
                active = np.ones((S, S), bool) if stop is None else (sides[stop[0]] == stop[1])
                tang = np.sqrt(max(1e-6, 1 - float(n @ nrm) ** 2))               # so cracks keep an even width
                here = np.abs(P @ n - d) / tang
                if i < GLOWING: dist = np.where(active, np.minimum(dist, here), dist)
                else: dark = np.where(active, np.minimum(dark, here), dark)
                cell = cell * 2 + np.where(active & (sides[i] > 0), 1, 0)
            cell = (cell * 2654435761) % 4096
            normal = nrm[None, None, :] + 0.20 * cell_tilt[cell]
            normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
            albedo = np.array([0.36, 0.37, 0.60])[None, None, :] * (1 + 0.30 * cell_shade[cell] + 0.12 * cloud + 0.06 * grain)[..., None]
            col = shade(albedo, normal, 26, 0.16)
            col *= (1 - 0.30 * depth * (name != "top"))[..., None]              # darker towards the underside
            col += 0.10 * np.exp(-(edge / 0.035) ** 2)[..., None] * (name == "top")   # lit rim on the top face
            groove = np.exp(-(dark / 0.011) ** 2)
            col = col * (1 - 0.80 * groove[..., None]) + np.array([0.10, 0.04, 0.30]) * (0.5 * groove)[..., None]
            flicker = 0.78 + 0.22 * mottle
            core = np.exp(-(dist / 0.013) ** 2) * flicker
            halo = np.exp(-(dist / 0.036) ** 2) * flicker
            spill = np.exp(-(dist / 0.130) ** 2) * 0.22
            col = col * (1 - 0.92 * halo[..., None]) + MAGENTA * (0.95 * halo + spill)[..., None]
            col = col * (1 - core[..., None]) + HOT * core[..., None]
            e = MAGENTA[None, None, :] * halo[..., None] + HOT[None, None, :] * core[..., None]
        else:  # "caged": a steel frame around glowing windows
            lo, hi = 0.20, 0.80
            inside = (u > lo) & (u < hi) & (v > lo) & (v < hi)
            win_edge = np.minimum(np.minimum(u - lo, hi - u), np.minimum(v - lo, hi - v))   # >0 inside the window
            steel = np.array([0.70, 0.71, 0.76]) if name == "top" else np.array([0.36, 0.36, 0.42])
            brushed = 1 + 0.10 * grain + 0.10 * cloud
            col = shade(steel[None, None, :] * brushed[..., None], np.broadcast_to(nrm, P.shape), 30, 0.22)
            col *= (1 - 0.28 * depth * (name != "top"))[..., None]
            col += 0.16 * np.exp(-(edge / 0.03) ** 2)[..., None]                 # bevel on the outer edges
            col *= (1 - 0.55 * np.exp(-(np.clip(-win_edge, 0, 1) / 0.035) ** 2))[..., None]  # shadowed inner lip
            lit = np.clip(0.55 + 0.75 * mottle - 0.35 * np.hypot(u - 0.5, v - 0.5), 0, 1.2)
            glow = MAGENTA[None, None, :] * lit[..., None] + HOT[None, None, :] * np.clip(lit - 0.80, 0, 1)[..., None] * 1.6
            bars = np.zeros((S, S))
            for t in (lo + (hi - lo) / 3, lo + 2 * (hi - lo) / 3):
                bars = np.maximum(bars, np.exp(-((u - t) / 0.022) ** 2)); bars = np.maximum(bars, np.exp(-((v - t) / 0.022) ** 2))
            glow = glow * (1 - 0.85 * bars[..., None]) + np.array([0.20, 0.02, 0.14]) * bars[..., None]
            glow *= np.clip(win_edge / 0.04, 0.25, 1)[..., None]                 # recessed, darker at the lip
            col = np.where(inside[..., None], glow, col)
            col += MAGENTA * (0.22 * np.exp(-(np.clip(-win_edge, 0, 1) / 0.07) ** 2) * (~inside))[..., None]  # light on the frame
            e = np.where(inside[..., None], glow * (1 - 0.85 * bars[..., None]), 0)
        rgb[m] = col[m]; alpha[m] = 1; emit[m] = e[m]

    body = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), alpha]) * 255).astype(np.uint8), "RGBA")
    strength = np.clip(emit.max(-1), 0, 1)
    bloom = Image.fromarray((np.dstack([np.clip(emit / np.maximum(strength, 1e-3)[..., None], 0, 1), strength]) * 255).astype(np.uint8), "RGBA")
    wide = bloom.filter(ImageFilter.GaussianBlur(26)); wide.putalpha(wide.getchannel("A").point(lambda a: int(min(255, a * 0.85))))
    tight = bloom.filter(ImageFilter.GaussianBlur(7)); tight.putalpha(tight.getchannel("A").point(lambda a: int(a * 0.45)))
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.alpha_composite(wide); out.alpha_composite(body); out.alpha_composite(tight)
    return out.resize((64, 64), Image.LANCZOS)

if __name__ == "__main__":
    out_dir = sys.argv[1]
    for seed in [int(x) for x in sys.argv[2:]] or [3]:
        render("cracks", seed).save(f"{out_dir}/fusion-matrix-cracks-{seed}.png")
    render("caged", 1).save(f"{out_dir}/fusion-matrix-caged.png")
