import os
import tempfile
import unittest
import wave

from seaglass import (DURATION, RATE, SURF, bell, chime, pitch, recite, recited, record, rest, sample,
                      sing, surf, tone)

PENTATONIC = {220 * 2 ** (s / 12) for s in (0, 2, 4, 7, 9, 12, 14, 16, 19, 21)}


class SeaglassTest(unittest.TestCase):
    def test_pitch_is_pentatonic_and_ignores_case(self):
        self.assertIn(pitch("moon"), PENTATONIC)
        self.assertEqual(pitch("Moon"), pitch("moon"))

    def test_sample_starts_silent(self):
        self.assertEqual(sample(440, 0.5, 0), 0)

    def test_bell_holds_one_sixteen_bit_frame_per_tick(self):
        count = int(RATE * 0.22)
        self.assertEqual(len(bell(440, 0.22, [0] * count)), count * 2)

    def test_bell_rings_over_its_wash(self):
        self.assertEqual(bell(440, 0.001, [7] * 16)[:2], (7).to_bytes(2, "little", signed=True))

    def test_surf_is_the_same_for_the_same_word(self):
        self.assertEqual(surf("moon", 400, 1500), surf("moon", 400, 1500))
        self.assertNotEqual(surf("moon", 400, 1500), surf("rust", 400, 1500))

    def test_surf_swells_from_silence_and_storms_are_louder(self):
        calm, storm = surf("moon", 8000, SURF["calm"]), surf("moon", 8000, SURF["storm"])
        self.assertEqual(calm[0], 0)
        self.assertGreater(max(map(abs, storm)), max(map(abs, calm)))

    def test_sing_writes_one_bell_per_word(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "tide.wav")
            sing(["moon", "rust"], "fog", path)
            with wave.open(path) as song:
                self.assertEqual(song.getframerate(), RATE)
                self.assertEqual(song.getnframes(), 2 * int(RATE * DURATION["fog"]))

    def test_record_writes_mono_sixteen_bit_frames_in_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "frames.wav")
            record(path, [rest(0.001), bell(440, 0.001, [7] * 16)])
            with wave.open(path) as song:
                self.assertEqual((song.getnchannels(), song.getsampwidth(), song.getframerate()), (1, 2, RATE))
                self.assertEqual(song.readframes(32), rest(0.001) + bell(440, 0.001, [7] * 16))

    def test_chime_is_a_word_bell_over_its_own_surf(self):
        count = int(RATE * DURATION["storm"])
        expected = bell(pitch("moon"), DURATION["storm"], surf("moon", count, SURF["storm"]))
        self.assertEqual(chime("moon", "storm"), expected)

    def test_rest_is_silence(self):
        self.assertEqual(rest(0.001), bytes(32))

    def test_recited_line_is_calm_bells_then_a_rest(self):
        line = recited("moon haunts rust")
        self.assertEqual(line, chime("moon", "calm") + chime("haunts", "calm")
                         + chime("rust", "calm") + rest(0.4))

    def test_recite_writes_every_line(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "recital.wav")
            recite(["moon haunts rust", "and fern listens"], path)
            with wave.open(path) as song:
                bells, pause = 6 * int(RATE * DURATION["calm"]), 2 * int(RATE * 0.4)
                self.assertEqual(song.getnframes(), bells + pause)

    def test_tone_fades_in_and_holds_its_length(self):
        played = tone(660, 0.1)
        self.assertEqual(len(played), 2 * int(RATE * 0.1))
        self.assertEqual(played[:2], bytes(2))


if __name__ == "__main__":
    unittest.main()
