#!/usr/bin/env python3
"""Generate index.html (the front door of /demo/) from canvas.json.

The index is GENERATED, never hand-edited: an artboard added to canvas.json cannot then be missing
from the front door. Adapted 2026-09-16 from demo.heartbank.ceo/build-index.py.

    python3 build-index.py
"""
import io, json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))

BLURB = {
    "page-1": "The front of the library, and the book with its three ways in: the story, the full debate and the record.",
    "page-2": "The story, for everyone: what happened, told in the narrator's voice. Words in quotation marks are exactly "
              "what a seat said, and a check confirms every one; each passage links to the debate it tells.",
    "page-3": "The full debate, for serious readers: the narrator's scene, the four moves in the seats' own words, a note "
              "in plain words checked by the seat it explains, the author's reply and the ledger.",
    "page-4": "Where a reader follows one objection across the years, sees how an edition was made, and reads the "
              "evidence and the two gauges.",
    "page-5": "Thanks, with money or with a note, and a printed copy of the story sold at cost. The thanks on a "
              "purchase comes after it, separately.",
    "page-6": "The story and a debate chapter on a wide screen.",
}


def main():
    canvas = json.load(io.open(os.path.join(HERE, "canvas.json"), encoding="utf-8"))
    boards = canvas["artboards"]
    by_page = {}
    for a in boards:
        by_page.setdefault(a.get("page", "page-1"), []).append(a)
    for v in by_page.values():
        v.sort(key=lambda a: (a["y"], a["x"]))
    sections = []
    for page in canvas["pages"]:
        pid = page["id"]
        rows = "\n".join(
            '      <a class="board" href="./{f}"><span class="t">{t}</span>'
            '<span class="d mono">{tag}{w}&times;{h}</span></a>'.format(
                f=html.escape(a["file"]), t=html.escape(a["title"]),
                tag=("desktop &middot; " if a["w"] > 430 else ""), w=a["w"], h=a["h"])
            for a in by_page.get(pid, []))
        sections.append('    <section class="surface">\n      <h2 class="mono">%s</h2>\n'
                        '      <p class="blurb">%s</p>\n%s\n    </section>'
                        % (html.escape(page["name"]), html.escape(BLURB.get(pid, "")), rows))
    out = TEMPLATE.replace("{{SECTIONS}}", "\n\n".join(sections)).replace("{{COUNT}}", str(len(boards)))
    io.open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(out)
    print("index.html written — %d artboards across %d surfaces" % (len(boards), len(canvas["pages"])))


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<!-- Out of SEARCH by naming the search crawlers, never a blanket robots meta: that form also reaches
     link-preview crawlers and the card disappears. There is deliberately no robots.txt on this host. -->
