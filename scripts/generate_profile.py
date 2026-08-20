from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import html
import json
import numpy as np
import os

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "profile-config.json"
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8")) if CFG_PATH.exists() else {}

PHOTO_PATH = ROOT / "source" / "profile-photo.png"
if not PHOTO_PATH.exists():
    PHOTO_PATH = ROOT / "source-photo.png"

OUT_PATH = ROOT / "assets" / "profile-hero.svg"

def generate_ascii_lines(image_path, target_cols=76):
    """
    Renders a high-readability terminal ASCII portrait.
    Compensates for character aspect ratio, isolates subject, and uses luminance ramp.
    """
    img = Image.open(image_path).convert("L")
    w, h = img.size

    # Crop tightly around face & upper torso if full avatar
    if w >= 200 and h >= 200:
        crop_box = (int(w * 0.16), int(h * 0.04), int(w * 0.84), int(h * 0.94))
        img = img.crop(crop_box)
        w, h = img.size

    arr = np.array(img).astype(float)

    # Subject isolation mask (face and upper body)
    Y, X = np.ogrid[:h, :w]
    cx = w * 0.48
    cy_face = h * 0.36
    cy_body = h * 0.72
    dist_face = ((X - cx) / (w * 0.38)) ** 2 + ((Y - cy_face) / (h * 0.36)) ** 2
    dist_body = ((X - cx) / (w * 0.48)) ** 2 + ((Y - cy_body) / (h * 0.48)) ** 2
    mask = np.clip(1.35 - np.minimum(dist_face, dist_body), 0, 1)

    arr_subject = arr * mask
    img_sub = Image.fromarray(arr_subject.astype(np.uint8))

    # Contrast & feature enhancement
    img_enhanced = ImageOps.autocontrast(img_sub, cutoff=1)
    img_enhanced = ImageEnhance.Contrast(img_enhanced).enhance(1.65)
    img_enhanced = img_enhanced.filter(ImageFilter.UnsharpMask(radius=1.6, percent=160, threshold=2))

    # Character aspect ratio in monospace fonts (width / height ~ 0.52)
    char_ratio = 0.52
    target_rows = int(target_cols * (h / w) * char_ratio)

    resized = img_enhanced.resize((target_cols, target_rows), Image.Resampling.LANCZOS)
    px = np.array(resized)

    ramp = " .:-=+*#%@"
    lines = []
    for y in range(target_rows):
        line = []
        for x in range(target_cols):
            v = px[y, x]
            if v < 22:
                line.append(" ")
            else:
                idx = int((v / 255) * (len(ramp) - 1))
                line.append(ramp[idx])
        lines.append("".join(line).rstrip())

    return lines, target_cols, target_rows

