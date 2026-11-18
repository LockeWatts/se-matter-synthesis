from PIL import Image, ImageDraw, ImageFilter
import math, sys
S = 512  # supersampled canvas
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))
cx, cy = S / 2, S / 2 + 6
R = 196                      # hexagon radius
h = R * math.sqrt(3) / 2
T, B = (cx, cy - R), (cx, cy + R)
UR, LR = (cx + h, cy - R / 2), (cx + h, cy + R / 2)
UL, LL = (cx - h, cy - R / 2), (cx - h, cy + R / 2)
C = (cx, cy)
hexagon = [T, UR, LR, B, LL, UL]

def inset(poly, f):
    mx = sum(p[0] for p in poly) / len(poly); my = sum(p[1] for p in poly) / len(poly)
    return [(mx + (x - mx) * f, my + (y - my) * f) for x, y in poly]

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

# soft contact shadow
sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse([cx - 170, cy + 150, cx + 170, cy + 222], fill=(0, 0, 0, 120))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))

# metal shell: three faces with different lighting
faces = [([T, UR, C, UL], (98, 96, 112)), ([UL, C, B, LL], (58, 56, 70)), ([C, UR, LR, B], (38, 36, 48))]
d = ImageDraw.Draw(img)
for poly, col in faces: d.polygon(poly, fill=col + (255,))

# glowing windows cut into each face
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for i in range(60, 0, -1):
    t = i / 60
    col = lerp((255, 255, 255), (255, 20, 150), min(1, t * 1.6))
    r = 210 * t
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (255,))
mask = Image.new("L", (S, S), 0)
md = ImageDraw.Draw(mask)
for poly, _ in faces: md.polygon(inset(poly, 0.62), fill=255)
img.paste(glow, (0, 0), mask)

# lattice lines inside the windows
d = ImageDraw.Draw(img)
def seg(a, b, t0, t1): return (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0, a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
for poly, _ in faces:
    p = inset(poly, 0.62)
    for k in (1 / 3, 2 / 3):
        a = (p[0][0] + (p[1][0] - p[0][0]) * k, p[0][1] + (p[1][1] - p[0][1]) * k)
        b = (p[3][0] + (p[2][0] - p[3][0]) * k, p[3][1] + (p[2][1] - p[3][1]) * k)
        d.line([a, b], fill=(120, 0, 70, 255), width=7)
        a = (p[0][0] + (p[3][0] - p[0][0]) * k, p[0][1] + (p[3][1] - p[0][1]) * k)
        b = (p[1][0] + (p[2][0] - p[1][0]) * k, p[1][1] + (p[2][1] - p[1][1]) * k)
        d.line([a, b], fill=(120, 0, 70, 255), width=7)
    d.line(p + [p[0]], fill=(20, 18, 26, 255), width=9, joint="curve")

# frame edges and bright rims
for a, b in [(T, UR), (UR, LR), (LR, B), (B, LL), (LL, UL), (UL, T), (C, UL), (C, UR), (C, B)]:
    d.line([a, b], fill=(18, 16, 24, 255), width=20)
for a, b, col in [(UL, T, (214, 212, 226)), (T, UR, (190, 188, 204)), (C, UL, (170, 168, 186)), (C, UR, (150, 148, 166)), (C, B, (120, 118, 136)), (UL, LL, (110, 108, 126)), (LL, B, (84, 82, 98)), (UR, LR, (84, 82, 98)), (LR, B, (66, 64, 80))]:
    d.line([a, b], fill=col + (255,), width=9)
for p in hexagon + [C]:
    d.ellipse([p[0] - 15, p[1] - 15, p[0] + 15, p[1] + 15], fill=(18, 16, 24, 255))
    d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill=(232, 230, 242, 255))

# outer bloom from the core
bloom = Image.new("RGBA", (S, S), (0, 0, 0, 0))
bloom.paste(Image.new("RGBA", (S, S), (255, 60, 170, 255)), (0, 0), mask)
bloom = bloom.filter(ImageFilter.GaussianBlur(22))
bloom.putalpha(bloom.getchannel("A").point(lambda v: int(v * 0.55)))
out = Image.alpha_composite(img, bloom)

icon = out.resize((64, 64), Image.LANCZOS)
icon.save(sys.argv[1] + "/fusion-matrix.png")
# preview sheet: large view plus actual-size views on Factorio-like slot colours
sheet = Image.new("RGBA", (560, 300), (36, 36, 36, 255))
sheet.alpha_composite(out.resize((256, 256), Image.LANCZOS), (20, 22))
for i, bg in enumerate([(64, 64, 64), (140, 140, 140), (30, 30, 30)]):
    x = 310 + i * 80
    ImageDraw.Draw(sheet).rectangle([x, 60, x + 71, 131], fill=bg + (255,))
    sheet.alpha_composite(icon, (x + 4, 64))
    ImageDraw.Draw(sheet).rectangle([x + 16, 170, x + 55, 209], fill=bg + (255,))
    sheet.alpha_composite(out.resize((32, 32), Image.LANCZOS), (x + 20, 174))
sheet.save(sys.argv[1] + "/fusion-matrix-preview.png")
