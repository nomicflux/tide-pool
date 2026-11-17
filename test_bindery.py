import unittest

from bindery import UNDATED, book, chapters, diary, leaf, pages

SHORE = "~ tide 1 ~\nmoon haunts rust\n\n~ tide 2 ~\n\n~ tide 1 ~\nsalt <shelters> bell\nand fern listens\n"
DATED = "~ tide 1 ~\nmoon haunts rust\n\n~ tide 3 · 2026-11-07 ~\nlantern holds window\n"


class BinderyTest(unittest.TestCase):
    def test_pages_keep_each_poem_and_skip_empty_tides(self):
        self.assertEqual(pages(SHORE), [
            (1, "", "moon haunts rust"),
            (1, "", "salt <shelters> bell\nand fern listens"),
        ])

    def test_pages_read_dated_and_undated_shells_together(self):
        self.assertEqual(pages(DATED), [(1, "", "moon haunts rust"),
                                        (3, "2026-11-07", "lantern holds window")])

    def test_diary_counts_each_day_in_shore_order(self):
        shore = DATED + "\n~ tide 4 · 2026-11-07 ~\nsalt shelters bell\n"
        self.assertEqual(diary(shore), f"{'before the shore kept dates':<28} o 1\n{'2026-11-07':<28} oo 2\n{'in all':<28} 3")
        self.assertEqual(diary("The shore is bare."), "")

    def test_pages_of_a_bare_shore(self):
        self.assertEqual(pages("The shore is bare. No tide has left a shell."), [])

    def test_leaf_escapes_the_poem(self):
        self.assertEqual(leaf(2, 1, "", "a <b>"),
                         "<section><p>page 2 · tide 1</p><pre>a &lt;b&gt;</pre></section>")

    def test_leaf_carries_the_day_when_the_shore_kept_one(self):
        self.assertIn("<p>page 2 · tide 3 · 2026-11-07</p>", leaf(2, 3, "2026-11-07", "a"))

    def test_chapters_head_each_new_day(self):
        kept = [(1, "", "moon"), (2, "2026-11-06", "rust"), (3, "2026-11-06", "lamp"), (4, "2026-11-07", "bell")]
        bound = chapters(kept)
        self.assertEqual(bound.count("<h2>"), 3)
        self.assertTrue(bound.startswith(f"<h2>{UNDATED}</h2>\n{leaf(1, 1, '', 'moon')}"))
        self.assertIn(f"{leaf(3, 3, '2026-11-06', 'lamp')}\n<h2>2026-11-07</h2>", bound)

    def test_book_numbers_pages_across_sessions(self):
        bound = book(SHORE)
        self.assertTrue(bound.startswith("<!DOCTYPE html>"))
        self.assertIn("page 1 · tide 1", bound)
        self.assertIn("page 2 · tide 1", bound)
        self.assertEqual(bound.count("<section>"), 2)


if __name__ == "__main__":
    unittest.main()
