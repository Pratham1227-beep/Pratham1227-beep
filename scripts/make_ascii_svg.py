"""Convert source-prepped.png (+ source-mask.png) into a self-typing,
monochrome ASCII portrait SVG (SMIL animation, plays on GitHub).

The SVG carries its own dark panel, so it looks the same in GitHub's
light and dark themes. On a dark panel dense glyphs read as *bright*,
so the ramp runs dark->bright = sparse->dense (background stays empty).

STATIC=1 emits the finished frame (for local previews).
"""
import os
import numpy as np
from PIL import Image

COLS = 100
CELL_W, CELL_H = 4.4, 8.0          # px per glyph cell (approx 0.55 aspect)
FONT_SIZE = 7.2
FILL = "#c9d1d9"                   # one light-gray colour = clean, not noisy
BG = "#0d1117"
RAMP = " .`:-=+*cs#%@"             # sparse -> dense
FLOOR, GAMMA = 3, 0.8
STAGGER, WIPE = 0.055, 0.55        # seconds
STATIC = os.environ.get("STATIC") == "1"

img = Image.open("source-prepped.png").convert("L")
mask = Image.open("source-mask.png").convert("L")
rows = int(round(COLS * (img.height / img.width) * (CELL_W / CELL_H)))
img = img.resize((COLS, rows), Image.LANCZOS)
mask = mask.resize((COLS, rows), Image.LANCZOS)
g = np.array(img, dtype=float) / 255.0
m = np.array(mask, dtype=float) / 255.0

# stretch subject tones so the full ramp is used
subj = g[m > 0.5]
lo, hi = np.percentile(subj, 2), np.percentile(subj, 98)
g = np.clip((g - lo) / max(hi - lo, 1e-6), 0, 1)

lines = []
for y in range(rows):
    s = ""
    for x in range(COLS):
        if m[y, x] < 0.5:
            s += " "
        else:
            # floor at ':' so dark hair/blazer keep a visible silhouette
            s += RAMP[FLOOR + int(round((g[y, x] ** GAMMA) * (len(RAMP) - 1 - FLOOR)))]
    lines.append(s.rstrip())

PAD = 12
W = COLS * CELL_W + PAD * 2
H = rows * CELL_H + PAD * 2 + 2


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="ASCII portrait of Pratham">',
       f'<rect width="{W:.0f}" height="{H:.0f}" rx="10" fill="{BG}"/>',
       f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'DejaVu Sans Mono\',monospace" font-size="{FONT_SIZE}" fill="{FILL}">']

inner_w = COLS * CELL_W
for i, line in enumerate(lines):
    if not line.strip():
        continue
    y = PAD + (i + 1) * CELL_H - 1.6
    begin = i * STAGGER
    text = (f'<text x="{PAD}" y="{y:.1f}" xml:space="preserve" textLength="{inner_w:.1f}" '
            f'lengthAdjust="spacingAndGlyphs">{esc(line.ljust(COLS))}</text>')
    if STATIC:
        out.append(text)
        continue
    cid = f"c{i}"
    out.append(
        f'<clipPath id="{cid}"><rect x="{PAD}" y="{PAD + i * CELL_H:.1f}" width="0" height="{CELL_H:.1f}">'
        f'<animate attributeName="width" from="0" to="{inner_w:.1f}" begin="{begin:.2f}s" dur="{WIPE}s" fill="freeze"/>'
        f'</rect></clipPath>'
        f'<g clip-path="url(#{cid})">{text}</g>'
        f'<rect x="{PAD}" y="{PAD + i * CELL_H + 1:.1f}" width="{CELL_W:.1f}" height="{CELL_H - 2:.1f}" fill="{FILL}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD + inner_w:.1f}" begin="{begin:.2f}s" dur="{WIPE}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.02;0.95;1" begin="{begin:.2f}s" dur="{WIPE}s" fill="freeze"/>'
        f'</rect>')
out.append("</g></svg>")

dest = "portrait-ascii.svg"
open(dest, "w").write("\n".join(out))
print(f"wrote {dest}  ({COLS}x{rows} chars, viewBox {W:.0f}x{H:.0f})")