<meta name="googlebot" content="noindex,nofollow">
<meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow">
<meta name="yandex" content="noindex,nofollow">
<title>Two Singularities — design</title>
<meta property="og:type" content="website">
<meta property="og:url" content="https://book.thonly.org/demo/">
<meta property="og:site_name" content="Books by Thon Ly">
<meta property="og:title" content="Two Singularities — the design">
<meta property="og:description" content="The reading site for Two Singularities, drawn screen by screen: the library, a chapter, the evidence, thanks and printed copies.">
<meta property="og:image" content="https://book.thonly.org/demo/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Two Singularities, on a dark ground with two lights.">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#6b4fa0">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  [hidden]{display:none!important}
  :root{
    --bg:#fcfbfe; --surface:#f4f1fb; --line:rgba(20,16,30,.12); --line-strong:rgba(20,16,30,.28);
    --ink:#16141c; --ink-dim:#5b5766; --ink-faint:#8b8796;
    --accent:#6b4fa0; --accent-soft:#563d85; --accent-wash:rgba(107,79,160,.09); --accent-edge:rgba(107,79,160,.28);
    --font-display:"Newsreader",Georgia,serif; --font-text:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
    --font-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  }
  @media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
    --bg:#0f0e14; --surface:#18171f; --line:rgba(255,255,255,.08); --line-strong:rgba(255,255,255,.18);
    --ink:#f3f1f7; --ink-dim:#a29eab; --ink-faint:#6f6b78;
    --accent:#b9a3e3; --accent-soft:#d6c9f0; --accent-wash:rgba(185,163,227,.12); --accent-edge:rgba(185,163,227,.32);
  }}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-text);font-size:16px;line-height:1.6}
  .mono{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
  a{color:inherit}
  .wrap{max-width:860px;margin:0 auto;padding:48px 22px 72px}
  @media (max-width:430px){.wrap{padding:28px 16px 44px}}
  h1{font-family:var(--font-display);font-size:clamp(2rem,6vw,2.8rem);font-weight:500;margin:0 0 10px;
     letter-spacing:-.02em;line-height:1.1}
  .sub{margin:0 0 30px;color:var(--ink-dim);max-width:58ch}
  .wall-link{display:block;text-decoration:none;border:2px solid var(--accent);background:var(--accent-wash);
     border-radius:20px;padding:20px 22px;margin:0 0 40px}
  .wall-link .kicker{font-family:var(--font-mono);font-size:.68rem;letter-spacing:.09em;text-transform:uppercase;
     color:var(--accent-soft);display:block;margin-bottom:6px}
  .wall-link h2{font-family:var(--font-display);font-size:1.45rem;font-weight:500;margin:0 0 6px}
  .wall-link p{margin:0;color:var(--ink-dim);font-size:.94rem}
  .wall-link.quiet{border:1px solid var(--line-strong);background:var(--surface)}
  .wall-link.quiet .kicker{color:var(--ink-faint)}
  .surface{margin-bottom:36px}
  .surface h2{font-size:.8rem;font-weight:500;letter-spacing:.06em;margin:0 0 5px;color:var(--accent-soft)}
  .blurb{margin:0 0 14px;color:var(--ink-dim);font-size:.9rem;max-width:64ch}
  .board{display:flex;align-items:center;justify-content:space-between;gap:14px;text-decoration:none;
     padding:12px 16px;border:1px solid var(--line);border-radius:14px;margin-bottom:7px}
  .board:hover{border-color:var(--accent);background:var(--surface)}
  .board .t{font-size:.96rem;font-weight:500}
  .board .d{font-size:.74rem;color:var(--ink-faint);flex:none}
  footer{margin-top:48px;padding-top:22px;border-top:1px solid var(--line);color:var(--ink-faint);font-size:.84rem}
  footer p{margin:0 0 9px;max-width:66ch}
  footer b{color:var(--ink-dim);font-weight:500}
</style>
</head>
<body>
<div class="wrap">
  <h1>Two Singularities &mdash; the design</h1>
  <p class="sub">The reading site at <span class="mono">book.thonly.org</span>, drawn screen by screen:
    {{COUNT}} artboards across six surfaces, in three layers: the story, the full debate, and the record behind them. Phase 3 of 4: the drawings, and a reader you can use.</p>

  <a class="wall-link start" href="./walkthrough.html">
    <span class="kicker">Start here</span>
    <h2>Try the reader</h2>
    <p>Read a chapter of the story, open the debate behind a quote, follow the objection, and say thanks, or buy a
      printed copy at cost. It works; nothing in it is sent or charged.</p>
  </a>

  <a class="wall-link quiet" href="./wall.html">
    <span class="kicker">All of it at once</span>
    <h2>The wall</h2>
    <p>Every screen on one pan-and-zoom surface, grouped by what the reader is doing.</p>
  </a>

{{SECTIONS}}

  <footer>
    <p><b>These are drawings, not the site.</b> Nothing here is live, nobody is charged, and no note is sent.</p>
    <p><b>Every quote is sample text.</b> No AI model wrote these words, and no model is named: the seats appear by
      role, and the model slot is left blank. The author's reply is sample text too.</p>
    <p><b>The cover is placeholder art</b>, and the printed-copy prices are sample figures.</p>
  </footer>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    main()
