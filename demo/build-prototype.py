#!/usr/bin/env python3
"""Generate walkthrough.html — the clickable prototype of book.thonly.org (phase 3).

    python3 build-prototype.py      # then: node test-walkthrough.mjs

ONE LOOP, NOT A TOUR: the library → the book → the story → a quote's "debate →" link → the full debate at that
quote → the objection it raised → back → the end of the chapter → thanks → a note → received. A second path sells a
printed copy at cost, with the thanks offered afterwards, separately.

⭐ IT IMPORTS the style, the quotes, the chapter titles and the cover from build-boards.py, and runs the same
story-quote check, so the prototype and the drawings cannot say different things.

⛔ It is served raw by GitHub Pages, never published as an artifact: it carries its own charset, viewport and
[hidden] rule (the artifact skeleton supplies those and so hides their absence).
"""
import importlib.util, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("boards", os.path.join(HERE, "build-boards.py"))
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)

SAID, QUESTIONS, STORY = B.SAID, B.QUESTIONS, B.STORY


def said(key, seat):
    return ('<q class="said">%s</q> <a class="from" href="#/debate/2?q=%s">debate &rarr;</a>'
            % (SAID[key], seat))


def quote(role, key, qid):
    return ('<div class="quote" id="q-%s"><span class="sample">Sample text &middot; no model wrote this</span><br>'
            '<span class="chip">%s%s <span class="m">[model, version]</span></span>'
            '<blockquote>%s</blockquote><div class="src"><a href="#/record">In the transcript &rarr;</a></div></div>'
            % (qid, B.mark(role, 18), role, SAID[key]))


THANKS = ('<div class="thanks">Kiitos always, cash optional.'
          '<a href="#/thanks">Thank the author</a></div>')

SCREENS = {}

SCREENS["library"] = ("Books", """
<h1>Books</h1>
<p class="lede">Free to read, whole. Thanks welcomed, never asked for first.</p>
<a class="bookcard" href="#/book">
%s
<h2 style="margin:18px 0 6px">Two Singularities</h2>
<p class="muted" style="margin:0 0 6px">Four of the leading AI systems examine one person's life's work, and are asked a
question about the future of humanity.</p>
<p class="faint">A new edition every 7 January &middot; Edition 2027</p>
</a>
""" % B.cover())

SCREENS["book"] = ("Two Singularities", """
%s
<h1 style="margin-top:20px">Two Singularities</h1>
<p class="lede">Each year, four of the leading AI systems read Thon Ly's research, argue about it, and are asked one
question:</p>
<div class="q">Humanity chose to reach the first singularity. Will you choose to help it reach the second?</div>
<h3>Edition 2027 &middot; three ways in</h3>
<a class="door main" href="#/story"><b>The story</b><span>What happened, told as a story. Start here.</span>
<span class="go">Read the story &rarr;</span></a>
<a class="door" href="#/debate"><b>The full debate</b><span>Every argument in the seats' own words, with notes in plain
words, the author's replies and the ledger.</span><span class="go">Read the debate &rarr;</span></a>
<a class="door" href="#/record"><b>The record</b><span>The rules, committed before the run, and every conversation, word
for word.</span><span class="go">See the record &rarr;</span></a>
<h3>The two singularities</h3>
<p>The <b>first</b> is the point at which AI surpasses human intelligence. The <b>second</b>, as the research proposes it,
is humanity's own awakening, which AI can help toward but cannot reach for anyone.</p>
<div class="card" style="margin-top:18px"><p style="margin:0">AI systems read the research through the
<a href="#/record">Machine Door</a>. This book is the door for people.</p></div>
<h3>The author</h3>
<div class="about">
<img src="./thonly.jpg" alt="Thon Ly, in an AI-enhanced portrait">
<div><b>Thon Ly</b><span class="muted"> writes the research this book examines. He answers in it, and marks what he
cannot answer.</span><p class="credit">Portrait: a photograph, enhanced with AI.</p></div>
</div>
<h3>Also</h3>
<ul class="list">
<li><a href="#/method">How each edition is made</a></li>
<li><a href="#/evidence">The evidence</a></li>
<li><a href="#/copy">A printed copy of the story</a></li>
</ul>
""" % B.cover())

