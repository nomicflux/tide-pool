"""The shore's most remembered words, drawn as a night sky."""

import math
from html import escape
from pathlib import Path
from textwrap import wrap
from zlib import crc32


def place(word):
    seed = crc32(word.encode("utf-8"))
    return 80 + seed % 940, 110 + (seed // 940) % 420


def star(word, count):
    x, y = place(word)
    return f'<circle class="star" cx="{x}" cy="{y}" r="{1 + count}" fill="#f6e7b8"/>'


def labels(counts):
    pieces = []
    baseline = 110
    for word, count in sorted(counts, key=lambda item: place(item[0])[1]):
        x, y = place(word)
        lines = wrap(f"{word} · {count}", width=36)
        pieces.append(f'<path d="M{x} {y} L1080 {y} L1120 {baseline - 5}" fill="none" stroke="#5c9392" stroke-width="0.5" stroke-dasharray="2 4"/>')
        spans = ''.join(f'<tspan x="1130" dy="{0 if i == 0 else 20}">{escape(line)}</tspan>'
                        for i, line in enumerate(lines))
        pieces.append(f'<text x="1130" y="{baseline}" font-family="monospace" font-size="14">{spans}</text>')
        baseline += 20 * len(lines) + 16
    return ''.join(pieces), max(600, baseline + 40)


def moon(lunation):
    """A circular limb and elliptical terminator, mirrored for the waning moon."""
    curve = math.cos(2 * math.pi * lunation)
    side = 1 if lunation < 0.5 else -1
    return (f'<g class="moon" transform="translate(1000 60) scale({side} 1)">'
            '<path fill="#f6e7b8" d="M 0 -26 A 26 26 0 0 1 0 26 '
            f'A {26 * abs(curve):.4f} 26 0 0 {int(curve < 0)} 0 -26 Z"/></g>')


def constellation(words):
    points = " ".join(f"{x},{y}" for x, y in map(place, words))
    return f'<polyline points="{points}" fill="none" stroke="#5c9392" stroke-width="0.6"/>'


def sky(counts, lunation):
    stars = "".join(star(word, count) for word, count in counts)
    names, height = labels(counts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="{height}" viewBox="0 0 1500 {height}">'
            f'<title>The sky over the shore</title><rect width="1500" height="{height}" fill="#0b1a24"/>'
            '<g fill="#ead9af" font-family="Georgia, serif">'
            '<text x="65" y="60" font-size="28">The sky over the shore</text>'
            f'{moon(lunation)}{constellation([word for word, _ in counts])}{names}{stars}</g></svg>')


def chart_sky(counts, lunation, path):
    Path(path).write_text(sky(counts, lunation), encoding="utf-8")
