from pathlib import Path
import json
import html
import os

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "profile-config.json").read_text(encoding="utf-8"))
OUT = ROOT / "info-card.svg"
static = os.getenv("STATIC") == "1"

W, H = 490, 350
rows = [
    ("Role", CFG["role"]),
    ("Focus", CFG["focus"]),
    ("Stack", CFG["stack"]),
    ("Builds", CFG["builds"]),
    ("Based", CFG["location"]),
    ("Web", CFG["website"]),
]

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<rect width="100%" height="100%" rx="14" fill="#0d1117"/>',
    '<rect x="1" y="1" width="488" height="348" rx="13" fill="none" stroke="#30363d"/>',
    '<g font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">',
    '<text x="24" y="36" font-size="17" font-weight="700" fill="#f0f6fc">Ahmad Khalil</text>',
    '<text x="24" y="56" font-size="11" fill="#8b949e">ahmad@github</text>',
    '<line x1="24" y1="72" x2="466" y2="72" stroke="#21262d"/>',
]

for i, (k, v) in enumerate(rows):
    y = 105 + i * 36
    opacity = "1" if static else "0"
    transform = "" if static else ' transform="translate(0 5)"'
    parts.append(f'<g opacity="{opacity}"{transform}>')
    parts.append(f'<text x="24" y="{y}" font-size="12" font-weight="700" fill="#7ee787">{html.escape(k):<8}</text>')
    parts.append(f'<text x="105" y="{y}" font-size="12" fill="#c9d1d9">{html.escape(v)}</text>')
    if not static:
        begin = 0.30 + i * 0.12
        parts.append(f'<animate attributeName="opacity" from="0" to="1" dur="0.30s" begin="{begin:.2f}s" fill="freeze"/>')
        parts.append(f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" dur="0.30s" begin="{begin:.2f}s" fill="freeze"/>')
    parts.append('</g>')

parts += [
    '<line x1="24" y1="314" x2="466" y2="314" stroke="#21262d"/>',
    '<text x="24" y="334" font-size="10" fill="#8b949e">TypeScript · React · AWS · Playwright · Design</text>',
    '</g>',
    '</svg>'
]
OUT.write_text("\n".join(parts), encoding="utf-8")
print(f"wrote {OUT}")
