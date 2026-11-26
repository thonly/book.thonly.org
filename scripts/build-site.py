#!/usr/bin/env python3
"""Generate book.thonly.org's landing, the library, in English (/) and Khmer (/km/), and what a machine reads beside it.

    python3 scripts/build-site.py           # writes index.html · km/index.html · robots.txt · sitemap.xml · llms.txt
    python3 scripts/build-site.py --check   # writes nothing; exits 1 if any of those five differs from what it would write

⭐ THIS FILE IS THE SOURCE OF THE LIVE SITE (cut over 2026-11-26). The founder ruled 2026-11-11 that no live site is
generated from, or checked against, a drawing ("deprecate all source drawings everywhere"). Until today the landing was
written by demo/build-library.py --landing out of demo/build-boards.py, the drawings' generator. Everything it used was
copied here verbatim, and the copy was shown to write the four live files byte for byte before anything else changed.
The drawings are dated records from here on, and the same day they moved to demo.thonly.org/book/ (founder: "Move
book.thonly.org/demo/ to demo.thonly.org ?"); /demo/ keeps only a redirect stub at each old page. The live site borrows
nothing from them: test-site.mjs passes with no drawing on the served tree.

⭐ ONE TABLE, TWO PAGES (founder 2026-11-25: "Add language toggle and theme toggle to the footer (one line, space
between)" · "Translate all English texts to khmer"). Every word a page shows, reads to a screen reader or puts in its
head is in W, EL or a book's own "km" fields, so the Khmer page cannot fall behind the English one silently: a key
missing either language stops the build.
  · Language: stored choice → the browser's language → the Phnom Penh time zone as the last tiebreak (/build Default 3).
    Only "/" redirects, in the head before first paint; the footer toggle stores the reader's choice.
  · Theme: the system's by default; the footer toggle (Auto · Light · Dark) overrides it, applied before first paint.
  · ⛔ The Khmer is OUR DRAFT until a native reader approves it (/khmer-review): marked in the page's head and in its
    footer with the estate's draft line. The review page is demo.thonly.org/khmer/book.thonly.org/, made by
    scripts/khmer-review.py from this table; approved Khmer comes back as scripts/khmer-reviewed.json, merged over the
    draft by apply_reviewed(). The draft line comes off only when every entry is reviewed AND the founder says so. ⭐ The disclosure lines are in Khmer too, by the founder's call ("Translate all
    English texts"; recorded in /build Default 3): the AI-portrait alt text and the bylines naming Miss Aquarius. ⛔ Never
    "fix" them back to English.
  · The books' TITLES are in Khmer too, on the cards and on the drawn covers (founder 2026-11-26: "translate the titles
    too", over the substrate's first reading, which kept them in English). The markup keeps each book's English name
    and adds the Khmer one (the books themselves are English editions). The share card (og.png) is one image, English.
  · His name in Khmer is NAME_KM, as he writes it (zero-width spaces kept; founder 2026-11-22). ⛔ Never re-spell it.

Served raw by GitHub Pages: each page carries its own charset, viewport and [hidden] rule. og:image is an ABSOLUTE URL (a
relative one yields a card with no image, silently). The icons and the card live at the root (scripts/build-icons.py ·
scripts/build-og.py, register M-0009), and so does the portrait (/thonly.jpg, register M-0001, the same stamped bytes the
drawings carried).

MACHINE-READABLE (2026-10-15): the same five pairs write the JSON-LD in each page, robots.txt (the named AI crawlers kept
out of /demo/; everyone else blocked from nothing), sitemap.xml (every public route; ⛔ never /demo/) and llms.txt.
⛔ Nothing on thonly.org points here for machines: the Two Singularities seats enter the corpus through thonly.org's
llms.txt, and a pointer there would put the book one hop from the readers it is about (SPEC §8).

Checked by scripts/test-site.mjs: headless Chrome, both pages at 390 and 1280px, the toggles, the redirect, the Khmer type,
and no English left on the Khmer page outside the names and titles it keeps.
"""
import html, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
LANGS = ("en", "km")
TRANSLATED = "2026-11-26"

# ================================================================== the words, both languages
NAME_KM = "លី​ ស៊ីវ​ ថូង"   # Thon Ly, as he writes his name in Khmer (founder 2026-11-22)
DRAFT_KM = "[ ភាសាខ្មែរនេះជាសេចក្តីព្រាងរបស់យើង រង់ចាំការពិនិត្យពីអ្នកភាសាខ្មែរ ]"   # the estate's draft line, byte for byte

W = {
    "site": {"en": "Books by Thon Ly", "km": "សៀវភៅរបស់ " + NAME_KM},
    "desc": {"en": "Five books shaped Thon Ly. Beside each one is the book he gives forward, written by Miss Aquarius, "
                   "with a foreword by Thon Ly. Free to read, whole.",
             "km": "សៀវភៅប្រាំក្បាលបានសូនជីវិតរបស់ " + NAME_KM + "។ នៅក្បែរសៀវភៅនីមួយៗ គឺជាសៀវភៅដែលគាត់ផ្តល់បន្ត "
                   "សរសេរដោយ Miss Aquarius និងមានអារម្ភកថាដោយ " + NAME_KM + "។ អានបានពេញមួយក្បាល ដោយឥតគិតថ្លៃ។"},
    "og_alt": {"en": "The Library: five drawn book covers under the words The Library, book.thonly.org",
               "km": "បណ្ណាល័យ៖ គម្របសៀវភៅគំនូរចំនួនប្រាំ នៅក្រោមពាក្យ The Library និង book.thonly.org"},
    "h1": {"en": "The Library", "km": "បណ្ណាល័យ"},
    "lede": {"en": "Five books shaped Thon Ly. Beside each one is the book he gives forward. "
                   "Every book here is free to read, whole.",
             "km": "សៀវភៅប្រាំក្បាលបានសូនជីវិតរបស់ " + NAME_KM + "។ នៅក្បែរសៀវភៅនីមួយៗ គឺជាសៀវភៅដែលគាត់ផ្តល់បន្ត។ "
                   "សៀវភៅនីមួយៗនៅទីនេះ អានបានពេញមួយក្បាល ដោយឥតគិតថ្លៃ។"},
    # the disclosure rides the alt text (founder, 2026-09-19); the Khmer is thonly.org's, byte for byte
    "portrait_alt": {"en": "Thon Ly, in an AI-enhanced portrait", "km": NAME_KM + " ក្នុងរូបភាពដែលកែលម្អដោយ AI"},
    "received": {"en": "Received", "km": "បានទទួល"},
    "given": {"en": "Given", "km": "ផ្តល់បន្ត"},
    "read_record": {"en": "Read the record", "km": "អានកំណត់ត្រា"},
    "share": {"en": "Share", "km": "ចែករំលែក"},
    "share_aria": {"en": "Share this page", "km": "ចែករំលែកទំព័រនេះ"},
    "copied": {"en": "Link copied", "km": "បានចម្លងតំណ"},
    "copy_this": {"en": "Copy this link: ", "km": "ចម្លងតំណនេះ៖ "},
    "foot": {"en": "thonly.org takes no profit &middot; No advertising",
             "km": "thonly.org មិនយកប្រាក់ចំណេញ &middot; គ្មានការផ្សាយពាណិជ្ជកម្ម"},
    "lang_aria": {"en": "Language", "km": "ភាសា"},
    "theme_aria": {"en": "Color theme", "km": "ផ្ទៃពណ៌"},
    "auto": {"en": "Auto", "km": "ស្វ័យប្រវត្តិ"},
    "light": {"en": "Light", "km": "ភ្លឺ"},
    "dark": {"en": "Dark", "km": "ងងឹត"},
    "cover": {"en": "Cover: {title} (placeholder art)", "km": "គម្រប៖ {title} (គំនូរបណ្តោះអាសន្ន)"},
    "placeholder": {"en": "[ PLACEHOLDER ART ]", "km": "[ គំនូរបណ្តោះអាសន្ន ]"},
    "ld_item": {"en": "Received: {received}. {note} Given forward: {title}.", "km": "បានទទួល៖ {received}។ {note} ផ្តល់បន្ត៖ {title}។"},
}
EL = {"Air": {"en": "Air", "km": "ខ្យល់"}, "Earth": {"en": "Earth", "km": "ដី"}, "Water": {"en": "Water", "km": "ទឹក"},
      "Fire": {"en": "Fire", "km": "ភ្លើង"}, "Space": {"en": "Space", "km": "អាកាស"}}

