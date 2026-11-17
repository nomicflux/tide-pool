import os
import tempfile
import unittest
import wave

from lamp import LETTERS, MORSE, UNIT, codes, flashes, letter_beats, light, signal_lines, sound, timing
from seaglass import RATE


class LampTest(unittest.TestCase):
    def test_every_letter_and_digit_has_a_code(self):
        self.assertEqual(len(MORSE), len(LETTERS))
        self.assertEqual(MORSE["a"], ".-")
        self.assertEqual(MORSE["z"], "--..")
        self.assertEqual(MORSE["0"], "-----")
        self.assertEqual(MORSE["9"], "----.")

    def test_flashes_spell_a_word_in_dots_and_dashes(self):
        self.assertEqual(flashes("SOS"), "··· ——— ···")
        self.assertEqual(flashes("moon"), "—— ——— ——— —·")

    def test_flashes_pass_over_what_the_lamp_cannot_say(self):
        self.assertEqual(flashes("it's"), "·· — ···")
        self.assertEqual(flashes("—"), "")

    def test_signal_lines_one_word_per_line(self):
        self.assertEqual(signal_lines("sos — at sea"), [
            f"{'sos':<14}··· ——— ···", f"{'at':<14}·— —", f"{'sea':<14}··· · ·—"])

    def test_codes_and_flashes_agree(self):
        self.assertEqual(codes("at"), [".-", "-"])
        self.assertEqual(flashes("at"), "·— —")

    def test_letter_beats_end_with_a_letter_gap(self):
        self.assertEqual(letter_beats(".-"), [(True, 1), (False, 1), (True, 3), (False, 3)])

    def test_timing_follows_the_morse_rhythm(self):
        self.assertEqual(timing("e"), [(True, 1), (False, 7)])
        self.assertEqual(timing("at e"), [(True, 1), (False, 1), (True, 3), (False, 3),
                                          (True, 3), (False, 7), (True, 1), (False, 7)])
        self.assertEqual(timing("—"), [])

    def test_sound_records_every_beat(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "signal.wav")
            sound("at", path)
            with wave.open(path) as song:
                frames = sum(int(RATE * units * UNIT) for _, units in timing("at"))
                self.assertEqual(song.getnframes(), frames)

    def test_light_matches_dot_and_word_gap(self):
        drawing = light("e")
        self.assertIn('dur="0.64s"', drawing)
        self.assertIn('keyTimes="0.00000000;0.12500000;1"', drawing)
        self.assertIn('values="1;0.12;0.12"', drawing)
        self.assertIn('calcMode="discrete"', drawing)

    def test_silent_light_does_not_animate(self):
        self.assertNotIn('<animate', light("—"))
        self.assertIn('<title>&lt;e&gt;</title>', light("<e>"))


if __name__ == "__main__":
    unittest.main()
