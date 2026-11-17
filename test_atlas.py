import unittest

from atlas import atlas, exhibit_list, prose, sea, section, story_html

CHART = ("# Coast\n\n```text\n   1 ~\n```\n\n"
         "**1 — [The lighthouse](stories/LIGHTHOUSE.md).** Keep the light.\n")
SHELF = {"lighthouse": "# The keeper\n\nLeave <three> things.\n\n```text\ndrop coat\ntide\n```\n\nThe end.",
         "spare_key": "# The spare key\n\nA key.\n"}


class AtlasTest(unittest.TestCase):
    def test_prose_turns_titles_and_paragraphs_into_html(self):
        self.assertEqual(prose("# Night\n\nA <lamp>.\n\nThe end."),
                         "<h3>Night</h3><p>A &lt;lamp&gt;.</p><p>The end.</p>")

    def test_sea_shows_commands_as_one_block(self):
        self.assertEqual(sea(["drop coat", "tide"]), '<pre class="sea">drop coat\ntide</pre>')

    def test_story_html_alternates_prose_and_sea(self):
        self.assertEqual(story_html(SHELF["lighthouse"]),
                         "<h3>The keeper</h3><p>Leave &lt;three&gt; things.</p>"
                         '<pre class="sea">drop coat\ntide</pre><p>The end.</p>')

    def test_section_carries_its_heading(self):
        self.assertTrue(section("lighthouse", "1 — The lighthouse", "A.").startswith('<section id="lighthouse"><h2>1 — The lighthouse</h2>'))

    def test_exhibit_list_links_each_hall(self):
        self.assertEqual(exhibit_list([]), "")
        self.assertIn('<a href="exhibits/first-night/book.html">First night &amp; after</a>',
                      exhibit_list([("first-night", "First night & after")]))

    def test_atlas_holds_the_chart_the_places_the_elsewhere_and_the_halls(self):
        page = atlas(CHART, SHELF, [("first-night", "First night")])
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertIn("<pre>   1 ~\n</pre>", page)
        self.assertIn("<h2>1 — The lighthouse</h2><h3>The keeper</h3>", page)
        self.assertIn('<h2>Elsewhere</h2><section id="spare_key"><h2>spare key</h2>', page)
        self.assertIn("exhibits/first-night/book.html", page)

    def test_contents_links_charted_and_uncharted_stories(self):
        page = atlas(CHART, SHELF, [])
        for name in SHELF:
            self.assertIn(f'href="#{name}"', page)
            self.assertEqual(page.count(f'id="{name}"'), 1)
        self.assertLess(page.index('href="#lighthouse"'), page.index('href="#spare_key"'))


if __name__ == "__main__":
    unittest.main()
