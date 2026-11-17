import os
import tempfile
import unittest

from shore import (acrostic, answer, brightest, crab_home, held_pages, remembering, shore_text, gaps, is_gap, rhymes, cast_bottle, heaps, initials, is_thing, kept_pages, kindred, meets, poem_lines, read_shore,
                   remembered, shell, shore_lines, take_bottle, things, traces, unpack_bottle, drifting,
                   wash_ashore, wrack)


class ShoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.shore = os.path.join(self.dir.name, "shore.txt")

    def tearDown(self):
        self.dir.cleanup()

    def test_shell_labels_poem_with_tide_number(self):
        self.assertEqual(shell(3, "moon becomes rust"), "~ tide 3 ~\nmoon becomes rust\n")

    def test_shell_carries_its_day(self):
        self.assertEqual(shell(3, "moon becomes rust", "2026-11-07"),
                         "~ tide 3 · 2026-11-07 ~\nmoon becomes rust\n")

    def test_kept_pages_reads_each_shell_and_none_from_a_bare_shore(self):
        self.assertEqual(kept_pages(self.shore), [])
        wash_ashore(self.shore, shell(1, "moon becomes rust", "2026-11-07"))
        self.assertEqual(kept_pages(self.shore), [(1, "2026-11-07", "moon becomes rust")])

    def test_poem_lines_skip_dated_headers_too(self):
        self.assertEqual(poem_lines("~ tide 3 · 2026-11-07 ~\nmoon becomes rust"), ["moon becomes rust"])

    def test_bare_shore(self):
        self.assertEqual(read_shore(self.shore), "The shore is bare. No tide has left a shell.")

    def test_wash_ashore_appends_entries(self):
        wash_ashore(self.shore, "first")
        wash_ashore(self.shore, "second")
        self.assertEqual(read_shore(self.shore), "first\nsecond")

    def test_poem_lines_keep_a_line_that_only_begins_like_a_header(self):
        text = "~ tide 1 · 2026-11-06 ~\n~ tide of salt becomes moon\n\n~ tide 2 ~\nrust listens"
        self.assertEqual(poem_lines(text), ["~ tide of salt becomes moon", "rust listens"])

    def test_poem_lines_skip_tide_headers_and_blanks(self):
        text = "~ tide 1 ~\nmoon haunts rust\n\n~ tide 2 ~\nand fern listens"
        self.assertEqual(poem_lines(text), ["moon haunts rust", "and fern listens"])

    def test_shore_lines_of_a_missing_shore(self):
        self.assertEqual(shore_lines(self.shore), [])

    def test_shore_text_is_empty_before_any_shell_never_the_bare_sentence(self):
        self.assertEqual(shore_text(self.shore), "")
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        self.assertEqual(shore_text(self.shore), "~ tide 1 ~\nmoon haunts rust")

    def test_shore_lines_of_a_kept_shore(self):
        wash_ashore(self.shore, shell(1, "moon haunts rust"))
        self.assertEqual(shore_lines(self.shore), ["moon haunts rust"])

    def test_bottles_are_found_oldest_first_and_only_once(self):
        sea = os.path.join(self.dir.name, "sea.txt")
        self.assertEqual(take_bottle(sea), "")
        cast_bottle(sea, "the light is still on")
        cast_bottle(sea, "bread on the table")
        self.assertEqual(take_bottle(sea), "the light is still on")
        self.assertEqual(take_bottle(sea), "bread on the table")
        self.assertEqual(take_bottle(sea), "")

    def test_take_bottle_passes_over_ones_own(self):
        sea = os.path.join(self.dir.name, "sea.txt")
        mine = cast_bottle(sea, "mine")
        cast_bottle(sea, "yours")
        self.assertEqual(take_bottle(sea, [mine]), "yours")
        self.assertEqual(take_bottle(sea, [mine]), "")
        self.assertEqual(take_bottle(sea), "mine")

    def test_old_plain_text_bottles_survive_beside_new_bottles(self):
        sea = os.path.join(self.dir.name, "sea.txt")
        with open(sea, "w", encoding="utf-8") as water:
            water.write("an old message\n")
        mine = cast_bottle(sea, "a new message")
        self.assertEqual(take_bottle(sea, [mine]), "an old message")
        self.assertEqual(take_bottle(sea, [mine]), "")
        self.assertEqual(take_bottle(sea), "a new message")

    def test_drifting_names_each_bottle_at_sea_oldest_first(self):
        sea = os.path.join(self.dir.name, "sea.txt")
        self.assertEqual(drifting(sea), [])
        with open(sea, "w", encoding="utf-8") as water:
            water.write("an old message\n")
        mine = cast_bottle(sea, "a new message")
        self.assertEqual(drifting(sea), [None, mine])


