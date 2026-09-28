# Jurong Digital Solutions — website

A static, responsive website. There is no framework and no build step is needed to view it: open `index.html` in a browser, or serve this folder with any static host (GitHub Pages, Netlify, S3 and so on).

## Pages
| File | Page |
|---|---|
| `index.html` | Home |
| `about.html` | About Us: vision, mission, partners, clients |
| `solutions.html` | Solutions overview |
| `immersive-training.html` · `ddam.html` · `aiva.html` | One page per solution (generated from `src/data/solutions.json`) |
| `industries.html` | Industries explorer (8 industries, deep links such as `industries.html#oil-gas`) |
| `resources.html` | Case studies and downloads |
| `contact.html` | Enquiry form (`contact.html?topic=brochure` preselects the topic) |

## Editing
The HTML files here are **generated**. Edit the sources in `../src/`, then rebuild:

```bash
python3 src/build.py
```

- `src/pages/*.html`: page content
- `src/data/solutions.json`: content for the three solution pages
- `src/data/industries.json`: industry challenges, solutions and FAQs
- `src/build.py`: shared header, footer, CTA, and the placeholder email and phone (`SITE`)
- `src/icons.py`: the icon set
- `site/assets/css/styles.css`: the "Precision" theme: design tokens (brand navy `#002060`, orange `#FF4D00`, IBM Plex Sans and Plex Mono) and components
- `site/assets/js/main.js`: mobile menu, industries tabs, scroll reveal, form validation

## Before going live
- Replace the placeholder email and phone in `SITE` in `src/build.py`.
- Connect the contact form to a backend (see the `TODO` in `main.js`).
- Link the brochure and company-deck PDFs, and the social profile URLs in the footer.