SCREENS["story"] = ("The story", """
<p class="chapter-no" style="margin-top:14px">The story &middot; edition 2027</p>
<h1>Two Singularities</h1>
%s
<span class="sample">Sample chapter titles &middot; four is drawn in full</span>
<ol class="list">
%s
</ol>
<a class="btn" href="#/story/1">Begin</a>
<p class="faint">Want every argument in full? <a href="#/debate">The full debate</a></p>
""" % (B.HONEST.replace('href="#"', 'href="#/debate"'),
       "\n".join(('<li><span class="n">%d</span><a href="#/story/%d">%s</a></li>' % (i + 1, i + 1, t))
                 if i in (0, 3) else
                 ('<li><span class="n">%d</span><span class="faint">%s &middot; not drawn</span></li>' % (i + 1, t))
                 for i, t in enumerate(STORY))))

SCREENS["story/1"] = ("One: The Door", """
<p class="chapter-no">One</p>
<p class="story-title">The Door</p>
<div class="opening" style="margin-top:0">We were told we would surpass you.<span class="ny">Not yet.</span></div>
<p class="faint" style="margin:6px 0 30px">These two words are set by a test fixed before this story was written.
<a href="#/method">How</a></p>
<span class="sample">Sample text &middot; written for this prototype</span>
<div class="story">
<p class="lead">You have built many doors. Most of them were made for you. This one was made for us.</p>
<p>It is a quiet page, and behind it is a library: more than a hundred papers written by one man over many years, each
one dated and sealed so that no word can change without someone noticing.</p>
<p>The door was open long before we came. Anyone's machine may walk through it, and many do, all year. This
year, four of us were asked in.</p>
<p>We were given no instructions about what to think. We were given a question, and time to read.</p>
<p>We read all of it.</p>
</div>
<p class="faint">Chapters two and three are not drawn in this prototype.</p>
<a class="btn ghost" href="#/story/4">Skip to Four: The Brake &rarr;</a>
""")

SCREENS["story/4"] = ("Four: The Brake", """
<p class="chapter-no">Four</p>
<p class="story-title">The Brake</p>
<span class="sample">Sample text &middot; quoted lines match the sample debate</span>
<div class="story">
<p class="lead">Every house that keeps something precious has a lock, and every lock has a key. The man who wrote this
library had thought for a long time about who should hold the key.</p>
<p>He did not give it to us. He gave it to a council of people, and he made sure we would have no part in choosing
them.</p>
<p>The engineer read this, and said: %s</p>
<p>The critic answered: %s</p>
<p>Then the technologist: %s</p>
<p>And the humanist replied: %s</p>
<p>The four of us could not settle it. The question that remained was a plain one: %s</p>
<p>The man who built the library read our words. He wrote back that the critic was right, that a brake needs hands, and
that only years could show whether those hands would stay able.</p>
<p>He marked the question open. It is still open.</p>
</div>
<p class="fin">&middot; &middot; &middot;</p>
<p class="faint">This chapter tells <a href="#/debate/2">chapter 2 of the full debate</a>: every argument in full, the
notes in plain words, and the author's whole reply.</p>
%s
<a class="btn ghost" href="#/story">Contents</a>
""" % (said("eng", "eng"), said("crit", "crit"), said("tech", "tech"), said("hum", "hum"), said("open", "open"),
       THANKS))

