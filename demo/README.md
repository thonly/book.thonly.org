# /demo — the design of book.thonly.org

Phases 2 and 3 of the four-phase build (spec → drawings → clickable prototype → implementation). Live, unlisted, at
<https://book.thonly.org/demo/>; everything on one surface at `/demo/wall.html`.

⛔ **Nothing here is the site.** No page is live, no note is sent, nobody is charged. **Every quote is sample text**: no
AI model wrote those words, and no model is named (the seats appear by role; the model slot is left blank). The
author's reply is sample text, the cover is placeholder art, and the printed-copy prices are sample figures.

⚠️ **When a screen and the private memory disagree, the memory is canonical** (see `../SPEC.md`'s header).

## Three layers (founder, 2026-09-16)

**The record** (the rules and every conversation, at `github.com/thonly/two-singularities`) → **the full debate** (for
serious readers) → **the story** (for everyone). The story may choose, order and describe; it may not invent. Words in
quotation marks are always a seat's exact words — `build-boards.py` refuses to build if a story quote is not found word
for word in the debate — and the story says what a seat said and did, never what it felt.

## Files

| | |
|---|---|
| `build-boards.py` | ⭐ **the source**: the shared style, the page chrome, and every board's content. Writes `*.dc.html` and `canvas.json` |
| `*.dc.html` | one artboard each — **generated**; edit `build-boards.py`, never these |
| `measure.mjs` | loads every board in headless Chrome at its design width, writes the real height into `canvas.json`, and **fails** on sideways overflow or a nested scroll container |
| `build-index.py` · `build-wall.py` | generate `index.html` (the front door) and `wall.html` (pan and zoom) from `canvas.json` |
| `build-og.py` | renders `og.png` and `og-walkthrough.png`, the 1200×630 link-preview cards, with headless Chrome |
| `build-prototype.py` | ⭐ writes `walkthrough.html`, **the clickable prototype** (phase 3) — it IMPORTS the style, quotes, titles and cover from `build-boards.py`, so the two cannot disagree |
| `test-walkthrough.mjs` | serves the prototype over HTTP and drives it in headless Chrome at 390 and 1280px: every screen, the note, the printed-copy total, the jump from a quote to the debate, Back, overflow, nested scrollers, exceptions |

## The loop

```sh
python3 build-boards.py && node measure.mjs && python3 build-prototype.py && node test-walkthrough.mjs \
  && python3 build-index.py && python3 build-wall.py && python3 build-og.py
```

Then the structural checks (div balance, quote integrity, tag nesting, and `node --check` on the wall's script), a
look at the screens, commit, push. GitHub Pages publishes in under a minute.

## Search and link previews

Search engines are kept out **by name** (`googlebot`, `bingbot`, `slurp`, `yandex`); there is no blanket robots meta
and **no `robots.txt` on this host** — either would also stop the link-preview crawlers, and Facebook caches a
robots file for about a day. Absence means allow. `og:image` is an absolute URL.

## What the screens are arguing

- Free to read, whole: no locks, no meters, **no reading progress bars**.
- The thanks line comes **after** reading; the thanks on a printed copy comes **after** the purchase, separately.
- A note in plain words is always checked by the seat it explains, and the answer is printed.
- The opening's "Not yet." is set by the arrival test, never by the author.
- An objection's page is ordered by edition only.
- The note form states its character limit once, with no running tally.
