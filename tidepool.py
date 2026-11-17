"""A little sea for words. Run with Python 3; no dependencies."""

import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from moon import SYNODIC_DAYS, age, daylight_at, next_water, part_of_day, phase, tidal_range, turn_of, water
from seaglass import recite, sing
from postcard import draw
from hermit import portrait
from bindery import UNDATED, book, diary, pages
from drift import drift
from dial import dial
from guestbook import entry, sign, signatures
from jetty import jetty, walk
from tidewall import tidewall
from lamp import light, signal_lines, sound
from skychart import chart_sky
from exhibits import chart_atlas, exhibit, hall_title, halls
from storybook import CHART, STORY_DIR, chart_places, chart_text, choose_story, stories, story_beats, story_path
from shore import (BARE, SHORE, shore_text, acrostic, answer, crab_home, gaps, held_pages, initials, remembering, rhymes, brightest, cast_bottle, drifting, heaps, kindred, meets,
                   kept_pages, read_shore, shell, shore_lines, take_bottle, things, traces, wash_ashore, wrack)
from weather import WEATHER, choices


class TidePool:
    def __init__(self):
        self.words = []
        self.tides = 0
        self.weather = "calm"
        self.cast = []

    def drop(self, phrase):
        self.words.extend(phrase.split())

    def ebb(self):
        if not self.words:
            return "Only water leaves the empty pool."
        word = self.words.pop(random.randrange(len(self.words)))
        return f"The water carries away {word}.\n{self.look()}"

    def look(self):
        if not self.words:
            return "    ~ an empty sea, waiting for a word ~"
        return "\n".join(" " * (4 + (i * 7 + self.tides * 3) % 24) + word
                         for i, word in enumerate(self.words))

    def tide(self):
        self.tides += 1
        if len(self.words) < 2:
            return "The water rises. It needs two words to make a meeting."
        random.shuffle(self.words)
        bridges = WEATHER[self.weather]
        lines = [f"{a} {random.choice(bridges)} {b}"
                 for a, b in zip(self.words[::2], self.words[1::2])]
        if len(self.words) % 2:
            lines.append(f"and {self.words[-1]} listens")
        return "\n".join(lines)


def now():
    return datetime.now(timezone.utc)


def day_of(when):
    return f"{when:%Y-%m-%d}"


def next_tide(shore):
    """The number the next shell takes: one past every poem the shore keeps."""
    return len(kept_pages(shore)) + 1


def tide_and_wash(pool, shore, day):
    poem = pool.tide()
    if len(pool.words) >= 2:
        wash_ashore(shore, shell(next_tide(shore), poem, day))
    return poem


def is_spring(when):
    return tidal_range(when) >= 8


def spring_tide(pool, shore, when):
    """A tide; and at spring tides, when the real moon pulls hardest, a shell washes back in."""
    poem = tide_and_wash(pool, shore, day_of(when))
    if not is_spring(when) or len(pool.words) < 2:
        return poem
    return f"{poem}\n\n{pick_up(pool, random.choice(shore_lines(shore)), 'The spring tide brings a shell in')}"


def pick_up(pool, line, finding):
    pool.drop(line)
    return f'{finding}: "{line}"\n{pool.look()}'


def comb(pool, shore):
    lines = shore_lines(shore)
    if not lines:
        return BARE
    return pick_up(pool, random.choice(lines), "You find a shell")


def water_note(when):
    """The water now, and when low water comes for wading."""
    if water(when) == "low water":
        return "The water is low water: wade out now."
    return f"The water is {water(when)}. Low water comes at {next_water(when, 'low water'):%H:%M} UTC."


def wade(pool, shore, when):
    """At low water, wade out to the oldest shell and bring its line into the pool."""
    if water(when) != "low water":
        return water_note(when)
    lines = shore_lines(shore)
    if not lines:
        return BARE
    return pick_up(pool, lines[0], "At low water you wade out to the oldest shell")


def water_times(when):
    """The water now, and when each state comes next, by the coast's own reckoning (UTC)."""
    rows = sorted((next_water(when, state), state) for state in ("high water", "falling", "low water", "rising")
                  if water(when) != state)
    times = "\n".join(f"  {at:%H:%M}  {state}" for at, state in rows)
    return f"The water is {water(when)} now. Next (UTC):\n{times}"


