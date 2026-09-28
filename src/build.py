#!/usr/bin/env python3
"""Build the static JDS website.

Pages live in src/pages/*.html. Each starts with a meta comment:
    <!--meta {"title": "...", "description": "...", "nav": "industries"} -->
The builder wraps each page with the shared <head>, header, CTA and footer
and writes it to site/<name>.html. Industry panels are generated from
src/data/industries.json. Run:  python3 src/build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "site"

SITE = {
    "name": "Jurong Digital Solutions",
    "email": "hello@example.com",  # placeholder — replace with the real address
    "phone": "+65 0000 0000",  # placeholder — replace with the real number
    "phone_href": "+6500000000",
}

# Lucide-style icons (24x24, stroke). Referenced as <svg class="icon"><use href="#i-name"/></svg>
ICONS = {
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.4-.5-2-1-3-1.1-2.1-.2-4 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.2.4-2.3 1-3.1.3 1.5 1.3 2.6 2.5 2.6z"/>',
    "factory": '<path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z"/><path d="M17 18h1M12 18h1M7 18h1"/>',
    "ship": '<path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1s1.2 1 2.5 1c2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M19.4 18.9 21.8 12H2.2l2.4 6.9"/><path d="M12 12V2l6 6H6"/>',
    "hardhat": '<path d="M2 18a1 1 0 0 0 1 1h18a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v2z"/><path d="M10 10V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v5"/><path d="M4 15v-3a6 6 0 0 1 6-6"/><path d="M14 6a6 6 0 0 1 6 6v3"/>',
    "flask": '<path d="M10 2v7.5L4.2 19a2 2 0 0 0 1.7 3h12.2a2 2 0 0 0 1.7-3L14 9.5V2"/><path d="M8.5 2h7M7 16h10"/>',
    "cap": '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/><path d="M22 10v6"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.7a1 1 0 0 0-.2-.6l-3.5-4.3a1 1 0 0 0-.8-.4H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "tower": '<path d="M4.9 16.1C1 12.2 1 5.8 4.9 1.9"/><path d="M7.8 4.7a6.1 6.1 0 0 0-.8 7.5"/><circle cx="12" cy="9" r="2"/><path d="M16.2 4.8c2 2 2.3 5 .8 7.4"/><path d="M19.1 1.9a10 10 0 0 1 0 14.1"/><path d="M9.5 18h5"/><path d="m8 22 4-11 4 11"/>',
    "vr": '<path d="M3 8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3.3a2 2 0 0 1-1.7-1l-1-1.7a1.2 1.2 0 0 0-2 0L10 16a2 2 0 0 1-1.7 1H5a2 2 0 0 1-2-2z"/><circle cx="8" cy="11.5" r="1.5"/><circle cx="16" cy="11.5" r="1.5"/>',
    "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><rect x="7" y="7" width="4" height="4"/><rect x="13" y="13" width="4" height="4"/><path d="M13 7h4v3M7 17v-3h3"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "cctv": '<path d="M16.8 9.9 19 8.7a1 1 0 0 0 .4-1.4l-2.6-4.4a1 1 0 0 0-1.4-.4L4.3 8.8a1 1 0 0 0-.4 1.4l1.9 3.2a1 1 0 0 0 1.4.4l2.6-1.5"/><path d="M13.5 11.8 16 16l3-1.7"/><path d="M2 21h3a2 2 0 0 0 2-2v-3"/><path d="M2 14v7"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.7 9a1 1 0 0 1-.7 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.2-2.7a1.2 1.2 0 0 1 1.5 0C14.5 3.8 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.5 12.9 17 22l-5-3-5 3 1.5-9.1"/>',
    "plug": '<path d="M12 22v-5M9 8V2M15 8V2"/><path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8z"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "phone-mobile": '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M18 17V9M13 17V5M8 17v-3"/>',
    "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/>',
    "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.7-9h1.8a4.5 4.5 0 1 1 0 9z"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M16 13H8M16 17H8M10 9H8"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.8 9.8 0 0 1 6.7 2.7L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.8 9.8 0 0 1-6.7-2.7L3 16"/><path d="M8 16H3v5"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.7z"/><path d="m3.3 7 8.7 5 8.7-5M12 22V12"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "headset": '<path d="M3 11h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5a9 9 0 0 1 18 0v5a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/><path d="M21 16v2a4 4 0 0 1-4 4h-5"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20M2 12h20"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>',
    "youtube": '<path d="M2.5 17a24 24 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.6 49.6 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24 24 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.6 49.6 0 0 1-16.2 0A2 2 0 0 1 2.5 17"/><path d="m10 15 5-3-5-3z"/>',
    "quote": '<path d="M3 21c3 0 7-1 7-8V5c0-1.2-.8-2-2-2H4c-1.2 0-2 .8-2 2v6c0 1.2.8 2 2 2h3c0 4-2 6-4 6M14 21c3 0 7-1 7-8V5c0-1.2-.8-2-2-2h-4c-1.2 0-2 .8-2 2v6c0 1.2.8 2 2 2h3c0 4-2 6-4 6"/>',
}


def icon(name, cls="icon"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def sprite():
    symbols = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{symbols}</svg>'


CIRCUIT = """<svg class="circuit {cls}" viewBox="0 0 400 600" preserveAspectRatio="xMaxYMin slice" aria-hidden="true">
  <path d="M120 0v160"/><circle cx="120" cy="170" r="10"/>
  <path d="M200 0v90l30 30v120"/><circle cx="230" cy="250" r="10"/>
  <path d="M280 0v260"/><circle cx="280" cy="270" r="8"/>
  <path d="M340 0v120l-20 20v100"/><circle cx="320" cy="250" r="8"/>
  <path d="M60 0v60"/><circle cx="60" cy="70" r="7"/>
  <path d="M380 0v330"/><circle cx="380" cy="340" r="9"/>
