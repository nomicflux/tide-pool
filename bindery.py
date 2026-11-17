"""Bind the shore's poems into a printable book, one poem to a page."""

import re
from collections import Counter
from html import escape

HEADER = re.compile(r"^~ tide (\d+)(?: · ([0-9-]+))? ~$", re.MULTILINE)
UNDATED = "before the shore kept dates"


def pages(shore_text):
    """Each kept poem as (tide, day, poem); day is "" for shells made before the shore kept dates."""
    heads = list(HEADER.finditer(shore_text))
    ends = [head.start() for head in heads[1:]] + [len(shore_text)]
    found = [(int(head[1]), head[2] or "", shore_text[head.end():end].strip())
             for head, end in zip(heads, ends)]
    return [page for page in found if page[2]]


def diary(shore_text):
    """How many poems each day left, in the order the shore kept them, then the shore's total."""
    days = Counter(day or UNDATED for _, day, _ in pages(shore_text))
    lines = [f"{day:<28} {'o' * count} {count}" for day, count in days.items()]
    return "\n".join(lines + [f"{'in all':<28} {days.total()}"]) if lines else ""


def leaf(page, tide, day, poem):
    dated = f" · {day}" if day else ""
    return (f'<section><p>page {page} · tide {tide}{dated}</p>'
            f'<pre>{escape(poem)}</pre></section>')


def chapters(kept):
    """Each page as a leaf, with its day as a heading wherever a new day begins."""
    parts = []
    for page, (tide, day, poem) in enumerate(kept, 1):
        if page == 1 or day != kept[page - 2][1]:
            parts.append(f"<h2>{escape(day or UNDATED)}</h2>")
        parts.append(leaf(page, tide, day, poem))
    return "\n".join(parts)


def book(shore_text):
    leaves = chapters(pages(shore_text))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>The shore, bound</title>
<style>
body {{ background: #f4ecd8; color: #102d38; font-family: Georgia, serif; }}
section {{ break-after: page; padding: 4em; }}
pre {{ font-family: Georgia, serif; font-size: 1.4em; white-space: pre-wrap; overflow-wrap: anywhere; }}
</style></head>
<body><h1>The shore, bound</h1>
{leaves}
</body></html>"""