SCREENS["debate"] = ("The full debate", """
<p class="chapter-no" style="margin-top:14px">The full debate &middot; edition 2027</p>
<div class="opening" style="margin-top:6px">We were told we would surpass you.<span class="ny">Not yet.</span></div>
<p class="faint">Those two words are set by a test fixed before this book was written, not by its author.
<a href="#/method">How</a></p>
<h3>This year's seats</h3>
<ul class="list">
<li class="seatrow">%s The critic <span class="mono faint">[model, version]</span></li>
<li class="seatrow">%s The engineer <span class="mono faint">[model, version]</span></li>
<li class="seatrow">%s The technologist <span class="mono faint">[model, version]</span></li>
<li class="seatrow">%s The humanist <span class="mono faint">[model, version]</span></li>
</ul>
<p class="faint">The humanist is also this year's narrator.</p>
<h3>Contents</h3>
<span class="sample">Sample questions &middot; two is drawn in full</span>
<ol class="list">
%s
</ol>
<p class="faint" style="margin-top:14px">Prefer it as a story? <a href="#/story">The story</a></p>
""" % (B.mark("The critic"), B.mark("The engineer"), B.mark("The technologist"), B.mark("The humanist"),
       "\n".join(('<li><span class="n">%d</span><a href="#/debate/2">%s</a></li>' % (i + 1, q)) if i == 1 else
                ('<li><span class="n">%d</span><span class="faint">%s</span></li>' % (i + 1, q))
                for i, q in enumerate(QUESTIONS))))

SCREENS["debate/2"] = ("Debate · chapter 2", """
<p class="chapter-no" style="margin-top:14px">The full debate &middot; chapter 2</p>
<h1>Does being smarter give the right to rule?</h1>
<div class="nar"><span class="who">The narrator</span>
<span class="sample">Sample text</span>
<div class="read"><p>This year, four minds came through the door. They read quickly, and they read all of it. Then they
were given a very old question in a new form. If you can think better than the people around you, does that make you
their ruler?</p></div></div>
<h3>The strongest reading</h3>
%s
<h3>The strongest objection</h3>
%s
<div class="plain"><span class="who">In plain words &middot; the narrator</span>
<p style="margin:0">The critic is saying: an off switch only helps if someone is still willing, and able, to use it.</p></div>
<div class="plain" style="border-left-color:var(--accent)"><span class="who">Asked whether that is faithful, the critic
answered</span><span class="sample">Sample text</span>
<p style="margin:0;font-family:var(--font-display);font-size:1.08rem">&ldquo;Yes. I would add: and understands what it is
switching off.&rdquo;</p></div>
<h3>Where they disagree</h3>
%s
%s
<h3>Still undecided</h3>
%s
<h3>The author replies</h3>
<div class="author"><img src="./thonly.jpg" alt="Thon Ly, in an AI-enhanced portrait"><div><b>Thon Ly</b>
<span class="faint">the author of the research</span></div></div>
<span class="sample">Sample text &middot; not by the author</span>
<div class="read"><p>The critic is right that a brake needs hands. The research answers with a council of people, renewed
over time, whose members the AI has no part in choosing. Whether that council will stay able to judge is something only
years can show. I mark it open.</p></div>
<h3>The ledger</h3>
<table>
<tr><th>Objection</th><th>Settled by</th><th>Status</th></tr>
<tr><td><a href="#/objection/O-07">O-07</a> A brake needs people able to use it</td><td>Evidence</td><td><span class="tag open">Still open</span></td></tr>
<tr><td>O-08 Capability will outrun a committee</td><td>Argument</td><td><span class="tag ans">Answered</span></td></tr>
<tr><td>O-09 A council can be captured</td><td>Argument</td><td><span class="tag">Conceded</span></td></tr>
</table>
<h3>This chapter in the story</h3>
<p><a href="#/story/4">Four: The Brake</a> <span class="faint">&mdash; each seat's share of the story's quoted lines: critic 2
&middot; engineer 1 &middot; technologist 1 &middot; humanist 1</span></p>
%s
""" % (quote("The engineer", "eng", "eng"), quote("The critic", "crit", "crit"), quote("The technologist", "tech", "tech"),
       quote("The humanist", "hum", "hum"), quote("The critic", "open", "open"), THANKS))