def tidetable(when, shore):
    path = os.path.join(os.path.dirname(shore), "tideclock.svg")
    Path(path).write_text(dial(turn_of(when), water(when)), encoding="utf-8")
    return f"{water_times(when)}\nSee the dial in {path}."


def echo(pool, shore):
    lines = shore_lines(shore)
    if not lines:
        return BARE
    return pick_up(pool, lines[-1], "The sea's last words come back")


def visit(pool, words, shore):
    """Pick up a thread from a hung exhibit: its last line comes into today's pool.
    Only the first word names the hall, so a row copied from `tour` still finds it."""
    name = words.partition(" ")[0]
    hall = os.path.join(os.path.dirname(shore), "exhibits")
    if name not in halls(hall):
        names = ", ".join(halls(hall))
        return f"Visit one of the halls: {names}." if names else "No exhibit hangs on this coast yet."
    lines = shore_lines(os.path.join(hall, name, "shore.txt"))
    return pick_up(pool, lines[-1], f"In {hall_name(hall, name)}, the sea's last words were")


def tour(word, shore):
    """Follow a word through the gallery: every hall whose kept shore remembers it."""
    if not word:
        return "Name a word to follow through the halls: tour lamp"
    hall = os.path.join(os.path.dirname(shore), "exhibits")
    shores = {name: read_shore(os.path.join(hall, name, "shore.txt")) for name in halls(hall)}
    found = remembering(word, shores)
    if not found:
        return f"No hall remembers {word}."
    rows = "\n".join(f"  {hall_name(hall, name)}: {count(lines, 'line')}" for name, lines in found)
    return f"{word} is remembered in {count(len(found), 'hall')}:\n{rows}"


def hall_name(hall, name):
    """A hall as `visit` knows it, with its catalogue's title when that says more."""
    title = hall_title(hall, name)
    return name if title == name else f"{name} ({title})"


def stars(shore):
    counts = brightest(shore_text(shore))
    if not counts:
        return "No stars yet. The sky is drawn from what the shore remembers."
    path = os.path.join(os.path.dirname(shore), "sky.svg")
    chart_sky(counts, age(now()) / SYNODIC_DAYS, path)
    return f"Open {path} to see the shore's words as a night sky."


def spell(word, shore):
    if not word:
        return "Name a word to spell from the shore: spell home"
    spelled = acrostic(word, shore_lines(shore))
    drawing = os.path.join(os.path.dirname(shore), "jetty.svg")
    Path(drawing).write_text(jetty(word, spelled), encoding="utf-8")
    steps = os.path.join(os.path.dirname(shore), "jetty.wav")
    walk(word, spelled, steps)
    missing = gaps(word, spelled)
    waiting = [f"Planks still missing: {', '.join(missing)}."] if missing else []
    return "\n".join([*spelled, *waiting, f"See the jetty in {drawing}.", f"Hear it walked in {steps}."])


def letters(shore):
    """Which letters remembered lines begin with, and how many, then the letters no line begins with yet."""
    counts = initials(shore_lines(shore))
    if not counts:
        return BARE
    begun = " · ".join(f"{letter} {counts[letter]}" for letter in sorted(counts))
    missing = " ".join(letter for letter in "abcdefghijklmnopqrstuvwxyz" if letter not in counts)
    return f"Lines begin with: {begun}\nNo line begins with: {missing}" if missing else f"Lines begin with: {begun}"


def rhyme(word, shore):
    if not word:
        return "Name a word to rhyme: rhyme home"
    found = rhymes(word, shore_lines(shore))
    return "\n".join(found) if found else f"Nothing on the shore rhymes with {word} yet."


def trace(word, shore):
    if not word:
        return "Name a word to trace: trace lantern"
    lines = traces(word, shore_text(shore))
    if not lines:
        return f"The shore has no memory of {word}."
    return f"{word} has washed up in {count(len(lines), 'line')}:\n" + "\n".join(lines)


END = {"first": 0, "last": -1}


def washed_up(word, end, shore):
    """Where `word` washed up first or last: the tide, the day, the poems kept since, and the line."""
    if not word:
        return f"Name a word to look back for: {end} lantern"
    held = held_pages(word, kept_pages(shore))
    if not held:
        return f"The shore has no memory of {word}."
    tide, day, lines, since = held[END[end]]
    return f"{word} {end} washed up on tide {tide} · {day or UNDATED}; {kept_since(since)}:\n{lines[END[end]]}"


