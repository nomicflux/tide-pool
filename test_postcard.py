import os
import tempfile
import unittest

from postcard import DAY_WATER, WATER, bobbing, draw, header, shoreline, svg, word_mark


class PostcardTest(unittest.TestCase):
    def test_daylight_keeps_the_words_and_weather_with_dark_ink(self):
        for weather in WATER:
            with self.subTest(weather=weather):
                day = svg(["bread & light"], weather, True)
                night = svg(["bread & light"], weather, False)
                self.assertIn(DAY_WATER[weather], day)
                self.assertIn('#183e48', day)
                self.assertIn(WATER[weather], night)
                self.assertIn('bread &amp; light', day)
                self.assertEqual(day.count('<animate'), night.count('<animate'))

    def test_canvas_grows_for_wrapped_phrases(self):
        self.assertIn('height="280"', svg([], "calm"))
        self.assertIn('height="380"', svg(["moon"] * 5, "calm"))
        self.assertIn('height="480"', svg(["moon"] * 6, "calm"))
        self.assertIn('height="406"', svg(["the room we left behind"], "calm"))

    def test_header_names_the_weather(self):
        self.assertEqual(header("fog", 380)[-1],
                         '<text x="65" y="110" font-size="16">fog water</text>')

    def test_word_mark_escapes_and_places_word(self):
        circle, text = word_mark(6, "<tide>", 275)
        self.assertEqual(circle, '<circle cx="320" cy="275" r="3"/>')
        self.assertIn(">&lt;tide&gt;</tspan>", text)

    def test_phrases_wrap_at_readable_size(self):
        self.assertIn('font-size="20"', word_mark(0, "moon")[1])
        text = word_mark(0, "the room we left behind")[1]
        self.assertIn('font-size="20"', text)
        self.assertIn('>the room we left</tspan>', text)
        self.assertIn('>behind</tspan>', text)

    def test_shoreline_sits_above_the_bottom(self):
        self.assertIn('d="M 65 310 Q 300 275', shoreline(380))

    def test_shoreline_breathes_between_still_and_swell(self):
        line = shoreline(380)
        self.assertIn('values="M 65 310 Q 300 275 550 310 T 1035 310;'
                      'M 65 310 Q 300 330 550 310 T 1035 310;', line)
        self.assertIn('repeatCount="indefinite"', line)

    def test_bobbing_wraps_a_mark_at_its_own_pace(self):
        held = bobbing(6, ["<circle/>", "<text/>"])
        self.assertEqual(held[:3], ["<g>", "<circle/>", "<text/>"])
        self.assertIn('dur="7s"', held[3])
        self.assertEqual(held[4], "</g>")

    def test_every_word_bobs(self):
        image = svg(["moon", "rust", "lantern"], "fog")
        self.assertEqual(image.count("<animateTransform"), 3)
        self.assertEqual(image.count("<animate "), 1)

    def test_svg_is_one_document(self):
        image = svg(["moon", "rust"], "calm")
        self.assertTrue(image.startswith("<svg "))
        self.assertTrue(image.endswith("</svg>"))
        self.assertEqual(image.count("<circle"), 2)

    def test_ice_holds_the_words_and_shore_still(self):
        image = svg(["moon", "rust"], "ice")
        self.assertNotIn("<animate", image)
        self.assertEqual(image.count("<circle"), 2)
        self.assertIn("<path", image)
        for weather in ("calm", "fog", "storm"):
            thawed = svg(["moon", "rust"], weather)
            self.assertEqual(thawed.count("<animateTransform"), 2)
            self.assertEqual(thawed.count("<animate "), 1)

    def test_draw_writes_the_svg(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "postcard.svg")
            draw(["moon"], "storm", path)
            with open(path, encoding="utf-8") as card:
                self.assertEqual(card.read(), svg(["moon"], "storm"))


if __name__ == "__main__":
    unittest.main()
