#!/usr/bin/env python3
"""Draw the library's icons and write them to the site root (founder 2026-10-15: "promote with a real favicon").

    python3 build-icons.py      # writes ../icon.svg · ../apple-touch-icon.png · ../favicon.ico

The icon is drawn in the covers' language: a lavender ring and a gold light on the covers' dark ground — the light of
Two Singularities' cover, small enough to read at 16px. One SVG is the source; the PNGs are rendered from it by headless
Chrome and resized with macOS `sips`, so the three cannot disagree.

⭐ THE GENERATOR STAMPS ITS OWN OUTPUT (/media): apple-touch-icon.png is stamped `drawn` under register M-0009 and the
build fails if the stamp does. icon.svg is markup with no packet (exempt in ../.mediaignore, the M-0005 precedent);
favicon.ico is not a media type the hook reads, and holds the same pixels as the stamped PNG.
⛔ Not thonly.org's favicon: that is a stock heart, never the institution's mark, and it should not spread.
"""
import io, os, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
STAMP = os.path.join(ROOT, "..", "..", "..", ".claude", "skills", "media", "scripts", "stamp.py")


def svg(rounded):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            '<rect width="32" height="32"%s fill="#14112a"/>'
            '<circle cx="16" cy="16" r="9" fill="none" stroke="#b9a3e3" stroke-width="2.2"/>'
            '<circle cx="16" cy="16" r="3.8" fill="#f2c46d"/></svg>') % (' rx="7"' if rounded else "")


def render(markup, out):
    """512px master from Chrome; the window is 512 wide so no minimum-width clamp crops it."""
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "icon.html")
        io.open(src, "w", encoding="utf-8").write(
            '<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:transparent}'
            'svg{display:block;width:512px;height:512px}</style></head><body>%s</body></html>' % markup)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
                        "--force-device-scale-factor=1", "--window-size=512,512", "--screenshot=" + out,
                        "file://" + src], check=True, capture_output=True)


def resize(src, px, out):
    subprocess.run(["sips", "-z", str(px), str(px), src, "--out", out], check=True, capture_output=True)


def ico(pngs, out):
    """An .ico holding PNG entries (every current browser reads PNG-in-ICO)."""
    data = [open(p, "rb").read() for p, _ in pngs]
    head = struct.pack("<HHH", 0, 1, len(pngs))
    off = 6 + 16 * len(pngs)
    entries = b""
    for (p, px), d in zip(pngs, data):
        entries += struct.pack("<BBBBHHII", px % 256, px % 256, 0, 0, 1, 32, len(d), off)
        off += len(d)
    open(out, "wb").write(head + entries + b"".join(data))


def main():
    if not os.path.exists(CHROME):
        sys.exit("Chrome not found at %s" % CHROME)
    io.open(os.path.join(ROOT, "icon.svg"), "w", encoding="utf-8").write(svg(True) + "\n")
    with tempfile.TemporaryDirectory() as tmp:
        round_master, square_master = os.path.join(tmp, "round.png"), os.path.join(tmp, "square.png")
        render(svg(True), round_master)
        render(svg(False), square_master)          # iOS rounds the corners of a touch icon itself
        touch = os.path.join(ROOT, "apple-touch-icon.png")
        resize(square_master, 180, touch)
        p16, p32 = os.path.join(tmp, "16.png"), os.path.join(tmp, "32.png")
        resize(round_master, 16, p16)
        resize(round_master, 32, p32)
        ico([(p16, 16), (p32, 32)], os.path.join(ROOT, "favicon.ico"))
    subprocess.run(["python3", STAMP, touch, "--source", "drawn", "--rights", "cc0", "--register", "M-0009",
                    "--disclosure", "https://book.thonly.org/",
                    "--note", "the library's home-screen icon, drawn by our own code"], check=True, capture_output=True)
    for f in ("icon.svg", "apple-touch-icon.png", "favicon.ico"):
        print("%s %d bytes" % (f, os.path.getsize(os.path.join(ROOT, f))))


if __name__ == "__main__":
    main()
