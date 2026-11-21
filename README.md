# Pizza Perks website

The one-page site at https://yourpizzaperks.com, served by GitHub Pages from the root of `main`.

## What is here

| | |
|---|---|
| `index.html`, `404.html` | The pages GitHub Pages serves. Built files: do not edit them by hand. |
| `assets/` | Images and the body font (DM Sans, SIL Open Font Licence). |
| `CNAME` | Tells GitHub Pages the site's domain. |
| `_build/` | The page templates and the script that builds them. GitHub Pages does not serve folders that start with an underscore. |

## Changing the page

Edit `_build/template.html` (or `_build/404.template.html`), then rebuild:

```bash
python3 _build/build.py
```

It needs `pip install fonttools uharfbuzz`, and the brand's display font, which it reads from the app's assets at `../PizzaPerksRN/assets/brand/Seatren.otf` (set `SEATREN_OTF` to use another copy). The font file is not in this repository on purpose: headings are drawn as outlines at build time instead. `_build/build.py` explains how.

Preview locally:

```bash
node _build/serve.js
```

then open http://localhost:8765.

## Wording

The copy follows the app's own help and FAQ text, so the site and the app say the same thing. It quotes no cashback rate and no price, because those change in the app and a page here would go stale.

The App Store and Google Play badges are left off until the app is published.