def most_remembered(shore):
    """The shore's most remembered word without its punctuation, or "" on a bare shore."""
    home = crab_home(shore_text(shore))
    return home[0].strip("?!.,;:") if home else ""


def wall(word, shore):
    """The harbour wall for `word`, or for the shore's most remembered word when none is named."""
    word = word or most_remembered(shore)
    kept = kept_pages(shore)
    held = held_pages(word, kept) if word else []
    if not held:
        return f"The shore has no memory of {word}." if word else BARE
    drawing = os.path.join(os.path.dirname(shore), "wall.svg")
    Path(drawing).write_text(tidewall(word, held, len(kept)), encoding="utf-8")
    return f"{word} has marked the harbour wall {count(len(held), 'time')}.\nSee the wall in {drawing}."


def kept_since(since):
    return f"{count(since, 'poem')} kept since" if since else "the newest poem"


def ask(question, shore):
    if not question:
        return "Ask the sea something: ask where is the lantern"
    line = answer(question, shore_text(shore))
    if not line:
        return "The sea has no answer yet. Drop your words in and let a tide make one."
    return f"The sea answers: {line}"


def signal(words, shore):
    lines = shore_lines(shore)
    text = words or (lines[-1] if lines else "")
    if not text:
        return "Nothing to signal yet. Try: signal fog on the rocks"
    flashed = "\n".join(signal_lines(text))
    if not flashed:
        return "The lamp needs letters A–Z or digits 0–9."
    path = os.path.join(os.path.dirname(shore), "signal.wav")
    sound(text, path)
    drawing = os.path.join(os.path.dirname(shore), "signal.svg")
    Path(drawing).write_text(light(text), encoding="utf-8")
    return f'The lamp flashes "{text}":\n{flashed}\nHear it in {path}.\nWatch it in {drawing}.'


def kin(word, shore):
    if not word:
        return "Name a word to find its kin: kin window"
    company = kindred(word, shore_text(shore))
    if not company:
        return f"{word} has no kin on this shore yet."
    return f"{word} keeps company with:\n{heaps(company)}"


def seek(pool, arg, shore):
    first, _, second = arg.partition(" ")
    if not second or first not in pool.words or second not in pool.words:
        return "Seek two words already in the water: seek moon lantern"
    for turn in range(1, 13):
        poem = pool.tide()
        if meets(poem, first, second):
            wash_ashore(shore, shell(next_tide(shore), poem, day_of(now())))
            return f"After {count(turn, 'tide')}, {first} met {second}:\n{poem}"
    return f"Twelve tides passed. {first} and {second} never met."


def recital(shore):
    lines = shore_lines(shore)
    if not lines:
        return BARE
    path = os.path.join(os.path.dirname(shore), "recital.wav")
    recite(lines, path)
    return f"Open {path} to hear the shore read aloud in bells, {count(len(lines), 'line')} long."


def shore_diary(day, shore):
    if not day:
        return diary(read_shore(shore)) or BARE
    day = {"today": day_of(now()), "yesterday": day_of(now() - timedelta(days=1))}.get(day, day)
    kept = [shell(tide, poem, kept_on).rstrip() for tide, kept_on, poem in kept_pages(shore) if kept_on == day]
    return "\n\n".join(kept) or f"No poems are dated {day}. Type diary to see the days."


def shells(count, shore):
    if not count:
        return read_shore(shore)
    if not count.isdigit() or int(count) == 0:
        return "Count shells with a number: shells 3"
    recent = kept_pages(shore)[-int(count):]
    if not recent:
        return read_shore(shore)
    return "\n\n".join(shell(tide, poem, day).rstrip() for tide, day, poem in recent)


def strandline(shore):
    if not os.path.exists(shore):
        return read_shore(shore)
    return wrack(read_shore(shore))


def crab(shore):
    home = crab_home(shore_text(shore))
    if not home:
        return "No shell on the shore is big enough for a hermit crab yet."
    word, line = home
    path = os.path.join(os.path.dirname(shore), "crab.svg")
    Path(path).write_text(portrait(word, line), encoding="utf-8")
    return (f'A hermit crab lives in the newest line that holds "{word}", the shore\'s most remembered word:\n{line}'
            f'\nSee the crab in {path}.')


def count(number, noun):
    return f"{number} {noun}{'' if number == 1 else 's'}"


