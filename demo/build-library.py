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
⭐ The icons and the link-preview card live at the ROOT (build-icons.py · build-og.py), declared under register
M-0009; og:image is an ABSOLUTE URL (a relative one yields a card with no image, silently).
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

# The share button: the system share sheet where there is one (phones); otherwise the link is copied and the page says
# so once. ⛔ Never a dialog (alert/prompt) — if copying is refused too, the link itself is shown to copy by hand.
SHARE_JS = """
(function () {
  var b = document.getElementById('share'), said = document.getElementById('share-said');
  if (!b || !said) return;
  function tell(t) { said.textContent = t; setTimeout(function () { if (said.textContent === t) said.textContent = ''; }, 2600); }
  b.addEventListener('click', function () {
    var c = document.querySelector('link[rel=canonical]'), url = c ? c.href : location.href;
    if (navigator.share) { navigator.share({ title: 'Books by Thon Ly', url: url }).catch(function () {}); return; }
    var shown = function () { said.textContent = 'Copy this link: ' + url; };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { tell('Link copied'); }, shown);
    } else { shown(); }
  });
})();
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
<meta property="og:image" content="https://book.thonly.org/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The Library: five drawn book covers under the words The Library, book.thonly.org">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#6b4fa0">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
%(canonical)s%(fonts)s
<style>%(css)s</style>
</head>
<body>
<div class="page">
<main class="lib">
<div class="top"><a class="home" href="/">Books by Thon Ly</a>%(share)s</div>
<p class="share-said" id="share-said" aria-live="polite"></p>
%(head)s
<p class="lib-lede">%(lede)s</p>
%(pairs)s
<footer class="foot">thonly.org takes no profit &middot; No advertising</footer>
</main>
</div>
%(caption)s<script>%(script)s</script>
</body>
</html>
"""


def render(landing):
    return PAGE % dict(
        robots="" if landing else UNLISTED,
        title="Books by Thon Ly" if landing else "The Library — draft — book.thonly.org",
        desc=DESC, url="https://book.thonly.org/" if landing else "https://book.thonly.org/demo/library.html",
        canonical='<link rel="canonical" href="https://book.thonly.org/">\n' if landing else "",
        fonts=B.FONTS, css=B.CSS + EXTRA, lede=B.LIB_LEDE, script=SHARE_JS,
        # ⚠️ the landing borrows the demo's signed portrait until the image is placed at the root with its own declaration
        head=B.library_head("/demo/thonly.jpg" if landing else "thonly.jpg"),
        pairs=B.library_html(), share=B.SHARE,
        caption="" if landing else ('<p class="draft">DRAFT &middot; THE LIBRARY, FOR REVIEW &middot; '
                                    'NOT YET THE LANDING PAGE</p>\n'))


if __name__ == "__main__":
    landing = "--landing" in sys.argv
    out = os.path.join(HERE, "..", "index.html") if landing else os.path.join(HERE, "library.html")
    io.open(out, "w", encoding="utf-8").write(render(landing))
    print("wrote %s" % os.path.relpath(out, HERE))
