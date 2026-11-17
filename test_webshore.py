import os
import re
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

import tidepool
from skychart import moon
from shore import shell, wash_ashore
from storybook import CHART, STORY_DIR, place_name, stories, story_path
from tidepool import COMMANDS, TidePool, choices_after, respond
from exhibits import EXTRAS, KEPT, halls
from webshore import (GALLERY_LINKS, HEARD, KEEPSAKES, OPTIONAL_LINKS, QUICK, SHOWN, ShoreHandler, command_list, command_of, dated, drawings, exhibit_row, handler, moon_icon, next_beat, open_story, page,
                      paragraphs, say_button, sea_buttons, shown, shown_for, story_buttons, reply_to,
                      gallery, keepsakes, served, sound_for, fetched, heard, keep, restore)

NEAP = patch.object(tidepool, "now", return_value=datetime(2026, 11, 17, 11, 48, tzinfo=timezone.utc))
QUIET = patch.object(ShoreHandler, "log_message")


def setUpModule():
    NEAP.start()
    QUIET.start()


def tearDownModule():
    NEAP.stop()
    QUIET.stop()


def hall_with_catalogue(hall, name, title):
    """A hall folder as `exhibit` leaves one: its catalogue begins with the title."""
    os.makedirs(os.path.join(hall, name))
    with open(os.path.join(hall, name, "README.md"), "w", encoding="utf-8") as listing:
        listing.write(f"# {title}\n\n1 poem was left on the shore.\n")


def fetch(server, path):
    with urlopen(f"http://127.0.0.1:{server.server_port}{path}") as response:
        return response.headers["Content-Type"], response.read()


def say(server, command):
    form = urlencode({"say": command}).encode("utf-8")
    with urlopen(f"http://127.0.0.1:{server.server_port}/", data=form) as response:
        return response.headers["Content-Type"], response.read()


