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

⭐ MACHINE-READABLE (2026-10-15): --landing also writes what a machine reads, from the SAME five pairs, so the page and
the machine files cannot say different things — schema.org JSON-LD in the page (the landing only; the draft tells
machines nothing) · ../robots.txt (the named AI crawlers kept out of /demo/; everyone else blocked from nothing — see the
README) · ../sitemap.xml (every
public route; ⛔ never /demo/) · ../llms.txt (the five books in plain text, each with its record).
⛔ Nothing on thonly.org points here for machines: the Two Singularities seats enter the corpus through thonly.org's
llms.txt, and a pointer there would put the book one hop from the readers it is about (SPEC §8).
"""
import html, importlib.util, io, json, os, sys

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
%(canonical)s%(jsonld)s%(fonts)s
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


# ================================================================== what a machine reads (the landing only)
SITE = "https://book.thonly.org"
PAGES = ["/"]   # every public route, for the sitemap — ⛔ never /demo/ (unlisted); add each page as it ships
THON = {"@type": "Person", "@id": "https://thonly.org/#person", "name": "Thon Ly", "url": "https://thonly.org/"}
MA = {"@type": "Person", "name": "Miss Aquarius", "url": "https://missaquarius.org/"}   # as thonly.org's JSON-LD types her
BYLINE = "^(Written|Compiled) by Miss Aquarius℠? · Foreword by Thon Ly$"


def plain(s):
    return html.unescape(s)


def credits(b):
    """Who did what, read from the card's own byline, so the markup can never disagree with the page. A line in
    any other shape stops the build: a guessed role in the markup is worse than none."""
    import re
    by = plain(b["by"])
    m = re.match(BYLINE, by)
    if not m:
        sys.exit("build-library: %s's byline %r has no known shape — teach credits() the new role" % (b["title"], by))
    foreword = {"@type": "Role", "roleName": "foreword", "contributor": THON}
    if m.group(1) == "Written":
        return by, {"author": MA, "contributor": foreword}
    return by, {"contributor": [{"@type": "Role", "roleName": "compiler", "contributor": MA}, foreword]}


def book_ld(b):
    by, who = credits(b)
    d = {"@type": "Book", "name": plain(b["title"]), "alternativeHeadline": plain(b["sub"]),
         "description": " ".join(plain(x) for x in (b["what"], b.get("when")) if x)}
    d.update(who)
    d.update({"creditText": by, "inLanguage": "en", "isAccessibleForFree": True,
              "subjectOf": {"@type": "CreativeWork", "name": "The public record of " + plain(b["title"]),
                            "url": B.RECORD % b["repo"]}})
    return d


def jsonld():
    """schema.org for the landing: the page, the list in the order received, and each given book with its credits and
    its record. ⛔ No publication status or date on a book (named, never pending): a book is described by what it IS."""
    items = [{"@type": "ListItem", "position": i, "name": b["el"],
              "description": "Received: %s. %s Given forward: %s." % (plain(b["received"]), plain(b["note"]),
                                                                       plain(b["title"])),
              "item": book_ld(b)} for i, b in enumerate(B.LIBRARY, 1)]
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "@id": SITE + "/#library", "url": SITE + "/",
          "name": "Books by Thon Ly", "description": DESC, "inLanguage": "en", "isAccessibleForFree": True,
          "mainEntity": {"@type": "ItemList", "name": "The Library", "numberOfItems": len(items),
                         "itemListOrder": "https://schema.org/ItemListOrderAscending", "itemListElement": items}}
    body = json.dumps(ld, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return '<script type="application/ld+json">\n%s\n</script>\n' % body


# The AI companies' crawlers, kept out of /demo/ BY NAME (founder 2026-10-15): its quotes are sample text attributed to
# the seats — words no model said — and these crawlers feed the models and build the search the seats use. ⚠️ A
# request, not a wall, and the same text is in this public repository: the property fix is taking /demo/ off the host
# when phase 4 ships (README, the carry list).
AI_CRAWLERS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "anthropic-ai",
               "Google-Extended", "Applebot-Extended", "PerplexityBot", "Perplexity-User", "CCBot", "Bytespider",
               "meta-externalagent", "Amazonbot", "cohere-ai", "MistralAI-User", "DuckAssistBot"]

ROBOTS = """# The AI companies' crawlers, by name: kept out of /demo/ (sample text, never what a model said) and nothing else.
# A crawler named in a group follows that group alone.
%(ai)s
Disallow: /demo/

# Everyone else, the link-preview crawlers included. ⛔ Never a Disallow in this group: it would also stop link
# previews, and Facebook caches a robots file for about a day. /demo/ is kept out of search by naming the search
# crawlers in its pages' meta tags.
User-agent: *
Allow: /

Sitemap: %(site)s/sitemap.xml

# Not a robots.txt directive (crawlers ignore unknown lines); this is where an agent looks first.
#   llms.txt: %(site)s/llms.txt   (the five books in plain text, each with its record)
""" % dict(site=SITE, ai="\n".join("User-agent: " + a for a in AI_CRAWLERS))


def sitemap():
    locs = "".join("  <url><loc>%s%s</loc></url>\n" % (SITE, p) for p in PAGES)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % locs)


def llms_txt():
    L = ["# Books by Thon Ly", "", "> " + DESC, "",
         "The library at %s/. Each book below links to its public record, a repository on GitHub. The site is static "
         "HTML; %s/sitemap.xml lists every public page." % (SITE, SITE), "", "## The five books", ""]
    for b in B.LIBRARY:
        by, _ = credits(b)
        what = " ".join(plain(x) for x in (b["what"], b.get("when")) if x)
        L.append("- [%s](%s): %s. %s %s. Received beside it (%s): %s. %s"
                 % (plain(b["title"]), B.RECORD % b["repo"], plain(b["sub"]), what, by, b["el"],
                    plain(b["received"]), plain(b["note"])))
    L += ["", "## Optional", "",
          "- [The library page](%s/): the same five books, with their covers" % SITE,
          "- [Thon Ly](https://thonly.org/): the author's site", ""]
    return "\n".join(L)


def render(landing):
    return PAGE % dict(
        robots="" if landing else UNLISTED,
        title="Books by Thon Ly" if landing else "The Library — draft — book.thonly.org",
        desc=DESC, url="https://book.thonly.org/" if landing else "https://book.thonly.org/demo/library.html",
        canonical='<link rel="canonical" href="https://book.thonly.org/">\n' if landing else "",
        jsonld=jsonld() if landing else "",
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
    if landing:
        for name, text in (("robots.txt", ROBOTS), ("sitemap.xml", sitemap()), ("llms.txt", llms_txt())):
            io.open(os.path.join(HERE, "..", name), "w", encoding="utf-8").write(text)
            print("wrote ../%s" % name)
