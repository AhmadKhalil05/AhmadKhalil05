from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "profile-config.json"
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8")) if CFG_PATH.exists() else {}
OUT_PATH = ROOT / "assets" / "profile-hero.svg"

def build_hero_svg():
    SVG_W = 1200
    SVG_H = 380

    display_name = CFG.get("display_name", "Ahmad Khalil")
    role = CFG.get("role", "Designer & Software Engineer")
    focus = CFG.get("focus", "Full-Stack · Cloud · QA")
    stack = CFG.get("stack", "TypeScript · React · AWS")
    builds = CFG.get("builds", "Serverless · Playwright · 3D Web")
    location = CFG.get("location", "Nablus, Palestine")
    website = CFG.get("website", "ahmadkh.framer.ai")

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}">')
    
    # Embedded styles & font stack
    svg.append("""  <style>
    .mono {
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    }
    .term-prompt { fill: #7ee787; font-weight: 600; font-size: 14px; }
    .term-path { fill: #8b949e; font-size: 14px; }
    .term-cmd { fill: #f0f6fc; font-weight: 600; font-size: 14px; }
    .term-dim { fill: #8b949e; font-size: 12px; }
    .name-title { fill: #f0f6fc; font-size: 32px; font-weight: 700; }
    .role-title { fill: #7ee787; font-size: 17px; font-weight: 600; }
    .bio-text { fill: #c9d1d9; font-size: 14px; line-height: 24px; }
    .meta-label { fill: #8b949e; font-size: 14px; font-weight: 600; }
    .meta-val { fill: #e6edf3; font-size: 14px; }
    .tag-box { fill: #161b22; stroke: #30363d; stroke-width: 1; rx: 4; }
    .tag-text { fill: #7ee787; font-size: 12px; font-weight: 500; }
  </style>""")

    # Outer Frame
    svg.append(f'  <rect x="1" y="1" width="{SVG_W - 2}" height="{SVG_H - 2}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.2"/>')

    # Top Terminal Header Bar
    svg.append('  <!-- Terminal Header -->')
    svg.append('  <g class="mono">')
    # Window controls
    svg.append('    <circle cx="28" cy="27" r="4.5" fill="#ff5f56" opacity="0.8"/>')
    svg.append('    <circle cx="44" cy="27" r="4.5" fill="#ffbd2e" opacity="0.8"/>')
    svg.append('    <circle cx="60" cy="27" r="4.5" fill="#27c93f" opacity="0.8"/>')
    # Prompt & command
    svg.append('    <text x="88" y="32" class="term-prompt">ahmad@github</text>')
    svg.append('    <text x="195" y="32" class="term-path"> ~ $ </text>')
    svg.append('    <text x="236" y="32" class="term-cmd">whoami --verbose</text>')
    # Blinking cursor
    svg.append('    <rect x="375" y="20" width="8" height="15" fill="#7ee787" rx="1">')
    svg.append('      <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>')
    svg.append('    </rect>')
    # Top-right indicator
    svg.append(f'    <text x="{SVG_W - 28}" y="32" text-anchor="end" class="term-dim">profile://AhmadKhalil05</text>')
    svg.append('  </g>')

    # Header Divider Line
    svg.append(f'  <line x1="1" y1="52" x2="{SVG_W - 1}" y2="52" stroke="#21262d" stroke-width="1"/>')

    # LEFT COLUMN: Identity & Bio
    svg.append('  <!-- Identity Section -->')
    svg.append('  <g class="mono">')
    svg.append(f'    <text x="55" y="112" class="name-title">{html.escape(display_name)}</text>')
    svg.append(f'    <text x="55" y="142" class="role-title">{html.escape(role)}</text>')
    
    svg.append('    <line x1="55" y1="168" x2="420" y2="168" stroke="#21262d" stroke-width="1"/>')
    
    svg.append('    <text x="55" y="202" class="bio-text">Crafting scalable cloud architectures,</text>')
    svg.append('    <text x="55" y="226" class="bio-text">automated testing pipelines, and</text>')
    svg.append('    <text x="55" y="250" class="bio-text">high-performance web interfaces.</text>')

    # Core tech tag pills
    tags = ["TypeScript", "React", "AWS", "Playwright", "Next.js"]
    tag_x = 55
    tag_y = 295
    for tag in tags:
        tag_w = len(tag) * 8.2 + 18
        svg.append(f'    <rect x="{tag_x}" y="{tag_y - 15}" width="{tag_w}" height="24" rx="4" class="tag-box"/>')
        svg.append(f'    <text x="{tag_x + tag_w / 2}" y="{tag_y + 1}" text-anchor="middle" class="tag-text">{tag}</text>')
        tag_x += tag_w + 10
    svg.append('  </g>')

    # VERTICAL DIVIDER
    svg.append('  <!-- Center Divider -->')
    svg.append(f'  <line x1="460" y1="75" x2="460" y2="{SVG_H - 30}" stroke="#21262d" stroke-width="1" stroke-dasharray="4 4"/>')

    # RIGHT COLUMN: Technical Specs (Neofetch Style)
    info_x = 500
    svg.append('  <!-- System & Technical Specs -->')
    svg.append('  <g class="mono">')
    
    specs = [
        ("Role", role),
        ("Focus", focus),
        ("Stack", stack),
        ("Builds", builds),
        ("Based", location),
        ("Website", website),
    ]

    for i, (label, val) in enumerate(specs):
        row_y = 112 + i * 38
        val_color = '#7ee787' if label == 'Website' else '#e6edf3'
        svg.append(f'    <g transform="translate(0, 0)">')
        svg.append(f'      <text x="{info_x}" y="{row_y}" class="meta-label">{html.escape(label):<9}</text>')
        svg.append(f'      <text x="{info_x + 95}" y="{row_y}" class="meta-val" fill="{val_color}">{html.escape(val)}</text>')
        svg.append('    </g>')
    
    # Sub note at bottom
    svg.append(f'    <line x1="{info_x}" y1="334" x2="{SVG_W - 40}" y2="334" stroke="#21262d" stroke-width="1"/>')
    svg.append(f'    <text x="{info_x}" y="354" font-size="12" fill="#8b949e">uptime: active · license: MIT · shell: zsh</text>')
    svg.append('  </g>')

    svg.append('</svg>')

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(svg), encoding="utf-8")
    print(f"Generated {OUT_PATH}")

if __name__ == "__main__":
    build_hero_svg()
