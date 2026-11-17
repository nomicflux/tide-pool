import os
import re
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import tidepool

from datetime import datetime, timedelta, timezone

from storybook import CHART, STORY_DIR, chart_places, stories, story_beats, story_path
from moon import NEW_MOON, TIDE_HOURS
from shore import BARE, read_shore, shell, wash_ashore
from bindery import pages
from tidepool import (COMMANDS, HELP, TidePool, almanac, ask, aside, book_of, cast, change_weather, comb, day_of, next_tide,
                      choices_after, complete, completions, count, crab, drop_and_look, enable_editing, guestbook, harbour, help_for, low_water_on, wading, sign_book, tidetable, tour, wade, water_note, water_times, dream, dream_once, ebb, echo, find, horizon, is_spring, hall_name, kept_since, kin, last_words, letters, most_remembered, moonrise, new_page, offshore, pick_up, rhyme, sea_of, spell, pause, play_story, read_story, recital,
                      respond, seek, shells, shore_diary, shore_note, signal, spring_tide, stars, strandline, tell,
                      tide_and_wash, tonight, trace, visit, wall, washed_up, watch_drift, welcome)
from weather import WEATHER

NEW_MOON = datetime(2026, 11, 9, 7, 2, tzinfo=timezone.utc)
FIRST_QUARTER = datetime(2026, 11, 17, 11, 48, tzinfo=timezone.utc)
NEAP = patch.object(tidepool, "now", return_value=FIRST_QUARTER)


def setUpModule():
    NEAP.start()


def tearDownModule():
    NEAP.stop()


class SpringTideTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.shore = os.path.join(self.dir.name, "shore.txt")

    def tearDown(self):
        self.dir.cleanup()

    def test_neap_tide_is_only_a_tide(self):
        pool = TidePool()
        pool.drop("moon rust")
        self.assertNotIn("spring tide", spring_tide(pool, self.shore, FIRST_QUARTER))
        self.assertEqual(sorted(pool.words), ["moon", "rust"])

    def test_spring_tide_washes_a_shell_back_in(self):
        pool = TidePool()
        pool.drop("moon rust")
        reply = spring_tide(pool, self.shore, NEW_MOON)
        self.assertIn('The spring tide brings a shell in: "', reply)
        self.assertGreater(len(pool.words), 2)

    def test_spring_tide_needs_a_meeting_first(self):
        pool = TidePool()
        pool.drop("moon")
        self.assertNotIn("spring tide", spring_tide(pool, self.shore, NEW_MOON))
        self.assertEqual(pool.words, ["moon"])

    def test_the_tide_command_reads_tonight_s_moon(self):
        pool = TidePool()
        pool.drop("moon rust")
        with patch.object(tidepool, "now", return_value=NEW_MOON):
            self.assertIn("spring tide", respond(pool, "tide", self.shore))