</svg>"""


def circuit(cls):
    return CIRCUIT.replace("{cls}", cls)


NAV = [
    ("home", "index.html", "Home"),
    ("about", "about.html", "About Us"),
    ("solutions", "solutions.html", "Solutions"),
    ("industries", "industries.html", "Industries"),
    ("resources", "resources.html", "Resources"),
    ("contact", "contact.html", "Contact"),
]

SOLUTIONS = [
    ("immersive-training.html", "vr", "Immersive Training", "VR & CBT safety and operations training"),
    ("ddam.html", "scan", "DDAM Smart Field Ops", "Smart labelling & digital twins"),
    ("aiva.html", "cctv", "AiVA Video Analytics", "AI compliance & quality monitoring"),
]


def header(active):
    items = []
    for key, href, label in NAV:
        current = ' aria-current="page"' if key == active else ""
        if key == "solutions":
            sub = "".join(
                f'<li><a href="{h}"><span class="submenu__icon">{icon(ic)}</span><span><strong>{t}</strong><span>{d}</span></span></a></li>'
                for h, ic, t, d in SOLUTIONS
            )
            sub += f'<li><a href="solutions.html"><span class="submenu__icon">{icon("layers")}</span><span><strong>All solutions</strong><span>Compare the three platforms</span></span></a></li>'
            items.append(
                f'<li class="nav__item--has-menu" data-open="false">'
                f'<button class="nav__link" type="button" aria-expanded="false" aria-controls="submenu-solutions"{current}>'
                f'{label} {icon("chevron")}</button>'
                f'<ul class="submenu" id="submenu-solutions">{sub}</ul></li>'
            )
        else:
            items.append(f'<li><a class="nav__link" href="{href}"{current}>{label}</a></li>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar">
  <div class="container">
    <span class="topbar__tag">Digital Transformation &amp; Innovation — Singapore</span>
    <div class="topbar__links">
      <a href="mailto:{SITE['email']}">{icon('mail')}{SITE['email']}</a>
      <a href="tel:{SITE['phone_href']}">{icon('phone')}{SITE['phone']}</a>
    </div>
  </div>
</div>
<header class="header">
  <div class="container">
    <a class="brand" href="index.html" aria-label="Jurong Digital Solutions — home">
      <img src="assets/img/jds-logo.png" alt="Jurong Digital Solutions" width="96" height="44">
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">{icon('menu')}</button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul class="nav__list">{''.join(items)}</ul>
      <a class="btn btn--primary nav__mobile-cta" href="contact.html?topic=consultation">Book a Consultation {icon('arrow', 'icon icon--arrow')}</a>
    </nav>
    <a class="btn btn--primary btn--sm header__cta" href="contact.html?topic=consultation">Book a Consultation {icon('arrow', 'icon icon--arrow')}</a>
  </div>
</header>"""


def cta(title, text, eyebrow="Let’s start your digital journey"):
    return f"""<section class="section section--tight" aria-labelledby="cta-title">
  <div class="container">
    <div class="cta reveal">
      {circuit('circuit--cta')}
      <div>
        <span class="eyebrow eyebrow--light">{eyebrow}</span>
        <h2 class="h2" id="cta-title">{title}</h2>
        <p>{text}</p>
      </div>
      <div class="btn-row">
        <a class="btn btn--primary" href="contact.html">Talk to Our Team {icon('arrow', 'icon icon--arrow')}</a>
        <a class="btn btn--ghost" href="contact.html?topic=brochure">Download Company Deck {icon('download')}</a>
      </div>
    </div>
  </div>
</section>"""


