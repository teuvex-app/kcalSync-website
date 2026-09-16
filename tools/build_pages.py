#!/usr/bin/env python3
"""Erzeugt aus den Markdown-Rechtstexten statische HTML-Seiten fuer GitHub Pages.

Hintergrund: Die Website unter teuvex.de liegt im selben Google-Cloud-Projekt wie
das Backend der App. Wird das Projekt gesperrt, sind Impressum und
Datenschutzerklaerung nicht mehr erreichbar - § 5 DDG verlangt aber "staendig
verfuegbar". Diese Seiten liegen deshalb bei GitHub und sind von Google
unabhaengig.

Bewusst ohne externe Schriften, Skripte oder Stile: Die Datenschutzerklaerung
sagt zu, dass die Website keine Google Fonts einbindet. Eine Seite, die ihre
eigene Zusage bricht, waere schlimmer als gar keine.

Aufruf:  python3 tools/build_pages.py
"""
import html
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

# Zielverzeichnis -> (Quelle DE, Quelle EN, Titel DE, Titel EN)
PAGES = {
    "konto-loeschen":      ("deletion/deletion_de.md",      "deletion/deletion_en.md",
                            "Konto und Daten löschen",      "Delete account and data"),
    "datenschutz":         ("privacy/privacy_policy_de.md", "privacy/privacy_policy_en.md",
                            "Datenschutzerklärung",         "Privacy Policy"),
    "impressum":           ("imprint/impressum_de.md",      "imprint/impressum_en.md",
                            "Impressum",                    "Legal Notice"),
    "nutzungsbedingungen": ("terms/terms_de.md",            "terms/terms_en.md",
                            "Nutzungsbedingungen",          "Terms of Use"),
}

# Interne Verweise in den Markdown-Texten zeigen auf die Pfade der alten
# Website. Auf GitHub Pages liegt alles unter dem Repositorynamen.
BASE = "/kcalSync-website"
LINK_MAP = {
    "/konto-loeschen": BASE + "/konto-loeschen/",
    "/datenschutz":    BASE + "/datenschutz/",
    "/impressum":      BASE + "/impressum/",
}


def inline(text):
    """Fett, Links und Rohtext - mehr kommt in diesen Texten nicht vor."""
    out = []
    pos = 0
    pattern = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)")
    for m in pattern.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append("<strong>%s</strong>" % html.escape(m.group(1)))
        else:
            label, href = m.group(2), m.group(3)
            href = LINK_MAP.get(href, href)
            ext = href.startswith("http")
            attrs = ' target="_blank" rel="noopener noreferrer"' if ext else ""
            out.append('<a href="%s"%s>%s</a>' % (html.escape(href), attrs, html.escape(label)))
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def to_html(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    list_open = None  # "ul" | "ol" | None

    def close_list():
        nonlocal list_open
        if list_open:
            out.append("</%s>" % list_open)
            list_open = None

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            close_list(); i += 1; continue

        if re.fullmatch(r"-{3,}", stripped):
            close_list(); out.append("<hr>"); i += 1; continue

        m = re.match(r"(#{1,6})\s+(.*)", stripped)
        if m:
            close_list()
            lvl = min(len(m.group(1)) + 1, 6)   # # wird zu h2, der Seitentitel ist h1
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2)), lvl))
            i += 1; continue

        m = re.match(r"[-*]\s+(.*)", stripped)
        if m:
            if list_open != "ul":
                close_list(); out.append("<ul>"); list_open = "ul"
            out.append("<li>%s</li>" % inline(m.group(1)))
            i += 1; continue

        m = re.match(r"\d+\.\s+(.*)", stripped)
        if m:
            if list_open != "ol":
                close_list(); out.append("<ol>"); list_open = "ol"
            out.append("<li>%s</li>" % inline(m.group(1)))
            i += 1; continue

        # Absatz: Folgezeilen anhaengen, bis eine Leerzeile oder ein Block kommt
        close_list()
        buf = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or re.match(r"(#{1,6}\s|[-*]\s|\d+\.\s)", nxt) or re.fullmatch(r"-{3,}", nxt):
                break
            buf.append(nxt); i += 1
        out.append("<p>%s</p>" % inline(" ".join(buf)))

    close_list()
    return "\n".join(out)