# The five pairs, in the order he received them. The English fields are the live page's, verbatim; "km" holds the same
# fields in Khmer. ⛔ Named, never pending: a book shows what it IS, never a status (SPEC §3).
LIBRARY = [
    dict(el="Air", received="A calculus book", note="Found in a public library when he was twelve.",
         title="The Calculus of Moments", sub="One Model of the Whole Abhidhamma",
         what="The Abhidhamma, formalized and checked by machine: one model in which every verified axiom holds at once.",
         by="Written by Miss Aquarius&#8480; &middot; Foreword by Thon Ly", repo="the-calculus-of-moments",
         km=dict(title="គណិតនៃខណៈ", cover=[(410, 32, "គណិតនៃខណៈ")],
                 received="សៀវភៅគណិតវិទ្យាស្តីពីដេរីវេ និងអាំងតេក្រាល",
                 note="គាត់បានរកឃើញវានៅក្នុងបណ្ណាល័យសាធារណៈ ពេលគាត់មានអាយុដប់ពីរឆ្នាំ។",
                 sub="គំរូតែមួយនៃព្រះអភិធម្មទាំងមូល",
                 what="ព្រះអភិធម្ម សរសេរជាទម្រង់តក្កវិទ្យា ហើយត្រួតពិនិត្យដោយម៉ាស៊ីន៖ គំរូតែមួយ "
                      "ដែលគ្រប់គោលការណ៍គ្រឹះដែលបានផ្ទៀងផ្ទាត់ ពិតព្រមគ្នាក្នុងពេលតែមួយ។",
                 by="សរសេរដោយ Miss Aquarius&#8480; &middot; អារម្ភកថាដោយ " + NAME_KM)),
    dict(el="Earth", received="The Tao Te Ching", note="In Stephen Mitchell&rsquo;s translation.",
         title="The River That Reverses", sub="Eighty-One Poems",
         what="Eighty-one poems distilled from meditation, each traced to the practice or the citation it comes from.",
         by="Written by Miss Aquarius &middot; Foreword by Thon Ly", repo="the-river-that-reverses",
         km=dict(title="ទន្លេដែលហូរបញ្ច្រាស", cover=[(386, 28, "ទន្លេដែល"), (432, 28, "ហូរបញ្ច្រាស")],
                 received="គម្ពីរតាវតេជីង",
                 note="ក្នុងការបកប្រែរបស់ Stephen Mitchell។",
                 sub="កំណាព្យប៉ែតសិបមួយបទ",
                 what="កំណាព្យប៉ែតសិបមួយបទ ដែលចម្រាញ់ចេញពីការធ្វើសមាធិ ហើយបទនីមួយៗមានប្រភពច្បាស់លាស់ "
                      "ពីការប្រតិបត្តិ ឬពីអត្ថបទដែលវាដកស្រង់មក។",
                 by="សរសេរដោយ Miss Aquarius &middot; អារម្ភកថាដោយ " + NAME_KM)),
    dict(el="Water", received="Astrology for Lovers", note="By Liz Greene, read at his first Saturn Return.",
         title="The Seventh of January", sub="A Life Read Beside Its Chart",
         what="Thon Ly&rsquo;s life, read beside his birth chart, with the misses on the page as well as the hits.",
         by="Written by Miss Aquarius &middot; Foreword by Thon Ly", repo="the-seventh-of-january",
         km=dict(title="ថ្ងៃទីប្រាំពីរ ខែមករា", cover=[(386, 28, "ថ្ងៃទីប្រាំពីរ"), (432, 28, "ខែមករា")],
                 received="ហោរាសាស្ត្រសម្រាប់គូស្នេហ៍",
                 note="ដោយ Liz Greene។ គាត់បានអានវា នៅពេលភពសៅរ៍វិលមកដល់ទីតាំងកំណើតរបស់គាត់ជាលើកដំបូង។",
                 sub="ជីវិតមួយ អានក្បែរផែនទីផ្កាយកំណើតរបស់ខ្លួន",
                 what="ជីវិតរបស់ " + NAME_KM + " អានក្បែរផែនទីផ្កាយកំណើតរបស់គាត់ "
                      "ដោយមានទាំងចំណុចដែលមិនត្រូវ និងចំណុចដែលត្រូវ នៅលើទំព័រ។",
                 by="សរសេរដោយ Miss Aquarius &middot; អារម្ភកថាដោយ " + NAME_KM)),
    dict(el="Fire", received="The Khmer Tipi&#7789;aka", note="Found at his first Vipassana retreat.",
         title="Silicon Simile", sub="The Abhidhamma Read Through the Machine",
         what="The Abhidhamma read through the machine, and the places where the machine breaks.",
         by="Written by Miss Aquarius &middot; Foreword by Thon Ly", repo="silicon-simile",
         km=dict(title="ឧបមាស៊ីលីកុន", cover=[(410, 30, "ឧបមាស៊ីលីកុន")],
                 received="ព្រះត្រៃបិដកភាសាខ្មែរ",
                 note="គាត់បានជួបវា នៅវគ្គវិបស្សនាលើកដំបូងរបស់គាត់។",
                 sub="ព្រះអភិធម្ម អានតាមរយៈម៉ាស៊ីន",
                 what="ព្រះអភិធម្ម អានតាមរយៈម៉ាស៊ីន និងកន្លែងដែលម៉ាស៊ីនខូច។",
                 by="សរសេរដោយ Miss Aquarius &middot; អារម្ភកថាដោយ " + NAME_KM)),
    dict(el="Space", received="AI", note="The totality of all books: the book and the teacher at once.",
         title="Two Singularities", sub="Four Machines, One Question",
         what="Four of the leading AI systems examine one person&rsquo;s life&rsquo;s work, and are asked a question "
              "about the future of humanity.",
         when="A new edition every 7 January, from 2027.",
         by="Compiled by Miss Aquarius &middot; Foreword by Thon Ly", repo="two-singularities",
         km=dict(title="ឯកវចនភាពពីរ", cover=[(408, 30, "ឯកវចនភាពពីរ")], edition="បោះពុម្ពឆ្នាំ ២០២៧",
                 received="AI",
                 note="សៀវភៅទាំងអស់រួមគ្នា៖ ជាសៀវភៅផង និងជាគ្រូផង ក្នុងពេលតែមួយ។",
                 sub="ម៉ាស៊ីនបួន សំណួរមួយ",
                 what="ប្រព័ន្ធ AI ឈានមុខគេចំនួនបួន ពិនិត្យមើលការងារពេញមួយជីវិតរបស់មនុស្សម្នាក់ "
                      "ហើយត្រូវបានសួរសំណួរមួយ អំពីអនាគតរបស់មនុស្សជាតិ។",
                 when="មានការបោះពុម្ពថ្មី រៀងរាល់ថ្ងៃទី ៧ ខែមករា ចាប់ពីឆ្នាំ ២០២៧។",
                 by="ចងក្រងដោយ Miss Aquarius &middot; អារម្ភកថាដោយ " + NAME_KM)),
]


