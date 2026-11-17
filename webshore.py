"""Tide Pool in a browser: one page, one line to speak into, the same sea."""

import os
import re
import shutil
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from moon import SYNODIC_DAYS, age, daylight_at
from postcard import svg
from skychart import moon
from storybook import CHART, choose_story, story_beats, story_path, walks
from shore import SHORE
from exhibits import EXHIBIT_NAME, chart_atlas, hall_title, halls
import tidepool
from tidepool import TidePool, respond, tell, welcome
from weather import WEATHER

PORT = 8000
KEEPSAKES = {"tide.wav": "audio/wav", "postcard.svg": "image/svg+xml", "sky.svg": "image/svg+xml",
             "book.html": "text/html; charset=utf-8", "recital.wav": "audio/wav",
             "signal.wav": "audio/wav", "signal.svg": "image/svg+xml", "atlas.html": "text/html; charset=utf-8",
             "jetty.svg": "image/svg+xml", "jetty.wav": "audio/wav", "crab.svg": "image/svg+xml",
             "wall.svg": "image/svg+xml",
             "tideclock.svg": "image/svg+xml", "three-rooms.html": "text/html; charset=utf-8",
             "barefoot.html": "text/html; charset=utf-8",
             "sketchbook.html": "text/html; charset=utf-8",
             "tomorrow.html": "text/html; charset=utf-8",
             "three-rows.html": "text/html; charset=utf-8",
             "same-chair.html": "text/html; charset=utf-8"}
HUNG = {**KEEPSAKES, "shore.txt": "text/plain; charset=utf-8"}
GALLERY_LINKS = (("book.html", "book"), ("postcard.svg", "postcard"), ("shore.txt", "shore"))
OPTIONAL_LINKS = (("tide.wav", "bells"), ("signal.svg", "lamp"), ("signal.wav", "Morse"), ("sky.svg", "sky"),
                  ("jetty.svg", "jetty"), ("jetty.wav", "planks"), ("crab.svg", "crab"), ("wall.svg", "wall"),
                  ("tideclock.svg", "dial"))


def paragraphs(text):
    return "".join(f"<p>{dated(line)}</p>" for line in text.splitlines())


def moon_icon(lunation):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="972 32 56 56" width="40" aria-hidden="true" '
            f'height="40">{moon(lunation)}</svg>')


def say_button(command, label):
    """A button that speaks one command into the sea, as if typed."""
    return (f'<form method="post" action="/" style="display:inline">'
            f'<button name="say" value="{escape(command)}">{escape(label)}</button></form>')


def story_buttons():
    """Charted places first, numbered as on the chart; then the walks kept off it."""
    return " ".join(say_button(f"read {target}", f"{target} {title}" if target.isdigit() else title)
                    for target, title in walks(Path(CHART).read_text(encoding="utf-8")))


QUICK = ("tide", "look", "ebb", "comb", "wade", "tidetable", "echo", "find", "horizon", "dream", "shells", "diary",
         "strandline", "stars", "listen", "postcard", "recite", "bind", "atlas", "moon",
         "almanac", "signal", "chart", "harbour", "guestbook", "help")


def sea_buttons():
    return " ".join(say_button(command, command) for command in QUICK)


def command_list():
    """The browser's answer to the terminal's Tab: every command, and each story, hall and kept day, offered as you type."""
    names = sorted((*tidepool.COMMANDS, "read"))
    names += [f"{first} {choice}" for first in ("read", "visit", "diary") for choice in sorted(tidepool.choices_after(first))]
    options = "".join(f'<option value="{escape(name)}">' for name in names)
    return f'<datalist id="commands">{options}</datalist>'


STYLE = """<style>
body { max-width: 70rem; margin: auto; }
svg, audio { display: block; max-width: 100%; }
svg { height: auto; }
audio { margin: 1rem 0; }
input { max-width: 100%; box-sizing: border-box; }
button, input { font: inherit; color: inherit; background: #0b1a24;
                 border: 1px solid #5c9392; padding: 0.3em 0.6em; }
input::placeholder { color: #a5bcb8; }
button { margin: 0.15em 0; }
button:hover, button:focus-visible { background: #28535d; }
pre { overflow-x: auto; }
</style>"""