class EbbTest(unittest.TestCase):
    def test_ebb_carries_one_word_away_without_changing_shore(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            pool = TidePool()
            pool.drop("moon moon")
            respond(pool, "tide", shore)
            before = read_shore(shore)
            self.assertIn("carries away moon", respond(pool, "ebb", shore))
            self.assertEqual(pool.words, ["moon"])
            self.assertEqual(read_shore(shore), before)

    def test_ebb_until_empty(self):
        pool = TidePool()
        pool.drop("moon")
        pool.ebb()
        self.assertEqual(pool.words, [])
        self.assertIn("Only water", pool.ebb())

    def test_ebb_all_empties_the_pool_but_not_the_shore(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            pool = TidePool()
            pool.drop("moon rust lantern")
            respond(pool, "tide", shore)
            before = read_shore(shore)
            self.assertEqual(respond(pool, "ebb all", shore),
                             "The low tide carries all 3 pieces away. The shore keeps their poems.")
            self.assertEqual(pool.words, [])
            self.assertEqual(read_shore(shore), before)

    def test_ebb_all_of_an_empty_pool(self):
        self.assertIn("Only water", ebb(TidePool(), "all"))

    def test_ebb_all_of_a_single_piece(self):
        pool = TidePool()
        pool.drop("moon")
        self.assertEqual(ebb(pool, "all"),
                         "The low tide carries the only piece away. The shore keeps their poems.")


class BottleTest(unittest.TestCase):
    def test_identical_messages_belong_to_distinct_keepers(self):
        alice, bob = TidePool(), TidePool()
        cast(alice, "the kettle is warm", self.shore)
        cast(bob, "the kettle is warm", self.shore)
        find(alice, self.shore)
        self.assertEqual(alice.words, ["the kettle is warm"])
        self.assertEqual(find(alice, self.shore), "No bottle has drifted in. Cast one for the next keeper: cast the light is still on")
        find(bob, self.shore)
        self.assertEqual(bob.words, ["the kettle is warm"])

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.shore = os.path.join(self.dir.name, "shore.txt")

    def tearDown(self):
        self.dir.cleanup()

    def test_a_cast_bottle_is_found_whole_in_another_pool(self):
        self.assertIn("drifts out to sea", respond(TidePool(), "cast the light is still on", self.shore))
        finder = TidePool()
        reply = respond(finder, "find", self.shore)
        self.assertTrue(reply.startswith('A bottle washes up: "the light is still on"'))
        self.assertEqual(finder.words, ["the light is still on"])
        self.assertFalse(os.path.exists(self.shore))

    def test_an_empty_sea_and_an_empty_message(self):
        self.assertEqual(find(TidePool(), self.shore), "No bottle has drifted in. Cast one for the next keeper: cast the light is still on")
        self.assertIn("cast the light is still on", cast(TidePool(), "", self.shore))

    def test_a_keeper_cannot_fish_back_their_own_bottle_in_the_same_session(self):
        keeper = TidePool()
        respond(keeper, "cast the light is still on", self.shore)
        self.assertEqual(respond(keeper, "find", self.shore), "No bottle has drifted in. Cast one for the next keeper: cast the light is still on")
        self.assertEqual(keeper.words, [])
        self.assertIn("the light is still on", respond(TidePool(), "find", self.shore))

    def test_horizon_counts_bottles_at_sea_and_ones_own(self):
        keeper = TidePool()
        self.assertEqual(horizon(keeper, self.shore), "No bottle drifts at sea.")
        cast(TidePool(), "the kettle is warm", self.shore)
        self.assertEqual(horizon(keeper, self.shore), "1 bottle drifts at sea; 0 cast by you this visit.")
        respond(keeper, "cast I am still here", self.shore)
        self.assertEqual(respond(keeper, "horizon", self.shore),
                         "2 bottles drift at sea; 1 cast by you this visit.")


class ShoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.shore = os.path.join(self.dir.name, "shore.txt")

    def tearDown(self):
        self.dir.cleanup()

    def test_tide_with_two_words_leaves_a_shell(self):
        pool = TidePool()
        pool.drop("moon lantern")
        poem = tide_and_wash(pool, self.shore, "2026-11-07")
        self.assertEqual(read_shore(self.shore), f"~ tide 1 · 2026-11-07 ~\n{poem}")

    def test_tides_are_numbered_along_the_shore_across_sessions(self):
        self.assertEqual(next_tide(self.shore), 1)
        for session in (TidePool(), TidePool()):
            session.drop("moon lantern")
            tide_and_wash(session, self.shore, "2026-11-07")
        self.assertEqual([tide for tide, _, _ in pages(read_shore(self.shore))], [1, 2])
        self.assertEqual(next_tide(self.shore), 3)

    def test_tide_with_one_word_leaves_nothing(self):
        pool = TidePool()
        pool.drop("moon")
        tide_and_wash(pool, self.shore, "2026-11-07")
        self.assertFalse(os.path.exists(self.shore))

    def test_the_tide_command_dates_its_shell(self):
        pool = TidePool()
        pool.drop("moon lantern")
        respond(pool, "tide", self.shore)
        self.assertTrue(read_shore(self.shore).startswith(f"~ tide 1 · {day_of(FIRST_QUARTER)} ~"))

    def test_day_of_is_the_calendar_date(self):
        self.assertEqual(day_of(NEW_MOON), "2026-11-09")

    def test_comb_drops_a_shell_line_into_the_pool(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        pool = TidePool()
        self.assertTrue(comb(pool, self.shore).startswith('You find a shell: "moon haunts rust"'))
        self.assertEqual(pool.words, ["moon", "haunts", "rust"])

    def test_comb_on_bare_shore(self):
        pool = TidePool()
        self.assertEqual(comb(pool, self.shore), read_shore(self.shore))
        self.assertEqual(pool.words, [])

    def test_echo_brings_back_the_newest_line(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        wash_ashore(self.shore, shell(2, "salt shelters bell"))
        pool = TidePool()
        reply = respond(pool, "echo", self.shore)
        self.assertTrue(reply.startswith('The sea\'s last words come back: "salt shelters bell"'))
        self.assertEqual(pool.words, ["salt", "shelters", "bell"])

    def test_echo_on_a_bare_shore(self):
        pool = TidePool()
        self.assertIn("shore is bare", echo(pool, self.shore))
        self.assertEqual(pool.words, [])

    def test_visit_carries_a_hall_s_last_line_into_the_pool(self):
        hall = os.path.join(self.dir.name, "exhibits", "night-two")
        os.makedirs(hall)
        wash_ashore(os.path.join(hall, "shore.txt"), shell(1, "moon haunts rust\nand fern listens"))
        Path(hall, "README.md").write_text("# The second night\n", encoding="utf-8")
        pool = TidePool()
        reply = respond(pool, "visit night-two", self.shore)
        self.assertTrue(reply.startswith('In night-two (The second night), the sea\'s last words were: "and fern listens"'))
        self.assertEqual(pool.words, ["and", "fern", "listens"])
        self.assertFalse(os.path.exists(self.shore))
        copied = respond(TidePool(), "visit night-two (The second night): 1 line", self.shore)
        self.assertEqual(copied, reply)

    def test_visit_names_the_halls_when_asked_for_another(self):
        self.assertEqual(visit(TidePool(), "atlantis", self.shore), "No exhibit hangs on this coast yet.")
        os.makedirs(os.path.join(self.dir.name, "exhibits", "night-two"))
        for name in ("atlantis", "../night-two", ""):
            with self.subTest(name=name):
                self.assertEqual(visit(TidePool(), name, self.shore),
                                 "Visit one of the halls: night-two.")

    def test_comb_on_empty_or_header_only_shore(self):
        for contents in ("", "\n", "~ tide 1 ~\n\n"):
            with self.subTest(contents=contents):
                with open(self.shore, "w") as shore:
                    shore.write(contents)
                pool = TidePool()
                self.assertIn("shore is bare", comb(pool, self.shore))
                self.assertEqual(pool.words, [])

    def test_stars_on_a_bare_shore(self):
        self.assertIn("No stars yet", stars(self.shore))
        self.assertFalse(os.path.exists(os.path.join(self.dir.name, "sky.svg")))

    def test_stars_draws_the_sky_beside_the_shore(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        self.assertIn("sky.svg", respond(TidePool(), "stars", self.shore))
        with open(os.path.join(self.dir.name, "sky.svg"), encoding="utf-8") as drawn:
            self.assertEqual(drawn.read().count('class="star"'), 2)

    def test_trace_reads_the_shore(self):
        self.assertIn("no memory of moon", trace("moon", self.shore))
        wash_ashore(self.shore, shell(1, "moon haunts rust\nand moon listens"))
        self.assertEqual(respond(TidePool(), "trace moon", self.shore),
                         "moon has washed up in 2 lines:\nmoon haunts rust\nand moon listens")

    def test_spell_reads_the_shore_and_a_bare_shore_spells_letters(self):
        drawing = os.path.join(self.dir.name, "jetty.svg")
        steps = os.path.join(self.dir.name, "jetty.wav")
        ending = f"See the jetty in {drawing}.\nHear it walked in {steps}."
        self.assertEqual(spell("to", self.shore), f"T\nO\nPlanks still missing: T, O.\n{ending}")
        self.assertTrue(os.path.isfile(steps))
        wash_ashore(self.shore, shell(1, "tide remembers owl\nowl listens"))
        self.assertEqual(respond(TidePool(), "spell to", self.shore),
                         f"tide remembers owl\nowl listens\n{ending}")
        self.assertIn("Planks still missing: O.\n", spell("too", self.shore))
        self.assertIn("tide remembers owl", Path(drawing).read_text(encoding="utf-8"))
        self.assertIn("spell home", spell("", self.shore))

    def test_rhyme_reads_the_shore(self):
        self.assertIn("rhyme home", rhyme("", self.shore))
        self.assertEqual(rhyme("home", self.shore), "Nothing on the shore rhymes with home yet.")
        wash_ashore(self.shore, shell(1, "moon remembers the dome"))
        self.assertEqual(respond(TidePool(), "rhyme home", self.shore), "moon remembers the dome")

    def test_the_crab_moves_into_the_shore_s_most_remembered_line(self):
        self.assertIn("No shell", crab(self.shore))
        drawing = Path(self.dir.name, "crab.svg")
        self.assertFalse(drawing.exists())
        wash_ashore(self.shore, shell(1, "moon haunts rust\nand moon listens"))
        self.assertEqual(respond(TidePool(), "crab", self.shore),
                         'A hermit crab lives in the newest line that holds "moon", '
                         "the shore's most remembered word:\nand moon listens"
                         f"\nSee the crab in {drawing}.")
        self.assertIn('House: moon', drawing.read_text())

    def test_count_names_one_or_many(self):
        self.assertEqual([count(n, "poem") for n in (0, 1, 2)], ["0 poems", "1 poem", "2 poems"])

    def test_the_harbourmaster_reports_a_bare_coast(self):
        report = harbour(self.shore, NEW_MOON).splitlines()
        self.assertEqual(report[:5], ["The harbourmaster's report:", "0 poems on the shore",
                                      "0 bottles at sea", "0 halls in the gallery", "0 signatures in the guestbook"])
        self.assertEqual(report[-2:], ["No crab has moved in yet.", "The water is high water. Low water comes at 12:00 UTC."])

    def test_shore_note_counts_the_day_s_poems(self):
        kept = [(1, "", "moon"), (2, "2026-11-06", "rust"), (3, "2026-11-07", "lamp")]
        self.assertEqual(shore_note(kept, "2026-11-07"), "3 poems on the shore, 1 today, tide 3 the newest")
        self.assertEqual(shore_note([], "2026-11-07"), "0 poems on the shore")

    def test_the_harbourmaster_counts_what_the_coast_holds(self):
        pool = TidePool()
        pool.drop("moon lantern")
        tide_and_wash(pool, self.shore, "2026-11-07")
        cast(pool, "the light is still on", self.shore)
        os.makedirs(os.path.join(self.dir.name, "exhibits", "first-night"))
        sign_book("Alice", self.shore, "2026-11-07")
        report = respond(TidePool(), "harbour", self.shore).splitlines()
        self.assertEqual(report[1:5], ["1 poem on the shore, 0 today, tide 1 the newest", "1 bottle at sea",
                                       "1 hall in the gallery", "1 signature in the guestbook"])
        places, walks = len(chart_places(Path(CHART).read_text(encoding="utf-8"))), len(stories(STORY_DIR))
        self.assertEqual(report[5], f"{places} places on the chart, {walks} walks on the shelf")
        self.assertIn(report[6], ('The crab lives by "moon".', 'The crab lives by "lantern".'))

    def test_tour_follows_a_word_through_the_halls(self):
        self.assertIn("tour lamp", tour("", self.shore))
        self.assertEqual(tour("lamp", self.shore), "No hall remembers lamp.")
        for name, poem in (("first-night", "lamp haunts rust\nand lamp listens"), ("quiet", "moon shelters salt"),
                           ("dusk", "lamp holds window")):
            os.makedirs(os.path.join(self.dir.name, "exhibits", name))
            wash_ashore(os.path.join(self.dir.name, "exhibits", name, "shore.txt"), shell(1, poem))
            Path(self.dir.name, "exhibits", name, "README.md").write_text(f"# {name}\n", encoding="utf-8")
        Path(self.dir.name, "exhibits", "first-night", "README.md").write_text("# First night\n", encoding="utf-8")
        self.assertEqual(respond(TidePool(), "tour lamp", self.shore),
                         "lamp is remembered in 2 halls:\n  dusk: 1 line\n  first-night (First night): 2 lines")

    def test_hall_name_adds_a_title_only_when_it_says_more(self):
        hall = os.path.join(self.dir.name, "exhibits")
        for name, title in (("dusk", "dusk"), ("dry-step", "The step stayed under the sea")):
            os.makedirs(os.path.join(hall, name))
            Path(hall, name, "README.md").write_text(f"# {title}\n", encoding="utf-8")
        self.assertEqual(hall_name(hall, "dusk"), "dusk")
        self.assertEqual(hall_name(hall, "dry-step"), "dry-step (The step stayed under the sea)")

    def test_water_note_says_when_to_wade(self):
        self.assertEqual(water_note(NEW_MOON), "The water is high water. Low water comes at 12:00 UTC.")
        low = NEW_MOON + timedelta(hours=TIDE_HOURS / 2)
        self.assertEqual(water_note(low), "The water is low water: wade out now.")

    def test_wade_reaches_the_oldest_shell_only_at_low_water(self):
        low = NEW_MOON + timedelta(hours=TIDE_HOURS / 2)
        self.assertEqual(wade(TidePool(), self.shore, low), BARE)
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        wash_ashore(self.shore, shell(2, "salt shelters bell"))
        pool = TidePool()
        self.assertTrue(wade(pool, self.shore, low).startswith(
            'At low water you wade out to the oldest shell: "moon haunts rust"'))
        self.assertEqual(pool.words, ["moon", "haunts", "rust"])
        self.assertEqual(wade(TidePool(), self.shore, NEW_MOON),
                         "The water is high water. Low water comes at 12:00 UTC.")
        self.assertEqual(respond(TidePool(), "wade", self.shore),
                         "The water is rising. Low water comes at 18:43 UTC.")

    def test_water_times_lists_the_next_turns_of_the_water(self):
        self.assertEqual(water_times(NEW_MOON), "The water is high water now. Next (UTC):\n"
                                                "  08:16  falling\n  12:00  low water\n  14:29  rising")

    def test_tidetable_draws_the_dial_beside_the_shore(self):
        drawing = os.path.join(self.dir.name, "tideclock.svg")
        self.assertEqual(tidetable(NEW_MOON, self.shore), f"{water_times(NEW_MOON)}\nSee the dial in {drawing}.")
        self.assertIn("<title>The water is high water</title>", Path(drawing).read_text(encoding="utf-8"))
        self.assertTrue(respond(TidePool(), "tidetable", self.shore).startswith("The water is rising now."))

    def test_the_guestbook_keeps_each_signature(self):
        self.assertIn("open and empty", guestbook(self.shore))
        self.assertIn("sign Alice", sign_book("", self.shore, "2026-11-06"))
        self.assertEqual(sign_book("Alice", self.shore, "2026-11-06"),
                         "The guestbook keeps your name: 2026-11-06 · Alice")
        respond(TidePool(), "sign Bob", self.shore)
        self.assertEqual(respond(TidePool(), "guestbook", self.shore),
                         f"The guestbook holds 2 signatures:\n  2026-11-06 · Alice\n  {day_of(FIRST_QUARTER)} · Bob")

    def test_completions_offer_the_commands_that_begin_so(self):
        self.assertEqual(completions("ho", "ho"), ["horizon"])
        self.assertEqual(completions("re", "re"), ["read", "recite"])
        self.assertEqual(completions("zz", "zz"), [])

    def test_completions_after_a_command_offer_its_stories_halls_or_commands(self):
        self.assertEqual(completions("read low", "low"), ["low_water"])
        self.assertEqual(completions("visit ticket", "ticket"), ["ticket-for-yesterday"])
        self.assertEqual(completions("help wa", "wa"), ["wade", "wall"])
        self.assertEqual(completions("drop ho", "ho"), [])

    def test_choices_after_name_what_each_command_takes(self):
        self.assertIn("lighthouse", choices_after("read"))
        self.assertIn("first-night", choices_after("visit"))
        self.assertIn("tide", choices_after("help"))
        self.assertEqual(choices_after("drop"), ())
        self.assertEqual(choices_after("trace", self.shore), set())
        self.assertEqual(choices_after("diary", self.shore), {"today", "yesterday"})
        wash_ashore(self.shore, shell(1, "Lantern haunts rust,", "2026-11-07"))
        self.assertEqual(choices_after("diary", self.shore), {"today", "yesterday", "2026-11-07"})
        for command in ("trace", "first", "last", "wall", "kin", "seek", "tour", "rhyme", "spell"):
            with self.subTest(command=command):
                self.assertEqual(choices_after(command, self.shore), {"lantern", "rust"})

    def test_complete_answers_each_state_then_none(self):
        self.assertEqual([complete("ti", "ti", state) for state in range(4)], ["tide", "tidetable", None, None])

    def test_enable_editing_installs_a_line_aware_completer(self):
        import readline
        enable_editing()
        self.assertEqual(readline.get_completer()("hor", 0), "horizon")
        self.assertEqual(readline.get_completer_delims(), " ")

    def test_washed_up_names_the_tide_and_day_a_word_arrived_and_last_came(self):
        self.assertEqual(washed_up("moon", "first", self.shore), "The shore has no memory of moon.")
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        wash_ashore(self.shore, shell(2, "moon listens\nand moon sleeps", "2026-11-09"))
        self.assertEqual(respond(TidePool(), "first moon", self.shore),
                         "moon first washed up on tide 1 · before the shore kept dates; 1 poem kept since:\nmoon haunts rust")
        self.assertEqual(respond(TidePool(), "last moon", self.shore),
                         "moon last washed up on tide 2 · 2026-11-09; the newest poem:\nand moon sleeps")

    def test_kept_since_counts_the_poems_after(self):
        self.assertEqual(kept_since(0), "the newest poem")
        self.assertEqual(kept_since(2), "2 poems kept since")

    def test_wall_draws_a_mark_for_every_poem_holding_the_word(self):
        drawing = os.path.join(self.dir.name, "wall.svg")
        self.assertEqual(wall("salt", self.shore), "The shore has no memory of salt.")
        wash_ashore(self.shore, shell(1, "salt haunts rust"))
        wash_ashore(self.shore, shell(2, "fern sleeps"))
        wash_ashore(self.shore, shell(3, "salt listens", "2026-11-09"))
        self.assertEqual(respond(TidePool(), "wall salt", self.shore),
                         f"salt has marked the harbour wall 2 times.\nSee the wall in {drawing}.")
        self.assertIn(">tide 3 · 2026-11-09</text>", Path(drawing).read_text(encoding="utf-8"))

    def test_wall_alone_paints_the_most_remembered_word(self):
        self.assertEqual(wall("", self.shore), BARE)
        wash_ashore(self.shore, shell(1, "rust haunts salt\nrust listens"))
        self.assertTrue(wall("", self.shore).startswith("rust has marked the harbour wall 1 time."))

    def test_most_remembered_drops_punctuation_and_is_empty_on_a_bare_shore(self):
        self.assertEqual(most_remembered(self.shore), "")
        wash_ashore(self.shore, shell(1, "rust, rust, salt"))
        self.assertEqual(most_remembered(self.shore), "rust")

    def test_washed_up_needs_a_word(self):
        self.assertIn("last lantern", washed_up("", "last", self.shore))

    def test_trace_needs_a_word(self):
        self.assertIn("trace lantern", trace("", self.shore))

    def test_ask_answers_from_the_shore(self):
        self.assertIn("no answer yet", ask("where is the lantern", self.shore))
        wash_ashore(self.shore, shell(1, "lantern haunts window\nmoon shelters rust"))
        self.assertEqual(respond(TidePool(), "ask where is the lantern?", self.shore),
                         "The sea answers: lantern haunts window")

    def test_ask_needs_a_question(self):
        self.assertIn("ask where is the lantern", ask("", self.shore))

    def test_signal_on_a_bare_shore_asks_for_words(self):
        self.assertIn("signal fog on the rocks", signal("", self.shore))

    def test_unencodable_signal_keeps_the_previous_signal(self):
        signal("home", self.shore)
        files = [Path(self.dir.name, name) for name in ("signal.svg", "signal.wav")]
        previous = [file.read_bytes() for file in files]
        self.assertIn("letters A–Z or digits 0–9", signal("— !!!", self.shore))
        self.assertEqual([file.read_bytes() for file in files], previous)

    def test_signal_flashes_and_sounds_the_words_given(self):
        sounded = os.path.join(self.dir.name, "signal.wav")
        drawing = os.path.join(self.dir.name, "signal.svg")
        self.assertEqual(respond(TidePool(), "signal sos", self.shore),
                         f'The lamp flashes "sos":\n{"sos":<14}··· ——— ···\nHear it in {sounded}.\nWatch it in {drawing}.')
        self.assertTrue(os.path.exists(sounded))
        self.assertIn('<animate', Path(drawing).read_text())

    def test_signal_without_words_flashes_the_sea_s_last_line(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust\nand fern listens"))
        self.assertTrue(signal("", self.shore).startswith('The lamp flashes "and fern listens":'))

    def test_kin_reads_the_shore(self):
        self.assertIn("no kin", kin("window", self.shore))
        wash_ashore(self.shore, shell(1, "window haunts coat\ncoat remembers window"))
        self.assertEqual(respond(TidePool(), "kin window", self.shore),
                         f"window keeps company with:\n{'coat':>14} oo")

    def test_kin_needs_a_word(self):
        self.assertIn("kin window", kin("", self.shore))

    def test_seek_two_lone_words_meet_at_once_and_only_the_meeting_is_kept(self):
        pool = TidePool()
        pool.drop("moon lantern")
        reply = respond(pool, "seek moon lantern", self.shore)
        self.assertTrue(reply.startswith("After 1 tide, moon met lantern:"))
        self.assertEqual(read_shore(self.shore).count("~ tide "), 1)

    def test_seek_gives_up_after_twelve_tides(self):
        pool = TidePool()
        pool.drop("moon lantern salt")
        with patch.object(pool, "tide", return_value="moon haunts salt\nand lantern listens"):
            self.assertIn("Twelve tides passed", seek(pool, "moon lantern", self.shore))
        self.assertFalse(os.path.exists(self.shore))

    def test_recital_on_a_bare_shore_writes_nothing(self):
        self.assertIn("shore is bare", recital(self.shore))
        self.assertEqual(os.listdir(self.dir.name), [])

    def test_recital_reads_every_poem_line(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust\nand fern listens"))
        reply = respond(TidePool(), "recite", self.shore)
        self.assertTrue(reply.endswith("2 lines long."))
        self.assertTrue(os.path.exists(os.path.join(self.dir.name, "recital.wav")))

    def test_atlas_gathers_the_coast_beside_the_shore(self):
        os.makedirs(os.path.join(self.dir.name, "exhibits", "first-night"))
        Path(self.dir.name, "exhibits", "first-night", "README.md").write_text("# First night\n", encoding="utf-8")
        reply = respond(TidePool(), "atlas", self.shore)
        written = os.path.join(self.dir.name, "atlas.html")
        self.assertEqual(reply, f"Open {written} to read the whole coast in one atlas.")
        with open(written, encoding="utf-8") as page:
            text = page.read()
        self.assertIn("<h2>1 — The lighthouse</h2>", text)
        self.assertIn("exhibits/first-night/book.html", text)

    def test_seek_needs_two_words_in_the_water(self):
        pool = TidePool()
        pool.drop("moon")
        for arg in ("moon", "moon lantern", ""):
            with self.subTest(arg=arg):
                self.assertIn("seek moon lantern", seek(pool, arg, self.shore))

    def test_strandline_on_bare_shore(self):
        self.assertEqual(strandline(self.shore), read_shore(self.shore))

    def test_strandline_reads_the_shore(self):
        wash_ashore(self.shore, shell(1, "salt shelters bell"))
        self.assertEqual(strandline(self.shore), f"{'salt':>14} o\n{'bell':>14} o")


class WeatherTest(unittest.TestCase):
    def test_valid_choice_changes_weather(self):
        pool = TidePool()
        self.assertEqual(change_weather(pool, "storm"), "The weather turns to storm.")
        self.assertEqual(pool.weather, "storm")

    def test_empty_choice_reports_weather(self):
        self.assertIn("is calm", change_weather(TidePool(), ""))

    def test_unknown_choice_keeps_weather(self):
        pool = TidePool()
        self.assertIn("Choose weather", change_weather(pool, "hail"))
        self.assertEqual(pool.weather, "calm")

    def test_ice_holds_words_still(self):
        pool = TidePool()
        pool.drop("moon rust")
        change_weather(pool, "ice")
        self.assertIn(pool.tide().split(" ", 1)[1].rsplit(" ", 1)[0], WEATHER["ice"])


class RespondTest(unittest.TestCase):
    def test_drop_then_look(self):
        pool = TidePool()
        self.assertEqual(respond(pool, "drop moon", "unused"), pool.look())
        self.assertEqual(pool.words, ["moon"])

    def test_shells_reads_shore(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            wash_ashore(shore, "a shell")
            self.assertEqual(respond(TidePool(), "shells", shore), "a shell")

    def test_shells_counts_back_from_the_newest(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            for tide, poem in ((1, "moon haunts rust"), (2, "salt shelters bell"), (1, "and fern listens")):
                wash_ashore(shore, shell(tide, poem))
            self.assertEqual(respond(TidePool(), "shells 2", shore),
                             "~ tide 2 ~\nsalt shelters bell\n\n~ tide 1 ~\nand fern listens")
            self.assertEqual(shells("9", shore), read_shore(shore))

    def test_shells_needs_a_real_count(self):
        for count in ("0", "three", "-1"):
            with self.subTest(count=count):
                self.assertEqual(shells(count, "unused"), "Count shells with a number: shells 3")
        self.assertIn("shore is bare", shells("2", "/no/such/shore.txt"))

    def test_diary_reads_the_shore_by_day(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            self.assertIn("shore is bare", shore_diary("", shore))
            wash_ashore(shore, shell(1, "moon haunts rust", "2026-11-06"))
            wash_ashore(shore, shell(2, "lantern holds window", "2026-11-07"))
            self.assertEqual(respond(TidePool(), "diary", shore),
                             f"{'2026-11-06':<28} o 1\n{'2026-11-07':<28} o 1\n{'in all':<28} 2")
            self.assertEqual(respond(TidePool(), "diary 2026-11-07", shore), "~ tide 2 · 2026-11-07 ~\nlantern holds window")
            self.assertEqual(shore_diary("2026-11-05", shore), "No poems are dated 2026-11-05. Type diary to see the days.")
            self.assertEqual(shore_diary("today", shore), "No poems are dated 2026-11-17. Type diary to see the days.")
            wash_ashore(shore, shell(3, "salt keeps time", "2026-11-17"))
            self.assertEqual(shore_diary("today", shore), "~ tide 3 · 2026-11-17 ~\nsalt keeps time")
            self.assertEqual(shore_diary("yesterday", shore), "No poems are dated 2026-11-16. Type diary to see the days.")

    def test_unknown_command_hints(self):
        self.assertIn("shells", respond(TidePool(), "swim", "unused"))

    def test_weather_argument_reaches_change_weather(self):
        pool = TidePool()
        respond(pool, "weather  fog", "unused")
        self.assertEqual(pool.weather, "fog")

    def test_listen_to_empty_pool(self):
        self.assertIn("silent", respond(TidePool(), "listen", "unused"))

    def test_listen_writes_tide_wav_beside_shore(self):
        with tempfile.TemporaryDirectory() as directory:
            pool = TidePool()
            pool.drop("moon")
            reply = respond(pool, "listen", os.path.join(directory, "shore.txt"))
            self.assertTrue(os.path.exists(os.path.join(directory, "tide.wav")))
            self.assertIn("tide.wav", reply)

    def test_postcard_writes_svg_beside_shore(self):
        with tempfile.TemporaryDirectory() as directory:
            pool = TidePool()
            pool.drop("moon")
            reply = respond(pool, "postcard", os.path.join(directory, "shore.txt"))
            self.assertTrue(os.path.exists(os.path.join(directory, "postcard.svg")))
            self.assertIn("postcard.svg", reply)
            with open(os.path.join(directory, "postcard.svg")) as card:
                self.assertIn('#d8e8df', card.read())

    def test_bind_on_bare_shore_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            reply = respond(TidePool(), "bind", os.path.join(directory, "shore.txt"))
            self.assertIn("shore is bare", reply)
            self.assertEqual(os.listdir(directory), [])

    def test_bind_writes_book_beside_shore(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            wash_ashore(shore, shell(1, "moon haunts rust"))
            self.assertIn("book.html", respond(TidePool(), "bind", shore))
            with open(os.path.join(directory, "book.html"), encoding="utf-8") as bound:
                self.assertIn("<pre>moon haunts rust</pre>", bound.read())

    def test_exhibit_hangs_every_keepsake(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            wash_ashore(shore, shell(1, "moon haunts rust"))
            pool = TidePool()
            pool.drop("moon rust")
            self.assertIn("exhibit hangs", respond(pool, "exhibit night-two", shore))
            hung = sorted(os.listdir(os.path.join(directory, "exhibits", "night-two")))
            self.assertEqual(hung, ["README.md", "book.html", "postcard.svg",
                                    "shore.txt", "sky.svg", "tide.wav", "tideclock.svg"])

    def test_dream_needs_two_pieces(self):
        pool = TidePool()
        pool.drop("moon")
        self.assertIn("needs two pieces", dream(pool, "unused"))
        self.assertEqual(pool.tides, 0)

    def test_dream_passes_through_every_weather_once(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            pool = TidePool()
            pool.drop("moon rust lantern")
            night = dream(pool, shore)
            headers = [line for line in night.splitlines() if line.startswith("~ ")]
            self.assertEqual(sorted(headers), sorted(f"~ {weather} ~" for weather in WEATHER))
            self.assertTrue(night.endswith(f"You wake to {pool.weather} water."))
            self.assertEqual(read_shore(shore).count("~ tide "), len(WEATHER))
            self.assertGreater(len(pool.words), 3)

    def test_dream_once_tides_then_combs(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            pool = TidePool()
            pool.drop("moon rust")
            told = dream_once(pool, shore, "fog")
            self.assertTrue(told.startswith("~ fog ~\n"))
            self.assertEqual(pool.weather, "fog")
            self.assertGreater(len(pool.words), 2)

    def test_help_for_one_command_gives_only_its_line(self):
        self.assertTrue(help_for("wade").startswith("wade "))
        self.assertEqual(len(help_for("wade").splitlines()), 1)
        self.assertEqual(respond(TidePool(), "help wade", "unused"), help_for("wade"))
        self.assertEqual(help_for("kraken"), "No command is called kraken. Type help for all of them.")
        self.assertEqual(respond(TidePool(), "help", "unused"), HELP)

    def test_help_names_every_command(self):
        for name in COMMANDS:
            with self.subTest(name=name):
                self.assertIn(f"\n{name} ", "\n" + HELP)

    def test_help_lines_align_and_stay_within_a_hundred_characters(self):
        guide = HELP.split("\n\n")[0].splitlines()
        for line in guide:
            with self.subTest(line=line):
                self.assertLessEqual(len(line), 100)
                self.assertEqual((line[18], line[19] != " "), (" ", True))

    def test_a_quiet_visitor_on_a_bare_shore_never_meets_a_short_tide(self):
        """Every story played with only Enter, on a bare shore beside a copy of the gallery."""
        with tempfile.TemporaryDirectory() as copies:
            gallery = shutil.copytree(os.path.join(os.path.dirname(STORY_DIR), "exhibits"),
                                      os.path.join(copies, "exhibits"))
            for name, file in stories(STORY_DIR).items():
                with self.subTest(story=name), tempfile.TemporaryDirectory() as directory:
                    os.symlink(gallery, os.path.join(directory, "exhibits"))
                    beats = story_beats(Path(STORY_DIR, file).read_text(encoding="utf-8"))
                    pool, shore = TidePool(), os.path.join(directory, "shore.txt")
                    told = "\n".join(tell(pool, beat, shore) for beat in beats)
                    self.assertNotIn("It needs two words", told)

    def test_every_story_speaks_only_sea_commands(self):
        for name, file in stories(STORY_DIR).items():
            with open(os.path.join(STORY_DIR, file), encoding="utf-8") as story:
                beats = story_beats(story.read())
            for command in (line for kind, body in beats if kind == "sea" for line in body):
                with self.subTest(story=name, command=command):
                    self.assertIn(command.partition(" ")[0], COMMANDS)

    def test_moonrise_drops_the_phase_name(self):
        pool = TidePool()
        reply = moonrise(pool, datetime(2026, 11, 24, 14, 53, tzinfo=timezone.utc))
        self.assertTrue(reply.startswith("The full moon rises."))
        self.assertEqual(pool.words, ["full", "moon"])

    def test_low_water_on_a_day_comes_after_now_or_none_is_left(self):
        anchor_day = datetime(2026, 11, 9, 7, 2, tzinfo=timezone.utc)
        self.assertEqual(low_water_on(anchor_day, anchor_day), "12:00")
        late = datetime(2026, 11, 9, 22, 0, tzinfo=timezone.utc)
        self.assertEqual(low_water_on(late, late), "none left")
        self.assertEqual(low_water_on(late + timedelta(days=1), late), "00:25")

    def test_almanac_charts_a_week_of_tides(self):
        rows = almanac(datetime(2026, 11, 9, 7, 2, tzinfo=timezone.utc)).splitlines()
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[0], "Mon 09  ~~~~~~~~~ new moon        low water 12:00")
        self.assertTrue(rows[1].endswith("low water 00:25"))

    def test_tonight_names_the_moon_and_draws_the_tide(self):
        new_moon = datetime(2026, 11, 9, 7, 2, tzinfo=timezone.utc)
        self.assertEqual(tonight(new_moon),
                         "This morning: new moon · tides ~~~~~~~~~ · high water · spring tide")
        first_quarter = datetime(2026, 11, 17, 11, 48, tzinfo=timezone.utc)
        self.assertEqual(tonight(first_quarter), "This morning: first quarter · tides ~ · rising")

    def test_drop_and_look_scatters_the_words_then_shows_the_pool(self):
        pool = TidePool()
        self.assertEqual(drop_and_look(pool, "moon rust"), "    moon\n           rust")
        self.assertEqual(pool.words, ["moon", "rust"])
        self.assertEqual(drop_and_look(pool, ""), "Drop some words: drop moon rust lantern")

    def test_pick_up_names_the_finding_and_drops_its_words(self):
        pool = TidePool()
        self.assertEqual(pick_up(pool, "moon rust", "The comb brought back"),
                         'The comb brought back: "moon rust"\n    moon\n           rust')
        self.assertEqual(pool.words, ["moon", "rust"])

    def test_letters_names_the_initials_and_the_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            self.assertIn("shore is bare", letters(shore))
            wash_ashore(shore, shell(1, "moon haunts rust\nand moon listens\nmist remembers"))
            self.assertEqual(respond(TidePool(), "letters", shore),
                             "Lines begin with: a 1 · m 2\nNo line begins with: b c d e f g h i j k l n o p q r s t u v w x y z")
            wash_ashore(shore, shell(2, "\n".join(f"{letter}oon" for letter in "bcdefghijklnopqrstuvwxyz")))
            self.assertEqual(letters(shore).splitlines(), [letters(shore).splitlines()[0]])
            self.assertTrue(letters(shore).startswith("Lines begin with: a 1 · b 1 · c 1"))

    def test_is_spring_at_new_moon_but_not_first_quarter(self):
        self.assertTrue(is_spring(NEW_MOON))
        self.assertFalse(is_spring(FIRST_QUARTER))

    def test_sea_and_guestbook_lie_beside_the_shore(self):
        shore = os.path.join("coast", "shore.txt")
        self.assertEqual(sea_of(shore), os.path.join("coast", "sea.txt"))
        self.assertEqual(book_of(shore), os.path.join("coast", "guestbook.txt"))

    def test_last_words_are_the_newest_poem_s_last_line(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            self.assertEqual(last_words(shore), [])
            wash_ashore(shore, shell(1, "moon haunts rust\nand lantern listens", "2026-11-07"))
            self.assertEqual(last_words(shore), ["The sea last said, on 2026-11-07: and lantern listens"])

    def test_welcome_remembers_the_last_line_the_sea_said(self):
        new_moon = datetime(2026, 11, 9, 7, 2, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            self.assertEqual(welcome(new_moon, shore), tonight(new_moon))
            wash_ashore(shore, shell(1, "moon haunts rust\nand lantern listens"))
            self.assertEqual(welcome(new_moon, shore),
                             f"{tonight(new_moon)}\nThe sea last said: and lantern listens\n{new_page(new_moon, shore)[0]}")
            wash_ashore(shore, shell(2, "salt shelters bell", "2026-11-09"))
            self.assertEqual(welcome(new_moon, shore),
                             f"{tonight(new_moon)}\nThe sea last said, on 2026-11-09: salt shelters bell")

    def test_new_page_invites_the_day_s_first_poem(self):
        new_moon = datetime(2026, 11, 9, 7, 2, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            self.assertEqual(new_page(new_moon, shore), [])
            wash_ashore(shore, shell(1, "salt shelters bell", "2026-11-08"))
            self.assertEqual(new_page(new_moon, shore),
                             ["No poem has been kept today yet; yours would open a new page in the diary."])
            wash_ashore(shore, shell(2, "moon haunts rust", "2026-11-09"))
            self.assertEqual(new_page(new_moon, shore), [])
            cast(TidePool(), "the kettle is warm", shore)
            self.assertEqual(welcome(new_moon, shore).splitlines()[-1], "A bottle drifts offshore. Type find to bring it in.")

    def test_the_greeting_mentions_wading_only_at_low_water(self):
        low = NEW_MOON + timedelta(hours=TIDE_HOURS / 2)
        self.assertEqual(wading(low), ["The water is low. Type wade to reach the oldest shell."])
        self.assertEqual(wading(NEW_MOON), [])
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            self.assertEqual(welcome(low, shore).splitlines()[-1], wading(low)[0])

    def test_offshore_counts_the_bottles_waiting(self):
        with tempfile.TemporaryDirectory() as directory:
            shore = os.path.join(directory, "shore.txt")
            self.assertEqual(offshore(shore), [])
            cast(TidePool(), "the kettle is warm", shore)
            self.assertEqual(offshore(shore), ["A bottle drifts offshore. Type find to bring it in."])
            cast(TidePool(), "I am still here", shore)
            self.assertEqual(offshore(shore), ["2 bottles drift offshore. Type find to bring the oldest in."])

    def test_moon_command_answers(self):
        self.assertIn("rises", respond(TidePool(), "moon", "unused"))

    def test_quit_says_farewell(self):
        self.assertEqual(respond(TidePool(), "quit", "unused"), "The sea keeps its silence.")


class StoryTest(unittest.TestCase):
    def test_tell_story_returns_prose(self):
        self.assertEqual(tell(TidePool(), ("story", "The beam fades."), "unused"), "The beam fades.")

    def test_tell_sea_runs_commands_against_pool(self):
        pool = TidePool()
        told = tell(pool, ("sea", ["drop lamp", "look"]), "unused")
        self.assertEqual(told, f"shore> drop lamp\n{pool.look()}\nshore> look\n{pool.look()}")
        self.assertEqual(pool.words, ["lamp"])


class TerminalReadingTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        shore = os.path.join(self.dir.name, "shore.txt")
        self.shore = patch.object(tidepool, "SHORE", shore)
        self.shore.start()

    def tearDown(self):
        self.shore.stop()
        self.dir.cleanup()

    def test_pause_answers_sea_commands_until_enter(self):
        pool, out = TidePool(), StringIO()
        with patch("builtins.input", side_effect=["drop moon", ""]), redirect_stdout(out):
            self.assertTrue(pause(pool))
        self.assertEqual(pool.words, ["moon"])

    def test_pause_leaves_on_q(self):
        with patch("builtins.input", side_effect=["q"]), redirect_stdout(StringIO()) as out:
            self.assertFalse(pause(TidePool()))
        self.assertIn("The sea keeps its silence.", out.getvalue())

    def test_play_story_into_an_existing_pool(self):
        pool = TidePool()
        pool.drop("compass")
        with patch("builtins.input", return_value=""), redirect_stdout(StringIO()):
            play_story(story_path("lighthouse"), pool)
        self.assertIn("compass", pool.words)
        self.assertIn("lighthouse", pool.words)

    def test_read_story_with_unknown_name_lists_the_shelf(self):
        with redirect_stdout(StringIO()) as out:
            read_story(TidePool(), "atlantis")
        self.assertTrue(out.getvalue().startswith("Choose a story:\n  read 1 "))
        self.assertIn("read 2              The bell\n", out.getvalue())

    def test_aside_handles_only_the_terminal_s_own_commands(self):
        with redirect_stdout(StringIO()) as out:
            self.assertTrue(aside(TidePool(), "read atlantis"))
            self.assertFalse(aside(TidePool(), "tide"))
            self.assertFalse(aside(TidePool(), "drifting"))
        self.assertTrue(out.getvalue().startswith("Choose a story"))

    def test_drift_hands_the_pool_and_weather_to_the_screen(self):
        pool = TidePool()
        pool.drop("moon rust")
        with patch("sys.stdout.isatty", return_value=True), patch.object(tidepool, "drift") as shown:
            self.assertTrue(aside(pool, "drift"))
        shown.assert_called_once_with(["moon", "rust"], "calm")

    def test_drift_without_a_terminal_says_so(self):
        with redirect_stdout(StringIO()) as out:
            watch_drift(TidePool())
        self.assertIn("needs a terminal window", out.getvalue())


if __name__ == "__main__":
    unittest.main()
