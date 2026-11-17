import os
import tempfile
import unittest
import wave

from jetty import footsteps, jetty, plank, span, walk
from seaglass import DURATION, RATE, chime, rest


class JettyTest(unittest.TestCase):
    def test_a_remembered_line_lies_on_a_plank(self):
        drawn = plank(0, "b", "bring a plank & a name", 720)
        self.assertIn('<rect x="24" y="40" width="672"', drawn)
        self.assertIn(">B</text>", drawn)
        self.assertIn("bring a plank &amp; a name", drawn)

    def test_a_letter_without_a_line_leaves_a_gap(self):
        drawn = plank(2, "b", "B", 720)
        self.assertNotIn("<rect", drawn)
        self.assertIn('y="130"', drawn)

    def test_the_jetty_widens_for_its_longest_line(self):
        self.assertEqual(span(["B", "short"]), 720)
        self.assertEqual(span(["x" * 120]), 104 + 7 * 120)

    def test_the_jetty_has_one_plank_per_letter_over_water(self):
        drawn = jetty("bob", ["bring a plank", "over the water", "B"])
        self.assertTrue(drawn.startswith("<svg"))
        self.assertIn("<title>bob</title>", drawn)
        self.assertEqual(drawn.count("<rect"), 3)
        self.assertIn('width="720" height="182"', drawn)
        self.assertIn('width="944"', jetty("b", ["b" * 120]))


class FootstepsTest(unittest.TestCase):
    def test_each_plank_chimes_its_letter_and_each_gap_is_a_silent_step(self):
        steps = footsteps("bob", ["bring a plank", "O", "beside your name"])
        self.assertEqual(steps, [chime("b", "calm"), rest(DURATION["calm"]), chime("b", "calm")])

    def test_walk_records_one_step_per_letter(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "jetty.wav")
            walk("bob", ["bring a plank", "O", "beside your name"], path)
            with wave.open(path) as heard:
                self.assertEqual(heard.getnframes(), 3 * int(RATE * DURATION["calm"]))


if __name__ == "__main__":
    unittest.main()