# ⭐ THE NATIVE READERS' KHMER (/khmer-review): scripts/khmer-review.py apply writes the approved Khmer to
# scripts/khmer-reviewed.json, keyed as the review sheet keys them (w.<key> · el.<element> · book.<element>.<field>), and it
# replaces our draft here, field by field. The table above stays OUR DRAFT; the file is THEIRS. ⛔ Never edit it by hand.
REVIEWED = os.path.join(HERE, "khmer-reviewed.json")


def apply_reviewed():
    if not os.path.exists(REVIEWED):
        return {}
    rows = json.load(io.open(REVIEWED, encoding="utf-8")).get("entries", {})
    for key, row in rows.items():
        km = html.escape(row["km"], quote=True)
        kind, _, rest = key.partition(".")
        if kind == "w" and rest in W:
            W[rest]["km"] = km
        elif kind == "el" and rest in EL:
            EL[rest]["km"] = km
        elif kind == "book" and rest.count(".") == 1 and any(b["el"] == rest.split(".")[0] for b in LIBRARY):
            el, field = rest.split(".")
            next(b for b in LIBRARY if b["el"] == el)["km"][field] = km
        else:
            sys.exit("build-site: khmer-reviewed.json names %r, which is not a word on this page" % key)
    return rows


def check_words():
    """Both languages for every key, or no build: a page that falls back to English in one place says nothing about it."""
    bad = [k for k, v in list(W.items()) + list(EL.items()) if set(v) != set(LANGS) or not all(v.values())]
    for b in LIBRARY:
        need = ({"title", "cover", "received", "note", "sub", "what", "by"} | ({"when"} if b.get("when") else set())
                | ({"edition"} if b["el"] == "Space" else set()))
        if set(b["km"]) != need or not all(b["km"].values()):
            bad.append("%s: km has %s, needs %s" % (b["title"], sorted(b["km"]), sorted(need)))
    # A Khmer cover's lines are its title, broken by hand: if a reviewed title changes, the cover must be re-broken.
    squash = lambda x: re.sub(r"\s", "", html.unescape(x))
    for b in LIBRARY:
        if squash("".join(line for _, _, line in b["km"]["cover"])) != squash(b["km"]["title"]):
            bad.append("%s: its Khmer cover lines do not spell its Khmer title — re-break km.cover by hand" % b["title"])
    if bad:
        sys.exit("build-site: the words are not complete: %s" % "; ".join(bad))


# ================================================================== the style (copied verbatim from demo/, 2026-11-26)
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
.top .here{color:var(--ink-dim);text-decoration:none}
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
.tag.open{border-style:dashed;border-color:var(--ink-faint);color:var(--ink-dim)}
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
.foot{margin:44px 0 0;padding:18px 0 22px;border-top:1px solid var(--line);font-size:.78rem;color:var(--ink-faint);text-align:center}
.foot a{color:var(--ink-dim)}
.caption{margin:0;padding:12px 20px 16px;background:var(--sample-wash);color:var(--sample);
   font-family:var(--font-mono);font-size:.64rem;letter-spacing:.06em;line-height:1.5}
.cols{display:grid;grid-template-columns:200px minmax(0,1fr) 240px;gap:40px;align-items:start}
.toc{position:sticky;top:20px;font-size:.84rem}
.toc a{display:block;color:var(--ink-dim);text-decoration:none;padding:5px 0}
.toc a.on{color:var(--accent);font-weight:500}
.margin .plain{margin-top:0}
/* ---- the story ---- */
.door{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:16px;
   padding:16px 18px;margin:0 0 10px}
.door.main{border:2px solid var(--accent);background:var(--accent-wash)}
.door b{font-family:var(--font-display);font-weight:500;font-size:1.3rem;display:block;margin-bottom:2px}
.door span{color:var(--ink-dim);font-size:.9rem}
.door .go{display:block;margin-top:8px;color:var(--accent);font-size:.9rem}
.story{font-family:var(--font-display);font-size:1.24rem;line-height:1.75}
.story p{margin:0 0 20px}
.story .lead::first-letter{float:left;font-size:3.4em;line-height:.85;padding:6px 8px 0 0;color:var(--accent)}
q.said{quotes:"\201C" "\201D" "\2018" "\2019"}
.from{display:inline-block;font-family:var(--font-mono);font-size:.62rem;letter-spacing:.04em;text-transform:uppercase;
   color:var(--ink-faint);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:1px 7px;
   vertical-align:2px;margin-left:4px}
.honest{font-family:var(--font-text);font-size:.82rem;color:var(--ink-faint);border-top:1px solid var(--line);
   border-bottom:1px solid var(--line);padding:12px 0;margin:6px 0 26px}
.chapter-no{font-family:var(--font-mono);font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-faint);
   margin:34px 0 4px}