def shore_note(kept, day):
    """The report's line for the poems: how many, how many kept today, and the newest tide."""
    if not kept:
        return "0 poems on the shore"
    today = sum(1 for _, kept_on, _ in kept if kept_on == day)
    return f"{count(len(kept), 'poem')} on the shore, {today} today, tide {kept[-1][0]} the newest"


def harbour(shore, when):
    """The harbourmaster's report: everything the coast holds right now, at a glance."""
    text = shore_text(shore)
    kept, home = pages(text), crab_home(text)
    places = chart_places(Path(CHART).read_text(encoding="utf-8"))
    return "\n".join([
        "The harbourmaster's report:",
        shore_note(kept, day_of(when)),
        count(len(drifting(sea_of(shore))), "bottle") + " at sea",
        count(len(halls(os.path.join(os.path.dirname(shore), "exhibits"))), "hall") + " in the gallery",
        count(len(signatures(book_of(shore))), "signature") + " in the guestbook",
        f"{count(len(places), 'place')} on the chart, {count(len(stories(STORY_DIR)), 'walk')} on the shelf",
        f'The crab lives by "{home[0]}".' if home else "No crab has moved in yet.",
        water_note(when)])


def dream_once(pool, shore, weather):
    pool.weather = weather
    poem = tide_and_wash(pool, shore, day_of(now()))
    comb(pool, shore)
    return f"~ {weather} ~\n{poem}"


def dream(pool, shore):
    if len(pool.words) < 2:
        return "The sea needs two pieces before it can dream."
    nights = [dream_once(pool, shore, weather)
              for weather in random.sample(list(WEATHER), len(WEATHER))]
    return "\n\n".join(nights) + f"\n\nYou wake to {pool.weather} water."


def change_weather(pool, choice):
    if choice in WEATHER:
        pool.weather = choice
        return f"The weather turns to {choice}."
    if choice:
        return f"Choose weather {choices()}."
    return f"The sea's weather is {pool.weather}. Choose {choices()}."


def drop_and_look(pool, phrase):
    if not phrase:
        return "Drop some words: drop moon rust lantern"
    pool.drop(phrase)
    return pool.look()


def ebb(pool, arg):
    if arg != "all" or not pool.words:
        return pool.ebb()
    count = len(pool.words)
    pool.words.clear()
    carried = "the only piece" if count == 1 else f"all {count} pieces"
    return f"The low tide carries {carried} away. The shore keeps their poems."


def bottle(pool, phrase):
    if not phrase:
        return "Try: bottle the room we left behind"
    pool.words.append(phrase)
    return pool.look()


def sea_of(shore):
    return os.path.join(os.path.dirname(shore), "sea.txt")


def book_of(shore):
    return os.path.join(os.path.dirname(shore), "guestbook.txt")


def sign_book(name, shore, day):
    if not name:
        return "Sign with a name: sign Alice"
    sign(book_of(shore), name, day)
    return f"The guestbook keeps your name: {entry(name, day)}"


def guestbook(shore):
    names = signatures(book_of(shore))
    if not names:
        return "The guestbook is open and empty. Type sign and your name."
    return f"The guestbook holds {count(len(names), 'signature')}:\n" + "\n".join(f"  {line}" for line in names)


def cast(pool, phrase, shore):
    if not phrase:
        return "Cast a message: cast the light is still on"
    pool.cast.append(cast_bottle(sea_of(shore), phrase))
    return "The bottle drifts out to sea. Someone may find it on another day."


def find(pool, shore):
    found = take_bottle(sea_of(shore), pool.cast)
    if not found:
        return "No bottle has drifted in. Cast one for the next keeper: cast the light is still on"
    pool.words.append(found)
    return f'A bottle washes up: "{found}"\n{pool.look()}'


def horizon(pool, shore):
    bottles = drifting(sea_of(shore))
    if not bottles:
        return "No bottle drifts at sea."
    yours = sum(identity in pool.cast for identity in bottles)
    drift = "bottle drifts" if len(bottles) == 1 else "bottles drift"
    return f"{len(bottles)} {drift} at sea; {yours} cast by you this visit."


def listen(pool, shore):
    if not pool.words:
        return "The empty pool is silent. Drop a word first."
    path = os.path.join(os.path.dirname(shore), "tide.wav")
    sing(pool.words, pool.weather, path)
    return f"Open {path} to hear the pool."