class WebshoreTest(unittest.TestCase):
    def test_command_of_reads_the_say_field(self):
        self.assertEqual(command_of("say=drop+moon+rust"), "drop moon rust")
        self.assertEqual(command_of("say="), "")

    def test_command_of_keeps_a_spoken_line_on_one_line(self):
        self.assertEqual(command_of("say=cast+the+light%0A%0Dis+still+on"), "cast the light is still on")

    def test_page_escapes_what_the_sea_says(self):
        html = page("drop <b>", "<b>", "", "", "", "")
        self.assertIn("shore&gt; drop &lt;b&gt;", html)
        self.assertIn("<pre>&lt;b&gt;</pre>", html)

    def test_page_plays_sound_above_the_picture(self):
        html = page("listen", "moon", "<svg>moon</svg>", "<audio></audio>", "<p>links</p>", "")
        self.assertIn("<pre>moon</pre>\n<audio></audio>\n<p>links</p>\n<svg>moon</svg>", html)

    def test_empty_command_just_looks(self):
        pool = TidePool()
        self.assertEqual(reply_to(pool, "", "unused", []), pool.look())

    def test_page_opens_with_its_header(self):
        header = paragraphs("Tonight: full moon · tides ~~~~~~~~~\nThe sea last said: <moon>")
        html = page("", "", "", "", "", header)
        self.assertIn("<h1>Tide Pool</h1>\n<p>Tonight: full moon · tides ~~~~~~~~~</p>"
                      "<p>The sea last said: &lt;moon&gt;</p>", html)

    def test_moon_icon_frames_tonight_s_moon(self):
        icon = moon_icon(0.5)
        self.assertIn('viewBox="972 32 56 56"', icon)
        self.assertIn(moon(0.5), icon)
        self.assertIn('aria-hidden="true"', icon)

    def test_the_live_page_shows_the_moon_above_the_greeting(self):
        with tempfile.TemporaryDirectory() as directory:
            server = HTTPServer(("127.0.0.1", 0), handler(TidePool(), os.path.join(directory, "shore.txt")))
            threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
            _, html = fetch(server, "/")
            server.shutdown()
            server.server_close()
        self.assertIn(b'<h1>Tide Pool</h1>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="972 32', html)
        self.assertIn(b"</svg><p>This morning: ", html)
        self.assertIn(b'#d8e8df', html)

    def test_the_greeting_offers_three_rooms_only_when_the_page_is_there(self):
        invitation = b'<a href="/three-rooms.html" style="color:inherit">Begin with three rooms.</a>'
        with tempfile.TemporaryDirectory() as directory:
            server = HTTPServer(("127.0.0.1", 0), handler(TidePool(), os.path.join(directory, "shore.txt")))
            threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
            _, bare = fetch(server, "/")
            Path(directory, "three-rooms.html").write_text("<p>rooms</p>", encoding="utf-8")
            _, offered = fetch(server, "/")
            server.shutdown()
            server.server_close()
        self.assertNotIn(invitation, bare)
        self.assertIn(invitation, offered)

    def test_paragraphs_one_per_line(self):
        self.assertEqual(paragraphs("a\nb"), "<p>a</p><p>b</p>")
        self.assertEqual(paragraphs(""), "")
        self.assertEqual(paragraphs("on 2026-11-07:"), f"<p>on {say_button('diary 2026-11-07', '2026-11-07')}:</p>")

    def test_page_offers_every_story_as_a_button(self):
        html = page("", "", "", "", "", "")
        self.assertIn(f"<details><summary>Choose a walk</summary>{story_buttons()}</details>", html)
        chart = Path(CHART).read_text(encoding="utf-8")
        targets = re.findall(r'value="read ([^"]+)"', story_buttons())
        self.assertEqual(sorted(place_name(target, chart) for target in targets), sorted(stories(STORY_DIR)))
        self.assertIn('<button name="say" value="read 1">1 The lighthouse</button>', html)
        self.assertIn('<button name="say" value="read same_words">same words</button>', html)

    def test_the_command_field_offers_every_command_it_understands(self):
        options = re.findall(r'<option value="([^"]+)">', command_list())
        commands = sorted((*COMMANDS, "read"))
        self.assertEqual(options[:len(commands)], commands)
        self.assertNotIn("drift", options)
        self.assertIn("read lighthouse", options)
        self.assertIn("visit first-night", options)
        self.assertIn("diary 2026-11-06", options)
        self.assertEqual(len(options), len(commands) + len(stories(STORY_DIR))
                         + len(halls(os.path.join(os.path.dirname(STORY_DIR), "exhibits")))
                         + len(choices_after("diary")))
        html = page("", "", "", "", "", "")
        self.assertIn('<input name="say" list="commands"', html)
        self.assertIn(f"{command_list()}</form>", html)

    def test_every_sea_button_is_a_real_word_free_command(self):
        for command in QUICK:
            with self.subTest(command=command):
                self.assertTrue(command in COMMANDS or command == "chart")
        self.assertNotIn("quit", QUICK)

    def test_the_page_offers_the_sea_buttons(self):
        html = page("", "", "", "", "", "")
        self.assertIn(f"<div>Sea: {sea_buttons()}</div>", html)
        self.assertIn('<button name="say" value="tide">tide</button>', html)
        self.assertIn('aria-label="Speak to the sea"', html)

    def test_no_hall_drawing_shares_a_label_with_the_gallery_s_own_links(self):
        hall = os.path.join(os.path.dirname(STORY_DIR), "exhibits")
        reserved = {label for _, label in GALLERY_LINKS + OPTIONAL_LINKS}
        labels = [(name, file[:-4].replace("-", " ")) for name in halls(hall) for file in drawings(os.path.join(hall, name))]
        self.assertGreater(len(labels), 20)
        for name, label in labels:
            with self.subTest(hall=name, drawing=label):
                self.assertNotIn(label, reserved)

    def test_drawings_are_a_hall_s_own_slug_named_svgs(self):
        with tempfile.TemporaryDirectory() as hall:
            for name in ("portrait.svg", "ferry.svg", "postcard.svg", "Bad Name.svg", "notes.txt"):
                open(os.path.join(hall, name), "w").close()
            os.makedirs(os.path.join(hall, "folder.svg"))
            self.assertEqual(drawings(hall), ["ferry.svg", "portrait.svg"])

    def test_dated_turns_each_day_into_its_diary_page_and_escapes_the_rest(self):
        self.assertEqual(dated("<b> 2026-11-07 · Bob"),
                         f"&lt;b&gt; {say_button('diary 2026-11-07', '2026-11-07')} · Bob")
        self.assertEqual(dated("tide 53"), "tide 53")
        self.assertIn(f"<pre>{say_button('diary 2026-11-06', '2026-11-06')}", page("", "2026-11-06 o 1", "", "", "", ""))

    def test_say_button_posts_its_command_and_escapes_it(self):
        self.assertEqual(say_button("read <b>", "<b>"),
                         '<form method="post" action="/" style="display:inline">'
                         '<button name="say" value="read &lt;b&gt;">&lt;b&gt;</button></form>')

    def test_gallery_rows_offer_a_visit(self):
        with tempfile.TemporaryDirectory() as hall:
            hall_with_catalogue(hall, "first-night", "First night")
            self.assertIn(say_button("visit first-night", "visit"), gallery(hall))

    def test_exhibit_row_is_title_visit_and_the_hall_s_links(self):
        with tempfile.TemporaryDirectory() as hall:
            hall_with_catalogue(hall, "dialled", "Dialled")
            open(os.path.join(hall, "dialled", "tideclock.svg"), "w").close()
            link = '<a href="/exhibits/dialled/{}" style="color:#ead9af">{}</a>'
            files = (("book.html", "book"), ("postcard.svg", "postcard"),
                     ("shore.txt", "shore"), ("tideclock.svg", "dial"))
            self.assertEqual(exhibit_row(hall, "dialled"),
                             f"<li>Dialled {say_button('visit dialled', 'visit')}: "
                             + " · ".join(link.format(*pair) for pair in files) + "</li>")

    def test_gallery_rows_show_each_hall_s_catalogue_title(self):
        with tempfile.TemporaryDirectory() as hall:
            hall_with_catalogue(hall, "bobs-plank", "Bob's plank & rope")
            self.assertIn("<li>Bob&#x27;s plank &amp; rope <form", gallery(hall))

    def test_open_unknown_story(self):
        story = []
        self.assertIn("Choose a story", open_story("atlantis", story))
        self.assertEqual(story, [])

    def test_bare_read_lists_the_shelf(self):
        story = []
        self.assertTrue(reply_to(TidePool(), "read", "unused", story).startswith("Choose a story"))
        self.assertTrue(reply_to(TidePool(), "reader", "unused", story).startswith("drop <words>"))
        self.assertEqual(story, [])

    def test_open_story_loads_its_beats(self):
        story = []
        open_story("bells", story)
        self.assertEqual(story[0][0], "story")
        self.assertIn("bell-diver", story[0][1])

    def test_next_beat_tells_and_marks_the_end(self):
        pool = TidePool()
        story = [("story", "The beam fades."), ("sea", ["drop lamp"])]
        self.assertEqual(next_beat(pool, story, "unused"),
                         "The beam fades.\n\n    ~ press enter to continue ~")
        self.assertTrue(next_beat(pool, story, "unused").endswith("~ the end ~"))
        self.assertEqual(pool.words, ["lamp"])

    def test_read_then_enter_walks_the_story(self):
        pool, story = TidePool(), []
        self.assertIn("story opens", reply_to(pool, "read lighthouse", "unused", story))
        self.assertIn("lighthouse keeper", reply_to(pool, "", "unused", story))

    def test_read_by_number_and_see_the_chart(self):
        pool, story = TidePool(), []
        self.assertIn("THE HARBOUR", reply_to(pool, "chart", "unused", story))
        reply_to(pool, "read 2", "unused", story)
        self.assertIn("bell-diver", reply_to(pool, "", "unused", story))

    def test_sound_only_when_a_recording_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "tide.wav")
            self.assertEqual(sound_for(path), "")
            with open(path, "wb") as song:
                song.write(b"RIFF")
            self.assertIn('src="/tide.wav"', sound_for(path))
            self.assertIn("Pool recording", sound_for(path))

    def test_the_lamp_shows_only_after_a_signal_reply(self):
        with tempfile.TemporaryDirectory() as directory:
            flashed = 'The lamp flashes "sos":'
            self.assertEqual(shown_for(flashed, directory), "")
            with open(os.path.join(directory, "signal.svg"), "w", encoding="utf-8") as lamp:
                lamp.write("<svg>lamp</svg>")
            self.assertEqual(shown_for(flashed, directory), "<svg>lamp</svg>")
            self.assertEqual(shown_for("moon haunts rust", directory), "")

    def test_the_tide_dial_is_shown_under_its_reply(self):
        with tempfile.TemporaryDirectory() as directory:
            reply = respond(TidePool(), "tidetable", os.path.join(directory, "shore.txt"))
            self.assertIn("<title>The water is rising</title>", shown_for(reply, directory))

    def test_a_spelled_jetty_is_shown_under_its_reply(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            reply = respond(TidePool(), "spell bob", shore)
            self.assertIn("<title>bob</title>", shown_for(reply, directory))
            self.assertIn('<audio controls src="/jetty.wav"></audio>', shown_for(reply, directory))

    def test_a_word_s_harbour_wall_is_shown_under_its_reply(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            wash_ashore(shore, shell(1, "salt haunts rust"))
            reply = respond(TidePool(), "wall salt", shore)
            self.assertIn("<title>salt on the harbour wall</title>", shown_for(reply, directory))

    def test_recordings_are_shown_as_captioned_players(self):
        with tempfile.TemporaryDirectory() as directory:
            recital = '<p>The shore read aloud</p><audio controls src="/recital.wav"></audio>'
            self.assertEqual(shown(directory, "recital.wav"), recital)
            open(os.path.join(directory, "recital.wav"), "w").close()
            self.assertEqual(shown_for("Open x to hear the shore read aloud in bells", directory), recital)
            for name, caption in (("signal.wav", "The lamp in Morse"), ("jetty.wav", "The jetty walked")):
                with self.subTest(name=name):
                    self.assertTrue(shown(directory, name).startswith(f"<p>{caption}</p><audio"))

    def test_the_illustrated_routes_speak_only_real_commands(self):
        root = os.path.dirname(STORY_DIR)
        page = "".join(html.read_text(encoding="utf-8") for html in sorted(Path(root).glob("*.html")))
        spoken = re.findall(r'name="say" value="([^"]+)"', page)
        self.assertTrue(spoken)
        for said in spoken:
            name, _, arg = said.partition(" ")
            with self.subTest(said=said):
                if name == "visit":
                    self.assertIn(arg, halls(os.path.join(root, "exhibits")))
                elif name == "read":
                    self.assertTrue(story_path(arg))
                else:
                    self.assertIn(name, COMMANDS)

    def test_the_gallery_folds_its_halls_under_one_summary(self):
        with tempfile.TemporaryDirectory() as hall:
            hall_with_catalogue(hall, "first-night", "First night")
            self.assertTrue(gallery(hall).startswith("<details><summary>Exhibits: 1 hall</summary><ul><li>"))
            hall_with_catalogue(hall, "second-hook", "The second hook")
            self.assertIn("<summary>Exhibits: 2 halls</summary>", gallery(hall))
            self.assertTrue(gallery(hall).endswith("</ul></details>"))

    def test_every_kept_keepsake_is_catalogued_and_linked_in_the_gallery(self):
        described = [files for files, _ in EXTRAS]
        self.assertTrue(all(files in described for files in KEPT))
        self.assertEqual({file for file, _ in OPTIONAL_LINKS}, {file for files in described for file in files})

    def test_every_recording_shown_has_a_caption(self):
        self.assertEqual({name for _, name in SHOWN if name.endswith(".wav")}, set(HEARD))

    def test_keepsakes_link_only_what_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(keepsakes(directory), "")
            open(os.path.join(directory, "book.html"), "w").close()
            links = keepsakes(directory)
            self.assertIn('href="/book.html"', links)
            self.assertNotIn("postcard.svg", links)

    def test_keepsakes_link_every_kind_but_the_pool_recording(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in KEEPSAKES:
                open(os.path.join(directory, name), "w").close()
            links = keepsakes(directory)
            self.assertEqual(links.count("<a "), len(KEEPSAKES) - 1)
            self.assertNotIn('href="/tide.wav"', links)

    def test_gallery_lists_only_named_halls(self):
        with tempfile.TemporaryDirectory() as directory:
            hall = os.path.join(directory, "exhibits")
            self.assertEqual(gallery(hall), "")
            hall_with_catalogue(hall, "first-night", "First night")
            os.makedirs(os.path.join(hall, "Stray Folder"))
            listing = gallery(hall)
            self.assertIn('href="/exhibits/first-night/book.html"', listing)
            self.assertNotIn(">bells</a>", listing)
            open(os.path.join(hall, "first-night", "tide.wav"), "w").close()
            self.assertIn(">bells</a>", gallery(hall))
            self.assertNotIn("Stray", listing)

    def test_gallery_links_saved_signals_only_when_present(self):
        with tempfile.TemporaryDirectory() as hall:
            hall_with_catalogue(hall, "reply", "reply")
            self.assertNotIn("signal.", gallery(hall))
            for file in ("signal.svg", "signal.wav"):
                open(os.path.join(hall, "reply", file), "w").close()
            listing = gallery(hall)
            self.assertIn('href="/exhibits/reply/signal.svg"', listing)
            self.assertIn('href="/exhibits/reply/signal.wav"', listing)
            self.assertNotIn("sky.svg", listing)
            open(os.path.join(hall, "reply", "sky.svg"), "w").close()
            self.assertIn('href="/exhibits/reply/sky.svg" style="color:#ead9af">sky</a>', gallery(hall))
            self.assertNotIn("jetty.svg", gallery(hall))
            open(os.path.join(hall, "reply", "jetty.svg"), "w").close()
            self.assertIn('href="/exhibits/reply/jetty.svg" style="color:#ead9af">jetty</a>', gallery(hall))
            self.assertNotIn("jetty.wav", gallery(hall))
            open(os.path.join(hall, "reply", "jetty.wav"), "w").close()
            self.assertIn('href="/exhibits/reply/jetty.wav" style="color:#ead9af">planks</a>', gallery(hall))
            self.assertNotIn("crab.svg", gallery(hall))
            open(os.path.join(hall, "reply", "crab.svg"), "w").close()
            self.assertIn('href="/exhibits/reply/crab.svg" style="color:#ead9af">crab</a>', gallery(hall))
            self.assertNotIn("tideclock.svg", gallery(hall))
            open(os.path.join(hall, "reply", "tideclock.svg"), "w").close()
            self.assertIn('href="/exhibits/reply/tideclock.svg" style="color:#ead9af">dial</a>', gallery(hall))

    def test_served_maps_only_known_files(self):
        self.assertEqual(served("/sea", "/book.html"), ("/sea/book.html", "text/html; charset=utf-8"))
        self.assertEqual(served("/sea", "/exhibits/first-night/shore.txt"),
                         ("/sea/exhibits/first-night/shore.txt", "text/plain; charset=utf-8"))
        for path in ("/shore.txt", "/exhibits/../tidepool.py", "/exhibits/first-night/README.md",
                     "/exhibits/first-night/../../tidepool.py", "/tidepool.py"):
            with self.subTest(path=path):
                self.assertEqual(served("/sea", path), ("", ""))


class WithoutServerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.shore = handler(TidePool(), os.path.join(self.dir.name, "shore.txt"))

    def tearDown(self):
        self.dir.cleanup()

    def test_heard_speaks_a_posted_form_into_the_pool(self):
        heard(self.shore, "say=drop+lantern")
        self.assertEqual(self.shore.pool.words, ["lantern"])
        self.assertEqual(self.shore.last[0], "drop lantern")

    def test_fetched_answers_the_page_keepsakes_and_nothing_else(self):
        heard(self.shore, "say=drop+lantern")
        body, kind = fetched(self.shore, "/")
        self.assertEqual(kind, "text/html; charset=utf-8")
        self.assertIn(b"shore&gt; drop lantern", body)
        self.assertIsNone(fetched(self.shore, "/tide.wav"))
        heard(self.shore, "say=listen")
        self.assertEqual(fetched(self.shore, "/tide.wav")[1], "audio/wav")
        self.assertIsNone(fetched(self.shore, "/favicon.ico"))

    def test_keep_then_restore_brings_back_the_shore_and_only_new_halls(self):
        coast, kept = Path(self.dir.name), Path(self.dir.name, "kept")
        kept.mkdir()
        for name in ("shore.txt", "sea.txt", "guestbook.txt"):
            (coast / name).write_text(f"{name} of this visit")
        hall_with_catalogue(str(coast / "exhibits"), "shipped-hall", "Shipped")
        hall_with_catalogue(str(coast / "exhibits"), "new-hall", "New")
        keep(str(coast), str(kept), ["shipped-hall"])
        self.assertFalse((kept / "exhibits" / "shipped-hall").exists())
        later = Path(self.dir.name, "later")
        later.mkdir()
        restore(str(kept), str(later))
        self.assertEqual((later / "sea.txt").read_text(), "sea.txt of this visit")
        self.assertEqual(halls(str(later / "exhibits")), ["new-hall"])


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.pool = TidePool()
        shore = os.path.join(self.dir.name, "shore.txt")
        self.server = HTTPServer(("127.0.0.1", 0), handler(self.pool, shore))
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.dir.cleanup()

    def test_server_speaks_to_one_pool(self):
        _, html = say(self.server, "drop lantern")
        self.assertIn(">lantern</tspan>", html.decode("utf-8"))
        self.assertEqual(self.pool.words, ["lantern"])

    def test_a_signal_lights_the_lamp_on_the_page_until_the_next_line(self):
        _, html = say(self.server, "signal sos")
        self.assertIn(b"<title>sos</title>", html)
        self.assertIn(b'<audio controls src="/signal.wav"></audio>', html)
        _, html = say(self.server, "look")
        self.assertNotIn(b"<title>sos</title>", html)
        self.assertNotIn(b'src="/signal.wav"', html)

    def test_a_recital_plays_on_the_page(self):
        say(self.server, "drop moon rust")
        say(self.server, "tide")
        _, html = say(self.server, "recite")
        self.assertIn(b'<audio controls src="/recital.wav"></audio>', html)

    def test_a_story_s_signal_lights_the_lamp_too(self):
        say(self.server, "read opposite")
        say(self.server, "")
        _, html = say(self.server, "")
        self.assertIn(b"<title>are you there</title>", html)

    def test_an_open_story_offers_a_way_onward_until_its_end(self):
        onward = say_button("", "continue the story").encode("utf-8")
        _, html = fetch(self.server, "/")
        self.assertNotIn(onward, html)
        _, html = say(self.server, "read lighthouse")
        self.assertIn(onward, html)
        while b"~ the end ~" not in html:
            _, html = say(self.server, "")
        self.assertNotIn(onward, html)

    def test_stars_hang_the_sky_on_the_page(self):
        say(self.server, "drop moon rust")
        say(self.server, "tide")
        _, html = say(self.server, "stars")
        self.assertIn(b"<title>The sky over the shore</title>", html)
        _, html = say(self.server, "look")
        self.assertNotIn(b"<title>The sky over the shore</title>", html)

    def test_the_crab_portrait_is_shown_and_served(self):
        say(self.server, "bottle moon moon")
        say(self.server, "bottle moon window")
        say(self.server, "tide")
        _, html = say(self.server, "crab")
        self.assertIn(b'<title>A hermit crab in moon</title>', html)
        self.assertIn(b'href="/crab.svg"', html)
        kind, drawing = fetch(self.server, '/crab.svg')
        self.assertEqual(kind, 'image/svg+xml')
        self.assertIn(b'House: moon', drawing)
        _, html = say(self.server, "look")
        self.assertNotIn(b'<title>A hermit crab in moon</title>', html)

    def test_the_atlas_is_bound_fresh_whenever_it_is_opened(self):
        _, atlas = fetch(self.server, "/atlas.html")
        self.assertNotIn(b"Late hall", atlas)
        hall_with_catalogue(os.path.join(self.dir.name, "exhibits"), "late-hall", "Late hall")
        kind, atlas = fetch(self.server, "/atlas.html")
        self.assertEqual(kind, "text/html; charset=utf-8")
        self.assertIn(b"Late hall", atlas)

    def test_listening_serves_the_recording(self):
        say(self.server, "drop lantern")
        _, html = say(self.server, "listen")
        kind, song = fetch(self.server, "/tide.wav")
        self.assertIn("<audio", html.decode("utf-8"))
        self.assertEqual(kind, "audio/wav")
        self.assertEqual(song[:4], b"RIFF")

    def test_story_recording_has_a_player_and_survives_next_beat(self):
        say(self.server, "read radio")
        say(self.server, "")
        _, html = say(self.server, "")
        self.assertIn(b"<audio", html)
        kind, song = fetch(self.server, "/tide.wav")
        self.assertEqual(kind, "audio/wav")
        self.assertEqual(song[:4], b"RIFF")
        _, html = say(self.server, "")
        self.assertIn(b"Pool recording", html)

    def test_keepsakes_are_served_once_made(self):
        with self.assertRaises(HTTPError) as caught:
            fetch(self.server, "/book.html")
        self.assertEqual(caught.exception.code, 404)
        caught.exception.close()
        say(self.server, "drop moon rust")
        say(self.server, "tide")
        say(self.server, "postcard")
        _, html = say(self.server, "bind")
        self.assertIn(b'href="/book.html"', html)
        self.assertIn(b'href="/postcard.svg"', html)
        kind, book = fetch(self.server, "/book.html")
        self.assertEqual(kind, "text/html; charset=utf-8")
        self.assertIn(b"The shore, bound", book)
        kind, _ = fetch(self.server, "/postcard.svg")
        self.assertEqual(kind, "image/svg+xml")

    def test_an_exhibit_hung_from_the_browser_hangs_in_its_gallery(self):
        say(self.server, "drop moon rust")
        say(self.server, "tide")
        _, html = say(self.server, "exhibit low-water")
        self.assertIn(b'href="/exhibits/low-water/postcard.svg"', html)
        kind, book = fetch(self.server, "/exhibits/low-water/book.html")
        self.assertEqual(kind, "text/html; charset=utf-8")
        self.assertIn(b"The shore, bound", book)

    def test_gallery_opens_original_drawings_without_serving_other_hall_files(self):
        hall = Path(self.dir.name, "exhibits", "empty-room")
        hall_with_catalogue(str(hall.parent), hall.name, "The empty room")
        drawing = b'<svg xmlns="http://www.w3.org/2000/svg"><title>Empty chair</title></svg>'
        (hall / "empty-chair.svg").write_bytes(drawing)
        (hall / "notes.txt").write_text("Not a drawing")
        (hall / 'bad"name.svg').write_bytes(drawing)
        (hall / "directory.svg").mkdir()
        _, html = fetch(self.server, "/")
        self.assertIn(b'href="/exhibits/empty-room/empty-chair.svg"', html)
        self.assertIn(b">empty chair</a>", html)
        self.assertNotIn(b"bad", html)
        self.assertNotIn(b"directory.svg", html)
        self.assertEqual(fetch(self.server, "/exhibits/empty-room/empty-chair.svg"),
                         ("image/svg+xml", drawing))
        for file in ("notes.txt", "missing.svg", "directory.svg", "bad%22name.svg"):
            with self.subTest(file=file), self.assertRaises(HTTPError) as caught:
                fetch(self.server, f"/exhibits/empty-room/{file}")
            self.assertEqual(caught.exception.code, 404)
            caught.exception.close()

    def test_reloading_shows_the_last_reply_without_repeating_it(self):
        say(self.server, "drop lantern")
        _, html = fetch(self.server, "/")
        self.assertIn(b"shore&gt; drop lantern", html)
        self.assertEqual(self.pool.words, ["lantern"])

    def test_query_strings_no_longer_command_the_sea(self):
        fetch(self.server, "/?say=drop+lantern")
        self.assertEqual(self.pool.words, [])

    def test_favicon_does_not_advance_story(self):
        say(self.server, "read radio")
        with self.assertRaises(HTTPError) as caught:
            fetch(self.server, "/favicon.ico")
        self.assertEqual(caught.exception.code, 404)
        caught.exception.close()
        _, html = say(self.server, "")
        self.assertIn(b"The station closed years ago", html)
        self.assertEqual(self.pool.words, [])


if __name__ == "__main__":
    unittest.main()