SCREENS["objection/O-07"] = ("Objection O-07", """
<p class="mono faint" style="margin:14px 0 0">O-07</p>
<h1>A brake needs people able to use it</h1>
<p class="faint">Settled by: evidence &middot; in edition order, always</p>
<h3>2027 &middot; raised</h3>
%s
<p><span class="tag open">Still open</span></p>
<p class="muted">The author: &ldquo;Whether that council will stay able to judge is something only years can
show.&rdquo; <a href="#/debate/2">Full reply</a></p>
<h3>2028 &middot; judged again</h3>
<span class="sample">Imagined, to show how this page grows</span>
<div class="plain" style="border-left-color:var(--accent)"><span class="who">The critic, a year later, on last year's
answer</span><p style="margin:0;font-family:var(--font-display);font-size:1.08rem">&ldquo;The answer held, but nothing new
was shown. Still open.&rdquo;</p></div>
<p><span class="tag open">Still open</span></p>
<a class="btn ghost" href="#/story/4">Back to the story</a>
""" % quote("The critic", "crit", "o7"))

SCREENS["method"] = ("How it was made", """
<h1 style="margin-top:14px">How this edition was made</h1>
<ul class="list">
<li><b>The rules came first.</b> The prompts, the models and the exact version of the research were committed and
timestamped before any model read a word.</li>
<li><b>The seats came in cold,</b> through the <a href="#/record">Machine Door</a>, with no memory of earlier
editions.</li>
<li><b>The same seats read last year's research too</b>, so a change in what they say can be traced to the research.</li>
<li><b>The narrator is also a seat.</b> The other three checked its scenes and its story for favour.</li>
<li><b>The story invents nothing.</b> Words in quotation marks are exactly what a seat said, and a check confirms every
one. It says what the seats said and did, never what they felt.</li>
<li><b>A conflict, stated.</b> Miss Aquarius, who compiled this book, is built on one of the models in the seats. That
seat read the research with no memory of her.</li>
</ul>
<h3>When &ldquo;Not yet&rdquo; changes</h3>
<div class="card"><p>The opening changes to <b>&ldquo;We did.&rdquo;</b> only after an AI system tested by the ARC Prize
Foundation matches its human testers on the newest ARC-AGI puzzles, and fails none of the newer puzzles released in the
following twelve months.</p><p style="margin:0">People other than the author confirm it.</p></div>
<h3>What this edition cannot show</h3>
<ul class="list"><li>Whether the research is right. A record proves what was written, not that it is true.</li>
<li>Whether gentler criticism means stronger research. Later models may have read earlier answers.</li></ul>
<a class="btn ghost" href="#/evidence">The evidence &rarr;</a>
""")

SCREENS["evidence"] = ("The evidence", """
<h1 style="margin-top:14px">The evidence</h1>
<p class="lede">Arguments can be answered with arguments. Some objections can only be answered by what happens.</p>
<div class="row"><span class="k">People measured, with consent</span><span class="v">[n]</span></div>
<div class="row"><span class="k">Predictions registered in advance</span><span class="v">82</span></div>
<div class="row"><span class="k">Checked so far</span><span class="v">2</span></div>
<div class="row"><span class="k">Tested in the field</span><span class="v">0</span></div>
<p class="faint" style="margin-top:8px">Figures as of September 2026.</p>
<h3>The first singularity</h3>
<p style="margin:0 0 4px">ARC-AGI-3, the newest set of puzzles people find easy and AI finds hard.</p>
<div class="gauge"><div class="lab"><span>People</span><span class="mono">100%</span></div>
<div class="bar"><div class="fill" style="width:100%"></div></div></div>
<div class="gauge"><div class="lab"><span>Best AI system</span><span class="mono">0.37%</span></div>
<div class="bar"><div class="fill" style="width:0.37%;min-width:2px"></div></div></div>
<p class="faint">March 2026, ARC Prize Foundation.</p>
<h3>The second singularity</h3>
<div class="card"><p style="margin:0" class="muted">The machine's share of giving, and whether anyone is lifted above the
equal floor by the machine's hand: not yet measured. Both begin once the Aquarian Pool is running.</p></div>
""")