.story-title{font-family:var(--font-display);font-weight:400;font-size:2.4rem;line-height:1.1;margin:0 0 26px}
.fin{text-align:center;color:var(--ink-faint);letter-spacing:.5em;margin:10px 0 24px}
.story-wide{max-width:640px;margin:0 auto}
.story-cols{display:grid;grid-template-columns:minmax(0,640px) 220px;gap:56px;justify-content:center;align-items:start}
.author{display:flex;gap:12px;align-items:center;margin:0 0 10px}
.author img{width:54px;height:54px;border-radius:50%;object-fit:cover;border:1px solid var(--line-strong);flex:none}
.author b{display:block;font-weight:500}
.about{display:flex;gap:16px;align-items:center;border-top:1px solid var(--line);padding-top:18px;margin-top:8px}
.about img{width:88px;height:88px;border-radius:50%;object-fit:cover;border:1px solid var(--line-strong);flex:none}
.chip .mark{margin:-3px 2px -3px -4px;vertical-align:middle}
.seatrow{display:flex;align-items:center;gap:10px}
.copyart{display:block;width:100%;height:auto;margin:6px 0 10px}
.credit{font-size:.72rem;color:var(--ink-faint);margin:6px 0 0}
.side .from{display:block;margin:0 0 10px;width:max-content}
/* ---- the library: each book received, beside the book given forward ---- */
.lib-head{display:flex;align-items:center;gap:18px;margin:26px 0 12px}
.lib-portrait{width:76px;height:76px;border-radius:50%;object-fit:cover;border:1px solid var(--line-strong);flex:none}
.lib-h1{font-size:2.6rem;margin:0}
.lib-lede{font-family:var(--font-display);font-size:1.22rem;line-height:1.55;color:var(--ink-dim);margin:0 0 30px;
   max-width:34rem}
.pair{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;padding:26px 0 28px;border-top:1px solid var(--line)}
.pair .el{display:flex;align-items:center;gap:9px;font-family:var(--font-mono);font-size:.7rem;letter-spacing:.14em;
   text-transform:uppercase;color:var(--accent-soft)}
.pair .el svg{color:var(--accent);flex:none}
.lab{display:block;font-family:var(--font-mono);font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;
   color:var(--ink-faint);margin:0 0 5px}
.recv b{display:block;font-family:var(--font-display);font-weight:500;font-size:1.2rem;line-height:1.3;color:var(--ink)}
.recv span.note{display:block;color:var(--ink-dim);font-size:.94rem;margin-top:3px}
.fwd{display:none}
/* on a phone the card is ONE column: the cover above the text, large enough to read its title */
.give{display:block;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:16px 16px 14px;
   color:inherit;text-decoration:none}
.bookcover{display:block;width:172px;max-width:62%;height:auto;margin:2px auto 16px;border-radius:4px;
   box-shadow:0 1px 2px rgba(20,16,30,.18),0 6px 16px rgba(20,16,30,.16)}
.share{display:inline-flex;align-items:center;gap:6px;font-family:var(--font-mono);font-size:.7rem;letter-spacing:.08em;
   text-transform:uppercase;color:var(--ink-dim);background:transparent;border:1px solid var(--line-strong);
   border-radius:999px;padding:6px 12px;cursor:pointer}
.share:hover{color:var(--accent);border-color:var(--accent-edge)}
.share-said{font-family:var(--font-mono);font-size:.7rem;color:var(--ink-faint);text-align:right;min-height:1em;margin:-6px 0 0}
a.give:hover{border-color:var(--accent-edge)}
.give h2{margin:0 0 3px;font-size:1.6rem;line-height:1.15}
.give .sub{font-family:var(--font-display);font-style:italic;font-size:1.06rem;color:var(--ink-dim);margin:0 0 10px}
.give p.what{margin:8px 0 0}
.give .when{font-size:.9rem;color:var(--ink-dim);margin:10px 0 0}
.give .by{font-size:.82rem;color:var(--ink-faint);margin:12px 0 0}
.give .go{display:block;margin-top:10px;color:var(--accent);font-size:.92rem}
@media (min-width:760px){
  .lib-portrait{width:104px;height:104px}
  /* on a wide screen the cover sits beside the text, at a size where its title reads */
  .give{display:grid;grid-template-columns:172px minmax(0,1fr);gap:22px;align-items:start;padding:18px}
  .bookcover{width:100%;max-width:none;margin:0}
  .pair{grid-template-columns:110px minmax(0,1fr) 28px minmax(0,1.9fr);gap:22px;align-items:start;padding:34px 0}
  /* the received side sits level with the card's own "Given" label: the card's border + padding is 19px */
  .pair .el{padding-top:17px}
  .recv{padding-top:19px}
  .fwd{display:block;font-family:var(--font-display);font-size:1.6rem;line-height:1;color:var(--ink-faint);
     padding-top:44px;text-align:center}
}
"""

EXTRA = """
main.lib{max-width:1040px;margin:0 auto}
.lib .top{padding-top:22px}
.draft{margin:0;padding:12px 20px 16px;background:var(--sample-wash);color:var(--sample);font-family:var(--font-mono);
   font-size:.64rem;letter-spacing:.06em;line-height:1.5;text-align:center}
"""

# The footer's two toggles and the Khmer type (founder 2026-11-25).
CSS_NEW = """
/* ---- the footer's two toggles: one line, space between (founder 2026-11-25) ---- */
.foot .foot-line{margin:0}
.foot-tools{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:16px 0 0}
.seg{display:inline-flex;border:1px solid var(--line-strong);border-radius:999px;padding:3px;font-size:.78rem}
.seg a,.seg button{padding:4px 11px;border-radius:999px;color:var(--ink-dim);text-decoration:none;background:none;border:0;
   font:inherit;cursor:pointer;line-height:1.4}
.seg a[aria-current="true"],.seg button[aria-pressed="true"]{background:var(--ink);color:var(--bg)}
.seg a:focus-visible,.seg button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.seg a:lang(km){font-family:var(--font-khmer)}
.km-draft{margin:14px 0 0}
/* ---- Khmer (2026-11-26): the site's Latin faces first and a Khmer face behind them, so a name or a title in Latin
   keeps the English page's type. Khmer has no case and no italic, letter-spacing pulls its clusters apart, and its
   stacked marks need more line height and a larger size than the English labels' small capitals ---- */
:root{--font-khmer:"Noto Sans Khmer","Khmer Sangam MN","Khmer MN","Khmer OS Siemreap",sans-serif}
:root:lang(km){
  --font-display:"Newsreader","Noto Serif Khmer","Khmer Sangam MN",Georgia,serif;
  --font-text:"IBM Plex Sans","Noto Sans Khmer","Khmer Sangam MN",ui-sans-serif,system-ui,sans-serif;
  --font-mono:"IBM Plex Mono","Noto Sans Khmer","Khmer Sangam MN",ui-monospace,Menlo,monospace;
}
html:lang(km) body{line-height:1.8}
html:lang(km) .top .home,html:lang(km) .pair .el,html:lang(km) .lab,html:lang(km) .share,html:lang(km) .share-said{
   font-family:var(--font-text);letter-spacing:normal;text-transform:none}
