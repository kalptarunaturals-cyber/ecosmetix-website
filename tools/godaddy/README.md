# What stays on GoDaddy

www.ecosmetix.in (the website) is served by GitHub Pages from this repository.
ecosmetix.in (no www) stays on GoDaddy hosting and runs only the server parts:

- /api/*.php: brief, brochure, contact, sample-status and status-request forms, download.php, and the old blog-cron scripts
- /data/: form submissions and samples.csv (sample tracker data)
- /downloads/: brochure PDFs handed out by the brochure form

Every other request to ecosmetix.in is redirected by public_html/.htaccess to https://www.ecosmetix.in (GitHub).

Files added on GoDaddy for this (17 Nov 2026):
- public_html/api/.htaccess: allows www.ecosmetix.in to call the forms (CORS) and stops the www redirect for /api/
- public_html/downloads/.htaccess: stops the www redirect for /downloads/