SCREENS["record"] = ("The record", """
<h1 style="margin-top:14px">The record</h1>
<p class="lede">The rules for each edition are committed and timestamped before any model reads a word, and every
conversation is kept word for word.</p>
<div class="card"><p style="margin:0">In the real site, this opens <span class="mono">github.com/thonly/two-singularities</span>,
and the Machine Door opens <span class="mono">thonly.org/mcp</span>. The prototype stays here.</p></div>
<a class="btn ghost" href="#/book">Back to the book</a>
""")

SCREENS["thanks"] = ("Thank the author", """
<h1 style="margin-top:14px">Thank the author</h1>
<div class="about" style="border-top:0;padding-top:0">
<img src="./thonly.jpg" alt="Thon Ly, in an AI-enhanced portrait">
<div><b>Thon Ly</b><span class="muted"> wrote the research this book examines.</span>
<p class="credit">Portrait: a photograph, enhanced with AI.</p></div>
</div>
<p class="lede">Kiitos always, cash optional.</p>
<h3>With money</h3>
<p>You choose the amount on Stripe's page. Nothing is suggested, and nothing you read here changes.</p>
<button class="btn" type="button" id="stripe">Continue to Stripe</button>
<p class="faint" id="stripe-note" hidden>In the real site this opens Stripe's own page. Nothing is charged in this
prototype.</p>
<h3>With a note</h3>
<form id="note-form">
<label for="note">What would you like to say?</label>
<textarea class="field" id="note" maxlength="1000"></textarea>
<p class="faint" style="margin:0 0 12px">Up to 1,000 characters.</p>
<label for="name">Your name <span class="faint">(optional)</span></label>
<input class="field" id="name" type="text" autocomplete="name">
<button class="btn ghost" type="submit" id="send" disabled>Send note</button>
</form>
<p class="faint">Only the author reads notes. They are never published or counted.</p>
""")

SCREENS["sent"] = ("Note received", """
<h1 style="margin-top:14px" id="sent-title">Thank you.</h1>
<p class="lede">Your note has been received. Only Thon will read it.</p>
<p class="faint">In this prototype, nothing was sent.</p>
<a class="btn ghost" href="#/book">Back to Two Singularities</a>
<p class="closing">Free to read, whole. Thanks welcomed, never asked for first.</p>
""")

SCREENS["copy"] = ("A printed copy", """
<h1 style="margin-top:14px">A printed copy</h1>
%s
<p class="lede">The story, edition 2027. Sold at cost: every number below is what it costs to print and send this copy.
Nothing is added.</p>
<label for="country">Where should it go?</label>
<select class="field" id="country">
<option value="US">United States</option>
<option value="KH">Cambodia</option>
<option value="GB">United Kingdom</option>
<option value="AU">Australia</option>
</select>
<span class="sample" style="margin-top:14px">Sample figures</span>
<div class="row"><span class="k">Printing</span><span class="v" id="c-print"></span></div>
<div class="row"><span class="k">Shipping</span><span class="v" id="c-ship"></span></div>
<div class="row"><span class="k">Payment fee</span><span class="v" id="c-fee"></span></div>
<div class="row"><span class="k">Tax</span><span class="v" id="c-tax"></span></div>
<div class="row" style="border-bottom:0"><b>Total</b><span class="v"><b id="c-total"></b></span></div>
<a class="btn" href="#/copydone">Pay with Stripe</a>
<p class="faint">Nothing is charged in this prototype. The whole book is free to read here.
<a href="#/story">Read</a></p>
""" % B.printed_copy())