def build_hero_svg():
    lines, cols, rows = generate_ascii_lines(PHOTO_PATH, target_cols=74)
    
    SVG_W = 1200
    SVG_H = 480
    
    # ASCII Placement parameters
    ascii_font_size = 7.4
    cell_w = 5.2
    cell_h = 8.6
    ascii_start_x = 42
    ascii_start_y = 78

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
    .ascii-text { fill: #c9d1d9; font-size: 7.4px; white-space: pre; }
    .name-title { fill: #f0f6fc; font-size: 30px; font-weight: 700; }
    .role-title { fill: #7ee787; font-size: 16px; font-weight: 600; }
    .meta-label { fill: #8b949e; font-size: 14px; font-weight: 600; }
    .meta-val { fill: #e6edf3; font-size: 14px; }
    .meta-dim { fill: #8b949e; font-size: 13px; font-style: italic; }
  </style>""")

    # Outer Frame
    svg.append(f'  <rect x="1" y="1" width="{SVG_W - 2}" height="{SVG_H - 2}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.2"/>')

    # Top Terminal Header Bar
    svg.append('  <!-- Terminal Header -->')
    svg.append('  <g class="mono">')
    # Terminal window controls
    svg.append('    <circle cx="28" cy="27" r="4.5" fill="#ff5f56" opacity="0.8"/>')
    svg.append('    <circle cx="44" cy="27" r="4.5" fill="#ffbd2e" opacity="0.8"/>')
    svg.append('    <circle cx="60" cy="27" r="4.5" fill="#27c93f" opacity="0.8"/>')
    # Prompt & whoami command
    svg.append('    <text x="88" y="32" class="term-prompt">ahmad@github</text>')
    svg.append('    <text x="195" y="32" class="term-path"> ~ $ </text>')
    svg.append('    <text x="236" y="32" class="term-cmd">whoami</text>')
    # Blinking cursor
    svg.append('    <rect x="300" y="20" width="8" height="15" fill="#7ee787" rx="1">')
    svg.append('      <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>')
    svg.append('    </rect>')
    # Top-right indicator
    svg.append(f'    <text x="{SVG_W - 28}" y="32" text-anchor="end" class="term-dim">profile://AhmadKhalil05</text>')
    svg.append('  </g>')

    # Header Divider Line
    svg.append(f'  <line x1="1" y1="52" x2="{SVG_W - 1}" y2="52" stroke="#21262d" stroke-width="1"/>')

    # LEFT: Animated ASCII Portrait
    svg.append('  <!-- Animated ASCII Portrait -->')
    svg.append('  <g class="mono ascii-text" xml:space="preserve">')
    for i, line in enumerate(lines):
        y = ascii_start_y + (i + 1) * cell_h
        safe_line = html.escape(line or " ")
        clip_id = f"ln{i}"
        full_w = max(1, len(line)) * cell_w
        begin = 0.15 + i * 0.035
        dur = max(0.20, min(0.60, len(line) * 0.010))
        svg.append(f'    <defs><clipPath id="{clip_id}"><rect x="{ascii_start_x}" y="{y - cell_h + 1:.1f}" width="0" height="{cell_h + 1:.1f}">')
        svg.append(f'      <animate attributeName="width" from="0" to="{full_w + 10:.1f}" dur="{dur:.2f}s" begin="{begin:.2f}s" fill="freeze"/>')
        svg.append(f'    </rect></clipPath></defs>')
        svg.append(f'    <text x="{ascii_start_x}" y="{y:.1f}" clip-path="url(#{clip_id})">{safe_line}</text>')
    svg.append('  </g>')

    # RIGHT: Profile Information
    info_x = 510
    svg.append('  <!-- Profile Information -->')
    svg.append('  <g class="mono">')
    
    # Name & Role
    svg.append(f'    <text x="{info_x}" y="112" class="name-title">{html.escape(display_name)}</text>')
    svg.append(f'    <text x="{info_x}" y="142" class="role-title">{html.escape(role)}</text>')
    
    # Sub-divider
    svg.append(f'    <line x1="{info_x}" y1="166" x2="{SVG_W - 40}" y2="166" stroke="#21262d" stroke-width="1"/>')

    # Core Technical Focus & Stack
    svg.append(f'    <g transform="translate(0, 5)">')
    # Focus
    svg.append(f'      <text x="{info_x}" y="200" class="meta-label">Focus</text>')
    svg.append(f'      <text x="{info_x + 85}" y="200" class="meta-val">{html.escape(focus)}</text>')
    # Stack
    svg.append(f'      <text x="{info_x}" y="234" class="meta-label">Stack</text>')
    svg.append(f'      <text x="{info_x + 85}" y="234" class="meta-val">{html.escape(stack)}</text>')
    # Builds
    svg.append(f'      <text x="{info_x}" y="268" class="meta-label">Builds</text>')
    svg.append(f'      <text x="{info_x + 85}" y="268" class="meta-val">{html.escape(builds)}</text>')
    svg.append('    </g>')

    # Sub-divider 2
    svg.append(f'    <line x1="{info_x}" y1="304" x2="{SVG_W - 40}" y2="304" stroke="#21262d" stroke-width="1"/>')

    # Location, Website, and Philosophy
    svg.append(f'    <g transform="translate(0, 10)">')
    # Location
    svg.append(f'      <text x="{info_x}" y="332" class="meta-label">Based</text>')
    svg.append(f'      <text x="{info_x + 85}" y="332" class="meta-val">{html.escape(location)}</text>')
    # Website
    svg.append(f'      <text x="{info_x}" y="366" class="meta-label">Website</text>')
    svg.append(f'      <text x="{info_x + 85}" y="366" class="meta-val" fill="#7ee787">{html.escape(website)}</text>')
    # Tagline
    svg.append(f'      <text x="{info_x}" y="408" class="meta-dim">Crafting resilient cloud architectures &amp; refined digital experiences.</text>')
    svg.append('    </g>')

    svg.append('  </g>')
    svg.append('</svg>')

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(svg), encoding="utf-8")
    print(f"Generated {OUT_PATH}")

if __name__ == "__main__":
    build_hero_svg()