DAY = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def dated(reply):
    """The reply as page text, each date in it a button that opens that day's page of the diary."""
    return DAY.sub(lambda day: say_button(f"diary {day[0]}", day[0]), escape(reply))


def page(command, reply, picture, sound, links, header):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tide Pool</title>{STYLE}</head>
<body style="background:#102d38;color:#ead9af;font-family:Georgia,serif;padding:2em">
<h1>Tide Pool</h1>
{header}
<form method="post" action="/"><input name="say" list="commands" autofocus size="40" aria-label="Speak to the sea" placeholder="drop moon rust lantern">{command_list()}</form>
<details><summary>Choose a walk</summary>{story_buttons()}</details>
<div>Sea: {sea_buttons()}</div>
<div>Weather: {" ".join(say_button(f"weather {name}", name) for name in WEATHER)}</div>
<p>Or type any command, such as drop moon rust lantern; read a place by its number.</p>
<p>shore&gt; {escape(command)}</p>
<pre>{dated(reply)}</pre>
{sound}
{links}
{picture}
</body></html>"""


def command_of(form):
    """The spoken command, on one line with single spaces, as the terminal would read it."""
    return " ".join(parse_qs(form).get("say", [""])[0].split())


def open_story(name, story):
    path = story_path(name)
    if not path:
        return choose_story()
    story[:] = story_beats(Path(path).read_text(encoding="utf-8"))
    return "The story opens. Press enter to begin."


def next_beat(pool, story, shore):
    told = tell(pool, story.pop(0), shore)
    return f"{told}\n\n    ~ {'press enter to continue' if story else 'the end'} ~"


def reply_to(pool, command, shore, story):
    if command.partition(" ")[0] == "read":
        return open_story(command[5:].strip(), story)
    if not command and story:
        return next_beat(pool, story, shore)
    return respond(pool, command, shore) if command else pool.look()


def sound_for(recording):
    if Path(recording).is_file():
        return '<p>Pool recording</p><audio controls src="/tide.wav"></audio>'
    return ""


SHOWN = (('The lamp flashes "', "signal.svg"), ('The lamp flashes "', "signal.wav"),
         ("as a night sky", "sky.svg"), ("hear the shore read aloud", "recital.wav"),
         ("See the jetty in", "jetty.svg"), ("Hear it walked in", "jetty.wav"),
         ("See the crab in", "crab.svg"), ("See the dial in", "tideclock.svg"), ("See the wall in", "wall.svg"))


HEARD = {"signal.wav": "The lamp in Morse", "recital.wav": "The shore read aloud",
         "jetty.wav": "The jetty walked"}


def shown(folder, name):
    """A drawing inline, or a recording as a captioned player like the pool's."""
    if name in HEARD:
        return f'<p>{HEARD[name]}</p><audio controls src="/{name}"></audio>'
    return Path(folder, name).read_text(encoding="utf-8")


def shown_for(reply, folder):
    """Render the matching keepsakes for a reply."""
    return "".join(shown(folder, name) for marker, name in SHOWN
                   if marker in reply and Path(folder, name).is_file())


def keepsakes(folder):
    """Links to every keepsake lying beside the shore, except the pool recording, which plays above."""
    names = [name for name in KEEPSAKES
             if name != "tide.wav" and os.path.isfile(os.path.join(folder, name))]
    if not names:
        return ""
    links = " · ".join(f'<a href="/{name}" style="color:#ead9af">{name}</a>' for name in names)
    return f"<p>Keepsakes: {links}</p>"


def drawings(folder):
    """Original SVG drawings, apart from the hall's generated keepsakes."""
    return sorted(path.name for path in Path(folder).glob("*.svg")
                  if path.is_file() and path.name not in HUNG and EXHIBIT_NAME.fullmatch(path.stem))


def exhibit_row(hall, name):
    files = list(GALLERY_LINKS)
    files.extend((file, label) for file, label in OPTIONAL_LINKS
                 if os.path.isfile(os.path.join(hall, name, file)))
    files.extend((file, file[:-4].replace("-", " ")) for file in drawings(os.path.join(hall, name)))
    links = " · ".join(f'<a href="/exhibits/{name}/{file}" style="color:#ead9af">{label}</a>'
                       for file, label in files)
    title = escape(hall_title(hall, name))
    return f"<li>{title} {say_button(f'visit {name}', 'visit')}: {links}</li>"


