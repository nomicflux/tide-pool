"""The coast's sky clock: tonight's moon, from one observed new moon and the mean synodic month, and the part of the day."""

import math
from datetime import datetime, timedelta, timezone

NEW_MOON = datetime(2026, 11, 9, 7, 2, tzinfo=timezone.utc)
SYNODIC_DAYS = 29.530588853
PHASES = ("new moon", "waxing crescent", "first quarter", "waxing gibbous",
          "full moon", "waning gibbous", "last quarter", "waning crescent")


def age(when):
    return (when - NEW_MOON).total_seconds() / 86400 % SYNODIC_DAYS


def phase(when):
    return PHASES[int(age(when) / SYNODIC_DAYS * 8 + 0.5) % 8]


def tidal_range(when):
    """0 at neap tides (quarter moons) up to 8 at spring tides (new and full)."""
    return round(4 + 4 * math.cos(4 * math.pi * age(when) / SYNODIC_DAYS))


DAYLIGHT = ("This morning", "This afternoon")


def part_of_day(when):
    """What to call this hour on the coast, which keeps UTC."""
    for start, name in ((21, "Tonight"), (17, "This evening"), (12, "This afternoon"), (5, "This morning")):
        if when.hour >= start:
            return name
    return "Tonight"


def daylight_at(when):
    """Daylight is the coast's morning and afternoon: 05:00 to 17:00 UTC."""
    return part_of_day(when) in DAYLIGHT


TIDE_HOURS = 12.42
WATER = ((0.1, "high water"), (0.4, "falling"), (0.6, "low water"), (0.9, "rising"), (1.0, "high water"))
BEGINS = dict(zip((name for _, name in WATER), (0.0, *(limit for limit, _ in WATER))))


def turn_of(when):
    """How far through its twice-daily tide the coast's water is, from 0 to 1."""
    return (when - NEW_MOON).total_seconds() / 3600 % TIDE_HOURS / TIDE_HOURS


def water(when):
    """Where the coast's twice-daily tide stands, by its own reckoning: high water at the anchoring new moon."""
    return next(name for limit, name in WATER if turn_of(when) < limit)


def next_water(when, state):
    """When the water next stands at `state`: now, if it already does."""
    if water(when) == state:
        return when
    return when + timedelta(hours=(BEGINS[state] - turn_of(when)) % 1 * TIDE_HOURS)
