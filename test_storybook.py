import os
import re
import tempfile
import unittest
from pathlib import Path

from storybook import (CHART, STORY_DIR, chart_drawing, chart_places, chart_text, choose_story, elsewhere,
                       place_name, stories, story_beats, story_path, walks)


class StorybookTest(unittest.TestCase):
    def test_story_beats_split_prose_and_commands(self):
        markdown = "# Night\n\nLeave a word.\n\n```text\ndrop lamp\nlook\n```\n\nThe end.\n"
        self.assertEqual(story_beats(markdown), [
            ("story", "# Night\n\nLeave a word."),
            ("sea", ["drop lamp", "look"]),
            ("story", "The end."),
        ])

    def test_every_story_on_the_shelf_opens_with_its_title(self):
        shelf = stories(STORY_DIR)
        self.assertGreater(len(shelf), 20)
        for name, file in shelf.items():
            with self.subTest(story=name):
                first = Path(STORY_DIR, file).read_text(encoding="utf-8").splitlines()[0]
                self.assertRegex(first, r"^# \S")

    def test_any_markdown_in_the_directory_is_a_story(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("Spare_Key.md", "notes.txt", "BELLS.md"):
                open(os.path.join(directory, name), "w").close()
            self.assertEqual(stories(directory),
                             {"bells": "BELLS.md", "spare_key": "Spare_Key.md"})

    def test_chart_places_read_numbered_entries(self):
        markdown = ("**1 — [The lighthouse](stories/LIGHTHOUSE.md).** Keep.\n"
                    "**12 — [The far reef](stories/FAR_REEF.md).** Go.\n")
        self.assertEqual(chart_places(markdown), {"1": ("The lighthouse", "lighthouse"),
                                                  "12": ("The far reef", "far_reef")})

    def test_place_name_turns_numbers_into_stories(self):
        markdown = "**3 — [The radio station](stories/RADIO.md).**"
        self.assertEqual(place_name("3", markdown), "radio")
        self.assertEqual(place_name("bells", markdown), "bells")

    def test_every_place_on_the_chart_is_a_story(self):
        places = chart_places(Path(CHART).read_text(encoding="utf-8"))
        self.assertIn("1", places)
        for _, name in places.values():
            with self.subTest(name=name):
                self.assertIn(name, stories(STORY_DIR))

    def test_story_path_by_name_or_chart_number(self):
        self.assertTrue(story_path("2").endswith(os.path.join("stories", "BELLS.md")))
        self.assertTrue(story_path("bells").endswith("BELLS.md"))
        self.assertEqual(story_path("atlantis"), "")
        self.assertEqual(story_path(""), "")

    def test_chart_drawing_is_the_fenced_map(self):
        self.assertEqual(chart_drawing("# Coast\n\n```text\n  1 ~\n```\n\nafter"), "  1 ~\n")

    def test_chart_text_draws_the_map_then_lists_places(self):
        markdown = ("```text\n  1 ~\n```\n\n**1 — [The lighthouse](stories/LIGHTHOUSE.md).** Keep.\n"
                    "**12 — [The far reef](stories/FAR_REEF.md).** Go.\n")
        self.assertEqual(chart_text(markdown), "  1 ~\n\nread 1  The lighthouse\nread 12 The far reef")

    def test_choose_story_lists_the_shelf_and_the_chart(self):
        listing = choose_story().splitlines()
        self.assertEqual(listing[0], "Choose a story:")
        self.assertEqual(listing[1], f"  read {'1':<14} The lighthouse")
        self.assertEqual(len(listing), 1 + len(stories(STORY_DIR)))

    def test_the_illustrated_coast_marks_every_place_on_the_chart(self):
        drawing = Path(os.path.dirname(STORY_DIR), "studies", "coast", "coast.svg").read_text(encoding="utf-8")
        labels = re.findall(r">(\d+(?:/\d+)*)</text>", drawing)
        marked = {number for label in labels for number in label.split("/")}
        self.assertEqual(marked, set(chart_places(Path(CHART).read_text(encoding="utf-8"))))

    def test_the_three_place_counts_agree(self):
        root = Path(os.path.dirname(STORY_DIR))
        captions = [root / "README.md", root / "studies" / "coast" / "README.md", root / "studies" / "coast" / "coast.svg"]
        counts = {re.search(r"([a-z-]+) places", path.read_text(encoding="utf-8"))[1] for path in captions}
        self.assertEqual(len(counts), 1, counts)

    def test_elsewhere_keeps_the_uncharted_in_shelf_order(self):
        self.assertEqual(elsewhere({"a": "", "b": "", "c": ""}, {"b"}), ["a", "c"])

    def test_walks_are_the_charted_places_by_number_then_the_rest(self):
        chart = Path(CHART).read_text(encoding="utf-8")
        found = walks(chart)
        charted = [target.isdigit() for target, _ in found]
        self.assertEqual(charted, sorted(charted, reverse=True))
        numbers = [int(target) for target, _ in found if target.isdigit()]
        self.assertEqual(numbers, sorted(int(number) for number in chart_places(chart)))
        self.assertEqual(found[0], ("1", "The lighthouse"))
        self.assertIn(("same_words", "same words"), found)
        self.assertEqual(len(found), len(stories(STORY_DIR)))


if __name__ == "__main__":
    unittest.main()
