"""Builds the mod's thumbnail.png (144 x 144, shown in Factorio's mod list) from the fusion matrix render.

Usage: python3 make_thumbnail.py OUTPUT.png
"""
import os, sys, importlib.util
import numpy as np
from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("render_fusion_matrix", os.path.join(here, "render_fusion_matrix.py"))
renderer = importlib.util.module_from_spec(spec); spec.loader.exec_module(renderer)

SIZE = 144
yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(float)
r = np.hypot(xx - SIZE / 2, yy - SIZE / 2) / (SIZE / 2)
glow = np.clip(1 - r, 0, 1) ** 1.6
background = np.zeros((SIZE, SIZE, 4), np.uint8)
background[..., 0] = 20 + 70 * glow      # dark slate with a soft magenta glow behind the matrix
background[..., 1] = 18 + 8 * glow
background[..., 2] = 26 + 46 * glow
background[..., 3] = 255
thumb = Image.fromarray(background, "RGBA")
matrix = renderer.render("caged", 1, size=128)
thumb.alpha_composite(matrix, ((SIZE - 128) // 2, (SIZE - 128) // 2))
thumb.convert("RGB").save(sys.argv[1])
