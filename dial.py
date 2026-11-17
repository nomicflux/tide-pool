"""The tide dial: the coast's twice-daily water as a clock face, its needle at the present turn."""

import math
from html import escape

CENTRE, RADIUS = (360, 270), 155
MARKS = (("High water", 360, 70), ("Falling", 610, 278), ("Low water", 360, 487), ("Rising", 110, 278))


def needle(turn):
    """Where the needle's tip lies: clockwise from high water at the top, one full turn per tide."""
    angle = 2 * math.pi * turn
    return (round(CENTRE[0] + RADIUS * math.sin(angle), 1), round(CENTRE[1] - RADIUS * math.cos(angle), 1))


def dial(turn, state):
    """The dial as SVG, titled with the water's state, its needle pointing at `turn`."""
    x, y = needle(turn)
    marks = "".join(f'<text x="{mx}" y="{my}">{name}</text>' for name, mx, my in MARKS)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="520" viewBox="0 0 720 520" role="img">'
            f'<title>The water is {escape(state)}</title><rect width="720" height="520" fill="#102d38"/>'
            f'<circle cx="{CENTRE[0]}" cy="{CENTRE[1]}" r="{RADIUS}" fill="none" stroke="#5c9392" stroke-width="3"/>'
            f'<g fill="#ead9af" font-family="Georgia, serif" font-size="26" text-anchor="middle">{marks}</g>'
            f'<line x1="{CENTRE[0]}" y1="{CENTRE[1]}" x2="{x}" y2="{y}" stroke="#f6e7b8" stroke-width="4"/>'
            f'<circle cx="{x}" cy="{y}" r="9" fill="#f6e7b8"/></svg>')