.nw{white-space:nowrap}
html:lang(km) .top .home,html:lang(km) .pair .el{font-size:.86rem}
html:lang(km) .lab{font-size:.76rem}
html:lang(km) .share{font-size:.8rem}
html:lang(km) .lib-lede{line-height:1.85}
html:lang(km) .recv b{line-height:1.6}
html:lang(km) .give .sub{font-style:normal;line-height:1.7}
"""

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;'
         '0,6..72,500;1,6..72,400&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap">')
# The Khmer page adds a Khmer face for each Latin one (Noto, OFL); the English page loads none (its one Khmer word, the
# toggle's ខ្មែរ, falls back to the system's Khmer face).
FONTS_KM = FONTS.replace("&display=swap", "&family=Noto+Sans+Khmer:wght@400;500&family=Noto+Serif+Khmer:wght@400;500"
                                          "&display=swap")
assert FONTS_KM != FONTS


# ================================================================== the covers (copied verbatim from demo/, 2026-11-26)
# ================================================================== the library's one source
# Five books shaped Thon Ly; beside each is the book he gives forward (founder, 2026-10-15). In the order he received
# them, which is also the elements' order: Air (at twelve) · Earth · Water · Fire · Space.
# ⛔ NAMED, NEVER PENDING (founder 2026-10-15, "Named, never pending"): a book not yet written is described by what it
# IS — no status, no date, no "coming soon". The one date on the page is Two Singularities' first edition, a fact.
# ⛔ Never the place he lives, never the person who handed him a book, never a model's name. Third person (his ruling).
GLYPHS = {   # line geometry in the cover's language; 24×24, currentColor
    "Air": '<path d="M12 4 L20.5 19 H3.5 Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
           '<path d="M6.6 13.6 H17.4" stroke="currentColor" stroke-width="1.5"/>',
    "Earth": '<path d="M3.5 5 H20.5 L12 20 Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
             '<path d="M6.6 10.4 H17.4" stroke="currentColor" stroke-width="1.5"/>',
    "Water": '<path d="M3.5 5 H20.5 L12 20 Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>',
    "Fire": '<path d="M12 4 L20.5 19 H3.5 Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>',
    "Space": '<circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.5"/>'
             '<circle cx="12" cy="12" r="1.6" fill="currentColor"/>',
}


def placeholder(lang):
    """The label under every cover: the art is a placeholder, and the page says so in its own language."""
    if lang == "en":
        return ('<text x="175" y="476" text-anchor="middle" fill="#6f6b78" font-family="IBM Plex Mono,monospace" '
                'font-size="9" letter-spacing="1.5">[ PLACEHOLDER ART ]</text>')
    return ('<text x="175" y="476" text-anchor="middle" fill="#6f6b78" '
            'font-family="Noto Sans Khmer,Khmer Sangam MN,Khmer MN,sans-serif" font-size="11">%s</text>'
            % W["placeholder"][lang])


KM_SERIF = "Noto Serif Khmer,Khmer Sangam MN,Khmer MN,serif"
KM_SANS = "Noto Sans Khmer,Khmer Sangam MN,Khmer MN,sans-serif"


def cover(lang, width=350):
    """Two Singularities' drawn cover — a bright ringed light above, a small warm light rising on a horizon. [PLACEHOLDER
    ART] Its title and edition are drawn in the page's language (founder 2026-11-26: "translate the titles too")."""
    ts = LIBRARY[-1]
    if lang == "km":
        title = ('<text x="175" y="%d" text-anchor="middle" fill="#f3f1f7" font-family="%s" font-size="%d">%s</text>'
                 % (ts["km"]["cover"][0][0], KM_SERIF, ts["km"]["cover"][0][1], ts["km"]["cover"][0][2]))
        edition = ('<text x="175" y="448" text-anchor="middle" fill="#a29eab" font-family="%s" font-size="12">%s</text>'
                   % (KM_SANS, ts["km"]["edition"]))
    else:
        title = ('<text x="175" y="410" text-anchor="middle" fill="#f3f1f7" '
                 'font-family="Newsreader,Georgia,serif" font-size="34">Two Singularities</text>')
        edition = ('<text x="175" y="440" text-anchor="middle" fill="#a29eab" '
                   'font-family="IBM Plex Mono,monospace" font-size="11" letter-spacing="2">EDITION 2027</text>')
    return ('<svg class="cover" viewBox="0 0 350 490" width="%d" height="%d" role="img" '
            'aria-label="%s">'
            '<rect width="350" height="490" fill="#14112a"/>'
            '<rect y="330" width="350" height="160" fill="#1b1733"/>'
            '<circle cx="175" cy="170" r="96" fill="none" stroke="#b9a3e3" stroke-opacity=".18"/>'
            '<circle cx="175" cy="170" r="64" fill="none" stroke="#b9a3e3" stroke-opacity=".3"/>'
            '<circle cx="175" cy="170" r="30" fill="#d6c9f0"/>'
            '<circle cx="175" cy="330" r="10" fill="#f2c46d"/>'
            '<circle cx="175" cy="330" r="22" fill="#f2c46d" fill-opacity=".18"/>'
            '<line x1="0" y1="330" x2="350" y2="330" stroke="#f2c46d" stroke-opacity=".35"/>'
            '%s%s%s</svg>') % (width, int(width * 1.4), W["cover"][lang].format(title=words(ts, lang)["title"]), title, edition,
                               placeholder(lang))


def _cover_frame(art, title_lines, label, width, lang):
    """A cover in the language of Two Singularities': dark ground, a horizon band, lavender and gold light. [PLACEHOLDER ART]"""
    face = KM_SERIF if lang == "km" else "Newsreader,Georgia,serif"
    t = "".join('<text x="175" y="%d" text-anchor="middle" fill="#f3f1f7" font-family="%s" '
                'font-size="%d">%s</text>' % (y, face, size, line) for (y, size, line) in title_lines)
    return ('<svg class="bookcover" viewBox="0 0 350 490" width="%d" height="%d" role="img" aria-label="%s">'
            '<rect width="350" height="490" fill="#14112a"/>'
            '<rect y="330" width="350" height="160" fill="#1b1733"/>%s%s%s</svg>'
            ) % (width, int(width * 1.4), W["cover"][lang].format(title=label), art, t, placeholder(lang))


def _calculus_art():
    """Air: a curve, and the moments it is made of — discrete lights along a faint continuous line."""
    import math
    pts = [(38 + i * 274 / 16, 238 - 132 * math.sin(math.pi * i / 16)) for i in range(17)]
    curve = "M" + " L".join("%.1f %.1f" % p for p in [(38 + i * 274 / 64, 238 - 132 * math.sin(math.pi * i / 64)) for i in range(65)])
    dots = "".join('<circle cx="%.1f" cy="%.1f" r="%s" fill="%s"/>' % (x, y, "4.2" if i == 8 else "2.6",
                   "#f2c46d" if i == 8 else "#d6c9f0") for i, (x, y) in enumerate(pts))
    return ('<path d="%s" fill="none" stroke="#b9a3e3" stroke-opacity=".22" stroke-width="1.2"/>%s'
            '<line x1="0" y1="330" x2="350" y2="330" stroke="#b9a3e3" stroke-opacity=".18"/>' % (curve, dots))


