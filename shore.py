"""The shore: where every poem is kept, and the ways of reading what it remembers."""

import os
import re
from uuid import uuid4
from collections import Counter

from bindery import HEADER, pages
from weather import BRIDGE_WORDS

SHORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shore.txt")
BARE = "The shore is bare. No tide has left a shell."


def shell(number, poem, day=""):
    dated = f" · {day}" if day else ""
    return f"~ tide {number}{dated} ~\n{poem}\n"


def wash_ashore(path, entry):
    with open(path, "a") as shore:
        shore.write(entry + "\n")


def read_shore(path):
    if not os.path.exists(path):
        return BARE
    with open(path) as shore:
        return shore.read().rstrip()


def kept_pages(path):
    """The shore's poems as (tide, day, poem), oldest first; none on a bare shore."""
    return pages(read_shore(path))


def cast_bottle(sea, phrase):
    identity = uuid4().hex
    with open(sea, "a", encoding="utf-8") as water:
        water.write(identity + "\t" + phrase + "\n")
    return identity


def unpack_bottle(line):
    """A sea line as (identity, phrase); bottles cast before identities have identity None."""
    identity, separator, phrase = line.partition("\t")
    if separator and re.fullmatch(r"[0-9a-f]{32}", identity):
        return identity, phrase
    return None, line


def drifting(sea):
    """The identities of the bottles at sea, oldest first; None for bottles cast before identities."""
    if not os.path.exists(sea):
        return []
    with open(sea, encoding="utf-8") as water:
        return [unpack_bottle(line)[0] for line in water.read().splitlines()]


def take_bottle(sea, mine=()):
    """The oldest bottle at sea that is not one of `mine`, taken out; "" when none drift in."""
    if not os.path.exists(sea):
        return ""
    with open(sea, encoding="utf-8") as water:
        bottles = water.read().splitlines()
    waiting = [i for i, line in enumerate(bottles) if unpack_bottle(line)[0] not in mine]
    if not waiting:
        return ""
    taken = bottles.pop(waiting[0])
    with open(sea, "w", encoding="utf-8") as water:
        water.writelines(line + "\n" for line in bottles)
    return unpack_bottle(taken)[1]


def poem_lines(shore_text):
    return [line for line in shore_text.splitlines()
            if line and not HEADER.fullmatch(line)]


def shore_text(shore):
    """The shore's kept text, or "" before any tide has left a shell (never the bare-shore sentence)."""
    return read_shore(shore) if os.path.exists(shore) else ""


def shore_lines(shore):
    return poem_lines(shore_text(shore))


SMALL_WORDS = {"a", "an", "the", "i", "me", "my", "you", "your", "we", "us", "our", "it", "its",
               "he", "she", "his", "her", "they", "them", "their", "is", "am", "are", "was", "be",
               "has", "have", "had", "to", "of", "in", "on", "at", "for", "with", "by", "from",
               "so", "but", "or", "if", "as", "that", "this", "not", "can", "will"}


def is_thing(word):
    """A word the shore remembers: not a weather's bridge and not a small grammar word."""
    return word not in BRIDGE_WORDS and word.strip("?!.,;:").casefold() not in SMALL_WORDS


def remembered(shore_text):
    return Counter(word for line in poem_lines(shore_text) for word in line.split() if is_thing(word))


def heaps(counts):
    return "\n".join(f"{word:>14} {'o' * count}" for word, count in counts.most_common(7))


def wrack(shore_text):
    things = remembered(shore_text)
    if not things:
        return "Nothing has washed up along the strandline yet."
    return heaps(things)


def traces(word, shore_text):
    pattern = re.compile(rf"\b{re.escape(word)}\b")
    return [line for line in poem_lines(shore_text) if pattern.search(line)]


def held_pages(word, kept):
    """(tide, day, lines, since) for each kept poem holding `word`, oldest first: the lines that hold it
    and how many poems were kept after it."""
    return [(tide, day, lines, len(kept) - 1 - n)
            for n, (tide, day, poem) in enumerate(kept) if (lines := traces(word, poem))]


def remembering(word, shores):
    """(name, lines) for each named shore text that traces `word`, in the order given."""
    found = ((name, len(traces(word, text))) for name, text in shores.items())
    return [(name, lines) for name, lines in found if lines]


def kindred(word, shore_text):
    company = remembered("\n".join(traces(word, shore_text)))
    for part in word.split():
        del company[part]
    return company


def meets(poem, first, second):
    return bool(set(traces(first, poem)) & set(traces(second, poem)))


def brightest(shore_text):
    return remembered(shore_text).most_common(12)


def crab_home(shore_text):
    """(word, line): the shore's most remembered word and the newest line holding it; None on a bare shore."""
    counts = remembered(shore_text)
    if not counts:
        return None
    word = counts.most_common(1)[0][0]
    return word, [line for line in poem_lines(shore_text) if word in line.split()][-1]


def things(text):
    words = (word.strip("?!.,;:") for word in text.split())
    return {word.casefold() for word in words if word and is_thing(word)}


ASKING = {"who", "what", "where", "when", "why", "how", "is", "are", "do", "does", "there"}


def acrostic(word, lines):
    """For each letter of `word`, the oldest unused line beginning with it, else the letter alone."""
    lines = list(lines)
    spelled = []
    for letter in word.lower():
        found = next((line for line in lines if line[0].lower() == letter), letter.upper())
        if found in lines:
            lines.remove(found)
        spelled.append(found)
    return spelled


def initials(lines):
    """How many remembered lines begin with each letter, the way `acrostic` reads them."""
    return Counter(line[0].lower() for line in lines if line[0].isalpha())


def is_gap(letter, line):
    """True where an acrostic found no remembered line for `letter`."""
    return line == letter.upper()


def gaps(word, spelled):
    """The letters of `word` still waiting for a line, each named once, in order."""
    return list(dict.fromkeys(letter.upper() for letter, line in zip(word, spelled)
                              if is_gap(letter, line) and letter.isalnum()))


def rhymes(word, lines):
    """Lines whose last word ends in the same two letters as `word`, without being `word`."""
    word = word.casefold()
    ends = [(line, line.split()[-1].strip("?!.,;:").casefold()) for line in lines]
    return [line for line, last in ends if last != word and last[-2:] == word[-2:]]


def answer(question, shore_text):
    """The newest shore line sharing the most things with the question, or "" if none share any."""
    asked = things(question) - ASKING
    scored = [(len(asked & things(line)), line) for line in poem_lines(shore_text)]
    best = max((score for score, _ in scored), default=0)
    return [line for score, line in scored if score == best][-1] if best else ""
