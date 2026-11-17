import unittest
from datetime import datetime, timedelta, timezone

from moon import (BEGINS, NEW_MOON, SYNODIC_DAYS, TIDE_HOURS, age, daylight_at, next_water, part_of_day,
                  phase, tidal_range, turn_of, water)


def utc(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


class DayClockTest(unittest.TestCase):
    def test_part_of_day_follows_the_utc_hour(self):
        for hour, name in ((0, "Tonight"), (4, "Tonight"), (5, "This morning"), (11, "This morning"),
                           (12, "This afternoon"), (16, "This afternoon"), (17, "This evening"),
                           (20, "This evening"), (21, "Tonight"), (23, "Tonight")):
            with self.subTest(hour=hour):
                self.assertEqual(part_of_day(utc(2026, 11, 6, hour)), name)

    def test_daylight_is_the_coasts_morning_and_afternoon(self):
        for hour, expected in ((4, False), (5, True), (12, True), (16, True), (17, False), (23, False)):
            with self.subTest(hour=hour):
                self.assertEqual(daylight_at(utc(2026, 11, 6, hour)), expected)


class WaterTest(unittest.TestCase):
    def test_the_water_turns_twice_a_day_from_high_water_at_the_anchor(self):
        for fraction, state in ((0.0, "high water"), (0.2, "falling"), (0.5, "low water"),
                                (0.75, "rising"), (0.95, "high water"), (1.2, "falling")):
            with self.subTest(fraction=fraction):
                self.assertEqual(water(NEW_MOON + timedelta(hours=fraction * TIDE_HOURS)), state)


class NextWaterTest(unittest.TestCase):
    def test_turn_of_runs_from_zero_at_the_anchor(self):
        self.assertEqual(turn_of(NEW_MOON), 0.0)
        self.assertAlmostEqual(turn_of(NEW_MOON + timedelta(hours=TIDE_HOURS / 4)), 0.25)

    def test_each_state_begins_where_the_one_before_it_ends(self):
        self.assertEqual(BEGINS, {"high water": 0.9, "falling": 0.1, "low water": 0.4, "rising": 0.6})

    def test_next_water_is_now_if_already_there_else_the_band_s_start(self):
        self.assertEqual(next_water(NEW_MOON, "high water"), NEW_MOON)
        low = next_water(NEW_MOON, "low water")
        self.assertAlmostEqual((low - NEW_MOON).total_seconds() / 3600, 0.4 * TIDE_HOURS)
        self.assertEqual(water(low), "low water")
        high = next_water(low, "high water")
        self.assertAlmostEqual((high - NEW_MOON).total_seconds() / 3600, 0.9 * TIDE_HOURS)


class MoonTest(unittest.TestCase):
    def test_anchor_is_new_moon(self):
        self.assertEqual(phase(NEW_MOON), "new moon")

    def test_observed_phases_of_november_2026(self):
        self.assertEqual(phase(utc(2026, 11, 5, 18)), "waning crescent")
        self.assertEqual(phase(utc(2026, 11, 17, 11, 48)), "first quarter")
        self.assertEqual(phase(utc(2026, 11, 24, 14, 53)), "full moon")

    def test_phase_repeats_each_synodic_month_in_either_direction(self):
        later = NEW_MOON + timedelta(days=SYNODIC_DAYS * 3 + 3)
        earlier = NEW_MOON - timedelta(days=SYNODIC_DAYS * 5 - 3)
        self.assertEqual(phase(later), "waxing crescent")
        self.assertEqual(phase(earlier), "waxing crescent")


    def test_age_counts_days_since_new_moon(self):
        self.assertAlmostEqual(age(NEW_MOON + timedelta(days=2.5)), 2.5)

    def test_spring_tides_at_new_and_full_moon_neap_at_quarters(self):
        self.assertEqual(tidal_range(NEW_MOON), 8)
        self.assertEqual(tidal_range(NEW_MOON + timedelta(days=SYNODIC_DAYS / 2)), 8)
        self.assertEqual(tidal_range(NEW_MOON + timedelta(days=SYNODIC_DAYS / 4)), 0)


if __name__ == "__main__":
    unittest.main()
