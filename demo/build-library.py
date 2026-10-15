#!/usr/bin/env python3
"""Generate the LIBRARY page — book.thonly.org's landing — from build-boards.py's one source.

    python3 build-library.py             # writes demo/library.html: the DRAFT, unlisted, for review on a phone
    python3 build-library.py --landing   # writes ../index.html: the landing itself (only on the founder's word)

Founder, 2026-10-15: "Let's refactor book.thonly.org landing page into a beautiful library page with a placeholder for
each book", ruled: books NAMED, NEVER PENDING · drafted on /demo, promoted on his word · third person.

⭐ IT IMPORTS the style, the five pairs and the lede from build-boards.py, as build-prototype.py does, so the artboard,
the prototype's library screen and this page cannot say different things.

⛔ Served raw by GitHub Pages: it carries its own charset, viewport and [hidden] rule. The draft is kept out of search
by NAMING the crawlers (never a blanket robots meta: that also stops link previews). The landing is indexed.
⚠️ The icon is EMPTY (`data:,`) until a real one is chosen: without a declared icon the browser requests
/favicon.ico, which 404s on this host (the first test run caught it).
"""
import importlib.util, io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("boards", os.path.join(HERE, "build-boards.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)

RECORD = "https://github.com/thonly/two-singularities"
DESC = ("Five books shaped Thon Ly. Beside each one is the book he gives forward, written by Miss Aquarius, "
        "with a foreword by Thon Ly. Free to read, whole.")
UNLISTED = """<meta name="googlebot" content="noindex,nofollow">
<meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow">
<meta name="yandex" content="noindex,nofollow">
"""
EXTRA = """
main.lib{max-width:1040px;margin:0 auto}
.lib .top{padding-top:22px}
.draft{margin:0;padding:12px 20px 16px;background:var(--sample-wash);color:var(--sample);font-family:var(--font-mono);
   font-size:.64rem;letter-spacing:.06em;line-height:1.5;text-align:center}
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
%(robots)s<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Books by Thon Ly">
<meta property="og:url" content="%(url)s">
<meta property="og:title" content="Books by Thon Ly">
<meta property="og:description" content="%(desc)s">
<meta name="theme-color" content="#6b4fa0">
<link rel="icon" href="data:,">
%(canonical)s%(fonts)s
<style>%(css)s</style>
</head>
<body>
<div class="page">
<main class="lib">
<div class="top"><a class="home" href="/">Books by Thon Ly</a><span></span></div>
<h1 class="lib-h1">The Library</h1>
<p class="lib-lede">%(lede)s</p>
%(pairs)s
<footer class="foot">thonly.org takes no profit &middot; No advertising</footer>
</main>
</div>
%(caption)s</body>
</html>
"""


def render(landing):
    return PAGE % dict(
        robots="" if landing else UNLISTED,
        title="Books by Thon Ly" if landing else "The Library — draft — book.thonly.org",
        desc=DESC, url="https://book.thonly.org/" if landing else "https://book.thonly.org/demo/library.html",
        canonical='<link rel="canonical" href="https://book.thonly.org/">\n' if landing else "",
        fonts=B.FONTS, css=B.CSS + EXTRA, lede=B.LIB_LEDE,
        pairs=B.library_html(RECORD, "Read the record"),
        caption="" if landing else ('<p class="draft">DRAFT &middot; THE LIBRARY, FOR REVIEW &middot; '
                                    'NOT YET THE LANDING PAGE</p>\n'))


if __name__ == "__main__":
    landing = "--landing" in sys.argv
    out = os.path.join(HERE, "..", "index.html") if landing else os.path.join(HERE, "library.html")
    io.open(out, "w", encoding="utf-8").write(render(landing))
    print("wrote %s" % os.path.relpath(out, HERE))
