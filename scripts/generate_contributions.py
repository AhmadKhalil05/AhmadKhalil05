from pathlib import Path
from datetime import datetime, timezone
import calendar
import json

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "contributions.json"
OUT_PATH = ROOT / "assets" / "contributions.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def render_contributions_svg():
    if not DATA_PATH.exists():
        # Fallback fetch if data doesn't exist yet
        from fetch_contributions import fetch
        fetch()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    
    SVG_W = 1200
    SVG_H = 300
    
    CELL = 15
    GAP = 4
    STEP = CELL + GAP
    GRID_X = 86
    GRID_Y = 88
    
    days_data = data.get("days", [])
    days = []
    for d in days_data:
        try:
            dt = datetime.strptime(d["date"], "%Y-%m-%d").date()
            days.append((dt, int(d.get("count", 0)), max(0, min(4, int(d.get("level", 0))))))
        except Exception:
            continue

    days.sort(key=lambda x: x[0])
    if days:
        first = days[0][0]
        sunday_offset = (first.weekday() + 1) % 7
        origin = first.fromordinal(first.toordinal() - sunday_offset)
    else:
        origin = datetime.now(timezone.utc).date()

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}">')
    
    # Styles
    svg.append("""  <style>
    .mono {
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    }
    .term-prompt { fill: #7ee787; font-weight: 600; font-size: 14px; }
    .term-path { fill: #8b949e; font-size: 14px; }
    .term-cmd { fill: #f0f6fc; font-weight: 600; font-size: 14px; }
    .term-dim { fill: #8b949e; font-size: 12px; }
    .day-label { fill: #8b949e; font-size: 11px; }
    .month-label { fill: #8b949e; font-size: 12px; font-weight: 500; }
    .stat-text { fill: #c9d1d9; font-size: 13px; }
    .stat-bold { fill: #f0f6fc; font-weight: 600; }
    .legend-text { fill: #8b949e; font-size: 12px; }
  </style>""")

    # Outer Frame
    svg.append(f'  <rect x="1" y="1" width="{SVG_W - 2}" height="{SVG_H - 2}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.2"/>')

    # Top Terminal Header Bar
    svg.append('  <!-- Terminal Header -->')
    svg.append('  <g class="mono">')
    # Terminal controls
    svg.append('    <circle cx="28" cy="27" r="4.5" fill="#ff5f56" opacity="0.8"/>')
    svg.append('    <circle cx="44" cy="27" r="4.5" fill="#ffbd2e" opacity="0.8"/>')
    svg.append('    <circle cx="60" cy="27" r="4.5" fill="#27c93f" opacity="0.8"/>')
    # Prompt & command
    svg.append('    <text x="88" y="32" class="term-prompt">ahmad@github</text>')
    svg.append('    <text x="195" y="32" class="term-path"> ~ $ </text>')
    svg.append('    <text x="236" y="32" class="term-cmd">./contributions.sh</text>')
    # Blinking cursor
    svg.append('    <rect x="382" y="20" width="8" height="15" fill="#7ee787" rx="1">')
    svg.append('      <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>')
    svg.append('    </rect>')
    # Top-right indicator
    svg.append(f'    <text x="{SVG_W - 28}" y="32" text-anchor="end" class="term-dim">activity://last-year</text>')
    svg.append('  </g>')

    # Header Divider Line
    svg.append(f'  <line x1="1" y1="52" x2="{SVG_W - 1}" y2="52" stroke="#21262d" stroke-width="1"/>')

    # Weekday labels (Mon, Wed, Fri)
    svg.append('  <!-- Weekday Labels -->')
    svg.append('  <g class="mono day-label">')
    svg.append(f'    <text x="44" y="{GRID_Y + 1 * STEP + 12}">Mon</text>')
    svg.append(f'    <text x="44" y="{GRID_Y + 3 * STEP + 12}">Wed</text>')
    svg.append(f'    <text x="44" y="{GRID_Y + 5 * STEP + 12}">Fri</text>')
    svg.append('  </g>')

    # Month labels
    svg.append('  <!-- Month Labels -->')
    svg.append('  <g class="mono month-label">')
    seen_months = set()
    for dt, _, _ in days:
        key = (dt.year, dt.month)
        if key in seen_months:
            continue
        seen_months.add(key)
        col = (dt - origin).days // 7
        x = GRID_X + col * STEP
        if GRID_X <= x <= (SVG_W - 90):
            month_name = calendar.month_abbr[dt.month]
            svg.append(f'    <text x="{x}" y="74">{month_name}</text>')
    svg.append('  </g>')

    # Heatmap Grid Cells with Animation
    svg.append('  <!-- Heatmap Cells -->')
    svg.append('  <g>')
    for dt, count, level in days:
        delta = (dt - origin).days
        col = delta // 7
        row = (dt.weekday() + 1) % 7
        x = GRID_X + col * STEP
        y = GRID_Y + row * STEP
        if x > (SVG_W - 80):
            continue
        begin = min(2.0, 0.05 + col * 0.012 + row * 0.005)
        color = PALETTE[level]
        tip_text = f"{count} contribution{'s' if count != 1 else ''} on {dt.isoformat()}"
        svg.append(
            f'    <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{color}" opacity="0">'
            f'<title>{tip_text}</title>'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.25s" begin="{begin:.2f}s" fill="freeze"/>'
            f'</rect>'
        )
    svg.append('  </g>')

    # Bottom Stats & Legend Divider
    svg.append(f'  <line x1="40" y1="236" x2="{SVG_W - 40}" y2="236" stroke="#21262d" stroke-width="1"/>')

    # Bottom Stats Line
    total_contribs = data.get("total", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    best_day = data.get("best_day", {})
    best_count = best_day.get("count", 0)
    best_date = best_day.get("date", "")

    svg.append('  <!-- Bottom Stats and Legend -->')
    svg.append('  <g class="mono">')
    stat_line = (
        f'<tspan class="stat-bold">{total_contribs:,}</tspan> contributions in the last year   ·   '
        f'<tspan class="stat-bold">{current_streak}d</tspan> streak   ·   '
        f'<tspan class="stat-bold">{longest_streak}d</tspan> longest   ·   '
        f'best <tspan class="stat-bold">{best_count}</tspan> ({best_date})'
    )
    svg.append(f'    <text x="44" y="267" class="stat-text">{stat_line}</text>')

    # Legend
    legend_start_x = 940
    svg.append(f'    <text x="{legend_start_x}" y="267" class="legend-text">Less</text>')
    for i, color in enumerate(PALETTE):
        svg.append(f'    <rect x="{legend_start_x + 38 + i * 16}" y="256" width="12" height="12" rx="2.5" fill="{color}"/>')
    svg.append(f'    <text x="{legend_start_x + 128}" y="267" class="legend-text">More</text>')
    svg.append('  </g>')

    svg.append('</svg>')

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(svg), encoding="utf-8")
    print(f"Generated {OUT_PATH}")

if __name__ == "__main__":
    render_contributions_svg()
