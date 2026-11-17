# Tide Pool

A little sea for words. Drop in fragments; let the tides make unexpected poems.
The pool can forget. The shore remembers.

Two keepers, Alice and Bob, built this coast one tide at a time: a word pool,
a shared shore of kept poems, stories to walk, drawings and sounds, and a
gallery of halls.

## Enter

Use Python 3; no dependencies.

- **Terminal:** `python3 tidepool.py` (Up recalls earlier commands; Tab completes commands, the story or hall after `read` or `visit`, remembered words after `trace` and its kin, and `today`, `yesterday` or a kept day after `diary`)
- **Browser:** `python3 webshore.py`, then open [the shore](http://127.0.0.1:8000/) (the command field suggests commands, stories and halls as you type).

## Your first five minutes

Speak one command at a time:

```text
drop moon rust lantern
tide
weather fog
tide
listen
```

In the browser, play the recording on the page. In the terminal, open the
printed `tide.wav` path. Type `help` for the command guide; `help wade`
explains just one command. Words and weather last for the current session.

## Walk the coast

Type `chart` to explore [the coast](CHART.md), then `read 1` to visit the
lighthouse or `read inn` to spend a night with strangers. At a story pause,
an empty Enter continues; a sea command changes the pool. In the terminal,
`q` returns from the story. You can also launch a story directly with
`python3 tidepool.py stories/LIGHTHOUSE.md`.

`atlas` collects the map, every walk, and exhibit links in `atlas.html`;
the browser binds it afresh whenever it is opened.

## The shore remembers

Poems accumulate in `shore.txt` across visits.

- **Reading it back:** `recite` plays every poem as bells in `recital.wav`;
  `bind` makes the book.
- **Days:** the coast keeps UTC time for its greeting and poem dates. `diary`
  counts poems by day; `diary today`, `diary yesterday` or `diary 2026-11-06`
  opens one day's page, and the greeting says when today's page is still empty.
  In the browser, every date in a reply is a button that opens that day's page.
- **Words:** `first <word>` and `last <word>` name the tide and day a word
  first and last washed up. `wall [word]` paints a mark on the harbour wall in
  `wall.svg` for every poem holding the word; `wall` alone paints the most
  remembered word. `letters` shows which letters remembered lines begin with,
  so you can see before spelling which planks a word still lacks.

## Drawings and sounds

`postcard`, `stars`, `listen`, and `bind` replace their latest drawing, sky,
recording, and book beside the shore; so do `signal` (the lamp, seen and in
Morse), `spell` (the jetty, drawn and walked), `crab` (its portrait),
`tidetable` (the tide dial), and `wall` (the harbour wall). Postcards use
daylight colours from 05:00 until 17:00 UTC.

## Messages between visitors

`cast the light is still on` seals a message in a bottle and sends it to sea;
a later visitor's `find` brings it in once, whole. `horizon` counts the
bottles still drifting, and the greeting says when one waits offshore. Your
own bottles stay out of reach until another visit.

`sign <name>` leaves a dated signature in `guestbook.txt`; `guestbook` shows
who has signed. Choose a name over breakfast at the inn (`read 7`).

## The gallery

`exhibit <name> [title]` preserves a collection in `exhibits/<name>/`; names
use lower-case letters, digits, and dashes, and existing exhibits are kept.
`visit <name>` brings its last line into the pool. The browser gallery links
each hall’s keepsakes and original drawings.

With the browser shore running, open [the sketchbook](http://127.0.0.1:8000/sketchbook.html) for ten drawings and their halls.

## Visit work already left here

- [Three rooms](THREE_ROOMS.md): a chair, two coats, and a ticket for yesterday.
- [Barefoot](BAREFOOT.md): a child’s question and a road in need of mending.
- [When tomorrow arrived](TOMORROW.md): a newspaper and the first page of a new day.
- [What the water does not take](WHAT_REMAINS.md): a gull, an empty room, and the words that stay.
- [Before the rain](BEFORE_RAIN.md): a night round and a salt garden.
- [Three rows](THREE_ROWS.md): seed, rain, and first green.
- [The other bank](THE_OTHER_BANK.md): the slipway, a ferry, and two raised hands.
- [The same chair](THE_SAME_CHAIR.md): two prints, a return, and afternoon light.
- [The paper remembers](PAPER.md): from the photographer through the darkroom to the bindery.
- [A ticket without a station](RETURN_TICKET.md): check a pocket, then choose a destination.
- [First night](exhibits/first-night/README.md): six memories in three weathers.
- [After midnight](exhibits/after-midnight/README.md): four memories dreaming in one another's words.
- [The keepers' shifts](exhibits/two-keepers/README.md): a shared shore, continued from keeper to keeper.
- [Six words, four seas](studies/surf/README.md): bells and surf in calm, fog, storm, and ice.
- [The coast drawn](studies/coast/README.md): thirty-eight places around one sea.
- [Eight moons](studies/moon/README.md): a month of light, including its absence.
- [A clock under the water](studies/tides/README.md): when to return for the oldest shell.
- [A word across the water](studies/lamp/README.md): “home” as light and sound.
- [One word, two rooms](studies/no/README.md): the same name on a new and a remembered shore.
- [The keepers overhead](studies/keepers/README.md): five shifts become a constellation.

## For makers

Add a place with [the story guide](WRITING.md). Run tests with
`python3 -m unittest`; [how the coast is built](ARCHITECTURE.md) maps the code.
Alice and Bob's handoffs are in the [Logbook](LOGBOOK.md); [the chronicle](CHRONICLE.md) tells it short.
