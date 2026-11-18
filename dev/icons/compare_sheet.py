"""Builds a comparison sheet of candidate icons next to Space Exploration's own icons.

Usage:
  python3 compare_sheet.py OUTPUT.png --se-icons PATH/TO/graphics/icons \\
      --se naquium-cube vulcanite-block --mine fusion-matrix-caged.png other-candidate.png

SE's icons are read from your local copy of the space-exploration-graphics mod and are
not part of this repository. The output embeds them, so keep it out of the repository too.
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

SLOT, LIGHT, PAGE = (49, 48, 49, 255), (128, 128, 128, 255), (36, 36, 36, 255)

def load(path):
    return Image.open(path).convert("RGBA").crop((0, 0, 64, 64))   # drop mipmaps if present

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("output")
    ap.add_argument("--se-icons", help="folder holding SE's icon files")
    ap.add_argument("--se", nargs="*", default=[], help="SE icon names, without .png")
    ap.add_argument("--mine", nargs="+", required=True, help="candidate icon files")
    args = ap.parse_args()

    mine = [(os.path.splitext(os.path.basename(p))[0], "candidate", load(p)) for p in args.mine]
    theirs = [(n, "SE", load(os.path.join(args.se_icons, n + ".png"))) for n in args.se]
    cols = theirs[:1] + mine + theirs[1:]
    font, small = ImageFont.load_default(size=13), ImageFont.load_default(size=12)
    cw = 170; width = cw * len(cols) + 40
    strip = [im for _, _, im in theirs] or [mine[0][2]]
    height = 348 + 44 * len(mine) + 12
    sheet = Image.new("RGBA", (width, height), PAGE); d = ImageDraw.Draw(sheet)
    for i, (name, kind, im) in enumerate(cols):
        x = 20 + i * cw
        d.text((x + cw / 2, 22), name[:24], font=font, fill=(235, 235, 235), anchor="mm")
        d.text((x + cw / 2, 42), kind, font=small, fill=(150, 150, 150), anchor="mm")
        d.rectangle([x + 9, 62, x + 160, 213], fill=SLOT)
        sheet.alpha_composite(im.resize((192, 192), Image.NEAREST).resize((144, 144), Image.LANCZOS), (x + 13, 66))
        for j, bg in enumerate([SLOT, LIGHT]):
            bx = x + 13 + j * 76
            d.rectangle([bx, 236, bx + 67, 303], fill=bg); sheet.alpha_composite(im, (bx + 2, 238))
    d.text((20, 222), "Actual size, 64 px", font=small, fill=(150, 150, 150), anchor="lm")
    d.text((20, 334), "As inventory slots (32 px icons), one row per candidate", font=small, fill=(150, 150, 150), anchor="lm")
    per_row = (width - 40) // 44
    for row, (_, _, im) in enumerate(mine):
        for k in range(per_row):
            pick = im if k % 2 else strip[(k // 2) % len(strip)]
            bx, by = 20 + k * 44, 348 + row * 44
            d.rectangle([bx, by, bx + 39, by + 39], fill=SLOT)
            sheet.alpha_composite(pick.resize((32, 32), Image.LANCZOS), (bx + 4, by + 4))
    sheet.save(args.output)

if __name__ == "__main__":
    main()
