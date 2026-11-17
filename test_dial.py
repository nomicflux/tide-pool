import unittest

from dial import dial, needle


class DialTest(unittest.TestCase):
    def test_the_needle_turns_clockwise_from_high_water_at_the_top(self):
        self.assertEqual(needle(0), (360, 115))
        self.assertEqual(needle(0.25), (515, 270))
        self.assertEqual(needle(0.5), (360, 425))
        self.assertEqual(needle(0.75), (205, 270))

    def test_the_dial_names_the_water_and_points_at_the_turn(self):
        drawn = dial(0.5, "low water")
        self.assertTrue(drawn.startswith("<svg"))
        self.assertIn("<title>The water is low water</title>", drawn)
        self.assertIn('x2="360.0" y2="425.0"', drawn)
        for mark in ("High water", "Falling", "Low water", "Rising"):
            self.assertIn(f">{mark}</text>", drawn)


if __name__ == "__main__":
    unittest.main()
