#!/usr/bin/env python3
"""Build the static JDS website.

Pages live in src/pages/*.html. Each starts with a meta comment:
    <!--meta {"title": "...", "description": "...", "nav": "industries"} -->
The builder wraps each page with the shared <head>, header and footer and
writes it to site/<name>.html. Solution detail pages are generated from
src/data/solutions.json and industry panels from src/data/industries.json.

Tokens available inside page files:
    {{icon:name [classes]}}   inline SVG icon from the sprite
    {{cta|Title|Text}}        closing call-to-action band
    {{industries_explorer}}   the tabbed industries explorer
    {{email}} {{phone}} {{phone_href}}

Run:  python3 src/build.py
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "site"
sys.path.insert(0, str(ROOT))
from icons import ICONS  # noqa: E402

SITE = {
    "name": "Jurong Digital Solutions",
    "email": "hello@example.com",  # placeholder — replace with the real address
    "phone": "+65 0000 0000",  # placeholder — replace with the real number
    "phone_href": "+6500000000",
}

NAV = [
    ("home", "index.html", "Home"),
    ("about", "about.html", "About"),
    ("solutions", "solutions.html", "Solutions"),
    ("industries", "industries.html", "Industries"),
    ("resources", "resources.html", "Resources"),
    ("contact", "contact.html", "Contact"),
]

SOLUTIONS = [
    ("immersive-training.html", "vr", "Immersive Training", "VR &amp; CBT safety and operations training"),
    ("ddam.html", "scan", "DDAM Smart Field Ops", "Smart labelling &amp; digital twins"),
    ("aiva.html", "cctv", "AiVA Video Analytics", "AI compliance &amp; quality monitoring"),
]


def icon(name, cls="icon"):
    if name not in ICONS:
        raise SystemExit(f"unknown icon: {name}")
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def sprite():
    symbols = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{symbols}</svg>'


def arrow():
    return icon("arrow", "icon icon--arrow")


# ---------------------------------------------------------------- chrome
def header(active):
    items = []
    for key, href, label in NAV:
        current = ' aria-current="page"' if key == active else ""
        if key == "solutions":
            links = "".join(
                f'<li><a href="{h}"><span class="mega__icon">{icon(ic)}</span><span><strong>{t}</strong><small>{d}</small></span></a></li>'
                for h, ic, t, d in SOLUTIONS
            )
            links += f'<li><a href="industries.html"><span class="mega__icon">{icon("layers")}</span><span><strong>Industries we serve</strong><small>Solutions mapped to 8 sectors</small></span></a></li>'
            links += f'<li class="mega__all"><a href="solutions.html"><span class="mega__icon">{icon("arrow")}</span><span><strong>All solutions</strong><small>Compare the three platforms side by side</small></span></a></li>'
            items.append(
                f'<li class="has-menu" data-open="false"><button class="nav__link" type="button" aria-expanded="false" aria-controls="menu-solutions"{current}>'
                f'{label}{icon("chevron")}</button><ul class="mega" id="menu-solutions">{links}</ul></li>'
            )
        else:
            items.append(f'<li><a class="nav__link" href="{href}"{current}>{label}</a></li>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="utility">
  <div class="container">
    <span class="utility__tag">Digital Transformation &amp; Innovation · Singapore</span>
    <div class="utility__links">
      <a href="mailto:{SITE['email']}">{icon('mail')}{SITE['email']}</a>
      <a href="tel:{SITE['phone_href']}">{icon('phone')}{SITE['phone']}</a>
    </div>
  </div>
</div>
<header class="header">
  <div class="container">
    <a class="brand" href="index.html" aria-label="Jurong Digital Solutions home"><img src="assets/img/jds-logo.png" alt="Jurong Digital Solutions" width="100" height="46"></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">{icon('menu')}</button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul class="nav__list">{''.join(items)}</ul>
      <a class="btn btn--primary nav__mobile-cta" href="contact.html?topic=consultation">Book a consultation {arrow()}</a>
    </nav>
    <a class="btn btn--primary btn--sm header__cta" href="contact.html?topic=consultation">Book a consultation {arrow()}</a>
  </div>
</header>"""