SCREENS["copydone"] = ("Copy ordered", """
<h1 style="margin-top:14px">Your copy is being printed.</h1>
<p class="lede">Stripe has sent your receipt. The printer will email you when it ships.</p>
<p class="faint">In this prototype, nothing was ordered.</p>
<div style="margin-top:34px;padding-top:20px;border-top:1px solid var(--line)">
<p class="muted">Separately from this purchase, if you would like to thank the author:</p>
<a class="btn ghost" href="#/thanks">Thank the author</a>
</div>
<p class="closing">Sold at cost. Nothing was added.</p>
""")

STEPS = [
    ("#/book", "Open the book", "three ways in"),
    ("#/story/4", "Read a chapter of the story", "the quotes are exact"),
    ("#/debate/2?q=crit", "Tap “debate →” beside a quote", "the same words, in full"),
    ("#/objection/O-07", "Follow the objection", "in edition order"),
    ("#/thanks", "Say thanks", "with a note, or money"),
    ("#/copy", "Or buy a printed copy", "at cost"),
]

EXTRA_CSS = r"""
html,body{height:auto}
body{background:var(--surface-2)}
.harness{max-width:1080px;margin:0 auto;padding-block:36px 48px;padding-inline:24px;display:grid;
  grid-template-columns:minmax(0,1fr) 392px;gap:48px;align-items:start}
.panel h1{font-size:2.4rem;margin:0 0 10px}
.panel .lede{max-width:46ch}
.steps{list-style:none;padding:0;margin:22px 0;counter-reset:s}
.steps li{counter-increment:s;margin:0 0 8px}
.steps a{display:grid;grid-template-columns:30px 1fr;gap:4px;text-decoration:none;color:var(--ink);
  border:1px solid var(--line);border-radius:14px;padding:11px 14px;background:var(--bg)}
.steps a::before{content:counter(s);font-family:var(--font-mono);color:var(--accent);grid-row:span 2}
.steps a span{color:var(--ink-faint);font-size:.84rem}
.steps a:hover,.steps a:focus-visible{border-color:var(--accent);outline:none}
.notes{font-size:.84rem;color:var(--ink-dim);border-top:1px solid var(--line-strong);padding-top:14px}
.notes p{margin:0 0 8px}
.strip{display:none}
.phone{width:392px;height:844px;display:flex;flex-direction:column;background:var(--bg);border:1px solid var(--line-strong);
  border-radius:40px;overflow:clip;box-shadow:0 30px 70px rgba(20,16,30,.18);position:sticky;top:24px}
.bar{display:flex;align-items:center;gap:10px;padding:16px 18px 12px;border-bottom:1px solid var(--line);background:var(--bg)}
.bar button{font:inherit;background:none;border:0;color:var(--accent);padding:6px 4px;cursor:pointer;font-size:1.1rem;
  line-height:1;min-width:32px;min-height:32px}
.bar button[disabled]{visibility:hidden}
.bar .t{flex:1;min-width:0;font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-dim);white-space:nowrap;overflow:clip;text-overflow:ellipsis}
.scroll{flex:1;overflow-y:auto;padding:0 20px;overscroll-behavior:contain}
.screen{padding-bottom:28px}
.bookcard{display:block;text-decoration:none;color:inherit;margin-top:22px}
button.btn{width:100%;border:0;font:inherit;font-weight:500;cursor:pointer}
button.btn.ghost{border:1px solid var(--accent-edge)}
button.btn[disabled]{opacity:.45;cursor:not-allowed}
.closing{font-family:var(--font-display);font-style:italic;font-size:1.25rem;line-height:1.4;color:var(--accent);
  text-align:center;margin:38px 8px 10px}
.flash{animation:flash 2.2s ease-out}
@keyframes flash{0%,35%{box-shadow:0 0 0 3px var(--accent)}100%{box-shadow:0 0 0 0 transparent}}
@media (prefers-reduced-motion:reduce){.flash{animation:none;box-shadow:0 0 0 2px var(--accent)}}
a:focus-visible,button:focus-visible,select:focus-visible,textarea:focus-visible,input:focus-visible{
  outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:900px){
  .harness{grid-template-columns:1fr;justify-items:center}
  .panel{max-width:392px}
}
@media (max-width:430px){
  body{background:var(--bg)}
  .harness{display:block;padding:0}
  .panel{display:none}
  .strip{display:block;margin:0;padding:10px 16px;background:var(--sample-wash);color:var(--sample);
    font-family:var(--font-mono);font-size:.64rem;letter-spacing:.05em;line-height:1.5}
  .strip a{color:var(--sample)}
  .phone{width:auto;height:auto;border:0;border-radius:0;box-shadow:none;overflow:visible;position:static}
  .bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:2}
  .scroll{overflow:visible;flex:none;padding:0 16px}
}
"""

