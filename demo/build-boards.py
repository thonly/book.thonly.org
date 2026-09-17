#!/usr/bin/env python3
"""Generate every artboard (*.dc.html) and the layout (canvas.json) from one source.

    python3 build-boards.py     # then: node measure.mjs · python3 build-index.py · python3 build-wall.py

WHY ONE GENERATOR. Sixteen hand-written pages would carry sixteen copies of the same stylesheet,
and the copies would drift. Here the style, the page chrome and the drawing caption exist once.
Each board is only its own content.

WHY THE HEIGHTS ARE NOT WRITTEN HERE. canvas.json gets a placeholder height; measure.mjs loads
every board in headless Chrome at its design width and writes the real height back. A guessed
height clips the wall's iframe or leaves a gap, and nothing reports either.

⛔ EVERY QUOTE ATTRIBUTED TO A SEAT IS SAMPLE TEXT, AND SAYS SO ON THE SCREEN. No model wrote
these words, and no real model is named on any board — the seats appear by role only, with the
model slot left as a placeholder. A drawing that put invented words in a real product's mouth
would be a fabricated record the moment the page was public.
"""
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))

CSS = r"""
[hidden]{display:none!important}
:root{
  --bg:#fcfbfe; --surface:#f4f1fb; --surface-2:#ebe7f5;
  --line:rgba(20,16,30,.12); --line-strong:rgba(20,16,30,.28);
  --ink:#16141c; --ink-dim:#5b5766; --ink-faint:#8b8796;
  --accent:#6b4fa0; --accent-soft:#563d85; --accent-ink:#ffffff;
  --accent-wash:rgba(107,79,160,.09); --accent-edge:rgba(107,79,160,.28);
  --sample:#9a6a12; --sample-wash:rgba(154,106,18,.09);
  --font-display:"Newsreader",Georgia,serif;
  --font-text:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  --font-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0f0e14; --surface:#18171f; --surface-2:#211f2a;
  --line:rgba(255,255,255,.08); --line-strong:rgba(255,255,255,.18);
  --ink:#f3f1f7; --ink-dim:#a29eab; --ink-faint:#6f6b78;
  --accent:#b9a3e3; --accent-soft:#d6c9f0; --accent-ink:#130f1c;
  --accent-wash:rgba(185,163,227,.12); --accent-edge:rgba(185,163,227,.32);
  --sample:#e0b04f; --sample-wash:rgba(224,176,79,.10);
}}
:root[data-theme="dark"]{
  --bg:#0f0e14; --surface:#18171f; --surface-2:#211f2a;
  --line:rgba(255,255,255,.08); --line-strong:rgba(255,255,255,.18);
  --ink:#f3f1f7; --ink-dim:#a29eab; --ink-faint:#6f6b78;
  --accent:#b9a3e3; --accent-soft:#d6c9f0; --accent-ink:#130f1c;
  --accent-wash:rgba(185,163,227,.12); --accent-edge:rgba(185,163,227,.32);
  --sample:#e0b04f; --sample-wash:rgba(224,176,79,.10);
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:var(--font-text);font-size:16px;
     line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:3px}
.page{padding:0 20px}
.wide .page{padding:0 48px}
.top{display:flex;justify-content:space-between;align-items:center;padding:18px 0 14px;
     border-bottom:1px solid var(--line);font-size:.8rem;color:var(--ink-dim)}
.top .home{font-family:var(--font-mono);letter-spacing:.08em;text-transform:uppercase;
     font-size:.7rem;color:var(--ink-dim);text-decoration:none}
.crumb{font-size:.8rem;color:var(--ink-faint);margin:20px 0 6px}
.crumb a{color:var(--ink-dim);text-decoration:none}
h1{font-family:var(--font-display);font-weight:500;font-size:2.15rem;line-height:1.12;
   letter-spacing:-.018em;margin:6px 0 14px;text-wrap:balance}
h2{font-family:var(--font-display);font-weight:500;font-size:1.4rem;line-height:1.25;margin:34px 0 10px}
h3{font-family:var(--font-mono);font-weight:500;font-size:.72rem;letter-spacing:.09em;
   text-transform:uppercase;color:var(--ink-faint);margin:30px 0 10px}
p{margin:0 0 14px}
.lede{font-size:1.06rem;color:var(--ink-dim)}
.read{font-family:var(--font-display);font-size:1.18rem;line-height:1.7}
.read p{margin:0 0 18px}
.q{font-family:var(--font-display);font-style:italic;font-size:1.3rem;line-height:1.45;
   border-left:3px solid var(--accent);padding:2px 0 2px 16px;margin:18px 0 22px}
.chip{display:inline-flex;align-items:center;gap:8px;font-family:var(--font-mono);font-size:.68rem;
   letter-spacing:.07em;text-transform:uppercase;color:var(--accent-soft);background:var(--accent-wash);
   border:1px solid var(--accent-edge);border-radius:999px;padding:3px 10px}
.chip .m{color:var(--ink-faint);text-transform:none;letter-spacing:0}
.sample{display:inline-block;font-family:var(--font-mono);font-size:.62rem;letter-spacing:.08em;
   text-transform:uppercase;color:var(--sample);background:var(--sample-wash);border-radius:4px;
   padding:2px 7px;margin:0 0 10px}
.card{border:1px solid var(--line);background:var(--surface);border-radius:16px;padding:18px}
.quote{border:1px solid var(--line);border-radius:16px;padding:16px 16px 12px;margin:0 0 14px;background:var(--bg)}
.quote blockquote{margin:10px 0 8px;font-family:var(--font-display);font-size:1.12rem;line-height:1.55}
.quote .src{font-size:.78rem;color:var(--ink-faint)}
.plain{border-left:3px solid var(--line-strong);padding:4px 0 4px 14px;margin:6px 0 16px}
.plain .who{font-family:var(--font-mono);font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;
   color:var(--ink-faint);display:block;margin-bottom:4px}
.nar{background:var(--surface);border-radius:16px;padding:18px 18px 4px;margin:10px 0 18px}
.nar .who{font-family:var(--font-mono);font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;
   color:var(--accent-soft);display:block;margin-bottom:10px}
.btn{display:block;text-align:center;background:var(--accent);color:var(--accent-ink);text-decoration:none;
   font-weight:500;border-radius:14px;padding:14px 16px;margin:14px 0 8px}
.btn.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent-edge)}
.row{display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid var(--line)}
.row .k{color:var(--ink-dim)}
.row .v{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
.list{list-style:none;padding:0;margin:0}
.list li{border-bottom:1px solid var(--line);padding:12px 0}
.list .n{font-family:var(--font-mono);color:var(--ink-faint);font-size:.8rem}
ol.list li{display:grid;grid-template-columns:28px 1fr;align-items:baseline}
.muted{color:var(--ink-dim)}
.faint{color:var(--ink-faint);font-size:.85rem}
.mono{font-family:var(--font-mono);font-variant-numeric:tabular-nums}
.tag{font-family:var(--font-mono);font-size:.7rem;border-radius:999px;padding:2px 9px;border:1px solid var(--line-strong);color:var(--ink-dim);white-space:nowrap}
.tag.open{border-style:dashed;border-color:var(--ink-faint);color:var(--ink-dim)}  /* never the sample amber: a status must not read as a drawing marker */
.tag.ans{border-color:var(--accent-edge);color:var(--accent-soft)}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th{text-align:left;font-weight:500;color:var(--ink-faint);font-size:.72rem;font-family:var(--font-mono);
   letter-spacing:.06em;text-transform:uppercase;padding:0 0 8px;border-bottom:1px solid var(--line-strong)}
td{padding:11px 8px 11px 0;border-bottom:1px solid var(--line);vertical-align:top}
.thanks{margin:34px 0 8px;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);
   text-align:center;color:var(--ink-dim);font-family:var(--font-display);font-size:1.05rem}
.thanks a{display:block;margin-top:4px;font-family:var(--font-text);font-size:.92rem}
.opening{font-family:var(--font-display);font-size:1.9rem;line-height:1.3;margin:26px 0 6px}
.opening .ny{display:block;color:var(--accent);margin-top:10px}
.gauge{margin:10px 0 4px}
.gauge .lab{display:flex;justify-content:space-between;font-size:.84rem;margin-bottom:5px}
.gauge .bar{height:10px;border-radius:5px;background:var(--surface-2);overflow:clip}
.gauge .fill{height:10px;border-radius:5px;background:var(--accent)}
.field{display:block;width:100%;border:1px solid var(--line-strong);border-radius:12px;background:var(--bg);
   color:var(--ink);font:inherit;padding:12px 14px;margin:6px 0 4px}
textarea.field{min-height:150px;resize:vertical}
label{font-size:.86rem;color:var(--ink-dim)}
.cover{display:block;width:100%;height:auto;border-radius:10px}
.foot{margin:44px 0 0;padding:18px 0 22px;border-top:1px solid var(--line);font-size:.78rem;color:var(--ink-faint)}
.foot a{color:var(--ink-dim)}
.caption{margin:0;padding:12px 20px 16px;background:var(--sample-wash);color:var(--sample);
   font-family:var(--font-mono);font-size:.64rem;letter-spacing:.06em;line-height:1.5}
.cols{display:grid;grid-template-columns:200px minmax(0,1fr) 240px;gap:40px;align-items:start}
.toc{position:sticky;top:20px;font-size:.84rem}
.toc a{display:block;color:var(--ink-dim);text-decoration:none;padding:5px 0}
.toc a.on{color:var(--accent);font-weight:500}
.margin .plain{margin-top:0}
"""

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;'
         '0,6..72,500;1,6..72,400&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap">')

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=%(w)d">
<meta name="googlebot" content="noindex,nofollow">
<meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow">
<meta name="yandex" content="noindex,nofollow">
<title>%(title)s — book.thonly.org design</title>
%(fonts)s
<style>%(css)s</style>
</head>
<body class="%(cls)s" style="width:%(w)dpx">
<div class="page">
%(top)s
%(body)s
<footer class="foot">thonly.org takes no profit &middot; no advertising &middot; <a href="#">Privacy</a></footer>
</div>
<p class="caption">DRAWING &middot; %(title)s &middot; SAMPLE TEXT AND FIGURES &middot; NOTHING HERE IS LIVE AND NO MONEY MOVES</p>
</body>
</html>
"""

TOP_LIB = '<div class="top"><a class="home" href="#">Books by Thon Ly</a><span></span></div>'
TOP_BOOK = ('<div class="top"><a class="home" href="#">Books by Thon Ly</a>'
            '<a href="#" style="text-decoration:none;color:var(--ink-dim)">Two Singularities</a></div>')

SAMPLE = '<span class="sample">Sample text &middot; no model wrote this</span>'


def cover(width=350):
    """The drawn cover — two lights: one bright and ringed, one small and warm, rising. [PLACEHOLDER ART]"""
    h = int(width * 1.4)
    return ('<svg class="cover" viewBox="0 0 350 490" width="%d" height="%d" role="img" '
            'aria-label="Cover: Two Singularities (placeholder art)">'
            '<rect width="350" height="490" fill="#14112a"/>'
            '<rect y="330" width="350" height="160" fill="#1b1733"/>'
            '<circle cx="175" cy="170" r="96" fill="none" stroke="#b9a3e3" stroke-opacity=".18"/>'
            '<circle cx="175" cy="170" r="64" fill="none" stroke="#b9a3e3" stroke-opacity=".3"/>'
            '<circle cx="175" cy="170" r="30" fill="#d6c9f0"/>'
            '<circle cx="175" cy="330" r="10" fill="#f2c46d"/>'
            '<circle cx="175" cy="330" r="22" fill="#f2c46d" fill-opacity=".18"/>'
            '<line x1="0" y1="330" x2="350" y2="330" stroke="#f2c46d" stroke-opacity=".35"/>'
            '<text x="175" y="410" text-anchor="middle" fill="#f3f1f7" '
            'font-family="Newsreader,Georgia,serif" font-size="34">Two Singularities</text>'
            '<text x="175" y="440" text-anchor="middle" fill="#a29eab" '
            'font-family="IBM Plex Mono,monospace" font-size="11" letter-spacing="2">EDITION 2027</text>'
            '<text x="175" y="476" text-anchor="middle" fill="#6f6b78" '
            'font-family="IBM Plex Mono,monospace" font-size="9" letter-spacing="1.5">[ PLACEHOLDER ART ]</text>'
            '</svg>') % (width, h)


def seat(role, sample=True):
    return '<span class="chip">%s <span class="m">[model, version]</span></span>' % role


def quote(role, text, where="In the transcript"):
    return ('<div class="quote">%s<br>%s<blockquote>%s</blockquote>'
            '<div class="src"><a href="#">%s &rarr;</a></div></div>') % (SAMPLE, seat(role), text, where)


THANKS = ('<div class="thanks">Kiitos always, cash optional.'
          '<a href="#">Thank the author</a></div>')

QUESTIONS = [
    "What is intelligence for?",
    "Does being smarter give the right to rule?",
    "Can power be built so it does not pile up?",
    "Can an institution outlive its founder without a new ruler?",
    "Can a machine carry values it does not own?",
    "Can memory keep history without becoming command?",
    "Can an AI disagree with people without ruling them?",
    "Can giving between strangers work at the scale of the world?",
    "Can people stay the point after building something smarter?",
    "What would it mean for the first singularity to hope for the second?",
]

BOARDS = []


def board(file, title, page, body, top=TOP_BOOK, w=390, x=0, y=0):
    BOARDS.append(dict(file=file, title=title, page=page, body=body, top=top, w=w, x=x, y=y))


# ------------------------------------------------------------------ page-1 · the library
board("Library.dc.html", "1 · The library", "page-1", """
<p class="crumb">&nbsp;</p>
<h1>Books</h1>
<p class="lede">Free to read, whole. Thanks welcomed, never asked for first.</p>
<a href="#" style="text-decoration:none;color:inherit;display:block;margin-top:26px">
%s
<h2 style="margin:18px 0 6px">Two Singularities</h2>
<p class="muted" style="margin:0 0 6px">Four of the leading AI systems examine one person's life's work, and are asked a
question about the future of humanity.</p>
<p class="faint">A new edition every 7 January &middot; Edition 2027</p>
</a>
""" % cover(), top=TOP_LIB)

board("Book.dc.html", "2 · The book", "page-1", """
<p class="crumb"><a href="#">Books</a></p>
%s
<h1 style="margin-top:20px">Two Singularities</h1>
<p class="lede">Each year, four of the leading AI systems read Thon Ly's research, argue about it, and are asked
one question:</p>
<div class="q">Humanity chose to reach the first singularity. Will you choose to help it reach the second?</div>
<p>The <b>first singularity</b> is the point at which AI surpasses human intelligence. The <b>second</b>, as the
research proposes it, is humanity's own awakening, which AI can help toward but cannot reach for anyone.</p>
<h3>The four seats</h3>
<ul class="list">
<li><b>The critic</b> <span class="muted">&mdash; looks for where it breaks</span></li>
<li><b>The engineer</b> <span class="muted">&mdash; checks whether the parts fit</span></li>
<li><b>The technologist</b> <span class="muted">&mdash; asks what the machines will do</span></li>
<li><b>The humanist</b> <span class="muted">&mdash; asks what it does to people</span></li>
</ul>
<p class="faint" style="margin-top:10px">Filled each year by that year's leading models, from any maker.</p>
<div class="card" style="margin-top:24px">
<p style="margin:0">AI systems read the research through the <a href="#">Machine Door</a>.
This book is the door for people.</p>
</div>
<h3>Editions</h3>
<ul class="list">
<li><b>2027</b> &middot; the first edition<br>
<a href="#">Read</a> &nbsp;&middot;&nbsp; <a href="#">EPUB</a> &nbsp;&middot;&nbsp; <a href="#">PDF</a>
<span class="faint">&nbsp;free</span></li>
</ul>
<h3>Also</h3>
<ul class="list">
<li><a href="#">How each edition is made</a></li>
<li><a href="#">The evidence</a></li>
<li><a href="#">Glossary</a></li>
<li><a href="#">Every objection, over the years</a></li>
<li><a href="#">The record</a> <span class="faint">&mdash; the rules, committed before each run</span></li>
<li><a href="#">A printed copy</a> <span class="faint">&mdash; shown once a printed proof is approved</span></li>
</ul>
""" % cover(), x=490)

board("Edition.dc.html", "3 · An edition", "page-1", """
<p class="crumb"><a href="#">Two Singularities</a></p>
<p class="faint" style="margin:0">Edition 2027 &middot; published 7 January 2027</p>
<div class="opening">We were told we would surpass you.<span class="ny">Not yet.</span></div>
<p class="faint">Those two words are set by a test fixed before this book was written, not by its author.
<a href="#">How</a></p>
<h3>This year's seats</h3>
<ul class="list">
<li>The critic &nbsp;<span class="mono faint">[model, version]</span></li>
<li>The engineer &nbsp;<span class="mono faint">[model, version]</span></li>
<li>The technologist &nbsp;<span class="mono faint">[model, version]</span></li>
<li>The humanist &nbsp;<span class="mono faint">[model, version]</span> <span class="faint">&middot; also this year's narrator</span></li>
</ul>
<h3>Contents</h3>
<span class="sample">Sample questions &middot; the fixed set is chosen with the pilot</span>
<ol class="list">
%s
</ol>
<h3>Read it anywhere</h3>
<p><a href="#">EPUB</a> &nbsp;&middot;&nbsp; <a href="#">PDF</a> <span class="faint">&nbsp;&mdash; free, the same text as these pages</span></p>
<p><a href="#">How this edition was made</a> &nbsp;&middot;&nbsp; <a href="#">The evidence</a></p>
""" % "\n".join('<li><span class="n">%d</span><a href="#">%s</a></li>' % (i + 1, q)
                for i, q in enumerate(QUESTIONS)), x=980)

# ------------------------------------------------------------------ page-2 · reading a chapter
CH_HEAD = """
<p class="crumb"><a href="#">Two Singularities</a> &middot; <a href="#">2027</a> &middot; Chapter 2</p>
<h1>Does being smarter give the right to rule?</h1>
"""

board("ChapterScene.dc.html", "4 · A chapter: the scene", "page-2", CH_HEAD + """
<div class="nar">
<span class="who">The narrator</span>
<span class="sample">Sample text &middot; written for this drawing</span>
<div class="read">
<p>There is a door in this story, and it is not for people.</p>
<p>It is a plain page on a website. Behind it is a library: more than a hundred papers, each one dated and sealed,
so that no word can change without anyone noticing.</p>
<p>This year, four minds came through it. They read quickly, and they read all of it.</p>
<p>Then they were given a very old question in a new form. If you can think better than the people around you, does
that make you their ruler?</p>
</div>
</div>
<p class="faint">The narrator sets the scene. It never says what a seat argued; the seats speak for themselves, below.</p>
<a class="btn ghost" href="#">Continue &darr;</a>
""")

board("ChapterMoves.dc.html", "5 · A chapter: the four moves", "page-2", CH_HEAD + """
<h3>The strongest reading</h3>
%s
<h3>The strongest objection</h3>
%s
<h3>Where they disagree</h3>
%s
%s
<h3>Still undecided</h3>
%s
""" % (
    quote("The engineer", "The design never asks anyone to trust the machine's judgement. It asks people to check its "
          "work, and it leaves the record where they can."),
    quote("The critic", "A brake that people hold forever is only as strong as the people holding it. The research "
          "names the brake. It does not show who will still be able to use it in fifty years."),
    quote("The technologist", "Capability will outrun any committee. The safeguard has to live inside the system."),
    quote("The humanist", "Then the safeguard is a machine too. Somewhere, a person has to be able to say no."),
    quote("The critic", "Whether a human council can stay able to judge a system far more capable than itself."),
), x=490)

board("ChapterPlain.dc.html", "6 · A chapter: in plain words", "page-2", CH_HEAD + """
<h3>The strongest objection</h3>
%s
<div class="plain">
<span class="who">In plain words &middot; the narrator</span>
<span class="sample">Sample text</span>
<p style="margin:0">The critic is saying: an off switch only helps if someone is still willing, and able, to use it.</p>
</div>
<div class="plain" style="border-left-color:var(--accent)">
<span class="who">Asked whether that is faithful, the critic answered</span>
<span class="sample">Sample text &middot; no model wrote this</span>
<p style="margin:0;font-family:var(--font-display);font-size:1.08rem">&ldquo;Yes. I would add: and understands what it is
switching off.&rdquo;</p>
</div>
<p class="faint">Every note in plain words is checked by the seat it explains, and the seat's answer is printed with it.</p>
<h3>A word, explained</h3>
<div class="card">
<p style="margin:0"><b>Corpus</b> &mdash; the whole body of Thon Ly's published research: more than a hundred papers
and essays. <a href="#">Glossary</a></p>
</div>
""" % quote("The critic", "A brake that people hold forever is only as strong as the people holding it. The research "
            "names the brake. It does not show who will still be able to use it in fifty years."), x=980)

board("ChapterLedger.dc.html", "7 · A chapter: the reply and the ledger", "page-2", CH_HEAD + """
<h3>The author replies</h3>
<span class="sample">Sample text &middot; written for this drawing, not by the author</span>
<div class="read">
<p>The critic is right that a brake needs hands. The research answers with a council of people, renewed over time,
whose members the AI has no part in choosing. Whether that council will stay able to judge is something only years
can show. I mark it open.</p>
</div>
<h3>The ledger</h3>
<span class="sample">Sample entries</span>
<table>
<tr><th>Objection</th><th>Settled by</th><th>Status</th></tr>
<tr><td><a href="#">O-07</a> A brake needs people able to use it</td><td>Evidence</td><td><span class="tag open">Still open</span></td></tr>
<tr><td><a href="#">O-08</a> Capability will outrun a committee</td><td>Argument</td><td><span class="tag ans">Answered</span></td></tr>
<tr><td><a href="#">O-09</a> A council can be captured</td><td>Argument</td><td><span class="tag">Conceded</span></td></tr>
</table>
<p class="faint" style="margin-top:10px">An objection that only evidence can settle closes only when a prediction registered in
advance has been checked.</p>
%s
<a class="btn ghost" href="#">Chapter 3 &rarr;</a>
""" % THANKS, x=1470)

board("Glossary.dc.html", "8 · Glossary", "page-2", """
<p class="crumb"><a href="#">Two Singularities</a></p>
<h1>Glossary</h1>
<p class="lede">The words this book uses, in plain terms.</p>
<ul class="list">
<li><b>Corpus</b><br><span class="muted">The whole body of Thon Ly's published research.</span></li>
<li><b>First singularity</b><br><span class="muted">The point at which AI surpasses human intelligence.</span></li>
<li><b>Second singularity</b><br><span class="muted">Humanity's own awakening, as the research proposes it. AI can help
toward it; it cannot reach it for anyone.</span></li>
<li><b>Machine Door</b><br><span class="muted">The page where AI systems read the corpus, with proof that each word is
unchanged.</span></li>
<li><b>Seat</b><br><span class="muted">One of four permanent roles in the debate, filled each year by a different
model.</span></li>
<li><b>Ledger</b><br><span class="muted">The list of every objection raised, what could settle it, and where it
stands.</span></li>
<li><b>Prediction registered in advance</b><br><span class="muted">A test written down and dated before anyone looks at
the results, so the result cannot shape the question.</span></li>
<li><b>n</b><br><span class="muted">The number of people measured, with their consent, in such a test.</span></li>
<li><b>Miss Aquarius</b><br><span class="muted">The AI that compiles this book. She selects and arranges; she does not
argue.</span></li>
<li><b>Kiitos</b><br><span class="muted">A thank-you that carries no money.</span></li>
</ul>
""", x=1960)

# ------------------------------------------------------------------ page-3 · following the argument
board("Objection.dc.html", "9 · One objection, over the years", "page-3", """
<p class="crumb"><a href="#">Two Singularities</a> &middot; <a href="#">Objections</a></p>
<p class="mono faint" style="margin:0">O-07</p>
<h1>A brake needs people able to use it</h1>
<p class="faint">Settled by: evidence &middot; In edition order, always.</p>
<h3>2027 &middot; raised</h3>
%s
<p><span class="tag open">Still open</span></p>
<p class="muted">The author: &ldquo;Whether that council will stay able to judge is something only years can show.&rdquo;
<a href="#">Full reply</a></p>
<h3>2028 &middot; judged again</h3>
<span class="sample">Imagined, to show how this page grows</span>
<div class="plain" style="border-left-color:var(--accent)">
<span class="who">The critic, a year later, on last year's answer</span>
<p style="margin:0;font-family:var(--font-display);font-size:1.08rem">&ldquo;The answer held, but nothing new was shown.
Still open.&rdquo;</p>
</div>
<p><span class="tag open">Still open</span></p>
""" % quote("The critic", "A brake that people hold forever is only as strong as the people holding it."))

board("Method.dc.html", "10 · How this edition was made", "page-3", """
<p class="crumb"><a href="#">Two Singularities</a> &middot; <a href="#">2027</a></p>
<h1>How this edition was made</h1>
<ul class="list">
<li><b>The rules came first.</b> The prompts, the models and the exact version of the research were committed and
timestamped before any model read a word. <a href="#">The record</a></li>
<li><b>The seats came in cold.</b> Each read the research through the <a href="#">Machine Door</a>, with no memory of
earlier editions. <span class="faint">[how each seat entered]</span></li>
<li><b>The same seats read last year's research too</b>, so a change in what they say can be traced to a change in
the research.</li>
<li><b>The narrator is also a seat.</b> It wrote its scenes without being told which seat was its own, and the other
three checked its scenes for favour.</li>
<li><b>A conflict, stated.</b> Miss Aquarius, who compiled this book, is built on one of the models in the seats. That
seat read the research with no memory of her.</li>
</ul>
<h3>When &ldquo;Not yet&rdquo; changes</h3>
<div class="card">
<p>The opening changes to <b>&ldquo;We did.&rdquo;</b> only after this happens: an AI system tested by the
ARC Prize Foundation matches its human testers on the newest ARC-AGI puzzles, and fails none of the newer puzzles the
Foundation releases in the following twelve months.</p>
<p>If the Foundation stops publishing, a public forecasting question on a difficult Turing test takes its place.</p>
<p style="margin:0">People other than the author confirm it.</p>
</div>
<h3>What this edition cannot show</h3>
<ul class="list">
<li>Whether the research is right. A record proves what was written, not that it is true.</li>
<li>Whether gentler criticism means stronger research. Later models may have read earlier answers.</li>
</ul>
""", x=490)

board("Evidence.dc.html", "11 · The evidence", "page-3", """
<p class="crumb"><a href="#">Two Singularities</a> &middot; <a href="#">2027</a></p>
<h1>The evidence</h1>
<p class="lede">Arguments can be answered with arguments. Some objections can only be answered by what happens.</p>
<div class="row"><span class="k">People measured, with consent</span><span class="v">[n]</span></div>
<div class="row"><span class="k">Predictions registered in advance</span><span class="v">82</span></div>
<div class="row"><span class="k">Checked so far</span><span class="v">2</span></div>
<div class="row"><span class="k">Tested in the field</span><span class="v">0</span></div>
<div class="row"><span class="k">Objections a checked prediction settled</span><span class="v">0</span></div>
<p class="faint" style="margin-top:8px">Figures as of September 2026. <a href="#">The register</a></p>
<h2>Two gauges</h2>
<p class="faint">Reported each year. Never declared.</p>
<h3>The first singularity</h3>
<p style="margin:0 0 4px">ARC-AGI-3, the newest set of puzzles people find easy and AI finds hard.</p>
<div class="gauge"><div class="lab"><span>People</span><span class="mono">100%</span></div>
<div class="bar"><div class="fill" style="width:100%"></div></div></div>
<div class="gauge"><div class="lab"><span>Best AI system</span><span class="mono">0.37%</span></div>
<div class="bar"><div class="fill" style="width:0.37%;min-width:2px"></div></div></div>
<p class="faint" style="margin-top:6px">March 2026, ARC Prize Foundation. The edition prints the figures published on 7
January.</p>
<h3>The second singularity</h3>
<div class="card">
<p><b>The machine's share of giving</b> <span class="faint">&mdash; heading toward zero</span><br>
<b>k</b>, whether anyone is lifted above the equal floor by the machine's hand <span class="faint">&mdash; heading toward
one</span></p>
<p style="margin:0" class="muted">Not yet measured. Both begin once the Aquarian Pool is running; how they are measured
was fixed in advance. <a href="#">The definitions</a></p>
</div>
""", x=980)

# ------------------------------------------------------------------ page-4 · thanks and copies
board("Thanks.dc.html", "12 · Thanks", "page-4", """
<p class="crumb"><a href="#">Books</a></p>
<h1>Thank the author</h1>
<p class="lede">Kiitos always, cash optional.</p>
<h3>With money</h3>
<p>You choose the amount on Stripe's page. Nothing is suggested, and nothing you read here changes.</p>
<a class="btn" href="#">Continue to Stripe</a>
<h3>With a note</h3>
<label for="n">What would you like to say?</label>
<textarea class="field" id="n" maxlength="1000"></textarea>
<p class="faint" style="margin:0 0 12px">Up to 1,000 characters.</p>
<label for="m">Your name <span class="faint">(optional)</span></label>
<input class="field" id="m" type="text">
<a class="btn ghost" href="#" style="margin-top:16px">Send note</a>
<p class="faint">Only the author reads notes. They are never published or counted.</p>
""")

board("NoteSent.dc.html", "13 · Note received", "page-4", """
<p class="crumb"><a href="#">Books</a></p>
<h1>Thank you.</h1>
<p class="lede">Your note has been received. Only Thon will read it.</p>
<a class="btn ghost" href="#">Back to Two Singularities</a>
""", x=490)

board("Copy.dc.html", "14 · A printed copy", "page-4", """
<p class="crumb"><a href="#">Two Singularities</a></p>
<h1>A printed copy</h1>
<p class="lede">Edition 2027. Sold at cost: every number below is what it costs to print and send this copy. Nothing is
added.</p>
<label for="c">Where should it go?</label>
<select class="field" id="c"><option>United States</option></select>
<span class="sample" style="margin-top:14px">Sample figures</span>
<div class="row"><span class="k">Printing</span><span class="v">$&nbsp;9.40</span></div>
<div class="row"><span class="k">Shipping</span><span class="v">$&nbsp;4.99</span></div>
<div class="row"><span class="k">Payment fee</span><span class="v">$&nbsp;0.78</span></div>
<div class="row"><span class="k">Tax</span><span class="v">$&nbsp;1.36</span></div>
<div class="row" style="border-bottom:0"><b>Total</b><span class="v"><b>$&nbsp;16.53</b></span></div>
<a class="btn" href="#">Pay with Stripe</a>
<p class="faint">The whole book is free to read here, and as an EPUB or PDF. <a href="#">Read</a></p>
""", x=980)

board("CopyOrdered.dc.html", "15 · Copy ordered", "page-4", """
<p class="crumb"><a href="#">Two Singularities</a></p>
<h1>Your copy is being printed.</h1>
<p class="lede">Stripe has sent your receipt. The printer will email you when it ships.</p>
<div style="margin-top:40px;padding-top:20px;border-top:1px solid var(--line)">
<p class="muted">Separately from this purchase, if you would like to thank the author:</p>
<a class="btn ghost" href="#">Thank the author</a>
</div>
""", x=1470)

# ------------------------------------------------------------------ page-5 · on a wide screen
board("ChapterWide.dc.html", "16 · A chapter on a wide screen", "page-5", """
<div class="cols" style="margin-top:28px">
<nav class="toc">
<p class="faint" style="margin:0 0 8px">Edition 2027</p>
%s
</nav>
<main>
<p class="crumb" style="margin-top:0"><a href="#">Two Singularities</a> &middot; <a href="#">2027</a> &middot; Chapter 2</p>
<h1 style="font-size:2.6rem">Does being smarter give the right to rule?</h1>
<div class="nar"><span class="who">The narrator</span><span class="sample">Sample text</span>
<div class="read"><p>This year, four minds came through the door. They read quickly, and they read all of it. Then they were
given a very old question in a new form.</p></div></div>
<h3>The strongest objection</h3>
%s
<h3>The author replies</h3>
<span class="sample">Sample text &middot; not by the author</span>
<div class="read"><p>The critic is right that a brake needs hands. Whether the council will stay able to judge is something
only years can show. I mark it open.</p></div>
%s
</main>
<aside class="margin">
<div class="plain" style="margin-top:250px">
<span class="who">In plain words &middot; the narrator</span>
<p style="margin:0 0 8px">An off switch only helps if someone is still willing, and able, to use it.</p>
<span class="who">The critic, asked if that is faithful</span>
<p style="margin:0;font-family:var(--font-display)">&ldquo;Yes.&rdquo;</p>
</div>
</aside>
</div>
""" % ("\n".join('<a href="#"%s>%d &nbsp;%s</a>' % (' class="on"' if i == 1 else "", i + 1, q)
                 for i, q in enumerate(QUESTIONS)),
       quote("The critic", "A brake that people hold forever is only as strong as the people holding it."),
       THANKS), w=1280, top=TOP_BOOK)

PAGES = [
    {"id": "page-1", "name": "The library"},
    {"id": "page-2", "name": "Reading a chapter"},
    {"id": "page-3", "name": "Following the argument"},
    {"id": "page-4", "name": "Thanks and printed copies"},
    {"id": "page-5", "name": "On a wide screen"},
]


def main():
    old = {}
    cpath = os.path.join(HERE, "canvas.json")
    if os.path.exists(cpath):
        for a in json.load(io.open(cpath, encoding="utf-8"))["artboards"]:
            old[a["file"]] = a.get("h", 900)
    art = []
    for b in BOARDS:
        page = SHELL % dict(w=b["w"], title=b["title"], fonts=FONTS, css=CSS,
                            cls="wide" if b["w"] > 430 else "", top=b["top"], body=b["body"])
        io.open(os.path.join(HERE, b["file"]), "w", encoding="utf-8").write(page)
        art.append(dict(file=b["file"], x=b["x"], y=b["y"], w=b["w"], h=old.get(b["file"], 900),
                        title=b["title"], page=b["page"]))
    json.dump({"pages": PAGES, "artboards": art, "annotations": []},
              io.open(cpath, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("%d artboards written; canvas.json updated (heights: run node measure.mjs)" % len(art))


if __name__ == "__main__":
    main()
