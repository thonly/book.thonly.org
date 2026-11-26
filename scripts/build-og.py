#!/usr/bin/env python3
"""Render the landing's link-preview card, og.png (1200x630), with headless Chrome, and stamp it (register M-0009).

    python3 scripts/build-og.py

Moved here from demo/build-og.py on 2026-11-26, when the drawings left for demo.thonly.org/book/: the card is the live
site's, so it is drawn from the live site's own covers (scripts/build-site.py), never from a drawing. The card's markup
was checked string-identical to the one demo/build-og.py drew before the move; the PNG was not re-rendered by the move.

The card: the library, light like the page, the five drawn covers in a row. No person in it. Chrome needs the network
for the fonts; offline it renders the fallback stack and looks wrong without erroring — check the image before publishing.
⭐ THE GENERATOR STAMPS ITS OWN OUTPUT (/media): a card rebuilt without the stamp is an undeclared file the next commit
would (rightly) refuse. It is drawn from the site's own tokens by headless Chrome: no AI in the image itself.
"""
import importlib.util, io, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location("site", os.path.join(HERE, "build-site.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
STAMP = os.path.join(ROOT, "..", "..", "..", ".claude", "skills", "media", "scripts", "stamp.py")

LIBRARY_CARD = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  *{box-sizing:border-box;margin:0}
  html,body{width:1200px;height:630px;overflow:hidden}
  body{background:#fcfbfe;color:#16141c;font-family:"Newsreader",Georgia,serif;position:relative;-webkit-font-smoothing:antialiased}
  .t{position:absolute;left:92px;top:64px;width:1000px}
  h1{font-weight:500;font-size:84px;line-height:1;letter-spacing:-.02em;margin-bottom:16px}
  p{font-size:30px;line-height:1.35;color:#5b5766}
  .row{position:absolute;left:92px;top:268px;display:flex;gap:26px}
  .bookcover{display:block;width:180px;height:auto;border-radius:5px;box-shadow:0 2px 4px rgba(20,16,30,.18),0 12px 28px rgba(20,16,30,.18)}
  .foot{position:absolute;right:92px;top:84px;font-family:"IBM Plex Mono",monospace;font-size:20px;letter-spacing:.08em;
        text-transform:uppercase;color:#6b4fa0}
</style></head><body>
<div class="t"><h1>The Library</h1><p>Five books shaped Thon Ly. Beside each is the book he gives forward.</p></div>
<div class="foot">book.thonly.org</div>
<div class="row">%s</div>
</body></html>""" % "".join(S.book_cover(el, "en", 180) for el in ("Air", "Earth", "Water", "Fire", "Space"))


def main():
    if not os.path.exists(CHROME):
        sys.exit("Chrome not found at %s" % CHROME)
    out = os.path.join(ROOT, "og.png")
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "card.html")
        io.open(src, "w", encoding="utf-8").write(LIBRARY_CARD)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=1200,630", "--virtual-time-budget=4000", "--screenshot=" + out, "file://" + src],
                       check=True, capture_output=True)
    print("og.png %d bytes" % os.path.getsize(out))
    subprocess.run(["python3", STAMP, out, "--source", "drawn", "--rights", "cc0", "--register", "M-0009",
                    "--disclosure", "https://book.thonly.org/",
                    "--note", "the library's link-preview card, drawn from the site's own tokens and covers"],
                   check=True, capture_output=True)


if __name__ == "__main__":
    main()
