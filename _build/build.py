#!/usr/bin/env python3
"""
Builds ../index.html (and ../404.html) from the templates in this folder.

    python3 _build/build.py        (needs: pip install fonttools uharfbuzz)

Why there is a build step at all: the brand's display face, Seatren, is what
makes a Pizza Perks heading look like one, but the font file is licensed
artwork and this repository is public. So headings are not set in a web font.
Each one marked in a template as

    {{st:Some words}}            or   {{st:SOME WORDS|Some words}}

is drawn here as outlines: the words are shaped with the real font (kerning
included), every letter used becomes one <path> in a shared <defs>, and each
word becomes a small inline <svg> of <use> references. Words stay separate
boxes in a wrapping row, so a heading still reflows like text on a phone.
The readable text goes alongside in a visually hidden span (the part after
the bar, when the lettering is capitals), which is what a screen reader and
a search engine get.

The font is read from the app's own assets and never copied here. Set
SEATREN_OTF to point somewhere else.

_build/ starts with an underscore, so GitHub Pages does not serve it.
"""
import html
import os
import re
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FONT = Path(os.environ.get("SEATREN_OTF", ROOT.parent / "PizzaPerksRN/assets/brand/Seatren.otf"))
PAGES = {"template.html": "index.html", "404.template.html": "404.html"}
PAD = 12  # font units of air above and below the tallest and deepest letter
LINE_PITCH = 1.1  # em from one wrapped line of a heading to the next

if not FONT.exists():
    sys.exit(f"font not found: {FONT}  (set SEATREN_OTF)")

tt = TTFont(str(FONT))
UPM = tt["head"].unitsPerEm
ASCENT = tt["hhea"].ascent  # the line the shared letter outlines hang from
glyph_set = tt.getGlyphSet()
glyph_order = tt.getGlyphOrder()
hb_font = hb.Font(hb.Face(hb.Blob.from_file_path(str(FONT))))

used = {}  # glyph name -> short id, in first-use order


def shape(word):
    """[(glyph name, x, y)], advance — one word, kerned."""
    buf = hb.Buffer()
    buf.add_str(word)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf, {"kern": True, "liga": True})
    out, x = [], 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = glyph_order[info.codepoint]
        if name == ".notdef":
            sys.exit(f"the font has no glyph for a character in {word!r}")
        out.append((name, x + pos.x_offset, pos.y_offset))
        x += pos.x_advance
    return out, x


def bounds(name):
    pen = BoundsPen(glyph_set)
    glyph_set[name].draw(pen)
    return pen.bounds  # (xMin, yMin, xMax, yMax) or None for a blank glyph


def lettering(match):
    shown, _, spoken = match.group(1).partition("|")
    spoken = spoken or shown
    words = [shape(w) for w in shown.split()]
    # One box for the whole heading, tight to the letters it actually uses:
    # every word then shares a baseline, and a caps-only label is not pushed
    # off-centre by room for descenders it does not have.
    tops, bottoms = [], []
    for glyphs, _ in words:
        for name, _, dy in glyphs:
            b = bounds(name)
            if b:
                bottoms.append(b[1] + dy)
                tops.append(b[3] + dy)
    top, bottom = max(tops) + PAD, min(bottoms) - PAD
    height = top - bottom
    parts = []
    for glyphs, advance in words:
        uses = []
        for name, x, dy in glyphs:
            if bounds(name) is None:
                continue
            gid = used.setdefault(name, f"g{len(used)}")
            y = f' y="{round(top - ASCENT - dy)}"' if round(top - ASCENT - dy) else ""
            uses.append(f'<use href="#{gid}" x="{round(x)}"{y}/>')
        parts.append(f'<svg class="w" viewBox="0 0 {round(advance)} {round(height)}" '
                     f'style="width:{advance / UPM:.3f}em">{"".join(uses)}</svg>')
    # The gap between wrapped lines makes up the difference to one fixed line
    # pitch, so a heading with no descenders (a shorter box) is not set tighter
    # than one that has them.
    gap = max(LINE_PITCH - height / UPM, 0.08)
    return (f'<span class="vh">{html.escape(spoken)}</span>'
            f'<span class="st" aria-hidden="true" style="--h:{height / UPM:.3f}em;--g:{gap:.3f}em">'
            f'{"".join(parts)}</span>')


def glyph_defs():
    """Every letter used, once. Drawn y-down with the font's ascender line at
    y = 0, so a <use> only has to say how far along the word it sits (and how
    far down, when a heading's box starts below the ascender)."""
    out = []
    for name, gid in used.items():
        pen = SVGPathPen(glyph_set, ntos=lambda v: str(round(v)))
        glyph_set[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, ASCENT)))
        out.append(f'<path id="{gid}" d="{pen.getCommands()}"/>')
    return "".join(out)


for src, dest in PAGES.items():
    used.clear()
    page = (HERE / src).read_text(encoding="utf-8")
    page = re.sub(r"\{\{st:([^}]+)\}\}", lettering, page)
    page = page.replace("{{glyphs}}", glyph_defs())
    left = re.findall(r"\{\{[^}]*\}\}", page)
    if left:
        sys.exit(f"{src}: unresolved placeholders {left}")
    (ROOT / dest).write_text(page, encoding="utf-8")
    print(f"{dest}: {len(page.encode()):,} bytes, {len(used)} letters drawn")
