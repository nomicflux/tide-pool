"""The coast's stories: reading their beats, the shelf, and the chart's numbered places."""

import os
import re
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
STORY_DIR = os.path.join(HERE, "stories")
CHART = os.path.join(HERE, "CHART.md")
PLACE = re.compile(r"\*\*(\d+) — \[([^\]]+)\]\(stories/([^)]+)\.md\)")


def story_beats(markdown):
    beats = []
    for i, chunk in enumerate(markdown.split("```")):
        if i % 2:
            beats.append(("sea", [line for line in chunk.splitlines()[1:] if line]))
        elif chunk.strip():
            beats.append(("story", chunk.strip()))
    return beats


def stories(directory):
    return {name[:-3].lower(): name for name in sorted(os.listdir(directory))
            if name.endswith(".md")}


def chart_places(markdown):
    return {number: (title, name.lower()) for number, title, name in PLACE.findall(markdown)}


def place_name(name, markdown):
    places = chart_places(markdown)
    return places[name][1] if name in places else name


def story_path(name):
    shelf = stories(STORY_DIR)
    name = place_name(name, Path(CHART).read_text(encoding="utf-8"))
    return os.path.join(STORY_DIR, shelf[name]) if name in shelf else ""


def elsewhere(shelf, charted):
    """The walks on the shelf that are not places on the chart, in shelf order."""
    return [name for name in shelf if name not in charted]


def walks(markdown):
    """Every walk as (what to read, title): the chart's places by number, then the walks kept off it."""
    places = chart_places(markdown)
    charted = [(number, title) for number, (title, _) in sorted(places.items(), key=lambda place: int(place[0]))]
    off_chart = elsewhere(stories(STORY_DIR), {name for _, name in places.values()})
    return charted + [(name, name.replace("_", " ")) for name in off_chart]


def choose_story():
    rows = "\n".join(f"  read {target:<14} {title}" for target, title in walks(Path(CHART).read_text(encoding="utf-8")))
    return f"Choose a story:\n{rows}"


def chart_drawing(markdown):
    return markdown.split("```text\n", 1)[1].split("```", 1)[0]


def chart_text(markdown):
    """The map, then every numbered place as the command that opens it."""
    places = "\n".join(f"read {number:<3}{title}"
                       for number, (title, _) in chart_places(markdown).items())
    return f"{chart_drawing(markdown)}\n{places}"
