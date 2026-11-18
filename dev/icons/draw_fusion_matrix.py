import numpy as np, sys
from PIL import Image, ImageFilter
S, K = 512, 8.0
C = np.array([27.5, 30.0]) * K
a = np.array([-20.0, -16.0]) * K   # towards upper-left
b = np.array([29.0, -13.0]) * K    # towards upper-right
c = np.array([0.5, 31.0]) * K      # straight down
FACES = {"top": (a, b), "left": (a, c), "right": (b, c)}
Y, X = np.mgrid[0:S, 0:S].astype(float) + 0.5
PINK = np.array([255, 40, 160.0]); WHITE = np.array([255, 235, 250.0])

def uv(e1, e2):
    det = e1[0] * e2[1] - e1[1] * e2[0]
    px, py = X - C[0], Y - C[1]
    return (px * e2[1] - py * e2[0]) / det, (e1[0] * py - e1[1] * px) / det

def line_dist(e1, e2, p, q):
    """Pixel distance from every pixel to the line through uv points p and q, and which side it is on."""
    P = C + p[0] * e1 + p[1] * e2; Q = C + q[0] * e1 + q[1] * e2
    d = Q - P; n = np.array([-d[1], d[0]]) / np.hypot(*d)
    s = (X - P[0]) * n[0] + (Y - P[1]) * n[1]
    return np.abs(s), np.sign(s)

def edge_dist(e1, e2, u, v):
    l1 = abs(e1[0] * e2[1] - e1[1] * e2[0]) / np.hypot(*e2)   # pixel height across u
    l2 = abs(e1[0] * e2[1] - e1[1] * e2[0]) / np.hypot(*e1)
    return np.minimum(np.minimum(u, 1 - u) * l1, np.minimum(v, 1 - v) * l2)

# Hand-placed fracture lines per face, as pairs of uv points on the face boundary.
CRACKS = {
    "top":   [((0.0, 0.34), (1.0, 0.66)), ((0.40, 0.0), (0.62, 1.0)), ((0.74, 0.0), (1.0, 0.38))],
    "left":  [((0.0, 0.26), (1.0, 0.56)), ((0.40, 0.0), (0.58, 1.0)), ((0.0, 0.72), (0.74, 1.0))],
    "right": [((0.0, 0.44), (1.0, 0.20)), ((0.46, 0.0), (0.30, 1.0)), ((0.0, 0.80), (1.0, 0.66))],
}
FACET_SHADE = [0.10, -0.08, 0.06, -0.05]

def render(style):
    rgb = np.zeros((S, S, 3)); alpha = np.zeros((S, S)); glow = np.zeros((S, S))
    if style == "grid":
        base = {"top": (112, 110, 128), "left": (66, 64, 80), "right": (40, 38, 52)}
    else:
        base = {"top": (104, 106, 138), "left": (58, 58, 84), "right": (34, 32, 50)}
    for name, (e1, e2) in FACES.items():
        u, v = uv(e1, e2)
        m = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1)
        shade = 1.0 + 0.22 * (0.5 - (u + v) / 2) * (-1 if name == "top" else 1)
        col = np.array(base[name], float)[None, None, :] * shade[..., None]
        g = np.zeros((S, S)); core = np.zeros((S, S))
        if style == "grid":
            lo, hi = 0.15, 0.85
            w = (u > lo) & (u < hi) & (v > lo) & (v < hi)
            lit = 1.0 - 0.45 * np.clip(np.hypot(u, v) / 1.2, 0, 1)
            g = np.where(w, lit, 0.0); core = np.where(w, np.clip(lit - 0.72, 0, 1) * 1.6, 0.0)
            bars = np.zeros((S, S), bool)
            for k in (1 / 3, 2 / 3):
                t = lo + (hi - lo) * k
                for p, q in (((t, 0), (t, 1)), ((0, t), (1, t))):
                    d, _ = line_dist(e1, e2, p, q); bars |= d < 5.5
            frame = np.zeros((S, S), bool)
            for t in (lo, hi):
                for p, q in (((t, 0), (t, 1)), ((0, t), (1, t))):
                    d, _ = line_dist(e1, e2, p, q); frame |= (d < 7) & (u > lo - 0.03) & (u < hi + 0.03) & (v > lo - 0.03) & (v < hi + 0.03)
            col = col * (1 - g[..., None]) + PINK[None, None, :] * g[..., None]
            col = col * (1 - core[..., None]) + WHITE[None, None, :] * core[..., None]
            col[bars & w] = (118, 0, 72); col[frame] = (20, 18, 28)
            glow += np.where(m, g, 0)
        else:
            for (p, q), sh in zip(CRACKS[name], FACET_SHADE):
                d, side = line_dist(e1, e2, p, q)
                col = col * (1 + sh * side)[..., None]
                g = np.maximum(g, np.exp(-(d / 8.0) ** 2)); core = np.maximum(core, np.exp(-(d / 2.8) ** 2))
            halo = np.clip(g * 0.85, 0, 1)
            col = col * (1 - halo[..., None]) + PINK[None, None, :] * halo[..., None]
            col = col * (1 - core[..., None]) + WHITE[None, None, :] * core[..., None]
            glow += np.where(m, g, 0)
        ed = edge_dist(e1, e2, u, v)
        rim = np.clip(1 - ed / 9.0, 0, 1) * (0.55 if name == "top" else 0.30)
        col = col * (1 + rim[..., None] * 0.5)            # soft bevel highlight along edges
        col[(ed < 3.2)] = col[(ed < 3.2)] * 0.35            # thin dark seam
        rgb[m] = np.clip(col, 0, 255)[m]; alpha[m] = 255
    img = Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), "RGBA")
    gl = np.clip(glow, 0, 1)
    bloom = Image.fromarray(np.dstack([np.full((S, S), 255), np.full((S, S), 50), np.full((S, S), 170), gl * 255]).astype(np.uint8), "RGBA")
    bloom = bloom.filter(ImageFilter.GaussianBlur(20 if style == "grid" else 16))
    bloom.putalpha(bloom.getchannel("A").point(lambda x: int(x * (0.45 if style == "grid" else 0.42))))
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.alpha_composite(bloom); out.alpha_composite(img)
    top = bloom.copy(); top.putalpha(top.getchannel("A").point(lambda x: int(x * 0.5)))
    out.alpha_composite(top)
    return out.resize((64, 64), Image.LANCZOS)

render("grid").save(sys.argv[1] + "/fusion-matrix-a-grid.png")
render("cracks").save(sys.argv[1] + "/fusion-matrix-b-cracks.png")
