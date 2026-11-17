import unittest

from drift import SPEED
from postcard import WATER
from seaglass import DURATION, SURF
from tidepool import HELP
from weather import BRIDGE_WORDS, WEATHER, choices


class WeatherTest(unittest.TestCase):
    def test_choices_name_every_weather(self):
        self.assertEqual(choices(), "calm, storm, fog, or ice")

    def test_bridge_words_are_every_word_of_every_bridge(self):
        self.assertTrue({"freezes", "beside", "mistakes", "itself", "and", "listens"} <= BRIDGE_WORDS)
        self.assertNotIn("moon", BRIDGE_WORDS)

    def test_every_weather_has_a_sound_a_water_and_a_mention(self):
        for weather in WEATHER:
            with self.subTest(weather=weather):
                self.assertIn(weather, DURATION)
                self.assertIn(weather, SURF)
                self.assertIn(weather, WATER)
                self.assertIn(weather, SPEED)
                self.assertIn(weather, HELP)


if __name__ == "__main__":
    unittest.main()
