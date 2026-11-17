"""A printable sea for the words currently in the pool."""

from html import escape
from pathlib import Path
from textwrap import wrap

WATER = {"calm": "#102d38", "fog": "#475b61", "storm": "#292039", "ice": "#3e6475"}
DAY_WATER = {"calm": "#d8e8df", "fog": "#d5dcda", "storm": "#aebbc4", "ice": "#e7f2f4"}


def header(weather, height, daylight=False):
    background = (DAY_WATER if daylight else WATER)[weather]
    ink = "#183e48" if daylight else "#ead9af"
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}">',
        '<title>Tide Pool — a coast that remembers</title>',
        f'<rect width="1100" height="{height}" fill="{background}"/>',
        f'<g fill="{ink}" font-family="Georgia, serif">',
        '<text x="65" y="75" font-size="32">A coast that remembers</text>',
        f'<text x="65" y="110" font-size="16">{escape(weather)} water</text>',
    ]


def word_mark(i, word, row_y=175):
    x = 110 + (i % 5) * 210
    y = row_y + (i % 3) * 12
    lines = wrap(word, width=16)
    text = ''.join(f'<tspan x="{x}" dy="{0 if n == 0 else 26}">{escape(line)}</tspan>'
                   for n, line in enumerate(lines))
    return [f'<circle cx="{x}" cy="{y}" r="3"/>',
            f'<text x="{x}" y="{y + 30}" text-anchor="middle" font-family="monospace" font-size="20">{text}</text>']


def bobbing(i, pieces):
    bob = ('<animateTransform attributeName="transform" type="translate" '
           f'values="0 0;0 -6;0 0" dur="{5 + i % 4}s" repeatCount="indefinite"/>')
    return ["<g>", *pieces, bob, "</g>"]


def shoreline(height, moving=True, daylight=False):
    y = height - 70
    still = f"M 65 {y} Q 300 {y-35} 550 {y} T 1035 {y}"
    swell = f"M 65 {y} Q 300 {y+20} 550 {y} T 1035 {y}"
    breath = f'<animate attributeName="d" values="{still};{swell};{still}" dur="9s" repeatCount="indefinite"/>'
    ink = "#466e70" if daylight else "#5c9392"
    return f'<path d="{still}" fill="none" stroke="{ink}">{breath if moving else ""}</path>'


def svg(words, weather, daylight=False):
    marks = []
    row_y = 175
    for start in range(0, len(words), 5):
        row = words[start:start + 5]
        for i, word in enumerate(row, start):
            pieces = word_mark(i, word, row_y)
            marks.extend(pieces if weather == "ice" else bobbing(i, pieces))
        row_y += max(100, 74 + 26 * max(len(wrap(word, width=16)) for word in row))
    height = row_y + 105
    return "\n".join(header(weather, height, daylight) + marks +
                     ["</g>", shoreline(height, weather != "ice", daylight), "</svg>"])


def draw(words, weather, path, daylight=False):
    Path(path).write_text(svg(words, weather, daylight), encoding="utf-8")