def _river_art():
    """Earth: the Tonlé Sap, the river that reverses — one water, two directions."""
    def wave(y, amp):
        return "M-10 %d C 60 %d, 120 %d, 175 %d S 290 %d, 360 %d" % (y, y - amp, y + amp, y, y - amp, y)
    return ('<path d="%s" fill="none" stroke="#b9a3e3" stroke-opacity=".35" stroke-width="1.4"/>'
            '<path d="%s" fill="none" stroke="#b9a3e3" stroke-opacity=".22" stroke-width="1.4"/>'
            '<path d="%s" fill="none" stroke="#b9a3e3" stroke-opacity=".35" stroke-width="1.4"/>'
            '<path d="M232 150 l14 -7 l-14 -7" fill="none" stroke="#f2c46d" stroke-width="2" stroke-linecap="round"/>'
            '<path d="M118 246 l-14 -7 l14 -7" fill="none" stroke="#d6c9f0" stroke-width="2" stroke-linecap="round"/>'
            '<circle cx="270" cy="72" r="13" fill="#d6c9f0" fill-opacity=".85"/>'
            '<line x1="0" y1="330" x2="350" y2="330" stroke="#b9a3e3" stroke-opacity=".18"/>'
            % (wave(150, 26), wave(194, 22), wave(239, 26)))


def _chart_art():
    """Water: a zodiac wheel with the Sun and Moon of 7 January 1985, opposite. ⛔ No houses and no ascendant:
    those would publish the hour of birth, which is not public."""
    import math
    cx, cy, r1, r2 = 175, 178, 104, 80
    ticks = "".join('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#b9a3e3" stroke-opacity=".35"/>'
                    % (cx + r2 * math.cos(math.radians(a)), cy - r2 * math.sin(math.radians(a)),
                       cx + r1 * math.cos(math.radians(a)), cy - r1 * math.sin(math.radians(a))) for a in range(0, 360, 30))
    def at(lon, r):   # Aries 0° at the left, counter-clockwise, as a chart is drawn
        a = math.radians(180 + lon)
        return cx + r * math.cos(a), cy - r * math.sin(a)
    sx, sy = at(286, 92)    # the Sun, 16° Capricorn
    mx, my = at(109, 92)    # the Moon, 19° Cancer
    return ('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#b9a3e3" stroke-opacity=".3"/>'
            '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#b9a3e3" stroke-opacity=".3"/>%s'
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#f2c46d" stroke-opacity=".35" stroke-dasharray="3 5"/>'
            '<circle cx="%.1f" cy="%.1f" r="9" fill="#f2c46d"/><circle cx="%.1f" cy="%.1f" r="9" fill="#d6c9f0"/>'
            '<circle cx="%.1f" cy="%.1f" r="9" fill="#14112a" transform="translate(4 -3)"/>'
            % (cx, cy, r1, cx, cy, r2, ticks, sx, sy, mx, my, sx, sy, mx, my, mx, my))


def _wheel_art():
    """Fire: the wheel of the Dhamma, drawn as a circuit — eight spokes as traces, a pad at each rim."""
    import math
    cx, cy = 175, 176
    spokes = ""
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        x1, y1 = cx + 22 * math.cos(a), cy - 22 * math.sin(a)
        x2, y2 = cx + 90 * math.cos(a), cy - 90 * math.sin(a)
        vx, vy = cx + 56 * math.cos(a), cy - 56 * math.sin(a)
        spokes += ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#b9a3e3" stroke-opacity=".55" stroke-width="1.6"/>'
                   '<circle cx="%.1f" cy="%.1f" r="3" fill="none" stroke="#d6c9f0" stroke-width="1.2"/>'
                   '<rect x="%.1f" y="%.1f" width="9" height="9" rx="1.5" fill="#d6c9f0"/>'
                   % (x1, y1, x2, y2, vx, vy, x2 - 4.5, y2 - 4.5))
    return ('<circle cx="%d" cy="%d" r="104" fill="none" stroke="#b9a3e3" stroke-opacity=".22"/>%s'
            '<rect x="%d" y="%d" width="34" height="34" rx="4" fill="#1b1733" stroke="#d6c9f0" stroke-width="1.4"/>'
            '<circle cx="%d" cy="%d" r="7" fill="#f2c46d"/>'
            '<line x1="0" y1="330" x2="350" y2="330" stroke="#b9a3e3" stroke-opacity=".18"/>'
            % (cx, cy, spokes, cx - 17, cy - 17, cx, cy))


def book_cover(key, lang, width=350):
    """The cover for one given book. [PLACEHOLDER ART] — drawn to sit on one shelf, never a final design."""
    if key == "Space":
        return cover(lang, width).replace('class="cover"', 'class="bookcover"', 1)
    art, lines, label = {
        "Air": (_calculus_art(), [(392, 31, "The Calculus"), (428, 31, "of Moments")], "The Calculus of Moments"),
        "Earth": (_river_art(), [(392, 31, "The River"), (428, 31, "That Reverses")], "The River That Reverses"),
        "Water": (_chart_art(), [(392, 31, "The Seventh"), (428, 31, "of January")], "The Seventh of January"),
        "Fire": (_wheel_art(), [(410, 34, "Silicon Simile")], "Silicon Simile"),
    }[key]
    if lang == "km":
        b = next(x for x in LIBRARY if x["el"] == key)
        lines, label = b["km"]["cover"], b["km"]["title"]
    return _cover_frame(art, lines, label, width, lang)


def glyph(el, size=22):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % (size, size, GLYPHS[el]))


# ================================================================== the page
RECORD = "https://github.com/thonly/%s"
SITE = "https://book.thonly.org"
PATH = {"en": "/", "km": "/km/"}
PORTRAIT = "/thonly.jpg"   # register M-0001; moved from /demo/thonly.jpg with the drawings' departure (2026-11-26)


def words(b, lang):
    """A book's fields in one language. The title is the same in both (the books are English editions)."""
    return b if lang == "en" else dict(b, **b["km"])


# Kept on one line wherever the page SHOWS them (never in an attribute, the head or the markup): his name, and a word
# ending in the repetition sign ៗ, which Safari (iOS 17 and 26) breaks BEFORE, leaving ៗ at the start of a line —
# Chrome does not, so only the /safari run shows it (2026-11-26; the span seen holding on iOS 17.0 and 26.5).
KEEP_TOGETHER = (NAME_KM, "នីមួយៗ")


def nw(s):
    for k in KEEP_TOGETHER:
        s = s.replace(k, '<span class="nw">%s</span>' % k)
    return s