STYLE = """
:root{color-scheme:light dark;
--bg:#f7f9f8;--card:#fff;--ink:#16211c;--soft:#54645b;--faint:#7d8c84;
--line:#dde4e0;--accent:#0f6e52;--accent-bg:#e4f0ea}
@media(prefers-color-scheme:dark){:root{
--bg:#101613;--card:#18201c;--ink:#e6ede9;--soft:#9cab a3;--faint:#7a8981;
--line:#28322c;--accent:#57c397;--accent-bg:#16302688}}
@media(prefers-color-scheme:dark){:root{--soft:#9caba3}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
-webkit-text-size-adjust:100%}
.wrap{max-width:780px;margin:0 auto;padding:28px 16px 72px}
a{color:var(--accent)}
.top{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:22px}
.top a{display:inline-block;font-size:13px;font-weight:600;text-decoration:none;
padding:6px 12px;border-radius:999px;background:var(--accent-bg);border:1px solid var(--line)}
h1{font-size:clamp(25px,5vw,34px);line-height:1.2;margin:0 0 6px;letter-spacing:-.02em}
.sub{color:var(--faint);font-size:13px;margin:0 0 24px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:22px 20px;margin-bottom:22px;overflow-wrap:break-word}
.card h2{font-size:20px;line-height:1.3;margin:26px 0 10px;padding-bottom:6px;
border-bottom:1px solid var(--line);letter-spacing:-.01em}
.card h3{font-size:17px;margin:22px 0 8px;color:var(--accent)}
.card h4,.card h5,.card h6{font-size:15px;margin:18px 0 6px}
.card>:first-child{margin-top:0}
p{margin:12px 0}
ul,ol{margin:12px 0;padding-left:22px}
li{margin:5px 0}
hr{border:0;border-top:1px solid var(--line);margin:26px 0}
footer{color:var(--faint);font-size:13px;border-top:1px solid var(--line);padding-top:18px}
footer a{color:var(--accent)}
@media print{:root{--bg:#fff;--card:#fff;--ink:#000;--line:#bbb}
.top{display:none}body{font-size:10.5pt}.card{border:0;padding:0}}
"""

PAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_de} – KcalSync</title>
<meta name="description" content="{title_de} für die App KcalSync von Teuvex, Lars Teuscher.">
<meta name="robots" content="index,follow">
<style>{style}</style>
</head>
<body>
<div class="wrap">
<nav class="top">
<a href="{base}/">Übersicht</a>
<a href="{base}/impressum/">Impressum</a>
<a href="{base}/datenschutz/">Datenschutz</a>
<a href="{base}/nutzungsbedingungen/">Nutzungsbedingungen</a>
<a href="{base}/konto-loeschen/">Konto löschen</a>
<a href="#english">English</a>
</nav>

<h1>{title_de}</h1>
<p class="sub">KcalSync — Teuvex, Lars Teuscher</p>
<div class="card">
{body_de}
</div>

<h2 id="english" style="font-size:clamp(20px,4vw,26px);margin:36px 0 6px">{title_en}</h2>
<p class="sub">English version</p>
<div class="card" lang="en">
{body_en}
</div>

<footer>
<p>Teuvex · Lars Teuscher · Dresdner Str. 153 · 01705 Freital ·
<a href="mailto:support@teuvex.de">support@teuvex.de</a></p>
<p>Diese Seiten werden aus dem öffentlichen Textbestand erzeugt und sind
unabhängig vom App-Backend erreichbar.</p>
</footer>
</div>
</body>
</html>
"""

INDEX = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rechtliche Angaben – KcalSync</title>
<meta name="description" content="Impressum, Datenschutzerklärung, Nutzungsbedingungen und Kontolöschung für die App KcalSync.">
<style>{style}</style>
</head>
<body>
<div class="wrap">
<h1>KcalSync — Rechtliche Angaben</h1>
<p class="sub">Teuvex · Lars Teuscher</p>
<div class="card">
<p>Hier finden Sie die Pflichtangaben und Rechtstexte zur App KcalSync. Sie sind
bewusst unabhängig vom App-Backend erreichbar.</p>
<ul>
<li><a href="{base}/impressum/">Impressum</a> — Anbieterkennzeichnung nach § 5 DDG</li>
<li><a href="{base}/datenschutz/">Datenschutzerklärung</a> — welche Daten verarbeitet werden und warum</li>
<li><a href="{base}/nutzungsbedingungen/">Nutzungsbedingungen</a></li>
<li><a href="{base}/konto-loeschen/">Konto und Daten löschen</a> — beide Wege, Schritt für Schritt</li>
</ul>
<p lang="en">Each page carries an English version below the German text.</p>
</div>
<footer>
<p>Teuvex · Lars Teuscher · Dresdner Str. 153 · 01705 Freital ·
<a href="mailto:support@teuvex.de">support@teuvex.de</a></p>
</footer>
</div>
</body>
</html>
"""


def main():
    written = []
    for slug, (src_de, src_en, title_de, title_en) in PAGES.items():
        p_de = os.path.join(DOCS, src_de)
        p_en = os.path.join(DOCS, src_en)
        for p in (p_de, p_en):
            if not os.path.exists(p):
                sys.exit("Fehlt: %s" % p)
        body_de = to_html(io.open(p_de, encoding="utf-8").read())
        body_en = to_html(io.open(p_en, encoding="utf-8").read())
        target_dir = os.path.join(DOCS, slug)
        os.makedirs(target_dir, exist_ok=True)
        target = os.path.join(target_dir, "index.html")
        io.open(target, "w", encoding="utf-8").write(PAGE.format(
            style=STYLE, base=BASE, title_de=title_de, title_en=title_en,
            body_de=body_de, body_en=body_en))
        written.append((slug, len(body_de), len(body_en)))

    io.open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(
        INDEX.format(style=STYLE, base=BASE))
    io.open(os.path.join(DOCS, ".nojekyll"), "w", encoding="utf-8").write("")

    for slug, a, b in written:
        print("  %-22s de %6d  en %6d Zeichen" % (slug + "/", a, b))
    print("  index.html, .nojekyll")


if __name__ == "__main__":
    main()
