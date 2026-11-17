import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dial import dial
from exhibits import SIGNAL, catalogue, chart_atlas, exhibit, hall_title, halls, hang, hang_bells, hang_dial, hang_sky, keep_beside, shelf
from moon import turn_of, water
from shore import read_shore, shell, wash_ashore
from storybook import STORY_DIR, stories
from tidepool import TidePool, respond, signal, stars

WHEN = datetime(2026, 11, 17, 11, 48, tzinfo=timezone.utc)


class HallTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.shore = os.path.join(self.dir.name, "shore.txt")

    def tearDown(self):
        self.dir.cleanup()

    def test_halls_are_only_named_exhibits(self):
        hall = os.path.join(self.dir.name, "exhibits")
        self.assertEqual(halls(hall), [])
        for name in ("second", "first", "Stray Folder"):
            os.makedirs(os.path.join(hall, name))
        self.assertEqual(halls(hall), ["first", "second"])

    def test_shelf_reads_every_story(self):
        self.assertEqual(set(shelf()), set(stories(STORY_DIR)))
        self.assertIn("bell-diver", shelf()["bells"])

    def test_catalogue_counts_poems_and_quotes_the_line_a_visit_would_bring(self):
        text = "~ tide 1 ~\nmoon haunts rust\nand fern listens\n\n~ tide 2 ~\nsalt shelters bell"
        listing = catalogue("night-two", text, set())
        self.assertTrue(listing.startswith("# night-two\n\n2 poems were left on the shore."))
        self.assertTrue(listing.endswith("The sea's last words were:\n\n> salt shelters bell\n"))
        self.assertNotIn("signal", listing)

    def test_catalogue_counts_a_single_poem_in_the_singular(self):
        listing = catalogue("one", "~ tide 1 ~\nmoon haunts rust", set())
        self.assertTrue(listing.startswith("# one\n\n1 poem was left on the shore."))

    def test_catalogue_links_a_kept_signal_with_the_other_keepsakes(self):
        listing = catalogue("night-two", "~ tide 1 ~\nmoon haunts rust", {"tide.wav", "signal.svg", "signal.wav"})
        self.assertIn("- [Hear its bells](tide.wav).\n- [Watch the last signal](signal.svg), "
                      "or [hear it in Morse](signal.wav).\n\nThe sea's last words", listing)

    def test_keep_beside_needs_every_file_beside_the_shore(self):
        hall = os.path.join(self.dir.name, "hall")
        os.mkdir(hall)
        open(os.path.join(self.dir.name, "signal.svg"), "w").close()
        self.assertEqual(keep_beside(self.shore, hall, SIGNAL), set())
        open(os.path.join(self.dir.name, "signal.wav"), "w").close()
        self.assertEqual(keep_beside(self.shore, hall, SIGNAL), {"signal.svg", "signal.wav"})
        self.assertEqual(sorted(os.listdir(hall)), ["signal.svg", "signal.wav"])

    def test_exhibit_keeps_the_last_jetty(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        respond(TidePool(), "spell moon", self.shore)
        exhibit(TidePool(), "spelled", self.shore, WHEN)
        hall = os.path.join(self.dir.name, "exhibits", "spelled")
        with open(os.path.join(self.dir.name, "jetty.svg"), "rb") as live, \
                open(os.path.join(hall, "jetty.svg"), "rb") as kept:
            self.assertEqual(kept.read(), live.read())
        with open(os.path.join(hall, "README.md"), encoding="utf-8") as listing:
            self.assertIn("- [Walk the last jetty](jetty.svg).\n- [Hear its planks underfoot](jetty.wav).\n",
                          listing.read())
        self.assertTrue(os.path.isfile(os.path.join(hall, "jetty.wav")))

    def test_exhibit_draws_the_water_as_it_is_hung(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        Path(self.dir.name, "tideclock.svg").write_text("<svg>stale</svg>", encoding="utf-8")
        exhibit(TidePool(), "dialled", self.shore, WHEN)
        hall = os.path.join(self.dir.name, "exhibits", "dialled")
        self.assertEqual(Path(hall, "tideclock.svg").read_text(encoding="utf-8"), dial(turn_of(WHEN), water(WHEN)))
        with open(os.path.join(hall, "README.md"), encoding="utf-8") as listing:
            self.assertIn("- [Read the water as the hall was hung](tideclock.svg).\n", listing.read())

    def test_hang_makes_the_hall_with_its_book_bells_sky_dial_and_catalogue(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        pool = TidePool()
        pool.drop("moon rust")
        folder = os.path.join(self.dir.name, "hung")
        hang(pool, folder, self.shore, read_shore(self.shore), WHEN, "hung")
        self.assertEqual(sorted(os.listdir(folder)), ["README.md", "book.html", "postcard.svg", "shore.txt",
                                                      "sky.svg", "tide.wav", "tideclock.svg"])
        self.assertTrue(Path(folder, "README.md").read_text(encoding="utf-8").startswith("# hung\n"))

    def test_an_empty_pool_hangs_no_bells(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        folder = os.path.join(self.dir.name, "quiet")
        hang(TidePool(), folder, self.shore, read_shore(self.shore), WHEN, "quiet")
        self.assertNotIn("tide.wav", os.listdir(folder))
        self.assertNotIn("bells", Path(folder, "README.md").read_text(encoding="utf-8"))

    def test_hang_bells_rings_only_a_pool_with_words(self):
        pool = TidePool()
        self.assertEqual(hang_bells(pool, self.dir.name), set())
        pool.drop("moon")
        self.assertEqual(hang_bells(pool, self.dir.name), {"tide.wav"})
        self.assertTrue(Path(self.dir.name, "tide.wav").is_file())

    def test_hang_dial_names_what_it_drew(self):
        self.assertEqual(hang_dial(self.dir.name, WHEN), {"tideclock.svg"})

    def test_exhibit_titles_its_catalogue_with_the_words_after_the_name(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        exhibit(TidePool(), "dry-step The step stayed under the sea", self.shore, WHEN)
        exhibit(TidePool(), "untitled", self.shore, WHEN)
        hall = os.path.join(self.dir.name, "exhibits")
        self.assertEqual(hall_title(hall, "dry-step"), "The step stayed under the sea")
        self.assertEqual(hall_title(hall, "untitled"), "untitled")

    def test_exhibit_keeps_the_last_crab(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        respond(TidePool(), "crab", self.shore)
        exhibit(TidePool(), "housed", self.shore, WHEN)
        hall = os.path.join(self.dir.name, "exhibits", "housed")
        with open(os.path.join(self.dir.name, "crab.svg"), "rb") as live, \
                open(os.path.join(hall, "crab.svg"), "rb") as kept:
            self.assertEqual(kept.read(), live.read())
        with open(os.path.join(hall, "README.md"), encoding="utf-8") as listing:
            self.assertIn("- [Meet the last crab](crab.svg).\n", listing.read())

    def test_exhibit_keeps_the_last_wall(self):
        wash_ashore(self.shore, shell(1, "salt haunts rust"))
        respond(TidePool(), "wall salt", self.shore)
        exhibit(TidePool(), "marked", self.shore, WHEN)
        hall = os.path.join(self.dir.name, "exhibits", "marked")
        with open(os.path.join(self.dir.name, "wall.svg"), "rb") as live, \
                open(os.path.join(hall, "wall.svg"), "rb") as kept:
            self.assertEqual(kept.read(), live.read())
        with open(os.path.join(hall, "README.md"), encoding="utf-8") as listing:
            self.assertIn("- [See the last marks on the harbour wall](wall.svg).\n", listing.read())

    def test_hall_title_reads_the_catalogue_s_first_line(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        exhibit(TidePool(), "titled", self.shore, WHEN)
        hall = os.path.join(self.dir.name, "exhibits")
        self.assertEqual(hall_title(hall, "titled"), "titled")
        with open(os.path.join(hall, "titled", "README.md"), "w", encoding="utf-8") as listing:
            listing.write("# Bob's plank & rope\n\nA hall.\n")
        self.assertEqual(hall_title(hall, "titled"), "Bob's plank & rope")

    def test_the_atlas_names_each_hall_by_its_title(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        exhibit(TidePool(), "titled", self.shore, WHEN)
        with open(os.path.join(self.dir.name, "exhibits", "titled", "README.md"), "w", encoding="utf-8") as listing:
            listing.write("# A titled hall\n")
        chart_atlas(self.shore)
        page = Path(self.dir.name, "atlas.html").read_text(encoding="utf-8")
        self.assertIn('<a href="exhibits/titled/book.html">A titled hall</a>', page)

    def test_hang_sky_needs_remembered_words(self):
        with tempfile.TemporaryDirectory() as hall:
            self.assertEqual(hang_sky(hall, "~ tide 1 ~\nand listens", WHEN), set())
            self.assertEqual(os.listdir(hall), [])

    def test_exhibit_keeps_the_last_signal(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        signal("sos", self.shore)
        exhibit(TidePool(), "signalled", self.shore, WHEN)
        hall = os.path.join(self.dir.name, "exhibits", "signalled")
        self.assertTrue({"signal.svg", "signal.wav"} <= set(os.listdir(hall)))
        with open(os.path.join(self.dir.name, "signal.svg"), "rb") as live, \
                open(os.path.join(hall, "signal.svg"), "rb") as kept:
            self.assertEqual(kept.read(), live.read())

    def test_exhibit_draws_a_sky_no_older_than_its_poems(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        stars(self.shore)
        wash_ashore(self.shore, shell(2, "kraken shelters bell"))
        exhibit(TidePool(), "starlit", self.shore, WHEN)
        hall = os.path.join(self.dir.name, "exhibits", "starlit")
        self.assertNotIn("signal.svg", os.listdir(hall))
        with open(os.path.join(hall, "sky.svg"), encoding="utf-8") as sky:
            self.assertIn("kraken", sky.read())
        with open(os.path.join(self.dir.name, "sky.svg"), encoding="utf-8") as stale:
            self.assertNotIn("kraken", stale.read())
        with open(os.path.join(hall, "README.md"), encoding="utf-8") as listing:
            text = listing.read()
        self.assertIn("- [See the shore's sky](sky.svg).\n", text)
        self.assertNotIn("signal", text)

    def test_a_hung_shore_can_be_continued_with_its_spacing(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        exhibit(TidePool(), "kept", self.shore, WHEN)
        hung = os.path.join(self.dir.name, "exhibits", "kept", "shore.txt")
        with open(os.path.join(os.path.dirname(hung), "postcard.svg")) as card:
            self.assertIn('#d8e8df', card.read())
        with open(self.shore, encoding="utf-8") as live, open(hung, encoding="utf-8") as kept:
            self.assertEqual(kept.read(), live.read())
        wash_ashore(hung, shell(2, "salt shelters bell"))
        self.assertIn("moon haunts rust\n\n~ tide 2 ~", read_shore(hung))

    def test_exhibit_refuses_bad_names_existing_halls_and_bare_shores(self):
        pool = TidePool()
        self.assertIn("shore is bare", exhibit(pool, "empty", self.shore, WHEN))
        for name in ("../escape", "Night", ""):
            with self.subTest(name=name):
                self.assertIn("lower-case", exhibit(pool, name, self.shore, WHEN))
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        exhibit(pool, "once", self.shore, WHEN)
        self.assertIn("already hangs", exhibit(pool, "once", self.shore, WHEN))
        self.assertEqual(os.listdir(os.path.join(self.dir.name, "exhibits")), ["once"])


if __name__ == "__main__":
    unittest.main()
