# Leave another place on the coast

Save a Markdown file in `stories/` and run `python3 tidepool.py stories/YOUR_STORY.md`.
Text outside triple-backtick fences is narrated on screen. Each fenced block
runs Tide Pool commands, one per line. The player pauses after each passage
or command block. Use `text` on the opening fence, as below.

Copy this walk into your file:

~~~~markdown
# The spare key

There is a key under the mat. The house is gone.

```text
bottle the door that used to be here
drop key rain
tide
```

Read the poem as directions. Which way does the door open?

```text
ebb
weather fog
tide
```

You leave before the rain remembers your name.

```text
quit
```
~~~~

`drop` scatters words; `bottle` keeps a phrase intact. A tide needs at least two
pieces. `ebb` takes one at random, so write the next passage to make sense
whichever piece leaves. `tide` shuffles the pool before pairing; a bottle
just found is not sure to lead. With exactly two bottled phrases beginning
with the same letter, either order gives that initial to the new line.
Make sure every `tide` has two pieces even for a reader who only presses Enter,
finds no bottle, and adds nothing (a test plays every story that way).

At any pause, the reader can type a sea command such
as `bottle my answer` without advancing the story. An empty Enter continues;
`q` leaves the terminal story.

`comb` can bring back a line from any earlier poem on the shared shore. Make
a tide first to guarantee it finds a line. `listen` and
`postcard` leave a recording and a drawing; give the reader a passage in
which to open them before another command overwrites them.

Small words can be characters. In a room with no door, `no` carries as much
of the memory as `door`. Try:

```text
bottle a room with no door
bottle a guest with no name
tide
kin no
trace no
```

`kin no` shows the words sharing its lines; `trace no` shows those lines.

Every story in `stories/` also appears in the browser's `read` menu, named by
its file name: `stories/SPARE_KEY.md` becomes `read spare_key`.

Readers may arrive with words already in the pool, by typing `read` inside a
session, so describe what your story adds rather than counting everything in
the water. The real moon adds more: on spring-tide nights every `tide` also
washes an old shore line back in. When a scene needs a clean pool, begin it
with `ebb all`; the shore keeps every poem. `echo` brings back the sea's last
line and `shells 1` shows the newest poem, which suit stories about returning.
`first <word>` and `last <word>` name the tide and day a word arrived and last
came back, so after the reader's own `tide`, `last` with a word from that poem
names it.

Some commands depend on the coast itself, so write the next passage to read
well either way: `wade` reaches the oldest shell only at low water
(`tidetable` says when), and `find` brings in a bottle only if one drifts.
On the live coast, `find` takes a real visitor's bottle; `horizon` counts
them without opening any. `diary today` shows only the poems kept on the
current UTC day, so just after midnight it is empty until the reader's first
`tide`. `spell <word>`, `crab`, `tidetable` and `wall` replace
their drawing beside the shore (the jetty, the crab, the dial, the wall), like
`postcard`; `tour <word>` follows a word through the halls, and `sign` with
`guestbook` lets a reader leave their name.

When you invite the reader to act at a pause, put your own version of that
command before the invitation, not after it, so your story does not overwrite
what the reader just made.

Run `python3 -m unittest` after saving: one test reads every story and names
any line that is not a sea command.

Hang a hall with `exhibit my-hall A rowing boat`: the name makes its folder,
and any words after it title the catalogue.

To illustrate a hall, save an SVG beside its catalogue, for example
`exhibits/my-hall/rowing-boat.svg`. The browser gallery links SVGs whose
names use lower-case letters, digits and hyphens, showing hyphens as spaces.
Add `![A boat between two banks](rowing-boat.svg)` to that hall’s README to
show it in the catalogue too.