def postcard(pool, shore):
    path = os.path.join(os.path.dirname(shore), "postcard.svg")
    draw(pool.words, pool.weather, path, daylight_at(now()))
    return f"Open {path} to see the pool."


def bind(shore):
    text = read_shore(shore)
    if not pages(text):
        return BARE
    path = os.path.join(os.path.dirname(shore), "book.html")
    with open(path, "w", encoding="utf-8") as bound:
        bound.write(book(text))
    return f"Open {path} to read the shore as a book."


def moonrise(pool, when):
    name = phase(when)
    pool.drop(name)
    return f"The {name} rises. Its name drifts into the water.\n{pool.look()}"


def low_water_on(day, now):
    """The next low water on `day` still to come after `now`, as HH:MM UTC, or "none left"."""
    at = next_water(max(now, day.replace(hour=0, minute=0)), "low water")
    return f"{at:%H:%M}" if at.date() == day.date() else "none left"


def almanac(today):
    days = [today + timedelta(days=n) for n in range(7)]
    chart = "\n".join(f"{day:%a %d}  {'~' * (1 + tidal_range(day)):<10}{phase(day):<16}"
                      f"low water {low_water_on(day, today)}"
                      for day in days)
    return (chart + "\n\n~~~~~~~~~ = spring tide; 'tide' also brings a shore line back into the pool."
            "\nlow water = the next still to come that day, in UTC; 'wade' reaches the oldest shell then.")


def tonight(when):
    spring = " · spring tide" if is_spring(when) else ""
    return f"{part_of_day(when)}: {phase(when)} · tides {'~' * (1 + tidal_range(when))} · {water(when)}{spring}"


def last_words(shore):
    kept = kept_pages(shore)
    if not kept:
        return []
    _, day, poem = kept[-1]
    said = f"The sea last said, on {day}:" if day else "The sea last said:"
    return [f"{said} {poem.splitlines()[-1]}"]


def new_page(when, shore):
    """A line inviting the day's first poem, once the shore has poems but none from today."""
    kept = kept_pages(shore)
    if not kept or kept[-1][1] == day_of(when):
        return []
    return ["No poem has been kept today yet; yours would open a new page in the diary."]


def offshore(shore):
    bottles = len(drifting(sea_of(shore)))
    if not bottles:
        return []
    return ["A bottle drifts offshore. Type find to bring it in." if bottles == 1
            else f"{bottles} bottles drift offshore. Type find to bring the oldest in."]


def wading(when):
    """At low water, the greeting's hint that the oldest shell is within reach."""
    return ["The water is low. Type wade to reach the oldest shell."] if water(when) == "low water" else []


def welcome(when, shore):
    return "\n".join([tonight(when), *last_words(shore), *new_page(when, shore), *offshore(shore), *wading(when)])


HELP = """drop <words>       Scatter words into the water.
bottle <phrase>    Keep a phrase together.
cast <message>     Throw a sealed message out to sea for someone to find another day.
find               Bring in the oldest bottle still drifting, whole, into the pool.
horizon            Count the bottles drifting at sea, and how many you cast.
look               See the pool.
tide               Make a poem and leave it on the shore; spring tides wash a shell back in.
ebb [all]          Let one piece drift away, or let the low tide take them all.
weather            See the weather; choose calm, storm, fog, or ice.
shells [n]         Read the shore's poems, or only the newest n.
diary [day]        See how many poems each day left, or one day's: diary today, diary yesterday
comb               Bring an old line back into the pool.
wade               At low water, wade out to the oldest shell and bring its line into the pool.
tidetable          See the water now, when each state comes next, and the dial as tideclock.svg.
echo               Bring back the last line the sea said.
visit <hall>       Bring an exhibit's last line into today's pool, to carry its thread on.
strandline         See which words the shore remembers most.
crab               Find the resident's remembered home and draw crab.svg.
harbour            Read the harbourmaster's report: everything the coast holds, and the water.
sign <name>        Sign the guestbook with your name and today's date.
guestbook          Read every signature in the guestbook.
moon               Drop the moon's phase name into the pool.
almanac            See a week of lunar wave patterns.
listen             Record the pool as tide.wav.
postcard           Draw the pool as postcard.svg.
bind               Bind the shore's poems into book.html.
exhibit <name>     Hang the shore in exhibits/<name>/; words after it title it: exhibit dusk At dusk
dream              Leave the sea alone overnight: one tide in every weather.
stars              Draw the shore's most remembered words as sky.svg.
trace <word>       Follow one word through every poem on the shore.
first <word>       See the tide and day a word first washed up on the shore.
last <word>        See the tide and day a word last washed up on the shore.
wall [word]        Paint a word's marks on the harbour wall in wall.svg; alone, the top word.
tour <word>        Follow one word through the gallery: which halls remember it, in how many lines.
spell <word>       Lay a word as planks of remembered lines: drawn in jetty.svg, walked in jetty.wav
letters            See which letters remembered lines begin with, for spelling, and which none do.
rhyme <word>       Find remembered lines that end with the word's sound.
ask <question>     The sea answers with the shore line that shares most with your question.
signal [words]     Flash and sound words, or the sea's last line, in Morse.
kin <word>         See which words have shared a line with this one most.
seek <a> <b>       Let the tides turn until two words meet in one line.
recite             Hear every poem on the shore as bells in recital.wav.
atlas              Gather the chart, every story, and the exhibits in atlas.html.
help [command]     Read this guide, or only one command's line: help wade
chart              See the coast map and the number that opens each place.
read <place>       Walk a story into this pool, by name or chart number.
drift              Watch the pool float on a moving sea; any key returns (terminal only).
quit               Leave the terminal pool.

Change the water with: weather fog"""


