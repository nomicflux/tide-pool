import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from skychart import chart_sky, constellation, moon, place, sky, star


class SkychartTest(unittest.TestCase):
    def test_a_word_always_rises_in_the_same_place(self):
        self.assertEqual(place("lantern"), place("lantern"))
        x, y = place("lantern")
        self.assertTrue(80 <= x < 1020 and 110 <= y < 530)

    def test_brighter_stars_for_words_remembered_more(self):
        self.assertIn('r="2"', star("moon", 1))
        self.assertIn('r="6"', star("moon", 5))

    def test_star_names_are_escaped(self):
        self.assertIn(">&lt;salt&gt; · 1</tspan>", sky([("<salt>", 1)], 0.25))

    def test_collocated_stars_have_separate_labels(self):
        with patch("skychart.place", return_value=(500, 300)):
            drawn = ET.fromstring(sky([("moon", 3), ("rust", 2)], 0.25))
        names = drawn.findall('.//{http://www.w3.org/2000/svg}text')[1:]
        self.assertEqual(len(names), 2)
        self.assertNotEqual(names[0].get('y'), names[1].get('y'))

    def test_constellation_joins_stars_in_order(self):
        (x1, y1), (x2, y2) = place("moon"), place("rust")
        self.assertIn(f'points="{x1},{y1} {x2},{y2}"', constellation(["moon", "rust"]))

    def test_sky_is_one_document_with_a_star_per_word(self):
        drawn = sky([("moon", 3), ("rust", 1)], 0.25)
        self.assertTrue(drawn.startswith("<svg ") and drawn.endswith("</svg>"))
        self.assertEqual(drawn.count('class="star"'), 2)
        self.assertEqual(drawn.count('class="moon"'), 1)

    def test_chart_sky_writes_the_svg(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sky.svg")
            chart_sky([("moon", 2)], 0.25, path)
            with open(path, encoding="utf-8") as drawn:
                self.assertEqual(drawn.read(), sky([("moon", 2)], 0.25))

    def test_new_moon_is_dark_full_moon_is_whole(self):
        self.assertIn('A 26.0000 26 0 0 0 0 -26', moon(0))
        self.assertIn('A 26.0000 26 0 0 1 0 -26', moon(0.5))

    def test_waxing_lights_the_right_waning_the_left(self):
        self.assertIn('scale(1 1)', moon(0.25))
        self.assertIn('scale(-1 1)', moon(0.75))
        for phase in (0.25, 0.75):
            self.assertIn('A 0.0000 26', moon(phase))


if __name__ == "__main__":
    unittest.main()
