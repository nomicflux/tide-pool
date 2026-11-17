"""The harbour wall: a painted mark for every kept poem a word washed up in, the oldest lowest."""

from html import escape

WIDTH = 640
TOP = 70
BOTTOM = 470


def mark_height(since, total):
    """How high a poem's mark sits: the shore's oldest poem at the foot of the wall, its newest at the top."""
    return round(BOTTOM - (BOTTOM - TOP) * (total - 1 - since) / max(total - 1, 1))


def label(y, tide, day):
    dated = f" · {day}" if day else ""
    return (f'<text x="432" y="{y + 4}" fill="#f6e7b8" font-size="13" font-family="Georgia, serif">'
            f'tide {tide}{escape(dated)}</text>')


def tidewall(word, held, total):
    """The wall for `word`: one white mark per poem in `held`, the lowest and highest named."""
    heights = [mark_height(since, total) for _, _, _, since in held]
    marks = "".join(f'<rect x="120" y="{y - 2}" width="280" height="4" fill="#f4f1e8"/>' for y in heights)
    names = "".join(label(heights[end], held[end][0], held[end][1]) for end in sorted({0, len(held) - 1}))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="520" viewBox="0 0 {WIDTH} 520">'
            f'<title>{escape(word)} on the harbour wall</title><rect width="{WIDTH}" height="520" fill="#0b1a24"/>'
            f'<rect x="100" y="{TOP - 20}" width="320" height="{BOTTOM - TOP + 40}" fill="#5b6066"/>{marks}{names}'
            f'<text x="110" y="34" fill="#ead9af" font-size="20" font-family="Georgia, serif">{escape(word)}</text>'
            f'<rect y="{BOTTOM + 20}" width="{WIDTH}" height="30" fill="#163447"/></svg>')