class UnpackBottleTest(unittest.TestCase):
    def test_a_new_bottle_carries_its_identity(self):
        identity = "0123456789abcdef0123456789abcdef"
        self.assertEqual(unpack_bottle(identity + "\tbread on the table"),
                         (identity, "bread on the table"))

    def test_an_old_bottle_is_its_whole_line(self):
        self.assertEqual(unpack_bottle("the light\tis still on"), (None, "the light\tis still on"))


class ReadingTest(unittest.TestCase):
    def test_remembering_names_the_shores_that_trace_a_word(self):
        shores = {"first": "~ tide 1 ~\nlamp haunts rust\nand lamp listens",
                  "second": "~ tide 1 ~\nmoon shelters salt",
                  "third": "~ tide 1 ~\nthe lamp remembers"}
        self.assertEqual(remembering("lamp", shores), [("first", 2), ("third", 1)])
        self.assertEqual(remembering("kraken", shores), [])

    def test_crab_home_is_the_newest_line_with_the_most_remembered_word(self):
        text = ("~ tide 1 ~\nmoon haunts rust\n\n~ tide 2 ~\nrust shelters lamp\n\n"
                "~ tide 3 ~\nthe lamp remembers rust\nand salt listens")
        self.assertEqual(crab_home(text), ("rust", "the lamp remembers rust"))
        self.assertEqual(crab_home("~ tide 1 ~\nand listens"), None)

    def test_crab_home_keeps_a_word_s_punctuation_as_remembered_does(self):
        self.assertEqual(crab_home("~ tide 1 ~\nlamp, lamp, rust"), ("lamp,", "lamp, lamp, rust"))

    def test_is_gap_knows_a_letter_left_alone(self):
        self.assertTrue(is_gap("k", "K"))
        self.assertFalse(is_gap("k", "kettle warms"))

    def test_gaps_name_each_waiting_letter_once_in_order(self):
        spelled = ["K", "E", "E", "P", "E", "R", "so am I"]
        self.assertEqual(gaps("keepers", spelled), ["K", "E", "P", "R"])
        self.assertEqual(gaps("a b", ["A", " ", "B"]), ["A", "B"])
        self.assertEqual(gaps("bob's", ["B", "O", "B", "'", "S"]), ["B", "O", "S"])
        self.assertEqual(gaps("so", ["so am I", "owl"]), [])

    def test_rhymes_share_the_last_two_letters_but_not_the_word(self):
        lines = ["the lamp is lit for home", "salt remembers the dome.", "bell listens to home"]
        self.assertEqual(rhymes("Home", lines), ["salt remembers the dome."])
        self.assertEqual(rhymes("kraken", lines), [])

    def test_acrostic_takes_the_oldest_unused_line_for_each_letter(self):
        lines = ["moon haunts rust", "Owl listens", "only salt", "mist remembers"]
        self.assertEqual(acrostic("moon", lines),
                         ["moon haunts rust", "Owl listens", "only salt", "N"])
        self.assertEqual(acrostic("mm", lines), ["moon haunts rust", "mist remembers"])

    def test_remembered_counts_things_only(self):
        text = "~ tide 1 ~\nthe moon haunts rust\nand moon listens"
        self.assertEqual(dict(remembered(text)), {"moon": 2, "rust": 1})

    def test_initials_count_lines_by_first_letter_like_an_acrostic(self):
        self.assertEqual(initials(["Moon haunts rust", "mist remembers", "and fern listens", "3 bells"]),
                         {"m": 2, "a": 1})

    def test_brightest_keeps_the_twelve_most_remembered(self):
        words = [f"word{chr(97 + n)}" for n in range(13)]
        text = "~ tide 1 ~\n" + "\n".join(" ".join(words[:n + 1]) for n in range(13))
        found = brightest(text)
        self.assertEqual(len(found), 12)
        self.assertEqual(found[0], ("worda", 13))
        self.assertNotIn(("wordm", 1), found)

    def test_no_remains_a_character_in_the_room_without_a_door(self):
        text = "~ tide 1 ~\na room with no door remembers a guest with no name"
        self.assertEqual(remembered(text)["no"], 2)
        self.assertEqual(crab_home(text), ("no", "a room with no door remembers a guest with no name"))

    def test_heaps_draw_the_seven_most_remembered(self):
        counts = remembered("~ tide 1 ~\nmoon haunts rust\nand moon listens")
        self.assertEqual(heaps(counts), f"{'moon':>14} oo\n{'rust':>14} o")

    def test_wrack_heaps_things_and_leaves_out_bridges(self):
        text = "~ tide 1 ~\nmoon haunts rust\nand moon listens\n\n~ tide 2 ~\nrust dreams of moon"
        self.assertEqual(wrack(text), f"{'moon':>14} ooo\n{'rust':>14} oo")

    def test_wrack_with_only_bridges(self):
        self.assertIn("Nothing has washed up", wrack("~ tide 1 ~\nand listens"))

    def test_wrack_leaves_articles_in_bottled_phrases_out_of_heaps(self):
        text = "~ tide 1 ~\nThe bell shelters a room\nan echo remembers the bell"
        self.assertEqual(wrack(text), f"{'bell':>14} oo\n{'room':>14} o\n{'echo':>14} o")

    def test_held_pages_lists_each_poem_holding_a_word_oldest_first(self):
        kept = [(1, "", "rust listens"), (2, "2026-11-06", "fern sleeps\nmoon haunts rust"), (3, "2026-11-07", "moon again")]
        self.assertEqual(held_pages("moon", kept), [(2, "2026-11-06", ["moon haunts rust"], 1),
                                                    (3, "2026-11-07", ["moon again"], 0)])
        self.assertEqual(held_pages("rust", kept), [(1, "", ["rust listens"], 2), (2, "2026-11-06", ["moon haunts rust"], 1)])
        self.assertEqual(held_pages("owl", kept), [])

    def test_traces_match_whole_words_and_phrases(self):
        text = ("~ tide 1 ~\nmoon haunts rust\nmoonlight shelters salt\n\n"
                "~ tide 2 ~\nthe last train home dreams of moon")
        self.assertEqual(traces("moon", text), ["moon haunts rust", "the last train home dreams of moon"])
        self.assertEqual(traces("last train", text), ["the last train home dreams of moon"])
        self.assertEqual(traces("~ tide", text), [])

    def test_kindred_counts_company_but_not_the_word_itself(self):
        text = ("~ tide 1 ~\nwindow haunts coat\nlighthouse shelters window\n\n"
                "~ tide 2 ~\ncoat remembers window\nrust dreams of salt")
        self.assertEqual(dict(kindred("window", text)), {"coat": 2, "lighthouse": 1})

    def test_kindred_of_a_phrase_leaves_out_its_own_words(self):
        text = "~ tide 1 ~\nthe last train home shelters moon"
        self.assertEqual(dict(kindred("last train", text)), {"home": 1, "moon": 1})

    def test_meets_needs_both_words_in_one_line(self):
        poem = "moon haunts rust\nand lantern listens"
        self.assertTrue(meets(poem, "moon", "rust"))
        self.assertFalse(meets(poem, "moon", "lantern"))

    def test_is_thing_leaves_out_bridges_and_small_words(self):
        self.assertTrue(is_thing("lantern"))
        for word in ("The", "a", "haunts", "listens", "and", "I,", "is", "to", "our"):
            with self.subTest(word=word):
                self.assertFalse(is_thing(word))

    def test_things_of_a_question_ignore_case_and_punctuation(self):
        self.assertEqual(things("Where is the Lantern?"), {"where", "lantern"})

    def test_answer_is_the_line_sharing_most_with_the_question(self):
        text = ("~ tide 1 ~\nlantern haunts window\nmoon shelters rust\n\n"
                "~ tide 2 ~\nwindow remembers moon")
        self.assertEqual(answer("Is the lantern by the window?", text), "lantern haunts window")
        self.assertEqual(answer("what of the moon", text), "window remembers moon")
        self.assertEqual(answer("any kraken?", text), "")
        self.assertEqual(answer("who is there?", "~ tide 1 ~\nwho is there"), "")
        self.assertEqual(answer("moon", "The shore is bare. No tide has left a shell."), "")


if __name__ == "__main__":
    unittest.main()
