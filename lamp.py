"""The lighthouse lamp: words flashed, and sounded, as International Morse code."""

from html import escape

from seaglass import record, rest, tone

LETTERS = "abcdefghijklmnopqrstuvwxyz0123456789"
CODES = (".- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - "
         "..- ...- .-- -..- -.-- --.. ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----.")
MORSE = dict(zip(LETTERS, CODES.split()))
UNIT = 0.08
PITCH = 660


def codes(word):
    return [MORSE[letter] for letter in word.casefold() if letter in MORSE]


def flashes(word):
    return " ".join(code.replace(".", "·").replace("-", "—") for code in codes(word))


def signal_lines(text):
    return [f"{word:<14}{flashes(word)}" for word in text.split() if flashes(word)]


def letter_beats(code):
    beats = [beat for symbol in code for beat in ((True, 1 if symbol == "." else 3), (False, 1))]
    return beats[:-1] + [(False, 3)]


def timing(text):
    """(sounding, units): dots 1, dashes 3; silences of 1 inside a letter, 3 between letters, 7 between words."""
    beats = []
    for word in text.split():
        letters = [beat for code in codes(word) for beat in letter_beats(code)]
        beats += (letters[:-1] + [(False, 7)]) if letters else []
    return beats


def sound(text, path):
    record(path, (tone(PITCH, units * UNIT) if sounding else rest(units * UNIT)
                  for sounding, units in timing(text)))


def light(text):
    beats = timing(text)
    total = sum(units for _, units in beats)
    elapsed, times, values = 0, [], []
    for sounding, units in beats:
        times.append(f"{elapsed / total:.8f}")
        values.append("1" if sounding else "0.12")
        elapsed += units
    animation = (f'<animate attributeName="opacity" calcMode="discrete" '
                 f'values="{";".join(values + ["0.12"])}" keyTimes="{";".join(times + ["1"])}" '
                 f'dur="{total * UNIT:g}s" repeatCount="indefinite"/>') if beats else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="240" viewBox="0 0 400 240">'
            f'<title>{escape(text)}</title><rect width="400" height="240" fill="#0b1a24"/>'
            f'<circle cx="200" cy="100" r="32" fill="#f6e7b8" opacity="0.12">{animation}</circle>'
            '<text x="200" y="190" text-anchor="middle" fill="#ead9af" font-family="Georgia, serif">'
            'The lamp</text></svg>')