def cta(title, text):
    return f"""<section class="cta" aria-labelledby="cta-title">
  <div class="container">
    <div class="reveal">
      <p class="label"><span>Next step</span>Let’s start your digital journey</p>
      <h2 class="h2" id="cta-title">{title}</h2>
      <p>{text}</p>
    </div>
    <div class="btn-row reveal">
      <a class="btn btn--accent" href="contact.html">Talk to our team {arrow()}</a>
      <a class="btn btn--ghost" href="contact.html?topic=brochure">Download company deck {icon('download')}</a>
    </div>
  </div>
</section>"""


def footer():
    sol = "".join(f'<li><a href="{h}">{t}</a></li>' for h, _, t, _ in SOLUTIONS)
    return f"""<footer class="footer">
  <div class="container">
    <div class="footer__top">
      <div class="footer__about">
        <a class="footer__logo" href="index.html"><img src="assets/img/jds-logo.png" alt="Jurong Digital Solutions" width="88" height="40" loading="lazy"></a>
        <p>Singapore-based industrial technology company helping critical industries digitise safety, training, operations and compliance with XR, AI and smart systems.</p>
        <div class="social">
          <a href="#" aria-label="JDS on LinkedIn">{icon('linkedin', 'icon icon--sm')}</a>
          <a href="#" aria-label="JDS on YouTube">{icon('youtube', 'icon icon--sm')}</a>
        </div>
      </div>
      <div><h2>Solutions</h2><ul class="footer__links">{sol}<li><a href="industries.html">Industries we serve</a></li></ul></div>
      <div><h2>Company</h2><ul class="footer__links">
        <li><a href="about.html">About JDS</a></li><li><a href="about.html#partners">Strategic partners</a></li>
        <li><a href="resources.html">Case studies</a></li><li><a href="contact.html">Contact</a></li></ul></div>
      <div><h2>Get in touch</h2><ul class="footer__links">
        <li><span>Singapore</span></li>
        <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
        <li><a href="tel:{SITE['phone_href']}">{SITE['phone']}</a></li>
        <li><a href="contact.html?topic=brochure">Download company deck</a></li></ul></div>
    </div>
    <div class="footer__bottom">
      <span>© <span data-year>2026</span> Jurong Digital Solutions Pte. Ltd. All rights reserved.</span>
      <nav aria-label="Legal"><span>PDPA &amp; GDPR aligned</span><a href="#">Privacy policy</a><a href="#">Terms</a></nav>
    </div>
  </div>
</footer>"""


def page(meta, body):
    title = meta["title"]
    full = f"{SITE['name']} — {title}" if meta.get("nav") == "home" else f"{title} | {SITE['name']}"
    desc = html.escape(meta["description"])
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full)}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#002060">
<meta property="og:title" content="{html.escape(full)}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/img/jds-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
{sprite()}
{header(meta.get('nav'))}
<main id="main">
{body}
</main>
{footer()}
<script src="assets/js/main.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- shared blocks
def accordion(faqs, first_open=True):
    return '<div class="accordion">' + "".join(
        f'<details{" open" if first_open and i == 0 else ""}><summary>{q}</summary><div class="acc__body">{a}</div></details>'
        for i, (q, a) in enumerate(faqs)
    ) + "</div>"


def index_list(rows):
    return '<ol class="index-list">' + "".join(f"<li><div><strong>{t}</strong><span>{d}</span></div></li>" for t, d in rows) + "</ol>"


