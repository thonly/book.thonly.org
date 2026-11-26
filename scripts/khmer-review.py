#!/usr/bin/env python3
"""This site's words for the native readers' Khmer review (/khmer-review), and the way their approved Khmer comes back.

    python3 scripts/khmer-review.py strings                    → staging/khmer-strings.json (staging/ is ignored; never served)
    python3 scripts/khmer-review.py apply <pulled.json> [--dry] → scripts/khmer-reviewed.json, then the build and its check
    python3 scripts/khmer-review.py capture                    → the review's pictures (this site served locally, in Khmer)

The review page is demo.thonly.org/khmer/book.thonly.org/ (/build Default 7: the root domain's own demo site), in the
father's group beside thonly.org (founder 2026-11-26: "do still open", after "Translate all English texts to khmer").

⭐ WHY NOT THE SKILL'S STATIC-SITE ENGINE (html-site.mjs). It reads the English and Khmer pages and writes approved Khmer back
INTO the Khmer page, and here that page is written by scripts/build-site.py: the next build would undo the review, and
--check would call the page stale. So the words come from the generator's own table, keyed as it keys them (w.<key> ·
el.<element> · book.<element>.<field>), and approved Khmer goes to scripts/khmer-reviewed.json, which build-site.py merges
over our draft. Its keys are stable across builds; a renamed key in the table orphans its reviews.
⚠️ A Khmer cover's lines (km.cover) are not entries: they are the reviewed title broken by hand, and the build stops when
they no longer spell it.
"""
import html, importlib.util, io, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MA = os.path.normpath(os.path.join(ROOT, "..", "..", ".."))
SKILL = os.path.join(MA, ".claude", "skills", "khmer-review")
OUT = os.path.join(ROOT, "staging", "khmer-strings.json")
SHOTS = os.path.join(ROOT, "..", "demo.thonly.org", "khmer", "book.thonly.org", "shots")

