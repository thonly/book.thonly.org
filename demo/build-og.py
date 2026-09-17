#!/usr/bin/env python3
"""Render the link-preview card for /demo/ to og.png (1200x630) with headless Chrome.

Adapted 2026-09-16 from demo.heartbank.ceo/build-og.py. The card is drawn from the same fonts and
colours as the pages, so it cannot drift from them. Chrome needs the network for the fonts; offline it
renders the fallback stack and looks wrong without erroring — check the image before publishing.

    python3 build-og.py
"""
import io, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CARD = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  *{box-sizing:border-box;margin:0}
  html,body{width:1200px;height:630px;overflow:hidden}
  body{background:#14112a;color:#f3f1f7;font-family:"Newsreader",Georgia,serif;position:relative;
       -webkit-font-smoothing:antialiased}
  svg{position:absolute;right:70px;top:0}
  .t{position:absolute;left:92px;top:150px;width:640px}
  h1{font-weight:500;font-size:92px;line-height:1.02;letter-spacing:-.02em;margin-bottom:26px}
  p{font-style:italic;font-size:32px;line-height:1.4;color:#d6c9f0}
  .foot{position:absolute;left:92px;bottom:56px;font-family:"IBM Plex Mono",monospace;font-size:22px;
        color:#b9a3e3;display:flex;gap:14px;align-items:center}
  .rule{width:52px;height:2px;background:#b9a3e3;opacity:.5}
</style></head><body>
<svg width="360" height="630" viewBox="0 0 360 630">
  <circle cx="180" cy="230" r="150" fill="none" stroke="#b9a3e3" stroke-opacity=".14"/>
  <circle cx="180" cy="230" r="100" fill="none" stroke="#b9a3e3" stroke-opacity=".26"/>
  <circle cx="180" cy="230" r="46" fill="#d6c9f0"/>
  <line x1="0" y1="470" x2="360" y2="470" stroke="#f2c46d" stroke-opacity=".35"/>
  <circle cx="180" cy="470" r="34" fill="#f2c46d" fill-opacity=".18"/>
  <circle cx="180" cy="470" r="15" fill="#f2c46d"/>
</svg>
<div class="t">
  <h1>Two Singularities</h1>
  <p>Humanity chose to reach the first singularity. Will you choose to help it reach the second?</p>
</div>
<div class="foot"><span class="rule"></span>book.thonly.org &middot; the design</div>
</body></html>"""


CARDS = {
    "og.png": CARD,
    "og-walkthrough.png": CARD.replace("<h1>Two Singularities</h1>", "<h1>Try the reader</h1>")
        .replace("<p>Humanity chose to reach the first singularity. Will you choose to help it reach the second?</p>",
                 "<p>A chapter of the story, the debate behind a quote, and thanks. Nothing is sent or charged.</p>")
        .replace("book.thonly.org &middot; the design", "book.thonly.org &middot; prototype"),
}


def main():
    if not os.path.exists(CHROME):
        sys.exit("Chrome not found at %s" % CHROME)
    for name, card in CARDS.items():
        assert card.count("<h1>") == 1
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "card.html")
            io.open(src, "w", encoding="utf-8").write(card)
            out = os.path.join(HERE, name)
            subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                            "--force-device-scale-factor=1", "--window-size=1200,630",
                            "--virtual-time-budget=4000", "--screenshot=" + out, "file://" + src],
                           check=True, capture_output=True)
            print("%s %d bytes" % (name, os.path.getsize(out)))


if __name__ == "__main__":
    main()