def gallery(hall):
    """The halls folded under one line that opens to the list, so the page stays short."""
    names = halls(hall)
    rows = "".join(exhibit_row(hall, name) for name in names)
    summary = f"Exhibits: {tidepool.count(len(names), 'hall')}"
    return f"<details><summary>{summary}</summary><ul>{rows}</ul></details>" if rows else ""


def served(folder, path):
    parts = path.split("/")[1:]
    if len(parts) == 1 and parts[0] in KEEPSAKES:
        return os.path.join(folder, parts[0]), KEEPSAKES[parts[0]]
    if len(parts) == 3 and parts[0] == "exhibits" and EXHIBIT_NAME.fullmatch(parts[1]):
        kind = HUNG.get(parts[2])
        if not kind and parts[2] in drawings(os.path.join(folder, *parts[:2])):
            kind = "image/svg+xml"
        if kind:
            return os.path.join(folder, *parts), kind
    return "", ""


def show(shore):
    now = tidepool.now()
    picture = svg(shore.pool.words, shore.pool.weather, daylight_at(now))
    onward = say_button("", "continue the story") if shore.story else ""
    recording = sound_for(os.path.join(shore.folder, "tide.wav"))
    sound = onward + recording + shown_for(shore.last[1], shore.folder)
    links = keepsakes(shore.folder) + gallery(os.path.join(shore.folder, "exhibits"))
    header = moon_icon(age(now) / SYNODIC_DAYS) + paragraphs(welcome(now, shore.shore))
    if Path(shore.folder, "three-rooms.html").is_file():
        header += '<p><a href="/three-rooms.html" style="color:inherit">Begin with three rooms.</a></p>'
    return page(shore.last[0], shore.last[1], picture, sound, links, header).encode("utf-8")


def fetched(shore, path):
    """The body and content type the shore answers a path with; None where it keeps nothing."""
    if path == "/atlas.html":
        chart_atlas(shore.shore)
    file, kind = served(shore.folder, path)
    if os.path.isfile(file):
        return Path(file).read_bytes(), kind
    if path == "/":
        return show(shore), "text/html; charset=utf-8"
    return None


def heard(shore, form):
    """Speak a posted form's command into the shore, keeping the exchange for the next page."""
    command = command_of(form)
    shore.last[:] = [command, reply_to(shore.pool, command, shore.shore, shore.story)]


HELD = ("shore.txt", "sea.txt", "guestbook.txt")


def keep(folder, kept, shipped):
    """Copy the visitor's poems, bottles, signatures, and the halls they hung beyond `shipped` into `kept`."""
    for name in HELD:
        shutil.copy(os.path.join(folder, name), kept)
    hall = os.path.join(folder, "exhibits")
    for name in set(halls(hall)) - set(shipped):
        shutil.copytree(os.path.join(hall, name), os.path.join(kept, "exhibits", name), dirs_exist_ok=True)


def restore(kept, folder):
    """Lay what a visitor kept back over the coast."""
    shutil.copytree(kept, folder, dirs_exist_ok=True)


class ShoreHandler(BaseHTTPRequestHandler):
    """Answers the browser. Each server's subclass, made by handler(), carries its own
    pool, shore, folder, open story, and last exchange as class attributes."""

    pool: TidePool
    shore: str
    folder: str
    story: list
    last: list

    def do_GET(self):
        found = fetched(self, urlparse(self.path).path)
        if found:
            self.send(*found)
        else:
            self.send(b"", "text/plain", 404)

    def do_POST(self):
        heard(self, self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def send(self, body, kind, status=200):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def handler(pool, shore):
    state = {"pool": pool, "shore": shore, "folder": os.path.dirname(shore),
             "story": [], "last": ["", pool.look()]}
    return type("Shore", (ShoreHandler,), state)


def serve():
    server = HTTPServer(("127.0.0.1", PORT), handler(TidePool(), SHORE))
    print(f"Tide Pool is open at http://127.0.0.1:{PORT}/")
    server.serve_forever()


if __name__ == "__main__":
    serve()
