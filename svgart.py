#!/usr/bin/env python3
"""Render a photo as colour block-text art in an SVG, beside a neofetch-style info panel.

usage: python3 svgart.py [cols] [out.svg] [--dark]
"""
import sys, html
from PIL import Image, ImageEnhance

SRC   = "/Users/murad/Downloads/196592706.jpeg"
COLS  = int(sys.argv[1]) if len(sys.argv) > 1 else 150
OUT   = sys.argv[2] if len(sys.argv) > 2 else "profile.svg"
DARK  = "--dark" in sys.argv

FS    = 12.0          # font-size
AD    = FS * 0.60     # monospace advance  -> cell width
LH    = FS * 1.00     # cell height: a full block glyph is ~1em tall, so rows butt together
ILH   = FS * 1.55     # line height for the info panel
CUT   = 240           # luminance at/above this counts as background
GAP   = 4             # blank columns between art and panel
RAMP  = "███▓▒░ "     # dark -> light

THEME = dict(bg="#0d1117", fg="#c9d1d9", dim="#30363d", key="#58a6ff", accent="#3fb950") if DARK \
   else dict(bg="#ffffff", fg="#1f2328", dim="#d0d7de", key="#0969da", accent="#1a7f37")
SWATCH = ["#ff7b72", "#ffa657", "#e3b341", "#3fb950", "#39c5cf", "#58a6ff", "#bc8cff", "#8b949e"]

INFO = [
    [("accent", "murad"), ("fg", "@"), ("accent", "github")],
    [("dim", "─" * 46)],
    [("key", "Name"), ("dim", ".............. "), ("fg", "Mohiuddin Murad")],
    [("key", "Role"), ("dim", ".............. "), ("fg", "Software Engineer @ StepUp")],
    [("key", "Location"), ("dim", ".......... "), ("fg", "Bangladesh")],
    [("key", "Editor"), ("dim", "............ "), ("fg", "VS Code, Sublime, PyCharm")],
    [],
    [("key", "Frontend"), ("dim", ".......... "), ("fg", "HTML5, CSS3, React, Tailwind, Sass")],
    [("key", "Backend"), ("dim", "........... "), ("fg", "Node.js, Express.js")],
    [("key", "Languages"), ("dim", "......... "), ("fg", "JavaScript, C, C++, Java, Python")],
    [("key", "Databases"), ("dim", "......... "), ("fg", "MongoDB, MySQL, Firebase")],
    [("key", "Tools"), ("dim", "............. "), ("fg", "Git, Docker, Postman, Figma, Linux")],
    [],
    [("key", "Learning"), ("dim", ".......... "), ("fg", "Node.js / Express.js / MongoDB")],
    [("key", "Ask.Me.About"), ("dim", "...... "), ("fg", "JavaScript, React, Tailwind, CSS3")],
    [],
    [("accent", "Contact")],
    [("key", "Email"), ("dim", "............. "), ("fg", "murad.stepup@gmail.com")],
    [("key", "Portfolio"), ("dim", "......... "), ("fg", "murad00.vercel.app")],
    [("key", "LinkedIn"), ("dim", ".......... "), ("fg", "linkedin.com/in/murad00")],
    [("key", "Twitter"), ("dim", "........... "), ("fg", "@muradmy00")],
    [("key", "GitHub"), ("dim", "............ "), ("fg", "github.com/muradmy00")],
]

# ---------- sample the photo ----------
src  = ImageEnhance.Color(ImageEnhance.Contrast(Image.open(SRC).convert("RGB")).enhance(1.1)).enhance(1.2)
rows = int(src.height / src.width * COLS * (AD / LH))
col  = src.resize((COLS, rows), Image.LANCZOS)
lum  = col.convert("L")
cp, lp = col.load(), lum.load()

def cell(x, y):
    v = lp[x, y]
    if v >= CUT:
        return None
    ch = RAMP[min(len(RAMP) - 1, int(v / CUT * (len(RAMP) - 1)))]
    if ch == " ":
        return None
    r, g, b = cp[x, y]
    return ch, f"#{r:02x}{g:02x}{b:02x}"

# drop lone specks left over in the background
keep = [[cell(x, y) for x in range(COLS)] for y in range(rows)]
for y in range(rows):
    for x in range(COLS):
        if keep[y][x] and lp[x, y] > CUT - 22:
            n = sum(1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if 0 <= y+dy < rows and 0 <= x+dx < COLS and keep[y+dy][x+dx])
            if n <= 3:
                keep[y][x] = None

# ---------- lay out ----------
info_w  = max((sum(len(t) for _, t in ln) for ln in INFO), default=0)
info_x0 = (COLS + GAP) * AD
width   = info_x0 + info_w * AD + 3 * AD
art_h   = rows * LH
height  = max(art_h, (len(INFO) + 2) * ILH) + 3 * LH

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
     f'viewBox="0 0 {width:.0f} {height:.0f}" font-family="ui-monospace,SFMono-Regular,Menlo,'
     f'Consolas,&quot;DejaVu Sans Mono&quot;,monospace" font-size="{FS}">',
     f'<rect width="100%" height="100%" fill="{THEME["bg"]}"/>']

pad = LH * 1.5
for y in range(rows):
    base = pad + y * LH + FS * 0.82
    spans, run, rx, rc = [], "", None, None
    for x in range(COLS):
        c = keep[y][x]
        if c and c[1] == rc:
            run += c[0]
        else:
            if run:
                spans.append(f'<tspan x="{rx:.1f}" fill="{rc}">{html.escape(run)}</tspan>')
            run, rx, rc = (c[0], x * AD + AD, c[1]) if c else ("", None, None)
    if run:
        spans.append(f'<tspan x="{rx:.1f}" fill="{rc}">{html.escape(run)}</tspan>')
    if spans:
        o.append(f'<text y="{base:.1f}" xml:space="preserve">{"".join(spans)}</text>')

off = max(0, (art_h - len(INFO) * ILH) / 2)
for i, line in enumerate(INFO):
    if not line:
        continue
    base, x, spans = pad + off + i * ILH + FS * 0.82, info_x0, []
    for kind, text in line:
        spans.append(f'<tspan x="{x:.1f}" fill="{THEME[kind]}">{html.escape(text)}</tspan>')
        x += len(text) * AD
    o.append(f'<text y="{base:.1f}" xml:space="preserve">{"".join(spans)}</text>')

sy = pad + off + (len(INFO) + 0.6) * ILH
for i, c in enumerate(SWATCH):
    o.append(f'<rect x="{info_x0 + i * 5.2 * AD:.1f}" y="{sy:.1f}" '
             f'width="{4.2 * AD:.1f}" height="{ILH * 0.62:.1f}" fill="{c}" rx="2"/>')

o.append("</svg>")
open(OUT, "w").write("\n".join(o))
print(f"{COLS}x{rows} cells -> {OUT}  {width:.0f}x{height:.0f}px")
