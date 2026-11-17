import unittest

from drift import frame, placed, wave_row, word_spot


class DriftTest(unittest.TestCase):
    def test_wave_row_is_a_line_of_water(self):
        row = wave_row(40, 0, "calm")
        self.assertEqual(len(row), 40)
        self.assertEqual(set(row), {"~", " "})

    def test_ice_holds_the_waves_and_words_still(self):
        self.assertEqual(wave_row(40, 0, "ice"), wave_row(40, 9, "ice"))
        self.assertEqual(word_spot(1, "moon", 0, "ice", 40, 10), word_spot(1, "moon", 9, "ice", 40, 10))

    def test_other_weathers_move(self):
        for weather in ("calm", "storm", "fog"):
            with self.subTest(weather=weather):
                self.assertNotEqual(wave_row(40, 0, weather), wave_row(40, 2, weather))

    def test_placed_writes_a_word_without_growing_the_row(self):
        self.assertEqual(placed("..........", 3, "moon"), "...moon...")
        self.assertEqual(placed(".....", 3, "moon"), "...mo")

    def test_word_spot_stays_above_the_water_and_on_screen(self):
        for i in range(6):
            x, y = word_spot(i, "lantern", 5.5, "storm", 40, 10)
            self.assertTrue(0 <= x <= 40 - len("lantern"))
            self.assertTrue(0 <= y < 10)

    def test_frame_is_sky_then_sea_with_every_word(self):
        rows = frame(["moon", "rust"], 0, "calm", 40, 20)
        self.assertEqual(len(rows), 20)
        self.assertTrue(all(len(row) == 40 for row in rows))
        self.assertTrue(set(rows[10]) <= {"~", " "})
        sky = "".join(rows[:10])
        self.assertIn("moon", sky)
        self.assertIn("rust", sky)


if __name__ == "__main__":
    unittest.main()
