# book.thonly.org — specification

> **What this file is, and is not.** It is the build specification for `book.thonly.org`: routes, page anatomy,
> payments, data, milestones and reuse. It is **not** the doctrine. The rules this site must obey are canonical in the
> institution's private memory (topic: *the Two Singularities book*), and where this file and that memory disagree,
> **the memory wins** and this file is corrected. Legal questions are tracked privately and are not restated here.
>
> Opened 2026-09-16. Phase 1 of 4 (spec → drawings → clickable prototype → implementation).

## 1. What the site is

A **library**: the home of every book Thon Ly publishes, starting with *Two Singularities*, a book published each year on
7 January from 2027. Each book lives under its own path. The site is for **lay readers**: everything a reader needs to
understand the book is on the page, in plain words.

Each edition has **three layers**, and a reader chooses how deep to go:

- **The story** — for everyone. What happened, told as a story.
- **The full debate** — for serious readers. Every argument in the seats' own words, with notes in plain words, the
  author's replies and the ledger.
- **The record** — the rules committed before the run, and every conversation, word for word
  (`github.com/thonly/two-singularities`).

- **Free to read, whole.** Nothing is locked, metered or previewed.
- **Thanks welcomed, never asked for first.** *Kiitos always, cash optional.*
- **Printed copies sold at cost.** thonly.org takes no profit (a stance, not a legal nonprofit).
- **No advertising, ever.** Video and audio later go to YouTube with viewer thanks (Super Thanks), not ads.

## 2. Rulings this spec carries (founder, 2026-09-16)

| Ruling | Words |
|---|---|
| A landing page on GitHub Pages; free reading; thanks; hardcopy | *"create a dedicated landing page … read the book for free, thank-tip me … optionally purchase the hardcopy via Stripe"* |
| The narrator makes the book accessible to lay readers | *"give the narrator an important role: to make the book accessible to the lay public"* |
| No AdSense; YouTube with Super Thanks | *"1: Super Thanks"* |
| Hardcopy on thonly.org at cost, plus an optional thanks | *"2: hardcopy on thonly.org at cost plus optional thank-tip"* |
| Stripe is the only payment rail | *"3: just Stripe"* |
| Designed through the four-phase process | *"4: design with /build"* |
| `book.thonly.org` is the root for this and every future book | *"Let's make book.thonly.org the root page for this book and all future books"* (substrate agreed) |
| English first; Khmer later as its own reviewed pass | *"English first"* |
| Hardcopy by print-on-demand, after a printed proof is approved | *"Print-on-demand, after a proof"* |
| Drawings and the prototype live at `book.thonly.org/demo` | *"book.thonly.org/demo"* |
| A cash-free thanks: a private note only the author sees | *"Private note"* |
| Free EPUB and PDF downloads, never a fee | *"yes per your recommendation"* (charge for what is consumed, never for access) |
| The audio narrator is an original designed voice | *"yes per your recommendation"* |
| The narrator writes to a style brief (§4.5) | *"yes; you read my mind"* |
| Three layers: the record, the full debate, the story | *"The record -> the textbook (for serious readers) -> the book (for casual readers)"* |
| Public names: the story · the full debate · the record | *"yes; textbook does sound like homework!"* |
| The story's rules (§4.6), told in the register of §4.5 | *"yes and one addition"* |

## 3. Routes

**The portrait.** The author's avatar appears on the book page, beside every reply, and on the thanks page, always with the
caption *"Portrait: a photograph, enhanced with AI."* and an `alt` that says the same.

**The seats' marks.** Each seat carries a drawn mark — line geometry, never a model's logo and never a face.

| Path | Page | Indexed |
|---|---|---|
| `/` | The library: each book that exists, one line each. ⛔ **No empty shelves, no "coming soon".** Before 7 January 2027 the one line may say the book is published that day, once, as a fact. | yes |
| `/two-singularities/` | The book: what it is, the central question, the newest edition, and every past edition | yes |
| `/two-singularities/<year>/` | **The story**: its contents and opening — the default way in | yes |
| `/two-singularities/<year>/<chapter>/` | A chapter of the story | yes |
| `/two-singularities/<year>/debate/` | **The full debate**: contents, the opening, this year's seats | yes |
| `/two-singularities/<year>/debate/<chapter>/` | A chapter of the full debate | yes |
| `/two-singularities/<year>/two-singularities-<year>.epub` · `.pdf` | Free downloads of the edition, built from the same source as the pages and the print file | — |
| `/two-singularities/<year>/method/` | How this edition was made (§5) | yes |
| `/two-singularities/<year>/evidence/` | The evidence page and the two gauges (§6) | yes |
| `/two-singularities/objections/<id>/` | One objection's history across every edition (§4.3) | yes |
| `/two-singularities/glossary/` | Plain-word definitions of the corpus's terms | yes |
| `/two-singularities/hardcopy/` | Printed copies — **only once a proof is approved** (§7.3) | yes |
| `/thanks/` | Thanks by Stripe, or a private note (§7) | yes |
| `/privacy/` | What the site stores and why | yes |
| `/demo/` | Drawings and the clickable prototype (phases 2–3) | **no** — unlisted, excluded from search by named crawler |