def footer():
    sol = "".join(f'<li><a href="{h}">{t}</a></li>' for h, _, t, _ in SOLUTIONS)
    return f"""<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__about">
        <a class="footer__logo" href="index.html"><img src="assets/img/jds-logo.png" alt="Jurong Digital Solutions" width="88" height="40" loading="lazy"></a>
        <p>Singapore-based industrial technology company helping critical industries digitise safety, training, operations and compliance with XR, AI and smart systems.</p>
        <div class="social">
          <a href="#" aria-label="JDS on LinkedIn">{icon('linkedin', 'icon icon--sm')}</a>
          <a href="#" aria-label="JDS on YouTube">{icon('youtube', 'icon icon--sm')}</a>
          <a href="index.html" aria-label="JDS website">{icon('globe', 'icon icon--sm')}</a>
        </div>
      </div>
      <div>
        <h2>Solutions</h2>
        <ul class="footer__links">{sol}<li><a href="industries.html">Industries We Serve</a></li></ul>
      </div>
      <div>
        <h2>Company</h2>
        <ul class="footer__links">
          <li><a href="about.html">About JDS</a></li>
          <li><a href="about.html#partners">Strategic Partners</a></li>
          <li><a href="resources.html">Case Studies</a></li>
          <li><a href="contact.html">Contact Us</a></li>
        </ul>
      </div>
      <div>
        <h2>Get in touch</h2>
        <ul class="footer__links">
          <li><span>Singapore</span></li>
          <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
          <li><a href="tel:{SITE['phone_href']}">{SITE['phone']}</a></li>
          <li><a href="contact.html?topic=brochure">Download Company Deck</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© <span data-year>2026</span> Jurong Digital Solutions Pte. Ltd. All rights reserved.</span>
      <nav aria-label="Legal"><span>PDPA &amp; GDPR aligned</span><a href="#">Privacy Policy</a><a href="#">Terms</a></nav>
    </div>
  </div>
</footer>"""


def page(meta, body):
    title = meta["title"]
    full_title = f"{title} | {SITE['name']}" if meta.get("nav") != "home" else f"{SITE['name']} — {title}"
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(meta['description'])}">
<meta name="theme-color" content="#002060">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(meta['description'])}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/img/jds-logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
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


# ---------- Industries explorer (generated from data) ----------
def industries_explorer():
    data = json.loads((ROOT / "data" / "industries.json").read_text())
    tabs, panels = [], []
    for i, ind in enumerate(data):
        slug = ind["slug"]
        sel = "true" if i == 0 else "false"
        tabs.append(
            f'<button class="explorer__tab" role="tab" id="tab-{slug}" data-slug="{slug}" aria-controls="panel-{slug}" '
            f'aria-selected="{sel}" tabindex="{0 if i == 0 else -1}"><span class="explorer__tab-icon">{icon(ind["icon"])}</span>{ind["name"]}</button>'
        )
        challenges = "".join(f"<li>{c}</li>" for c in ind["challenges"])
        solutions = "".join(f"<li>{s}</li>" for s in ind["solutions"])
        faqs = "".join(
            f'<details{" open" if j == 0 else ""}><summary>{q}</summary><div class="faq__a">{a}</div></details>'
            for j, (q, a) in enumerate(ind["faqs"])
        )
        panels.append(f"""<div class="panel" role="tabpanel" id="panel-{slug}" aria-labelledby="tab-{slug}" tabindex="0"{'' if i == 0 else ' hidden'}>
  <div class="panel__head"><span class="card__icon">{icon(ind['icon'])}</span><h2 class="h3">{ind['name']}</h2></div>
  <div class="panel__cols">
    <div><h3>Key challenges</h3><ol class="numlist">{challenges}</ol></div>
    <div><h3>JDS solutions</h3><ul class="checklist">{solutions}</ul></div>
  </div>
  <h3>FAQs</h3>
  <div class="faq faq--full">{faqs}</div>
  <div class="btn-row" style="margin-top:28px">
    <a class="btn btn--navy btn--sm" href="contact.html?topic=consultation">Discuss your {ind['short']} project {icon('arrow', 'icon icon--arrow')}</a>
  </div>
</div>""")
    return f"""<div class="explorer">
  <div class="explorer__tabs" role="tablist" aria-label="Industries" aria-orientation="vertical">{''.join(tabs)}</div>
  <div>{''.join(panels)}</div>
</div>"""


def build():
    OUT.mkdir(exist_ok=True)
    for src in sorted((ROOT / "pages").glob("*.html")):
        raw = src.read_text()
        m = re.match(r"\s*<!--meta (\{.*?\}) -->\s*", raw, re.S)
        meta = json.loads(m.group(1))
        body = raw[m.end():]
        body = body.replace("{{industries_explorer}}", industries_explorer())
        body = re.sub(r"\{\{circuit:([\w-]+)\}\}", lambda mm: circuit(mm.group(1)), body)
        body = re.sub(r"\{\{icon:([\w-]+)(?:\s+([\w -]+))?\}\}", lambda mm: icon(mm.group(1), mm.group(2) or "icon"), body)
        body = re.sub(r"\{\{cta\|(.+?)\|(.+?)\}\}", lambda mm: cta(mm.group(1), mm.group(2)), body, flags=re.S)
        for k, v in SITE.items():
            body = body.replace("{{" + k + "}}", v)
        leftover = re.findall(r"\{\{.*?\}\}", body)
        if leftover:
            raise SystemExit(f"{src.name}: unresolved tokens {leftover}")
        (OUT / src.name).write_text(page(meta, body))
        print("built", src.name)


if __name__ == "__main__":
    build()
