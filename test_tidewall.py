import unittest

from tidewall import BOTTOM, TOP, label, mark_height, tidewall


class TidewallTest(unittest.TestCase):
    def test_the_oldest_poem_marks_the_foot_of_the_wall_and_the_newest_its_top(self):
        self.assertEqual(mark_height(4, 5), BOTTOM)
        self.assertEqual(mark_height(0, 5), TOP)
        self.assertEqual(mark_height(2, 5), (BOTTOM + TOP) // 2)
        self.assertEqual(mark_height(0, 1), BOTTOM)

    def test_a_label_names_the_tide_and_its_day(self):
        self.assertIn(">tide 3 · 2026-11-09</text>", label(100, 3, "2026-11-09"))
        self.assertIn(">tide 1</text>", label(100, 1, ""))

    def test_the_wall_has_one_mark_per_poem_and_names_the_lowest_and_highest(self):
        held = [(1, "", ["salt"], 3), (5, "2026-11-07", ["salt"], 1), (7, "2026-11-09", ["salt & sand"], 0)]
        drawn = tidewall("salt & sand", held, 4)
        self.assertTrue(drawn.startswith("<svg"))
        self.assertIn("<title>salt &amp; sand on the harbour wall</title>", drawn)
        self.assertEqual(drawn.count('fill="#f4f1e8"'), 3)
        self.assertIn(">tide 1</text>", drawn)
        self.assertIn(">tide 7 · 2026-11-09</text>", drawn)
        self.assertNotIn(">tide 5", drawn)

    def test_a_word_in_one_poem_is_named_once(self):
        self.assertEqual(tidewall("salt", [(2, "", ["salt"], 0)], 3).count(">tide 2</text>"), 1)


if __name__ == "__main__":
    unittest.main()