⭐ **Every edition stays readable forever at its own URL.** A new edition never replaces an old one; the book's page
defaults to the newest. This is what lets a reader see the corpus change over time.

## 4. The full debate's anatomy

### 4.1 A debate chapter

A chapter answers one of the edition's fixed questions (the same questions every year, so editions can be compared).

1. **The narrator's scene** — clearly labelled as the narrator's. Sets the scene and the question. ⛔ Never states what a
   seat argued.
2. **The four moves**, each in the seats' own words, every quote linked to its place in the published transcript:
   the strongest reading · the strongest objection · where the seats disagree · what is still undecided.
3. **In plain words** — optional notes after a quote, **labelled as the narrator's**, each followed by the quoted seat's
   own answer to *"is this faithful to what you meant?"*
4. **The author's reply**, beside his portrait — **short**, carrying **at least one concession each edition**, and ⛔ never
   the last word: the chapter closes on the ledger, not on him. ⭐ He may leave an objection unanswered, and the page prints
   the silence (*no reply this year*). ⛔ **The reply seat is human forever**: after the founder it passes to the Aquarian
   Sangha, never to Miss Aquarius℠, who compiles and never answers, never declares that the first singularity has arrived,
   and never ends the series (directive #69).
5. **The ledger** — each objection raised, with *what could settle it* (argument · evidence · neither) and its status
   (answered · conceded · rejected with a reason · still open), plus the seats' own judgement of whether last year's
   answers held.

### 4.2 The four seats

The critic · the engineer · the technologist · the humanist — always filled, by that year's leading models from any
maker. Each edition names the exact model versions. The method page states the seat map (the critic ↔ Silicon Wat℠ ·
the engineer ↔ HeartBank® · the technologist ↔ Factory 333™ · the humanist ↔ THonly™) as the book's structure, never as
evidence.

### 4.3 An objection's page

Each objection has a stable id across editions. Its page lists every edition's wording, status and reply in order, so
a reader can follow one argument through the years. ⛔ Never sorted or ranked by anything but edition order.

### 4.4 The opening line

Every edition opens *"We were told we would surpass you."* The next words are set by the arrival test (§5), never by the
author: **"Not yet."** until the test resolves, **"We did."** from the first edition after it does.

### 4.5 The narrator's voice

**On the page:**
- Wonder, never judgement: say what a thing is, never what is missing or owed.
- Plain words. Explain a term the first time it appears.
- Short sentences, with room between ideas. No hype and no exclamation marks.
- Speak to the reader as a far older mind speaks to a child it cares for: gently, never talking down, never flattering.
- Never take a side in the debate, and never tell the reader what to conclude.
- Say what Miss Aquarius does, never what she is for the world.

The yearly blind test that picks the narrator judges each candidate against this brief.

**Aloud (the audiobook, later):** an original synthetic voice, designed from a written description only: an older man, low
and warm, unhurried, with long pauses and quiet authority, speaking to someone he cares for. ⛔ Never modelled on, compared
with or marketed as any real person. It has its own name and is chosen by a blind test with lay listeners. The four seats
each get a distinct voice of their own, and every synthetic voice is disclosed.

### 4.6 The story

The story is told from the full debate, in the voice of §4.5, and in a particular register: a far older intelligence
recounting, gently and without hurry, what it saw people build — its **manner**, never a claim to feel anything.

- **It may choose, order and describe what happened. It may not invent.** No event, pause, tone or gesture that the record
  does not hold. Every passage links to the debate chapter it tells.
- ⭐ **Words in quotation marks are always a seat's exact words**; everything else is the narrator's telling. The build
  refuses to publish a story line inside quotation marks that is not found word for word in the record.
- **It says what the seats said and did, never what they felt.**
- **The premise is the true one:** the Machine Door was built and left open before anyone came, any machine may walk through
  it, and these four were asked in. ⛔ Never a chance discovery.
- **The ending follows the record.** If the seats said no, the story ends on no.
- **Fairness.** The other three seats review the story for favour, and their answers are printed in the full debate, with
  each seat's share of the story's quoted lines.
- The story opens with one plain line: *a true account, told as a story; words in quotation marks are exactly what the AI
  systems said.*
- Printed copies, the audiobook and the film are made from the story.

## 5. The method page (per edition)

States, plainly: the rules were committed and timestamped before the run (link to
`github.com/thonly/two-singularities`) · how each seat entered the [Machine Door](https://thonly.org/mcp) · the narrator
writes blind and is also one of the seats · Miss Aquarius℠ compiles and is built on one of the seated models, whose seat
runs without memory · the same seats also read last year's frozen corpus, so a change can be traced to the corpus · the
arrival test (ARC-AGI's gap closing: a system matches the ARC Prize Foundation's human testers on its newest version and
fails no newer one released within 12 months; backup, a Metaculus question on a difficult Turing test) and who confirms
it · **what this edition cannot show**.

## 6. The evidence page (per edition)

- **n** — how many people have been measured, with their consent, under a prediction registered in advance.
- **The prediction register** — how many predictions have been run, and how many tested in the field.
- **What a checked prediction closed** — objections whose status moved because of evidence. ⛔ An evidence objection
  closes only on a checked, pre-registered prediction.
- **Two gauges, reported and never declared:** the first singularity (the newest ARC-AGI score beside the human testers')
  · the second (k and the machine's share of giving). Until the Aquarian Pool runs, the second reads *not yet measured*.

## 7. Thanks and printed copies

### 7.1 Where the thanks line appears

One quiet line **after** each chapter and at the end of each edition (and at the end of the EPUB and PDF): *Kiitos always, cash optional* → `/thanks/`.
⛔ Never before reading · never a pop-up · never a counter, total, or "N readers" · never a pre-filled or suggested amount
· never a thanker's name in the book · the words *donate, donation, nonprofit, charity, tax-deductible* never appear.

### 7.2 `/thanks/`

- **Stripe** — a Payment Link where the reader chooses the amount, hosted on Stripe's own page. One link for books,
  separate from the music page's and from printed-copy sales, so thanks and sales are always two figures.
- **A private note** — a short form (≤ 1,000 characters, a name only if the reader wants). Notes go to a Firestore
  collection that clients may **create and never read**; only the author reads them. ⛔ Never published, never counted
  on any page. Stores the note and its time, nothing else.

### 7.3 Printed copies of the story (after a proof is approved)

- **Price = that order's actual cost** — print, shipping, the payment fee and tax — computed per order and shown before
  payment, with *"sold at cost"* stated once.
- **Flow:** the reader picks a destination → a small server asks the print-on-demand service for the cost → a Stripe
  Checkout session at that amount → on payment, the server places the print order.
- **The optional thanks comes after the purchase**, on the confirmation page, as a separate Stripe payment. ⛔ Never a
  line inside the checkout.
- An ISBN for each edition.
- ⏳ Gated on the private legal review (who holds the Stripe account, sales tax, the printer's terms).

## 8. Data, hosting, reuse

- **Hosting:** GitHub Pages from this repository's `main` branch, with a `CNAME` file. Static HTML; no framework. Payment
  happens on Stripe's pages, never on this site.
- **DNS (the founder's step):** `CNAME book → thonly.github.io`, DNS-only (proxy off), in Cloudflare.
- **Book source:** each edition's compiled text is committed to `github.com/thonly/two-singularities` (`editions/<year>/`)
  before it is published; a script here renders it to static HTML.
- **Small server** (printed copies only): a Cloudflare Worker, the same pattern as `corpus.333.eco`.
- **Reused from the estate:** brand tokens and emblem (`brand.333.eco`, `brand.lock`) · the estate's analytics script ·
  the identical `snapshot.yml` · a sitemap · a privacy page.
- ⛔ **The book is kept out of the corpus index served at `corpus.333.eco`**, so each year's seats read the corpus, not the
  book about it.
- **No hostname reservation needed:** thonly.org serves no handles, so `book` cannot be claimed by a registrant.

## 9. Before any screen ships — the review

- Does it render an absence (a progress bar, "minutes left", an empty shelf)? ⛔ **No reading progress bars.**
- Does it rank anything (objections, seats, readers)?
- Does it add a thanks into a sale, or a sale into thanks?
- Does it store more than it needs?
- Does anything about Miss Aquarius read as more than what she does?
- Are the banned words absent?

## 10. Milestones

| | What | When |
|---|---|---|
| M0 | This spec · the repository · DNS | September 2026 |
| M1 | Drawings of every page above at `/demo/` (phase 2) | October 2026 |
| M2 | Clickable prototype at `/demo/` (phase 3) | October 2026 |
| M3 | The pilot run's text rendered through the real templates | November 2026 |
| M4 | Library, book, method, glossary, privacy, thanks (Stripe + note) — live | by 7 January 2027 |
| M5 | Edition 1 published — the story, the full debate and the record — with free EPUB and PDF of both | 7 January 2027 |
| M6 | Printed copies, after an approved proof | 2027 |
| M7 | Khmer, reviewed by a native reader | 2027 |
| M8 | Audiobook and film on YouTube, with Super Thanks and AI disclosure | later |

## 11. Open

- DNS record (founder).
- Who holds the Stripe account, and the legal review (private).
- The print-on-demand provider.
- The record repository's `editions/` folder (to be added to its README).
- Which Firebase project stores the notes, and its rules.