_spec = importlib.util.spec_from_file_location("site", os.path.join(HERE, "build-site.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
S.apply_reviewed()   # the sheet shows the site's CURRENT words: approved Khmer where there is some, our draft elsewhere
plain = lambda x: html.unescape(x)

# Where each word appears, in both languages (the page is public: a place, never a design note).
TOP = [("site", "the site's name, top left, and the tab's title", "ឈ្មោះគេហទំព័រ ខាងលើផ្នែកខាងឆ្វេង និងចំណងជើងផ្ទាំង"),
       ("share", "the button, top right", "ប៊ូតុង ខាងលើផ្នែកខាងស្តាំ"),
       ("h1", "the page's title, beside the portrait", "ចំណងជើងទំព័រ នៅក្បែររូបភាព"),
       ("lede", "the paragraph under the title", "កថាខណ្ឌនៅក្រោមចំណងជើង"),
       ("received", "the small label above each book received", "ស្លាកតូចនៅពីលើសៀវភៅដែលបានទទួលនីមួយៗ"),
       ("given", "the small label above each book given forward", "ស្លាកតូចនៅពីលើសៀវភៅដែលផ្តល់បន្តនីមួយៗ"),
       ("read_record", "the link at the bottom of each book's card", "តំណនៅខាងក្រោមកាតសៀវភៅនីមួយៗ"),
       ("placeholder", "the small line under each drawn cover", "បន្ទាត់តូចនៅក្រោមគម្របដែលគូរនីមួយៗ")]
FOOT = [("foot", "the footer's first line", "បន្ទាត់ទីមួយនៃបាតកថា"),
        ("auto", "the footer, the light and dark switch: follow this device", "បាតកថា កុងតាក់ភ្លឺ និងងងឹត៖ តាមឧបករណ៍នេះ"),
        ("light", "the footer, the light and dark switch", "បាតកថា កុងតាក់ភ្លឺ និងងងឹត"),
        ("dark", "the footer, the light and dark switch", "បាតកថា កុងតាក់ភ្លឺ និងងងឹត")]
UNSEEN = [("desc", "what search engines and link previews show under the page's name",
           "អ្វីដែលម៉ាស៊ីនស្វែងរក និងការមើលតំណជាមុន បង្ហាញនៅក្រោមឈ្មោះទំព័រ"),
          ("og_alt", "the link preview picture's description, read aloud (the picture shows English words)",
           "ការពិពណ៌នារូបភាពនៃការមើលតំណជាមុន ដែលអានឮៗ (រូបភាពនោះបង្ហាញពាក្យអង់គ្លេស)"),
          ("portrait_alt", "the portrait's description, read aloud: it says the portrait was enhanced with AI",
           "ការពិពណ៌នារូបភាព ដែលអានឮៗ៖ វាប្រាប់ថារូបភាពនេះត្រូវបានកែលម្អដោយ AI"),
          ("share_aria", "the share button, read aloud", "ប៊ូតុងចែករំលែក ដែលអានឮៗ"),
          ("copied", "shown after the share button copies the link", "បង្ហាញក្រោយពេលប៊ូតុងចែករំលែកចម្លងតំណ"),
          ("copy_this", "shown when the link cannot be copied, followed by the link", "បង្ហាញនៅពេលមិនអាចចម្លងតំណបាន ហើយតំណនោះនៅបន្ទាប់"),
          ("lang_aria", "the language switch in the footer, read aloud", "កុងតាក់ភាសានៅបាតកថា ដែលអានឮៗ"),
          ("theme_aria", "the light and dark switch in the footer, read aloud", "កុងតាក់ភ្លឺ និងងងឹតនៅបាតកថា ដែលអានឮៗ"),
          ("cover", "each drawn cover's description, read aloud; {title} is the book's title",
           "ការពិពណ៌នាគម្របដែលគូរនីមួយៗ ដែលអានឮៗ៖ {title} គឺជាចំណងជើងសៀវភៅ"),
          ("ld_item", "what a search engine reads for each pair; {received}, {note} and {title} are filled in",
           "អ្វីដែលម៉ាស៊ីនស្វែងរកអានសម្រាប់គូនីមួយៗ៖ {received} {note} និង {title} ត្រូវបានបំពេញ")]
FIELDS = [("received", "the book received", "សៀវភៅដែលបានទទួល"),
          ("note", "under the book received", "នៅក្រោមសៀវភៅដែលបានទទួល"),
          ("title", "the book given forward: its title, on the card and on the drawn cover",
           "សៀវភៅដែលផ្តល់បន្ត៖ ចំណងជើងរបស់វា នៅលើកាត និងនៅលើគម្របដែលគូរ"),
          ("sub", "under the title", "នៅក្រោមចំណងជើង"),
          ("what", "the card's paragraph", "កថាខណ្ឌនៃកាត"),
          ("when", "the card, under its paragraph", "កាត នៅក្រោមកថាខណ្ឌរបស់វា"),
          ("edition", "on the drawn cover, under the title", "នៅលើគម្របដែលគូរ នៅក្រោមចំណងជើង"),
          ("by", "the card's last line", "បន្ទាត់ចុងក្រោយនៃកាត")]
ORDINAL = ["first", "second", "third", "fourth", "fifth"]
ORDINAL_KM = ["ទីមួយ", "ទីពីរ", "ទីបី", "ទីបួន", "ទីប្រាំ"]
ENGLISH_EDITION = "EDITION 2027"   # the English cover's own words (build-site.py cover()), for the one cover entry


def entry(key, en, km, note, note_km):
    return {"key": key, "en": plain(en), "km": plain(km), "note": note, "note_km": note_km}


def sheet():
    groups = [{"name": "1 · The top of the page", "name_km": "១ · ផ្នែកខាងលើនៃទំព័រ",
               "entries": [entry("w." + k, S.W[k]["en"], S.W[k]["km"], n, nk) for k, n, nk in TOP]}]
    for i, b in enumerate(S.LIBRARY):
        es = [entry("el." + b["el"], S.EL[b["el"]]["en"], S.EL[b["el"]]["km"], "the pair's element, at its left",
                    "ធាតុនៃគូនេះ នៅខាងឆ្វេង")]
        for f, n, nk in FIELDS:
            if f in b["km"]:
                es.append(entry("book.%s.%s" % (b["el"], f), ENGLISH_EDITION if f == "edition" else b[f], b["km"][f], n, nk))
        groups.append({"name": "%d · The %s pair: %s" % (i + 2, ORDINAL[i], b["el"]),
                       "name_km": "%s · គូ%s៖ %s" % ("២៣៤៥៦"[i], ORDINAL_KM[i], plain(S.EL[b["el"]]["km"])), "entries": es})
    groups.append({"name": "7 · The footer", "name_km": "៧ · បាតកថា",
                   "entries": [entry("w." + k, S.W[k]["en"], S.W[k]["km"], n, nk) for k, n, nk in FOOT]})
    groups.append({"name": "8 · What a screen reader, a search engine or a link preview reads",
                   "name_km": "៨ · អ្វីដែលកម្មវិធីអានអេក្រង់ ម៉ាស៊ីនស្វែងរក ឬការមើលតំណជាមុនអាន",
                   "entries": [entry("w." + k, S.W[k]["en"], S.W[k]["km"], n, nk) for k, n, nk in UNSEEN]})
    keys = [e["key"] for g in groups for e in g["entries"]]
    assert len(keys) == len(set(keys)), "a key twice"
    # every word of the table is on the sheet, except his name (never re-spelled) and the estate's draft line
    table = {"w." + k for k in S.W} | {"el." + e for e in S.EL} | {"book.%s.%s" % (b["el"], f) for b in S.LIBRARY
                                                                     for f in b["km"] if f != "cover"}
    missing = table - set(keys)
    if missing:
        sys.exit("khmer-review: words in the table with no place on the sheet: %s" % ", ".join(sorted(missing)))
    sha = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    return {"version": 1, "surface": "book.thonly.org", "title": "book.thonly.org", "title_km": "book.thonly.org",
            "about": "The library of books by Thon Ly: five books he received, beside the five Miss Aquarius writes and he gives "
                     "forward. Our Khmer, drafted 2026-11-26.",
            "about_km": "បណ្ណាល័យសៀវភៅរបស់ " + S.NAME_KM + "៖ សៀវភៅប្រាំក្បាលដែលគាត់បានទទួល នៅក្បែរសៀវភៅប្រាំក្បាលដែល "
                        "Miss Aquarius សរសេរ ហើយគាត់ផ្តល់បន្ត។ ភាសាខ្មែររបស់យើង ព្រាងនៅថ្ងៃទី ២៦ ខែវិច្ឆិកា ឆ្នាំ ២០២៦។",
            "accent": "#6b4fa0", "made": time.strftime("%Y-%m-%d"), "commit": sha, "groups": groups}


def strings():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = sheet()
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print("wrote staging/khmer-strings.json · %d entries in %d groups"
          % (sum(len(g["entries"]) for g in data["groups"]), len(data["groups"])))


def apply(pulled_file, dry):
    """Approved Khmer (review.mjs pull --out) into scripts/khmer-reviewed.json; then the build. A word the sheet no longer
    has is named and left out; a cover whose title changed stops the build until km.cover is re-broken by hand."""
    pulled = json.load(io.open(pulled_file, encoding="utf-8"))
    known = {e["key"]: e for g in sheet()["groups"] for e in g["entries"]}
    who = {}
    for kind in ("approved", "corrected"):
        for r in pulled.get(kind, []) or []:
            if isinstance(r, dict) and r.get("key"):
                who[r["key"]] = {"from": r.get("by"), "at": r.get("at")}
    path = os.path.join(HERE, "khmer-reviewed.json")
    have = json.load(io.open(path, encoding="utf-8")) if os.path.exists(path) else {"version": 1, "entries": {}}
    changed, same, unknown = [], 0, []
    for key, km in (pulled.get("khmer") or {}).items():
        if key not in known:
            unknown.append(key)
            continue
        draft = known[key]["km"]
        if draft.endswith(" ") and not km.endswith(" "):
            km += " "   # the copy message runs into the link that follows it
        row = dict({"km": km}, **{k: v for k, v in who.get(key, {}).items() if v})
        if have["entries"].get(key, {}).get("km") == km:
            same += 1
            continue
        have["entries"][key] = row
        changed.append(key)
    print("%d changed · %d already so%s" % (len(changed), same, " · (dry run: nothing written)" if dry else ""))
    for k in changed:
        print("  %s: %s → %s" % (k, known[k]["km"], have["entries"][k]["km"]))
    if unknown:
        print("  ⚠️ not on this site's sheet any more: %s" % ", ".join(unknown))
    if dry or not changed:
        sys.exit(1 if unknown else 0)
    io.open(path, "w", encoding="utf-8").write(json.dumps(have, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    r = subprocess.run([sys.executable, os.path.join(HERE, "build-site.py")])
    if r.returncode:
        sys.exit("khmer-review: the build stopped (above); khmer-reviewed.json is written, fix what it names and build again")
    print("built. Next: node scripts/test-site.mjs, then /deploy")
    sys.exit(1 if unknown else 0)


def capture():
    strings()
    server = subprocess.Popen([sys.executable, "-m", "http.server", "4352", "--bind", "127.0.0.1"], cwd=ROOT,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    try:
        subprocess.run(["node", os.path.join(SKILL, "capture.mjs"), "--strings", OUT, "--states",
                        os.path.join(HERE, "khmer-states.json"), "--out", os.path.normpath(SHOTS)], check=True)
    finally:
        server.kill()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["strings"]:
        strings()
    elif a[:1] == ["apply"] and len(a) >= 2:
        apply(a[1], "--dry" in a)
    elif a[:1] == ["capture"]:
        capture()
    else:
        sys.exit(__doc__)
