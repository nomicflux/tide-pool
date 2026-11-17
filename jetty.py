"""The jetty: a spelled word drawn as planks reaching out over the water, and walked as footsteps."""

from html import escape

from seaglass import DURATION, chime, record, rest
from shore import is_gap

NARROWEST = 720
PLANK = 34
CHARACTER = 7


def span(spelled):
    """How wide the jetty must be for its longest line to stay on its plank."""
    return max(NARROWEST, 104 + CHARACTER * max(map(len, spelled), default=0))


def plank(row, letter, line, width):
    """One plank: the letter at its end and the remembered line along it; a gap when the line is only the letter."""
    y = 40 + row * PLANK
    mark = (f'<text x="36" y="{y + 22}" fill="#ead9af" font-size="18" font-family="Georgia, serif">'
            f'{escape(letter.upper())}</text>')
    if is_gap(letter, line):
        return mark
    return (f'<rect x="24" y="{y}" width="{width - 48}" height="{PLANK - 6}" rx="3" fill="#7a5b3a"/>'
            + mark + f'<text x="64" y="{y + 19}" fill="#f6e7b8" font-size="13" '
            f'font-family="Georgia, serif">{escape(line)}</text>')


def jetty(word, spelled):
    """The whole jetty for `word`, one plank per letter of `spelled`, over dark water."""
    width, height = span(spelled), 80 + len(spelled) * PLANK
    planks = "".join(plank(row, letter, line, width)
                     for row, (letter, line) in enumerate(zip(word, spelled)))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}"><title>{escape(word)}</title>'
            f'<rect width="{width}" height="{height}" fill="#0b1a24"/>{planks}</svg>')


def footsteps(word, spelled):
    """Walking the jetty: a calm chime for each plank, pitched by its letter, and a silent step over each gap."""
    return [rest(DURATION["calm"]) if is_gap(letter, line) else chime(letter, "calm")
            for letter, line in zip(word, spelled)]


def walk(word, spelled, path):
    record(path, footsteps(word, spelled))