def industries_explorer():
    data = json.loads((ROOT / "data" / "industries.json").read_text())
    tabs, panels = [], []
    for i, ind in enumerate(data):
        slug, first = ind["slug"], i == 0
        tabs.append(
            f'<button class="explorer__tab" role="tab" id="tab-{slug}" data-slug="{slug}" aria-controls="panel-{slug}" '
            f'aria-selected="{str(first).lower()}" tabindex="{0 if first else -1}">{icon(ind["icon"])}{ind["name"]}</button>'
        )
        challenges = "".join(f"<li><span>{c}</span></li>" for c in ind["challenges"])
        solutions = "".join(f"<li>{s}</li>" for s in ind["solutions"])
        panels.append(f"""<div class="panel" role="tabpanel" id="panel-{slug}" aria-labelledby="tab-{slug}" tabindex="0"{'' if first else ' hidden'}>
  <div class="panel__head"><span class="cell__icon">{icon(ind['icon'], 'icon icon--lg')}</span><h2 class="h2">{ind['name']}</h2></div>
  <div class="panel__cols">
    <div><h3>Key challenges</h3><ol class="index-list">{challenges}</ol></div>
    <div><h3>JDS solutions</h3><ul class="ticks">{solutions}</ul></div>
  </div>
  <h3>Frequently asked</h3>
  {accordion(ind['faqs'])}
  <div class="btn-row" style="margin-top:32px"><a class="btn btn--primary" href="contact.html?topic=consultation">Discuss your {ind['short']} project {arrow()}</a></div>
</div>""")
    return f"""<div class="explorer">
  <div class="explorer__tabs" role="tablist" aria-label="Industries" aria-orientation="vertical">{''.join(tabs)}</div>
  <div>{''.join(panels)}</div>
</div>"""


# ---------------------------------------------------------------- solution pages
def solution_page(s):
    chips = "".join(
        f'<a class="chip" href="{h}"' + (' aria-current="page"' if h == s["file"] else "") + f">{icon(ic)}{t}</a>"
        for h, ic, t, _ in SOLUTIONS
    )
    facts = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in s["facts"])
    blocks, n = [], 1

    ov = s["overview"]
    paras = "".join(f'<p class="lead">{p}</p>' if j == 0 else f'<p class="muted">{p}</p>' for j, p in enumerate(ov["paras"]))
    ov_list = f'<ul class="ticks ticks--2">{"".join(f"<li>{x}</li>" for x in ov["list"])}</ul>' if ov.get("list") else ""
    ov_index = index_list(ov["index"]) if ov.get("index") else ""
    blocks.append(f"""<section class="section" aria-labelledby="ov-title">
  <div class="container cols cols--5-7">
    <div class="stack reveal"><p class="label"><span>{n:02d}</span>{ov['label']}</p><h2 class="h2" id="ov-title">{ov['title']}</h2></div>
    <div class="stack stack--lg reveal">{paras}{ov_list}{ov_index}</div>
  </div>
</section>""")
    n += 1

    off = s["offerings"]
    cells = []
    for j, o in enumerate(off["items"]):
        text = f"<p>{o['text']}</p>" if o.get("text") else ""
        bullets = f'<ul class="ticks">{"".join(f"<li>{b}</li>" for b in o["bullets"])}</ul>' if o.get("bullets") else ""
        cells.append(
            f'<div class="cell"><div class="cell__top"><span class="cell__icon">{icon(o["icon"])}</span>'
            f'<span class="cell__num">{j + 1:02d}</span></div><h3>{o["title"]}</h3>{text}{bullets}</div>'
        )
    lead = f'<p class="lead">{off["lead"]}</p>' if off.get("lead") else ""
    blocks.append(f"""<section class="section section--paper" aria-labelledby="off-title">
  <div class="container">
    <div class="sec-head sec-head--split reveal"><div class="stack"><p class="label"><span>{n:02d}</span>{off['label']}</p><h2 class="h2" id="off-title">{off['title']}</h2></div>{lead}</div>
    <div class="ruled ruled--{off.get('cols', 3)} reveal">{''.join(cells)}</div>
  </div>
</section>""")
    n += 1

    if s.get("features"):
        f = s["features"]
        flead = f'<p class="lead">{f["lead"]}</p>' if f.get("lead") else ""
        blocks.append(f"""<section class="section" aria-labelledby="feat-title">
  <div class="container cols cols--5-7">
    <div class="stack reveal"><p class="label"><span>{n:02d}</span>{f['label']}</p><h2 class="h2" id="feat-title">{f['title']}</h2>{flead}</div>
    <div class="reveal">{index_list(f['items'])}</div>
  </div>
</section>""")
        n += 1

    uc = "".join(f"<li>{x}</li>" for x in s["use_cases"])
    bf = "".join(f"<li>{x}</li>" for x in s["benefits"])
    blocks.append(f"""<section class="section{' section--paper' if s.get('features') else ''}" aria-labelledby="uc-title">
  <div class="container cols cols--2">
    <div class="stack stack--lg reveal"><p class="label"><span>{n:02d}</span>Use cases</p><h2 class="h2" id="uc-title">Where teams use it</h2><ul class="ticks">{uc}</ul></div>
    <div class="stack stack--lg reveal"><p class="label"><span>{n + 1:02d}</span>Benefits</p><h2 class="h2">What you gain</h2><ul class="ticks">{bf}</ul></div>
  </div>
</section>""")
    n += 2

    steps = "".join(f"<li><strong>{t}</strong><span>{d}</span></li>" for t, d in s["steps"])
    blocks.append(f"""<section class="section section--dark" aria-labelledby="steps-title">
  <div class="container">
    <div class="sec-head reveal"><p class="label"><span>{n:02d}</span>Onboarding process</p><h2 class="h2" id="steps-title">{s['steps_title']}</h2></div>
    <ol class="steps reveal">{steps}</ol>
  </div>
</section>""")
    n += 1

    blocks.append(f"""<section class="section" aria-labelledby="faq-title">
  <div class="container cols cols--4-8">
    <div class="stack reveal"><p class="label"><span>{n:02d}</span>FAQs</p><h2 class="h2" id="faq-title">Common questions</h2><p class="muted">Can’t find an answer? <a class="accent" href="contact.html">Ask our team</a>.</p></div>
    <div class="reveal">{accordion(s['faqs'])}</div>
  </div>
</section>""")

    body = f"""<section class="page-hero">
  <div class="container">
    <nav aria-label="Breadcrumb"><ol class="crumbs"><li><a href="index.html">Home</a></li><li><a href="solutions.html">Solutions</a></li><li><span aria-current="page">{s['short']}</span></li></ol></nav>
    <div class="page-hero__grid">
      <div>
        <p class="label"><span>Solution</span>{s['tagline']}</p>
        <h1 class="h1">{s['title']}</h1>
        <p class="lead">{s['lead']}</p>
        <div class="btn-row"><a class="btn btn--primary" href="contact.html?topic={s['topic']}">Request a demo {arrow()}</a><a class="btn btn--outline" href="contact.html?topic=brochure">{s['brochure']} {icon('download')}</a></div>
      </div>
      <dl class="hero-meta">{facts}</dl>
    </div>
    <nav class="chips" aria-label="Solutions" style="margin-top:48px">{chips}</nav>
  </div>
</section>
{''.join(blocks)}
{cta(s['cta_title'], s['cta_text'])}"""
    return page({"title": s["name"], "description": s["description"], "nav": "solutions"}, body)


