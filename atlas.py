"""An atlas of the coast: the chart, every story set as a page, and the exhibits, in one HTML file."""

from html import escape

from storybook import chart_drawing, chart_places, elsewhere, story_beats


def prose(text):
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    return "".join(f"<h3>{escape(block[2:])}</h3>" if block.startswith("# ")
                   else f"<p>{escape(block)}</p>" for block in blocks)


def sea(commands):
    shown = escape("\n".join(commands))
    return f'<pre class="sea">{shown}</pre>'


def story_html(markdown):
    return "".join(prose(body) if kind == "story" else sea(body)
                   for kind, body in story_beats(markdown))


def section(name, heading, markdown):
    return f'<section id="{escape(name, quote=True)}"><h2>{escape(heading)}</h2>{story_html(markdown)}</section>'


def exhibit_list(halls):
    """Each hall as (folder name, catalogue title), linked to its bound book."""
    items = "".join(f'<li><a href="exhibits/{name}/book.html">{escape(title)}</a></li>' for name, title in halls)
    return f"<h2>Exhibits</h2><ul>{items}</ul>" if halls else ""


STYLE = """<style>
body { max-width: 46rem; margin: auto; padding: 2rem; background: #f4ecd8; color: #102d38; font-family: Georgia, serif; }
section { break-before: page; }
pre.sea { background: #102d38; color: #ead9af; padding: 0.6rem 1rem; }
</style>"""


def atlas(chart, shelf, exhibits):
    """chart is CHART.md's text, shelf maps story names to their markdown, exhibits are (hall name, title) pairs."""
    places = chart_places(chart)
    drawing = chart_drawing(chart)
    entries = [(name, f"{number} — {title}") for number, (title, name) in places.items()]
    uncharted = [(name, name.replace("_", " "))
                 for name in elsewhere(shelf, {name for _, name in places.values()})]
    contents = ''.join(f'<li><a href="#{escape(name, quote=True)}">{escape(title)}</a></li>'
                       for name, title in entries + uncharted)
    charted = "".join(section(name, title, shelf[name]) for name, title in entries)
    others = "".join(section(name, title, shelf[name]) for name, title in uncharted)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Atlas of a coast that remembers</title>{STYLE}</head>
<body><p><a href="http://127.0.0.1:8000/">Back to the browser shore</a></p>
<h1>Atlas of a coast that remembers</h1>
<p>To play a walk in Tide Pool, type <code>read</code> followed by its place
number or story name.</p>
<pre>{escape(drawing)}</pre>
<nav aria-label="Contents"><ul>{contents}</ul></nav>
{charted}<h2>Elsewhere</h2>{others}{exhibit_list(exhibits)}
<p><a href="http://127.0.0.1:8000/">Back to the browser shore</a></p></body></html>"""