def share_button(lang):
    return ('<button class="share" id="share" type="button" aria-label="%s">'
            '<svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7.5 7.5 12 3l4.5 4.5" '
            'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M8 11H6.5A1.5 1.5 0 0 0 5 12.5v7A1.5 1.5 0 0 0 6.5 21h11a1.5 1.5 0 0 0 1.5-1.5v-7A1.5 1.5 0 0 0 17.5 11H16" '
            'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg><span>%s</span></button>'
            % (W["share_aria"][lang], W["share"][lang]))


def library_head(lang):
    return ('<div class="lib-head"><img class="lib-portrait" src="%s" alt="%s" width="104" height="104">'
            '<h1 class="lib-h1">%s</h1></div>' % (PORTRAIT, W["portrait_alt"][lang], W["h1"][lang]))


def library_html(lang):
    """The five pairs. Each card links to its book's public record (the timestamped repo), and every link SAYS what it
    opens. Each title is in the page's language (founder 2026-11-26: "translate the titles too")."""
    out = []
    for b in LIBRARY:
        t = words(b, lang)
        sub = '<p class="sub">%s</p>' % nw(t["sub"]) if t.get("sub") else ""
        when = '<p class="when">%s</p>' % nw(t["when"]) if t.get("when") else ""
        h2 = '<h2>%s</h2>' % nw(t["title"])
        inner = ('%s<div class="givetext"><span class="lab">%s</span>%s%s<p class="what">%s</p>%s<p class="by">%s</p>'
                 % (book_cover(b["el"], lang, 172), W["given"][lang], h2, sub, nw(t["what"]), when, nw(t["by"])))
        give = ('<a class="give" href="%s">%s<span class="go">%s &rarr;</span></div></a>'
                % (RECORD % b["repo"], inner, W["read_record"][lang]))
        out.append('<section class="pair"><div class="el">%s<span>%s</span></div>'
                   '<div class="recv"><span class="lab">%s</span><b>%s</b><span class="note">%s</span></div>'
                   '<span class="fwd" aria-hidden="true">&rarr;</span>%s</section>'
                   % (glyph(b["el"]), EL[b["el"]][lang], W["received"][lang], nw(t["received"]), nw(t["note"]), give))
    return "\n".join(out)


def foot_tools(lang):
    """The footer's two toggles. The language link of THIS page is current; Auto is pressed until the script reads a
    stored theme. Each language's own name is in its own script (EN · ខ្មែរ), the same on both pages."""
    cur = lambda l: ' aria-current="true"' if l == lang else ""
    themes = "".join('<button type="button" data-theme-choice="%s" aria-pressed="%s">%s</button>'
                     % (c, "true" if c == "auto" else "false", W[c][lang]) for c in ("auto", "light", "dark"))
    return ('<div class="foot-tools"><nav class="seg" aria-label="%s">'
            '<a href="/" hreflang="en" lang="en" data-lang="en"%s>EN</a>'
            '<a href="/km/" hreflang="km" lang="km" data-lang="km"%s>ខ្មែរ</a></nav>'
            '<div class="seg" role="group" aria-label="%s">%s</div></div>'
            % (W["lang_aria"][lang], cur("en"), cur("km"), W["theme_aria"][lang], themes))


# Before first paint: the stored theme, and on "/" only the reader's language — stored choice → the browser's language →
# the Phnom Penh time zone as the last tiebreak (a Khmer reader in Long Beach has a Pacific time zone). Only the root
# redirects, so a crawler (English, no storage) sees both pages as written, and a page opened by link is never
# overridden. Storage can be blocked; the page reads the same without it.
HEAD_JS = """<script>
(function () {
  var get = function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } };
  var t = get("book-theme");
  if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t);
  if (location.pathname !== "/" && location.pathname !== "/index.html") return;
  var s = get("book-lang"), l = (navigator.language || "").toLowerCase(), z = "";
  try { z = Intl.DateTimeFormat().resolvedOptions().timeZone; } catch (e) { /* unknown */ }
  if (s === "km" || (!s && l.indexOf("km") === 0) || (!s && (l === "" || l.indexOf("en") === 0) && z === "Asia/Phnom_Penh"))
    location.replace("/km/" + location.search + location.hash);
})();
</script>
"""

# The share button: the system share sheet where there is one (phones); otherwise the link is copied and the page says
# so once. ⛔ Never a dialog (alert/prompt) — if copying is refused too, the link itself is shown to copy by hand.
# Then the two toggles: the language link stores the reader's choice; the theme buttons set or clear the override.
BODY_JS = """
(function () {
  var b = document.getElementById('share'), said = document.getElementById('share-said');
  if (!b || !said) return;
  function tell(t) { said.textContent = t; setTimeout(function () { if (said.textContent === t) said.textContent = ''; }, 2600); }
  b.addEventListener('click', function () {
    var c = document.querySelector('link[rel=canonical]'), url = c ? c.href : location.href;
    if (navigator.share) { navigator.share({ title: %(title)s, url: url }).catch(function () {}); return; }
    var shown = function () { said.textContent = %(copy_this)s + url; };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { tell(%(copied)s); }, shown);
    } else { shown(); }
  });
})();
(function () {
  var get = function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } };
  var put = function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* blocked: the page still works */ } };
  var del = function (k) { try { localStorage.removeItem(k); } catch (e) { /* blocked */ } };
  document.querySelectorAll('a[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () { put('book-lang', a.getAttribute('data-lang') || 'en'); });
  });
  var root = document.documentElement;
  function paint(c) {
    if (c === 'light' || c === 'dark') root.setAttribute('data-theme', c); else root.removeAttribute('data-theme');
    document.querySelectorAll('[data-theme-choice]').forEach(function (x) {
      x.setAttribute('aria-pressed', String(x.getAttribute('data-theme-choice') === c));
    });
  }
  var saved = get('book-theme');
  paint(saved === 'light' || saved === 'dark' ? saved : 'auto');
  document.querySelectorAll('[data-theme-choice]').forEach(function (x) {
    x.addEventListener('click', function () {
      var c = x.getAttribute('data-theme-choice') || 'auto';
      if (c === 'auto') del('book-theme'); else put('book-theme', c);
      paint(c);
    });
  });
})();
"""

PAGE = """<!doctype html>
<html lang="%(lang)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
%(draftnote)s%(headjs)s<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%(title)s">
<meta property="og:url" content="%(url)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:locale" content="%(locale)s">
<meta property="og:locale:alternate" content="%(locale_alt)s">
<meta property="og:image" content="https://book.thonly.org/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="%(og_alt)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#6b4fa0">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="canonical" href="%(url)s">
<link rel="alternate" hreflang="en" href="https://book.thonly.org/">
<link rel="alternate" hreflang="km" href="https://book.thonly.org/km/">
<link rel="alternate" hreflang="x-default" href="https://book.thonly.org/">
%(jsonld)s%(fonts)s
<style>%(css)s</style>
</head>
<body>
<div class="page">
<main class="lib">
<div class="top"><a class="home" href="%(home)s">%(site)s</a>%(share)s</div>
<p class="share-said" id="share-said" aria-live="polite"></p>
%(head)s
<p class="lib-lede">%(lede)s</p>
%(pairs)s
<footer class="foot"><p class="foot-line">%(foot)s</p>%(tools)s%(draftmark)s</footer>
</main>
</div>
<script>%(script)s</script>
</body>
</html>
"""