# ---------------------------------------------------------------- build
def expand(body, src_name):
    body = body.replace("{{industries_explorer}}", industries_explorer())
    body = re.sub(r"\{\{icon:([\w-]+)(?:\s+([\w -]+))?\}\}", lambda m: icon(m.group(1), m.group(2) or "icon"), body)
    body = re.sub(r"\{\{cta\|(.+?)\|(.+?)\}\}", lambda m: cta(m.group(1), m.group(2)), body, flags=re.S)
    for k, v in SITE.items():
        body = body.replace("{{" + k + "}}", v)
    leftover = re.findall(r"\{\{.*?\}\}", body)
    if leftover:
        raise SystemExit(f"{src_name}: unresolved tokens {leftover}")
    return body


def build():
    OUT.mkdir(exist_ok=True)
    for src in sorted((ROOT / "pages").glob("*.html")):
        raw = src.read_text()
        m = re.match(r"\s*<!--meta (\{.*?\}) -->\s*", raw, re.S)
        meta = json.loads(m.group(1))
        (OUT / src.name).write_text(page(meta, expand(raw[m.end():], src.name)))
        print("built", src.name)
    for s in json.loads((ROOT / "data" / "solutions.json").read_text()):
        (OUT / s["file"]).write_text(solution_page(s))
        print("built", s["file"])


if __name__ == "__main__":
    build()
