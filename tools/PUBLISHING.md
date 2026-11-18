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

## Daily automatic flow (all run by Claude scheduled tasks, no PC needed)
1. ~9:15 AM IST: the writing task researches a topic (tools/blog-plan.md), writes `drafts/<YYYY-MM-DD>/spec.json`
   on the `drafts` branch (not public) and emails the draft for approval from kalptarunaturals@gmail.com (Gmail
   connector) to info@ecosmetix.in, subject "[Approval needed] Ecosmetix blog: <title> [EBX <date>]".
2. The owner replies from info@ecosmetix.in: APPROVE, or the changes wanted.
3. ~11:40 AM, 1 PM, 3 PM and 6 PM IST: the check task reads the reply. Changes -> revise and email again.
   APPROVE -> from 1 PM it builds the post with tools/blog_tool.py, pushes to main (live in ~2 min) and replies
   "Published" with the link.
(tools/blog_pipeline.py is an unused alternative that sends from info@ecosmetix.in via GitHub Actions; it needs a
Google app password as the MAIL_APP_PASSWORD secret and its workflow is not installed.)

## Rules for every post
- 1,500–2,600 words of article (body + FAQs + references), at least 4 H2s, primary keyword in
  seo_title (≤60 chars, keyword first), H1, slug, first 100 words, two H2s, and the 140–158 char meta description.
- At least 2 charts/diagrams/tables drawn by us (inline SVG or HTML tables). No images copied from other websites.
- 6–8 FAQs, 3–6 credible sources, at least 3 internal links (service pages, /product-brief/, other posts).
- Never name competitors (BO International, Maxnova, Dermat India) or brands we must not show
  (Cureskin, Curehair, Nature4Nature, Leafon). Clients that may be named: Numour, Just Herbs.
- Never invent numbers, studies or results. Use only site facts, cited sources or keyword-tool data.
- Original writing only (no repetition, no plagiarism). `check` and `build` refuse a post that reuses the slug,
  title or primary keyword of any published post or draft, shares more than 3% of its 8-word phrases with one,
  or has an identical run of 16+ words. Before emailing a draft, also run
  `python3 tools/blog_tool.py originality <spec> [folder of saved research pages]` and search each printed
  sentence on Google in quotes; any exact match on another site must be rewritten in our own words. Quote a
  law or standard only inside quotation marks with the source cited.

## Forms
The brief, brochure, contact and sample-status forms post to PHP files under `/api/` that run on GoDaddy
hosting. GitHub Pages cannot run PHP, so these need a new home before the DNS switch.

## Domain
The site's canonical host is `www.ecosmetix.in`. When switching, add a `CNAME` file containing
`www.ecosmetix.in`, keep `.nojekyll`, and change only the website DNS records at GoDaddy (never MX or email records).
