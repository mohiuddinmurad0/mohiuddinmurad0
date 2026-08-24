#!/usr/bin/env python3
"""Render a photo as monochrome block-text art in an SVG, beside a neofetch-style info panel.

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
RAMP  = "███▓▒░ "     # densest -> empty

# monochrome only: one ink colour, one muted tone, plus the page ground
# strictly neutral greys -- no hue anywhere, so the art reads the same on any ground
THEME = dict(bg="#000000", ink="#ededed", mute="#707070") if DARK \
   else dict(bg="#ffffff", ink="#141414", mute="#949494")
# neofetch's colour strip, rendered as a tonal ramp instead
GREYS  = ["#242424", "#3c3c3c", "#545454", "#707070", "#949494", "#b4b4b4", "#d4d4d4", "#f0f0f0"]
SWATCH = GREYS if DARK else GREYS[::-1]

INFO = [
    [("bold", "murad"), ("ink", "@"), ("bold", "github")],
    [("mute", "─" * 46)],
    [("ink", "Name"), ("mute", ".............. "), ("ink", "Mohiuddin Murad")],
    [("ink", "Role"), ("mute", ".............. "), ("ink", "Software Engineer @ StepUp")],
    [("ink", "Location"), ("mute", ".......... "), ("ink", "Bangladesh")],
    [("ink", "Editor"), ("mute", "............ "), ("ink", "VS Code, Sublime, PyCharm")],
    [],
    [("ink", "Frontend"), ("mute", ".......... "), ("ink", "HTML5, CSS3, React, Tailwind, Sass")],
    [("ink", "Backend"), ("mute", "........... "), ("ink", "Node.js, Express.js")],
    [("ink", "Languages"), ("mute", "......... "), ("ink", "JavaScript, C, C++, Java, Python")],
    [("ink", "Databases"), ("mute", "......... "), ("ink", "MongoDB, MySQL, Firebase")],
    [("ink", "Tools"), ("mute", "............. "), ("ink", "Git, Docker, Postman, Figma, Linux")],
    [],
    [("ink", "Learning"), ("mute", ".......... "), ("ink", "Node.js / Express.js / MongoDB")],
    [("ink", "Ask.Me.About"), ("mute", "...... "), ("ink", "JavaScript, React, Tailwind, CSS3")],
    [],
    [("bold", "Contact")],
    [("ink", "Email"), ("mute", "............. "), ("ink", "murad.stepup@gmail.com")],
    [("ink", "Portfolio"), ("mute", "......... "), ("ink", "murad00.vercel.app")],
    [("ink", "LinkedIn"), ("mute", ".......... "), ("ink", "linkedin.com/in/murad00")],
    [("ink", "Twitter"), ("mute", "........... "), ("ink", "@muradmy00")],
    [("ink", "GitHub"), ("mute", "............ "), ("ink", "github.com/mohiuddinmurad0")],
]

# ---------- sample the photo ----------
src  = ImageEnhance.Contrast(Image.open(SRC).convert("L")).enhance(1.1)
rows = int(src.height / src.width * COLS * (AD / LH))
lum  = src.resize((COLS, rows), Image.LANCZOS)
lp   = lum.load()

def cell(x, y):
    """Pick a ramp glyph for this cell, or None to leave the background bare.

    On a light ground more ink means darker; on a dark ground the ink *is* the
    light, so the mapping flips — otherwise the portrait comes out a negative.
    """
    v = lp[x, y]
    if v >= CUT:
        return None
    t = (CUT - 1 - v) / CUT if DARK else v / CUT
    ch = RAMP[min(len(RAMP) - 1, int(t * (len(RAMP) - 1)))]
    return None if ch == " " else ch

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
    spans, run, rx = [], "", None
    for x in range(COLS):
        c = keep[y][x]
        if c:
            if not run:
                rx = x * AD + AD
            run += c
        else:
            if run:
                spans.append(f'<tspan x="{rx:.1f}">{html.escape(run)}</tspan>')
            run, rx = "", None
    if run:
        spans.append(f'<tspan x="{rx:.1f}">{html.escape(run)}</tspan>')
    if spans:
        o.append(f'<text y="{base:.1f}" fill="{THEME["ink"]}" '
                 f'xml:space="preserve">{"".join(spans)}</text>')

off = max(0, (art_h - len(INFO) * ILH) / 2)
for i, line in enumerate(INFO):
    if not line:
        continue
    base, x, spans = pad + off + i * ILH + FS * 0.82, info_x0, []
    for kind, text in line:
        # no colour to lean on, so emphasis is carried by weight
        attr = f'fill="{THEME["ink"]}" font-weight="700"' if kind == "bold" \
          else f'fill="{THEME[kind]}"'
        spans.append(f'<tspan x="{x:.1f}" {attr}>{html.escape(text)}</tspan>')
        x += len(text) * AD
    o.append(f'<text y="{base:.1f}" xml:space="preserve">{"".join(spans)}</text>')

sy = pad + off + (len(INFO) + 0.6) * ILH
for i, c in enumerate(SWATCH):
    o.append(f'<rect x="{info_x0 + i * 5.2 * AD:.1f}" y="{sy:.1f}" '
             f'width="{4.2 * AD:.1f}" height="{ILH * 0.62:.1f}" fill="{c}" rx="2"/>')

o.append("</svg>")
open(OUT, "w").write("\n".join(o))
print(f"{COLS}x{rows} cells -> {OUT}  {width:.0f}x{height:.0f}px")
