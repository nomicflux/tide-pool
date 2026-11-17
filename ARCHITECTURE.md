# How the coast is built

Tide Pool is plain Python 3 with no dependencies. Every module has a test file
beside it (`test_<module>.py`); run them all with `python3 -m unittest`.

## The modules

Leaves (they import nothing from the coast):

| Module | Keeps |
| --- | --- |
| `weather.py` | The weathers and their bridges; `BRIDGE_WORDS`; `choices()`. |
| `moon.py` | The sky clock: tonight's phase, the moon's age, the tidal range, the twice-daily water (`water`), and the part of the day (`part_of_day`, `daylight_at`). |
| `seaglass.py` | Sound: bells over surf, tones, rests, and writing `.wav` files. |
| `postcard.py` | The pool drawn as an SVG sea, with day and night palettes. |
| `dial.py` | The twice-daily water as a clock face, its needle at the present turn. |
| `guestbook.py` | The guestbook beside the shore: one dated line per signature. |
| `hermit.py` | The resident crab and its remembered address, drawn as SVG. |
| `skychart.py` | The shore's remembered words as a starry SVG, with tonight's moon. |
| `bindery.py` | The shore split into pages and bound as an HTML book. |
| `drift.py` | The pool floating live on a moving sea in the terminal (curses). |
| `storybook.py` | Story beats, the shelf in `stories/`, and the chart's numbered places. |

Built on those:

| Module | Keeps | Imports |
| --- | --- | --- |
| `shore.py` | `shore.txt` itself, and the ways of reading it (heaps, traces, kin). | bindery (its HEADER and pages), weather |
| `lamp.py` | Morse code, flashed as text and sounded as tones. | seaglass |
| `jetty.py` | A spelled word as SVG planks over water, and walked as chimes with silent steps; a gap (`shore.is_gap`) where the shore has no line. | seaglass, shore |
| `tidewall.py` | A word's marks on the harbour wall as SVG: one per kept poem holding it, the oldest lowest, the lowest and highest named. | none |
| `atlas.py` | The whole coast as one HTML page. | storybook |
| `exhibits.py` | Hanging a shore as an exhibit (catalogue, the pool's bells if it holds words, kept signal, jetty, its planks, crab and wall, fresh sky and dial), the halls, and the atlas file. | atlas, bindery, dial, moon, postcard, seaglass, shore, skychart, storybook |
| `tidepool.py` | The pool, every command, `HELP`, and the terminal. | all of the above except atlas, which it reaches through exhibits |
| `webshore.py` | The browser: one page, buttons, keepsakes, the gallery, stories by number, every date a door to its diary page, and an atlas bound fresh when opened. | tidepool, exhibits, shore, storybook, moon, postcard, skychart, weather |

Imports only point down this list, so nothing is circular.

`index.html` runs `webshore` without a server, in the visitor's browser under
Pyodide: it answers links with `fetched`, forms with `heard`, and after each
command `keep`s the shore, bottles, guestbook and new halls in the browser's
IndexedDB, which `restore` lays back on the next visit.
`.github/workflows/pages.yml` publishes it to GitHub Pages on every push to
`main`, with the coast zipped beside it as `coast.zip`.

## The shore's format

`shore.txt` is a sequence of shells: a `~ tide N · YYYY-MM-DD ~` line (the UTC
day the tide was made; shells from before the shore kept dates have only
`~ tide N ~`), the poem's lines, and a blank line. A new shell is numbered
one past the poems already on the shore (`next_tide`), so numbers run along
the whole shore across sessions. Shells written before that carry their
session's own count, so the live shore's first 27 are mostly tide 1. `shore.py` writes and reads shells; `bindery.pages` reads both header
forms; `exhibit` copies the file byte for byte.

`sea.txt`, beside the shore, holds bottles cast out by `cast`, one message per
line. New lines contain a 32-character hexadecimal bottle ID, a tab, and the
message; older plain-text lines remain readable. `find` takes the oldest
bottle not cast by the current pool, comparing IDs rather than words.
`horizon` counts the bottles at sea and how many the current pool cast,
without opening any.
The browser never serves it.

## Where to change things

- **A new command:** a function in `tidepool.py`, one entry in `COMMANDS`, and
  one line in `HELP` (a test fails if a command has no help line). The browser
  gets it for free through `respond`, and both shores offer its name as you
  type (Tab in the terminal, the field's suggestions in the browser). If it
  takes a remembered word, add it to `WORDED` so Tab offers the shore's words
  after it; if it needs no words, consider a button in webshore's `QUICK`.
- **A new keepsake file:** write it beside the shore, then add its name and
  content type to `KEEPSAKES` in `webshore.py` (the keepsake links follow it).
  To show it under the reply that made it, add a marker to `SHOWN`; a
  recording also needs its caption in `HEARD` (a test checks). For halls to
  keep it, add its group to `KEPT` and a catalogue line to `EXTRAS` in
  `exhibits.py`, and a label to `OPTIONAL_LINKS` (a test checks all three agree).
- **A new illustrated page:** an `.html` file beside the shore with a
  `<title>`, and its name in `KEEPSAKES` as `text/html; charset=utf-8`.
  Tests check its title, that every `href` or `src` beginning `/` that it holds is served, and
  that every `say` button speaks a real command, story or hall.
- **A new weather:** bridges in `weather.WEATHER`, then a bell length and surf
  in `seaglass.py`, day and night water colours in `postcard.py`, a drift speed in
  `drift.py`, and a mention in `HELP`;
  `test_weather.py` fails until every table has it.
- **A new story:** a Markdown file in `stories/` (see [WRITING.md](WRITING.md)).
  To give it a place, add `**N — [Title](stories/FILE.md).**` to
  [CHART.md](CHART.md), mark N on its map and on the illustrated coast
  (`studies/coast/coast.svg`). Tests check that every story uses
  only sea commands, that every place on the chart is a story, and that a
  quiet visitor (only Enter, on a bare shore beside the gallery) never meets
  a tide with fewer than two pieces.