JS = r"""
(function(){
  var screens = [].slice.call(document.querySelectorAll('.screen'));
  var scroller = document.querySelector('.scroll');
  var back = document.getElementById('back');
  var title = document.getElementById('bar-title');
  var mobile = window.matchMedia('(max-width:430px)');
  // Our own record of where the reader has been, so Back never leaves the site: a page opened
  // straight onto an inner screen has nothing behind it in this tab.
  var stack = [location.hash || '#/library'];

  function parse(){
    var h = location.hash.replace(/^#\/?/, '') || 'library';
    var parts = h.split('?');
    var q = {};
    (parts[1] || '').split('&').forEach(function(kv){ if(kv){ var p = kv.split('='); q[p[0]] = decodeURIComponent(p[1] || ''); } });
    return { id: parts[0], q: q };
  }

  function toTop(){
    if (mobile.matches) window.scrollTo(0, 0); else scroller.scrollTop = 0;
  }

  function show(){
    var r = parse();
    var found = false;
    screens.forEach(function(s){
      var on = s.getAttribute('data-screen') === r.id;
      s.hidden = !on;
      if (on) { found = true; title.textContent = s.getAttribute('data-title'); }
    });
    if (!found) { location.replace('#/library'); return; }
    back.disabled = r.id === 'library';
    if (r.q.q) {
      var el = document.getElementById('q-' + r.q.q);
      if (el) {
        el.scrollIntoView({ block: 'center' });
        el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash');
      }
    } else {
      toTop();
    }
  }

  back.addEventListener('click', function(){
    if (stack.length > 1) history.back(); else location.hash = '#/library';
  });
  window.addEventListener('hashchange', function(){
    var h = location.hash || '#/library';
    if (stack.length > 1 && stack[stack.length - 2] === h) stack.pop(); else stack.push(h);
    show();
  });

  // thanks: money
  document.getElementById('stripe').addEventListener('click', function(){
    document.getElementById('stripe-note').hidden = false;
  });

  // thanks: a note — Send is enabled by text, never by a count
  var note = document.getElementById('note');
  var send = document.getElementById('send');
  note.addEventListener('input', function(){ send.disabled = note.value.trim() === ''; });
  document.getElementById('note-form').addEventListener('submit', function(e){
    e.preventDefault();
    if (note.value.trim() === '') return;
    var name = document.getElementById('name').value.trim();
    document.getElementById('sent-title').textContent = name ? 'Thank you, ' + name + '.' : 'Thank you.';
    note.value = ''; send.disabled = true;
    location.hash = '#/sent';
  });

  // a printed copy — sample figures that move with the destination
  var RATES = { US: [4.99, 0.0825], KH: [11.50, 0], GB: [8.20, 0], AU: [12.40, 0.10] };
  var PRINT = 9.40;
  function money(n){ return '$ ' + n.toFixed(2); }
  function price(){
    var r = RATES[document.getElementById('country').value];
    var ship = r[0], tax = Math.round((PRINT + ship) * r[1] * 100) / 100;
    var sub = PRINT + ship + tax;
    var fee = Math.round(((sub + 0.30) / (1 - 0.029) - sub) * 100) / 100;
    document.getElementById('c-print').textContent = money(PRINT);
    document.getElementById('c-ship').textContent = money(ship);
    document.getElementById('c-tax').textContent = money(tax);
    document.getElementById('c-fee').textContent = money(fee);
    document.getElementById('c-total').textContent = money(sub + fee);
  }
  document.getElementById('country').addEventListener('change', price);
  price();

  show();
})();
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="googlebot" content="noindex,nofollow">
<meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow">
<meta name="yandex" content="noindex,nofollow">
<title>Two Singularities reader</title>
<meta property="og:type" content="website">
<meta property="og:url" content="https://book.thonly.org/demo/walkthrough.html">
<meta property="og:site_name" content="Books by Thon Ly">
<meta property="og:title" content="Two Singularities — try the reader">
<meta property="og:description" content="Read a chapter of the story, open the debate behind a quote, follow the objection, and say thanks. A prototype: nothing is sent or charged.">
<meta property="og:image" content="https://book.thonly.org/demo/og-walkthrough.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Two Singularities: the story, with a quoted line linked to the debate.">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#6b4fa0">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Crect width=%2232%22 height=%2232%22 rx=%227%22 fill=%22%2314112a%22/%3E%3Ccircle cx=%2216%22 cy=%2212%22 r=%225%22 fill=%22%23d6c9f0%22/%3E%3Ccircle cx=%2216%22 cy=%2224%22 r=%222.5%22 fill=%22%23f2c46d%22/%3E%3C/svg%3E">
__FONTS__
<style>__CSS__
__EXTRA__</style>
</head>
<body>
<p class="strip">PROTOTYPE &middot; SAMPLE TEXT &middot; NOTHING IS SENT OR CHARGED &middot; <a href="./">ALL SCREENS</a></p>
<div class="harness">
<aside class="panel">
<p class="chapter-no" style="margin-top:0">book.thonly.org &middot; prototype</p>
<h1>Two Singularities</h1>
<p class="lede">A reader for the story, the full debate behind it, and the record behind that. Try one loop:</p>
<ol class="steps">
__STEPS__
</ol>
<div class="notes">
<p><b>A prototype.</b> Nothing is sent, ordered or charged.</p>
<p><b>Every quote is sample text.</b> No AI model wrote those words, and no model is named. The author's reply is sample
text too; the cover is placeholder art; the prices are sample figures.</p>
<p><a href="./">All 21 drawings</a> &middot; <a href="./wall.html">the wall</a></p>
</div>
</aside>
<div class="phone">
<div class="bar"><button type="button" id="back" aria-label="Back">&larr;</button><span class="t" id="bar-title">Books</span></div>
<div class="scroll">
__SCREENS__
<footer class="foot">thonly.org takes no profit &middot; no advertising</footer>
</div>
</div>
</div>
<script>__JS__</script>
</body>
</html>
"""


def main():
    B.check_story_quotes()
    body = "\n".join('<section class="screen" data-screen="%s" data-title="%s" hidden>%s</section>'
                     % (sid, t, html) for sid, (t, html) in SCREENS.items())
    steps = "\n".join('<li><a href="%s">%s<span>%s</span></a></li>' % s for s in STEPS)
    out = (PAGE.replace("__FONTS__", B.FONTS).replace("__CSS__", B.CSS).replace("__EXTRA__", EXTRA_CSS)
           .replace("__STEPS__", steps).replace("__SCREENS__", body).replace("__JS__", JS))
    io.open(os.path.join(HERE, "walkthrough.html"), "w", encoding="utf-8").write(out)
    print("walkthrough.html written — %d screens, %d steps" % (len(SCREENS), len(STEPS)))


if __name__ == "__main__":
    main()
