from pathlib import Path
from datetime import datetime
import calendar
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
OUT = ROOT / "contrib-heatmap.svg"

W, H = 860, 205
CELL = 11
GAP = 3
STEP = CELL + GAP
GRID_X = 64
GRID_Y = 44
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

days = []
for d in DATA.get("days", []):
    try:
        dt = datetime.strptime(d["date"], "%Y-%m-%d").date()
    except Exception:
        continue
    days.append((dt, int(d.get("count", 0)), max(0, min(4, int(d.get("level", 0))))))

days.sort(key=lambda x: x[0])
if days:
    first = days[0][0]
    # GitHub columns are Sunday-first.
    sunday_offset = (first.weekday() + 1) % 7
    origin = first.fromordinal(first.toordinal() - sunday_offset)
else:
    origin = datetime.utcnow().date()

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<rect width="100%" height="100%" rx="14" fill="#0d1117"/>',
    '<rect x="1" y="1" width="858" height="203" rx="13" fill="none" stroke="#30363d"/>',
    '<g font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">',
    '<text x="22" y="25" font-size="11" fill="#8b949e">activity://last-year</text>',
    '<text x="22" y="76" font-size="9" fill="#8b949e">Mon</text>',
    '<text x="22" y="104" font-size="9" fill="#8b949e">Wed</text>',
    '<text x="22" y="132" font-size="9" fill="#8b949e">Fri</text>',
]

# Month labels, placed at the first week containing a new month.
seen = set()
for dt, _, _ in days:
    key = (dt.year, dt.month)
    if key in seen:
        continue
    seen.add(key)
    col = (dt - origin).days // 7
    x = GRID_X + col * STEP
    if 56 <= x <= 805:
        parts.append(f'<text x="{x}" y="37" font-size="9" fill="#8b949e">{calendar.month_abbr[dt.month]}</text>')

for idx, (dt, count, level) in enumerate(days):
    delta = (dt - origin).days
    col = delta // 7
    row = (dt.weekday() + 1) % 7
    x = GRID_X + col * STEP
    y = GRID_Y + row * STEP
    if x > 810:
        continue
    begin = min(2.4, 0.06 + (col + row) * 0.025)
    parts.append(
        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[level]}" opacity="0">'
        f'<title>{count} contribution{"s" if count != 1 else ""} on {dt.isoformat()}</title>'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.28s" begin="{begin:.2f}s" fill="freeze"/>'
        f'</rect>'
    )

legend_x = 642
parts.append(f'<text x="{legend_x}" y="183" font-size="9" fill="#8b949e">Less</text>')
for i, color in enumerate(PALETTE):
    parts.append(f'<rect x="{legend_x + 34 + i*15}" y="174" width="10" height="10" rx="2" fill="{color}"/>')
parts.append(f'<text x="{legend_x + 113}" y="183" font-size="9" fill="#8b949e">More</text>')

best = DATA.get("best_day") or {"count": 0, "date": "—"}
footer = f'{DATA.get("total", 0):,} contributions · {DATA.get("current_streak", 0)}d streak · best {best.get("count", 0)}'
parts.append(f'<text x="22" y="183" font-size="10" fill="#c9d1d9">{footer}</text>')
parts += ['</g>', '</svg>']
OUT.write_text("\n".join(parts), encoding="utf-8")
print(f"wrote {OUT}")
