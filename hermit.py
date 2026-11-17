"""A portrait of the shore's resident and the line it calls home."""

from html import escape
from textwrap import wrap

CRAB = '''<g stroke="#d98969" stroke-width="7" stroke-linecap="round" fill="none">
<path d="M295 195 Q260 205 240 240 M320 200 Q300 220 285 250
         M365 200 Q395 220 410 250 M390 190 Q430 210 450 235"/>
<path d="M255 175 L244 140 M278 170 L277 135"/>
</g>
<ellipse cx="335" cy="190" rx="100" ry="30" fill="#c66d50"/>
<ellipse cx="265" cy="180" rx="38" ry="27" fill="#d98969"/>
<path d="M235 190 Q180 165 184 202 Q200 222 230 201
         M235 185 Q198 143 185 167 L210 183" fill="#d98969"/>
<circle cx="244" cy="138" r="6" fill="#ead9af"/>
<circle cx="277" cy="133" r="6" fill="#ead9af"/>
<ellipse cx="373" cy="132" rx="86" ry="69" fill="#bca47a"/>
<path d="M429 160 C463 94 371 55 332 100 C299 143 357 185 391 151
         C417 123 375 99 359 120 C347 137 370 149 379 135"
      fill="none" stroke="#6e624c" stroke-width="5" stroke-linecap="round"/>'''


def portrait(word, line):
    rows = wrap(f'House: {word}', 64) + [''] + wrap(line, 64)
    height = 320 + 22 * len(rows)
    caption = ''.join(f'<text x="32" y="{300 + 22 * i}">{escape(row)}</text>'
                      for i, row in enumerate(rows))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="{height}" viewBox="0 0 720 {height}">'
            f'<title>A hermit crab in {escape(word)}</title>'
            f'<rect width="720" height="{height}" fill="#102d38"/>'
            '<text x="32" y="40" fill="#ead9af" font-family="Georgia, serif" font-size="26">'
            'The shore’s resident</text>' + CRAB +
            '<g fill="#ead9af" font-family="monospace" font-size="16">' + caption + '</g></svg>')