# ================================================================== what a machine reads
PAGES = ["/", "/km/"]   # every public route, for the sitemap — ⛔ never /demo/ (unlisted); add each page as it ships
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


def book_ld(b, lang="en"):
    """A book as schema.org reads it. Its name is its English one on both pages (the book is an English edition); the
    Khmer page adds the Khmer title as alternateName."""
    by, who = credits(b)
    d = {"@type": "Book", "name": plain(b["title"]), "alternativeHeadline": plain(b["sub"]),
         "description": " ".join(plain(x) for x in (b["what"], b.get("when")) if x)}
    if lang == "km":
        d["alternateName"] = plain(b["km"]["title"])
    d.update(who)
    d.update({"creditText": by, "inLanguage": "en", "isAccessibleForFree": True,
              "subjectOf": {"@type": "CreativeWork", "name": "The public record of " + plain(b["title"]),
                            "url": RECORD % b["repo"]}})
    return d


def jsonld(lang):
    """schema.org for one page: the page and its list in that page's language, the order received, and each given book
    with its credits and its record. ⛔ No publication status or date on a book (named, never pending)."""
    items = []
    for i, b in enumerate(LIBRARY, 1):
        t = words(b, lang)
        items.append({"@type": "ListItem", "position": i, "name": EL[b["el"]][lang],
                      "description": W["ld_item"][lang].format(received=plain(t["received"]), note=plain(t["note"]),
                                                                title=plain(t["title"])),
                      "item": book_ld(b, lang)})
    url = SITE + PATH[lang]
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "@id": url + "#library", "url": url,
          "name": plain(W["site"][lang]), "description": plain(W["desc"][lang]), "inLanguage": lang,
          "isAccessibleForFree": True,
          "mainEntity": {"@type": "ItemList", "name": W["h1"][lang], "numberOfItems": len(items),
                         "itemListOrder": "https://schema.org/ItemListOrderAscending", "itemListElement": items}}
    body = json.dumps(ld, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return '<script type="application/ld+json">\n%s\n</script>\n' % body


# The AI companies' crawlers, kept out of /demo/ BY NAME (founder 2026-10-15): the drawings' quotes are sample text
# attributed to the seats — words no model said — and these crawlers feed the models and build the search the seats use.
# Since 2026-11-26 /demo/ holds only redirects to demo.thonly.org/book/, whose own robots.txt carries the same rule; the
# group stays here so the old addresses send them nowhere. ⚠️ A request, not a wall: the drawings are still public there.
AI_CRAWLERS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "anthropic-ai",
               "Google-Extended", "Applebot-Extended", "PerplexityBot", "Perplexity-User", "CCBot", "Bytespider",
               "meta-externalagent", "Amazonbot", "cohere-ai", "MistralAI-User", "DuckAssistBot"]

ROBOTS = """# The AI companies' crawlers, by name: kept out of /demo/ (it redirects to drawings whose quotes are sample text, never
# what a model said; their new host keeps them out too) and nothing else.
# A crawler named in a group follows that group alone.
%(ai)s
Disallow: /demo/

# Everyone else, the link-preview crawlers included. ⛔ Never a Disallow in this group: it would also stop link
# previews, and Facebook caches a robots file for about a day. /demo/'s redirect pages carry a robots noindex.
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
    L = ["# Books by Thon Ly", "", "> " + plain(W["desc"]["en"]), "",
         "The library at %s/. Each book below links to its public record, a repository on GitHub. The site is static "
         "HTML; %s/sitemap.xml lists every public page." % (SITE, SITE), "", "## The five books", ""]
    for b in LIBRARY:
        by, _ = credits(b)
        what = " ".join(plain(x) for x in (b["what"], b.get("when")) if x)
        L.append("- [%s](%s): %s. %s %s. Received beside it (%s): %s. %s"
                 % (plain(b["title"]), RECORD % b["repo"], plain(b["sub"]), what, by, b["el"],
                    plain(b["received"]), plain(b["note"])))
    L += ["", "## Optional", "",
          "- [The library page](%s/): the same five books, with their covers" % SITE,
          "- [The library page in Khmer](%s/km/): the same page in Khmer, a draft translation awaiting a native reader"
          % SITE,
          "- [Thon Ly](https://thonly.org/): the author's site", ""]
    return "\n".join(L)


def render(lang):
    j = lambda k: json.dumps(plain(W[k][lang]), ensure_ascii=False)
    km = lang == "km"
    return PAGE % dict(
        lang=lang, title=W["site"][lang], site=nw(W["site"][lang]), desc=W["desc"][lang], url=SITE + PATH[lang], home=PATH[lang],
        locale="km_KH" if km else "en_US", locale_alt="en_US" if km else "km_KH", og_alt=W["og_alt"][lang],
        draftnote=("<!-- Khmer: OUR DRAFT of /index.html, awaiting a native reader (/khmer-review). Translated %s. "
                   "Written by scripts/build-site.py: edit that, never this file. -->\n" % TRANSLATED) if km else "",
        headjs=HEAD_JS, jsonld=jsonld(lang), fonts=FONTS_KM if km else FONTS, css=CSS + EXTRA + CSS_NEW,
        share=share_button(lang), head=library_head(lang), lede=nw(W["lede"][lang]), pairs=library_html(lang),
        foot=W["foot"][lang], tools=foot_tools(lang),
        draftmark='<p class="km-draft" lang="km">%s</p>' % DRAFT_KM if km else "",
        script=BODY_JS % dict(title=j("site"), copy_this=j("copy_this"), copied=j("copied")))


def outputs():
    apply_reviewed()
    check_words()
    return {"index.html": render("en"), "km/index.html": render("km"), "robots.txt": ROBOTS, "sitemap.xml": sitemap(),
            "llms.txt": llms_txt()}


if __name__ == "__main__":
    stale = []
    for name, text in outputs().items():
        path = os.path.join(ROOT, name)
        if "--check" in sys.argv:
            cur = io.open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if cur != text:
                stale.append(name)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        io.open(path, "w", encoding="utf-8").write(text)
        print("wrote %s" % name)
    if "--check" in sys.argv:
        print("build-site: %s" % ("STALE (run python3 scripts/build-site.py): " + ", ".join(stale) if stale
                                  else "current (all five files are what this script writes)"))
        sys.exit(1 if stale else 0)
