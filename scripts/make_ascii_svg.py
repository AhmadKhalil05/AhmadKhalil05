from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import html
import os

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source-prepped.png"
if not SOURCE.exists():
    SOURCE = ROOT / "source-photo.png"
OUTPUT = ROOT / "ahmad-ascii.svg"

# A terminal-friendly portrait renderer. Dark flat backgrounds disappear,
# while brighter face/detail pixels turn into denser glyphs.
COLS = 58
ROWS = 44
RAMP = "  .`':-~=+*#%@"
CELL_W = 6.15
CELL_H = 7.35
PAD_X = 10
PAD_Y = 38

img = Image.open(SOURCE).convert("L")
img = ImageOps.autocontrast(img, cutoff=1)
img = ImageEnhance.Contrast(img).enhance(1.25)
img = img.resize((COLS, ROWS))
px = img.load()

rows = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        v = px[x, y]
        # Keep very dark background transparent/blank.
        if v < 18:
            ch = " "
        else:
            idx = int((v / 255) * (len(RAMP) - 1))
            ch = RAMP[idx]
        chars.append(ch)
    rows.append("".join(chars).rstrip())

width = PAD_X * 2 + COLS * CELL_W
height = PAD_Y * 2 + ROWS * CELL_H
static = os.getenv("STATIC") == "1"

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">',
    '<rect width="100%" height="100%" rx="14" fill="#0d1117"/>',
    f'<rect x="1" y="1" width="{width-2:.0f}" height="{height-2:.0f}" rx="13" fill="none" stroke="#30363d"/>',
    '<g font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" font-size="7.1" fill="#c9d1d9" xml:space="preserve">'
]

for i, line in enumerate(rows):
    y = PAD_Y + (i + 1) * CELL_H
    safe = html.escape(line or " ")
    if static:
        parts.append(f'<text x="{PAD_X}" y="{y:.1f}">{safe}</text>')
        continue
    clip_id = f"clip{i}"
    full_w = max(1, len(line)) * CELL_W
    begin = 0.20 + i * 0.045
    dur = max(0.20, min(0.75, len(line) * 0.012))
    parts.append(
        f'<defs><clipPath id="{clip_id}"><rect x="{PAD_X}" y="{y-CELL_H+1:.1f}" width="0" height="{CELL_H+2:.1f}">'
        f'<animate attributeName="width" from="0" to="{full_w:.1f}" dur="{dur:.2f}s" begin="{begin:.2f}s" fill="freeze"/>'
        f'</rect></clipPath></defs>'
    )
    parts.append(f'<text x="{PAD_X}" y="{y:.1f}" clip-path="url(#{clip_id})">{safe}</text>')

parts += [
    '</g>',
    '<text x="14" y="22" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" font-size="10" fill="#7ee787">●</text>',
    '<text x="30" y="22" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace" font-size="10" fill="#8b949e">portrait://AhmadKhalil05</text>',
    '</svg>'
]
OUTPUT.write_text("\n".join(parts), encoding="utf-8")
print(f"wrote {OUTPUT}")
