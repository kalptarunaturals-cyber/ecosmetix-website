# Publishing to www.ecosmetix.in (GitHub Pages)

This repository is a copy of the live ecosmetix.in site, served by GitHub Pages from
the `main` branch. Every push to `main` goes live in about 1–2 minutes once the domain
points to GitHub. Until the GoDaddy DNS is switched, the live site is still the GoDaddy copy.

## Publishing an approved blog post
1. Write the spec JSON at `tools/specs/<date>-<slug>.json` (fields are listed at the top of `tools/blog_tool.py`).
2. Check it: `python3 tools/blog_tool.py check tools/specs/<date>-<slug>.json`
3. Preview for approval: `python3 tools/blog_tool.py preview tools/specs/<date>-<slug>.json preview.html`
   (absolute links to https://www.ecosmetix.in so it renders standalone; do not commit it).
4. After approval, build in place: `python3 tools/blog_tool.py build tools/specs/<date>-<slug>.json`
   This writes `blog/<slug>/index.html`, adds the card to the top of `blog/index.html` and adds the URL to `sitemap.xml`.
5. Commit ("Publish blog: <title>") and push to `main`.

## Rules for every post
- 1,500–2,600 words of article (body + FAQs + references), at least 4 H2s, primary keyword in
  seo_title (≤60 chars, keyword first), H1, slug, first 100 words, two H2s, and the 140–158 char meta description.
- At least 2 charts/diagrams/tables drawn by us (inline SVG or HTML tables). No images copied from other websites.
- 6–8 FAQs, 3–6 credible sources, at least 3 internal links (service pages, /product-brief/, other posts).
- Never name competitors (BO International, Maxnova, Dermat India) or brands we must not show
  (Cureskin, Curehair, Nature4Nature, Leafon). Clients that may be named: Numour, Just Herbs.
- Never invent numbers, studies or results. Use only site facts, cited sources or keyword-tool data.

## Forms
The brief, brochure, contact and sample-status forms post to PHP files under `/api/` that run on GoDaddy
hosting. GitHub Pages cannot run PHP, so these need a new home before the DNS switch.

## Domain
The site's canonical host is `www.ecosmetix.in`. When switching, add a `CNAME` file containing
`www.ecosmetix.in`, keep `.nojekyll`, and change only the website DNS records at GoDaddy (never MX or email records).
