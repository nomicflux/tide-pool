"""The exhibit halls: hanging a shore with its keepsakes, listing the halls, and the atlas."""

import os
import re
import shutil
from pathlib import Path

from atlas import atlas
from bindery import book, pages
from dial import dial
from moon import SYNODIC_DAYS, age, daylight_at, turn_of, water
from postcard import draw
from seaglass import sing
from shore import BARE, brightest, read_shore
from skychart import chart_sky
from storybook import CHART, STORY_DIR, stories

EXHIBIT_NAME = re.compile(r"[a-z0-9-]+")
SIGNAL = ("signal.svg", "signal.wav")
JETTY = ("jetty.svg",)
PLANKS = ("jetty.wav",)
CRAB = ("crab.svg",)
WALL = ("wall.svg",)
DIAL = ("tideclock.svg",)
BELLS = ("tide.wav",)
KEPT = (SIGNAL, JETTY, PLANKS, CRAB, WALL)
EXTRAS = (
    (BELLS, "- [Hear its bells](tide.wav).\n"),
    (SIGNAL, "- [Watch the last signal](signal.svg), or [hear it in Morse](signal.wav).\n"),
    (("sky.svg",), "- [See the shore's sky](sky.svg).\n"),
    (JETTY, "- [Walk the last jetty](jetty.svg).\n"),
    (PLANKS, "- [Hear its planks underfoot](jetty.wav).\n"),
    (CRAB, "- [Meet the last crab](crab.svg).\n"),
    (WALL, "- [See the last marks on the harbour wall](wall.svg).\n"),
    (DIAL, "- [Read the water as the hall was hung](tideclock.svg).\n"),
)


def halls(hall):
    names = sorted(os.listdir(hall)) if os.path.isdir(hall) else []
    return [name for name in names if EXHIBIT_NAME.fullmatch(name)]


def hall_title(hall, name):
    """The title on the first line of a hall's catalogue, without its '# '."""
    with open(os.path.join(hall, name, "README.md"), encoding="utf-8") as listing:
        return listing.readline().strip().removeprefix("# ")


def shelf():
    return {name: Path(STORY_DIR, file).read_text(encoding="utf-8")
            for name, file in stories(STORY_DIR).items()}


def chart_atlas(shore):
    folder = os.path.dirname(shore)
    path = os.path.join(folder, "atlas.html")
    chart = Path(CHART).read_text(encoding="utf-8")
    hall = os.path.join(folder, "exhibits")
    titled = [(name, hall_title(hall, name)) for name in halls(hall)]
    Path(path).write_text(atlas(chart, shelf(), titled), encoding="utf-8")
    return f"Open {path} to read the whole coast in one atlas."


def catalogue(name, shore_text, kept):
    poems = pages(shore_text)
    last = poems[-1][2].splitlines()[-1]
    extras = "".join(line for files, line in EXTRAS if set(files) <= kept)
    count = "1 poem was" if len(poems) == 1 else f"{len(poems)} poems were"
    return (f"# {name}\n\n{count} left on the shore.\n\n"
            "- [Read them bound](book.html), or [the plain shore](shore.txt).\n"
            "- [See the last pool](postcard.svg).\n"
            f"{extras}\n"
            f"The sea's last words were:\n\n> {last}\n")


def keep_beside(shore, folder, files):
    """Copy a keepsake lying beside the shore (the last signal, the last jetty) into the hall, as it was made."""
    beside = [os.path.join(os.path.dirname(shore), name) for name in files]
    if not all(os.path.isfile(path) for path in beside):
        return set()
    for path in beside:
        shutil.copy(path, folder)
    return set(files)


def hang_sky(folder, shore_text, when):
    """Draw the hall its own sky from the shore it keeps, so it is never older than the poems."""
    counts = brightest(shore_text)
    if not counts:
        return set()
    chart_sky(counts, age(when) / SYNODIC_DAYS, os.path.join(folder, "sky.svg"))
    return {"sky.svg"}


def hang_dial(folder, when):
    """Draw the water at the hour the hall is hung, so its dial is never older than the hall."""
    Path(folder, "tideclock.svg").write_text(dial(turn_of(when), water(when)), encoding="utf-8")
    return set(DIAL)


def hang_bells(pool, folder):
    """Ring the pool's words into the hall as bells; an empty pool keeps none."""
    if not pool.words:
        return set()
    sing(pool.words, pool.weather, os.path.join(folder, "tide.wav"))
    return set(BELLS)


def hang(pool, folder, shore, text, when, title):
    os.makedirs(folder)
    shutil.copyfile(shore, os.path.join(folder, "shore.txt"))
    kept = set().union(*(keep_beside(shore, folder, files) for files in KEPT))
    kept |= hang_sky(folder, text, when) | hang_dial(folder, when) | hang_bells(pool, folder)
    Path(folder, "book.html").write_text(book(text), encoding="utf-8")
    Path(folder, "README.md").write_text(catalogue(title, text, kept), encoding="utf-8")
    draw(pool.words, pool.weather, os.path.join(folder, "postcard.svg"), daylight_at(when))


def exhibit(pool, words, shore, when):
    """Hang the shore as exhibits/<name>/; any words after the name become the catalogue's title."""
    name, _, title = words.partition(" ")
    folder = os.path.join(os.path.dirname(shore), "exhibits", name)
    text = read_shore(shore)
    if not EXHIBIT_NAME.fullmatch(name):
        return "Name it with lower-case letters, digits, and dashes: exhibit first-night"
    if os.path.exists(folder):
        return f"An exhibit called {name} already hangs on this coast."
    if not pages(text):
        return BARE
    hang(pool, folder, shore, text, when, title or name)
    return f"The exhibit hangs in {folder}. Its README.md is the catalogue."