COMMANDS = {
    "chart": lambda pool, arg, shore: chart_text(Path(CHART).read_text(encoding="utf-8")),
    "help": lambda pool, arg, shore: help_for(arg) if arg else HELP,
    "bottle": lambda pool, arg, shore: bottle(pool, arg),
    "cast": lambda pool, arg, shore: cast(pool, arg, shore),
    "find": lambda pool, arg, shore: find(pool, shore),
    "horizon": lambda pool, arg, shore: horizon(pool, shore),
    "postcard": lambda pool, arg, shore: postcard(pool, shore),
    "bind": lambda pool, arg, shore: bind(shore),
    "exhibit": lambda pool, arg, shore: exhibit(pool, arg, shore, now()),
    "dream": lambda pool, arg, shore: dream(pool, shore),
    "stars": lambda pool, arg, shore: stars(shore),
    "trace": lambda pool, arg, shore: trace(arg, shore),
    "first": lambda pool, arg, shore: washed_up(arg, "first", shore),
    "last": lambda pool, arg, shore: washed_up(arg, "last", shore),
    "wall": lambda pool, arg, shore: wall(arg, shore),
    "tour": lambda pool, arg, shore: tour(arg, shore),
    "spell": lambda pool, arg, shore: spell(arg, shore),
    "letters": lambda pool, arg, shore: letters(shore),
    "rhyme": lambda pool, arg, shore: rhyme(arg, shore),
    "ask": lambda pool, arg, shore: ask(arg, shore),
    "signal": lambda pool, arg, shore: signal(arg, shore),
    "seek": lambda pool, arg, shore: seek(pool, arg, shore),
    "kin": lambda pool, arg, shore: kin(arg, shore),
    "recite": lambda pool, arg, shore: recital(shore),
    "atlas": lambda pool, arg, shore: chart_atlas(shore),
    "almanac": lambda pool, arg, shore: almanac(now()),
    "moon": lambda pool, arg, shore: moonrise(pool, now()),
    "listen": lambda pool, arg, shore: listen(pool, shore),
    "drop": lambda pool, arg, shore: drop_and_look(pool, arg),
    "look": lambda pool, arg, shore: pool.look(),
    "tide": lambda pool, arg, shore: spring_tide(pool, shore, now()),
    "ebb": lambda pool, arg, shore: ebb(pool, arg),
    "weather": lambda pool, arg, shore: change_weather(pool, arg),
    "shells": lambda pool, arg, shore: shells(arg, shore),
    "diary": lambda pool, arg, shore: shore_diary(arg, shore),
    "comb": lambda pool, arg, shore: comb(pool, shore),
    "wade": lambda pool, arg, shore: wade(pool, shore, now()),
    "tidetable": lambda pool, arg, shore: tidetable(now(), shore),
    "echo": lambda pool, arg, shore: echo(pool, shore),
    "visit": lambda pool, arg, shore: visit(pool, arg, shore),
    "strandline": lambda pool, arg, shore: strandline(shore),
    "crab": lambda pool, arg, shore: crab(shore),
    "harbour": lambda pool, arg, shore: harbour(shore, now()),
    "sign": lambda pool, arg, shore: sign_book(arg, shore, day_of(now())),
    "guestbook": lambda pool, arg, shore: guestbook(shore),
    "quit": lambda pool, arg, shore: "The sea keeps its silence.",
}


