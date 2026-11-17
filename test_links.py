import re
import unittest
import wave
from pathlib import Path

from atlas import atlas
from bindery import book
from exhibits import halls
from storybook import story_path
from webshore import page, served

HERE = Path(__file__).parent
FENCED = re.compile(r"^(```|~~~~).*?^\1", re.MULTILINE | re.DOTALL)
CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\]\(([^)\s]+)\)")
ROOTED = re.compile(r'(?:href|src)="(/[^"]*)"')
PICTURE = re.compile(r"!\[([^\]]*)\]\(")


def links(markdown):
    """The link targets in prose, leaving out code spans and fenced examples."""
    return LINK.findall(CODE.sub("", FENCED.sub("", markdown)))


class LinkTest(unittest.TestCase):
    def test_links_skip_code_and_examples(self):
        text = "[a](one.md) `[b](two.md)`\n```text\n[c](three.md)\n```\n[d](four.md#part)"
        self.assertEqual(links(text), ["one.md", "four.md#part"])

    def test_every_relative_link_in_the_coast_s_pages_resolves(self):
        followed = 0
        for page in sorted(HERE.rglob("*.md")):
            for target in links(page.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#")):
                    continue
                followed += 1
                with self.subTest(page=str(page.relative_to(HERE)), target=target):
                    self.assertTrue((page.parent / target.split("#")[0]).exists())
        self.assertGreater(followed, 100)


class ReadmeTest(unittest.TestCase):
    def test_the_readme_links_every_top_level_page(self):
        linked = set(links((HERE / "README.md").read_text(encoding="utf-8")))
        pages = [page.name for page in sorted(HERE.glob("*.md")) if page.name not in {"README.md", "AGENTS.md", "LOGBOOK.md"}]
        self.assertGreater(len(pages), 10)
        for name in pages:
            with self.subTest(page=name):
                self.assertIn(name, linked)


SPOKEN = re.compile(r"`(read|visit) ([^`<]+)`")
NOT_FOR_VISITORS = {"WRITING.md", "ARCHITECTURE.md", "LOGBOOK.md"}


class SpokenCommandTest(unittest.TestCase):
    def test_every_read_and_visit_a_page_suggests_still_opens(self):
        pages = [page for page in sorted(HERE.rglob("*.md")) if page.name not in NOT_FOR_VISITORS]
        spoken = [(page, name, arg) for page in pages for name, arg in SPOKEN.findall(page.read_text(encoding="utf-8"))]
        self.assertGreater(len(spoken), 10)
        for page, name, arg in spoken:
            with self.subTest(page=str(page.relative_to(HERE)), said=f"{name} {arg}"):
                if name == "read":
                    self.assertTrue(story_path(arg))
                else:
                    self.assertIn(arg, halls(str(HERE / "exhibits")))


class DrawingTest(unittest.TestCase):
    def test_every_drawing_on_the_coast_has_a_title(self):
        drawings = sorted(HERE.rglob("*.svg"))
        self.assertGreater(len(drawings), 50)
        for drawing in drawings:
            with self.subTest(drawing=str(drawing.relative_to(HERE))):
                self.assertIn("<title", drawing.read_text(encoding="utf-8"))

    def test_every_root_link_in_a_page_is_served(self):
        followed = 0
        for html in sorted(HERE.rglob("*.html")):
            for path in ROOTED.findall(html.read_text(encoding="utf-8")):
                followed += 1
                with self.subTest(page=str(html.relative_to(HERE)), path=path):
                    file, _ = served(str(HERE), path)
                    self.assertTrue(path == "/" or Path(file).is_file())
        self.assertGreater(followed, 10)

    def test_every_hall_quotes_only_what_its_shore_holds(self):
        quoted = 0
        for hall in halls(str(HERE / "exhibits")):
            folder = HERE / "exhibits" / hall
            shore = (folder / "shore.txt").read_text(encoding="utf-8")
            for line in (folder / "README.md").read_text(encoding="utf-8").splitlines():
                if line.startswith("> "):
                    quoted += 1
                    with self.subTest(hall=hall, quote=line):
                        self.assertIn(line[2:], shore)
        self.assertGreater(quoted, 40)

    def test_every_recording_on_the_coast_has_sound(self):
        recordings = sorted(HERE.rglob("*.wav"))
        self.assertGreater(len(recordings), 30)
        for recording in recordings:
            with self.subTest(recording=str(recording.relative_to(HERE))), wave.open(str(recording)) as song:
                self.assertGreater(song.getnframes(), 0)

    def test_every_picture_in_the_coast_s_pages_is_described(self):
        pictures = [(page, alt) for page in sorted(HERE.rglob("*.md"))
                    for alt in PICTURE.findall(page.read_text(encoding="utf-8"))]
        self.assertGreater(len(pictures), 40)
        for page, alt in pictures:
            with self.subTest(page=str(page.relative_to(HERE))):
                self.assertTrue(alt.strip())

    def test_every_page_the_coast_generates_declares_its_language(self):
        made = {"atlas": atlas("```text\n1\n```", {}, []), "book": book(""), "browser": page("", "", "", "", "", "")}
        for name, html in made.items():
            with self.subTest(page=name):
                self.assertTrue(html.startswith('<!DOCTYPE html>\n<html lang="en">'))

    def test_every_page_on_the_coast_has_a_title(self):
        pages = sorted(HERE.rglob("*.html"))
        self.assertGreater(len(pages), 30)
        for html in pages:
            with self.subTest(page=str(html.relative_to(HERE))):
                self.assertIn("<title", html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