def help_for(name):
    """Only the guide's line for one command."""
    lines = [line for line in HELP.splitlines() if line.split(" ", 1)[0] == name]
    return "\n".join(lines) if lines else f"No command is called {name}. Type help for all of them."


def respond(pool, command, shore):
    name, _, arg = command.partition(" ")
    if name not in COMMANDS:
        return HELP
    return COMMANDS[name](pool, arg.strip(), shore)


def main():
    pool = TidePool()
    print("TIDE POOL\nDrop words into the water. Each tide makes a new poem.")
    print(welcome(now(), SHORE))
    print("Try: drop moon rust lantern, then tide. Type help for all commands.\n")
    while True:
        try:
            command = input("shore> ").strip()
        except (EOFError, KeyboardInterrupt):
            command = "quit"
            print()
        if aside(pool, command):
            continue
        print(respond(pool, command, SHORE))
        if command == "quit":
            break


def aside(pool, command):
    """The terminal's own commands, which the browser cannot offer. True when one was handled."""
    if command.partition(" ")[0] == "read":
        read_story(pool, command[5:].strip())
    elif command == "drift":
        watch_drift(pool)
    else:
        return False
    return True


def watch_drift(pool):
    if not sys.stdout.isatty():
        print("Drift needs a terminal window to move in.")
        return
    drift(pool.words, pool.weather)


def tell(pool, beat, shore):
    kind, body = beat
    if kind == "story":
        return body
    return "\n".join(f"shore> {command}\n{respond(pool, command, shore)}"
                     for command in body)


def pause(pool):
    while True:
        try:
            answer = input("    ~ enter to continue / sea command / q to leave ~ ").strip()
        except (EOFError, KeyboardInterrupt):
            answer = "q"
            print()
        if answer.lower() in ("q", "quit"):
            print(respond(pool, "quit", SHORE))
            return False
        if not answer:
            return True
        print(respond(pool, answer, SHORE))


def play_story(path, pool):
    with open(path) as story:
        beats = story_beats(story.read())
    for beat in beats:
        print(tell(pool, beat, SHORE) + "\n")
        if not pause(pool):
            return


def read_story(pool, name):
    path = story_path(name)
    if path:
        play_story(path, pool)
    else:
        print(choose_story())


TYPED = (*COMMANDS, "read", "drift")
WORDED = ("trace", "first", "last", "wall", "kin", "seek", "tour", "rhyme", "spell")


def choices_after(first, shore=SHORE):
    """What may follow a command's name: a story, a hall, a command, a word the shore remembers, or a kept day."""
    if first == "read":
        return stories(STORY_DIR)
    if first == "visit":
        return halls(os.path.join(os.path.dirname(shore), "exhibits"))
    if first in WORDED:
        return things("\n".join(shore_lines(shore)))
    if first == "diary":
        return {"today", "yesterday"} | {day for _, day, _ in kept_pages(shore) if day}
    return TYPED if first == "help" else ()


def completions(line, text):
    """What the word being typed (`text`) may become, given the whole `line` so far."""
    first, space, _ = line.lstrip().partition(" ")
    names = choices_after(first) if space else TYPED
    return sorted(name for name in names if name.startswith(text))


def complete(line, text, state):
    """readline's completer, given the line: the state-th completion of `text`, then None."""
    found = completions(line, text)
    return found[state] if state < len(found) else None


def enable_editing():
    """Line editing and arrow-key history for input(), and Tab completing whatever choices_after offers."""
    import readline
    readline.set_completer(lambda text, state: complete(readline.get_line_buffer(), text, state))
    readline.set_completer_delims(" ")
    readline.parse_and_bind("bind ^I rl_complete" if readline.backend == "editline" else "tab: complete")


if __name__ == "__main__":
    enable_editing()
    if len(sys.argv) > 1:
        play_story(sys.argv[1], TidePool())
    else:
        main()
