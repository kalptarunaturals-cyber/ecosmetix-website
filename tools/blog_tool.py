#!/usr/bin/env python3
"""Ecosmetix blog tool.

Builds a new blog post for www.ecosmetix.in from a JSON spec, using an existing
post as the page shell, so header, footer, styles and schema match the site.

Usage (run from the repository root):
  python3 tools/blog_tool.py check   tools/specs/<date>-<slug>.json
  python3 tools/blog_tool.py preview tools/specs/<date>-<slug>.json out.html
  python3 tools/blog_tool.py build   tools/specs/<date>-<slug>.json
  python3 tools/blog_tool.py originality <spec> [research-source-folder]

`check` (and `build`) refuse a post that repeats an existing post or draft: same slug,
title or primary keyword, more than 3% shared 8-word phrases, or an identical run of
16+ words. `originality` also compares the post with the research pages saved in the
folder (plain text or HTML, one file per page) and prints sentences to search on Google
in quotes; an exact match anywhere on the web means the sentence must be rewritten.

Spec fields:
  slug          lowercase-hyphen URL slug (primary keyword in it)
  date          YYYY-MM-DD (publish date)
  title         H1 shown on the page
  seo_title     <title> text, max 60 chars, primary keyword first ("| Ecosmetix" is added)
  description   meta description, 140-158 chars, contains the primary keyword
  primary_keyword
  secondary_keywords  list
  image         hero image path, e.g. /assets/img/lab_glass.webp (must exist in repo)
  image_alt     alt text containing the primary keyword
  card_title    optional shorter title for the blog index card (defaults to title)
  body_html     article HTML (h2/h3/p/ul/ol/table/figure with inline SVG charts...)
  faqs          list of {"q": "...", "a": "..."} (6-8), rendered and added as FAQPage schema
  sources       list of {"title": "...", "url": "..."} (3-5), rendered as a References list
"""
import html, json, os, re, sys, datetime

SITE = 'https://www.ecosmetix.in'
SHELL = 'blog/how-to-write-cosmetic-product-brief/index.html'
WORD_MIN, WORD_MAX = 1500, 2600


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def esc(s):
    return html.escape(s, quote=True).replace('&#x27;', '&#39;')


def words(h):
    t = re.sub(r'<(script|style|svg)[\s\S]*?</\1>', ' ', h)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'%.-]*", t))


def nice_date(d):
    return datetime.date.fromisoformat(d).strftime('%d %B %Y')


def article_html(spec):
    out = [spec['body_html'].strip()]
    if spec.get('faqs'):
        out.append("<h2 id='faqs'>Frequently asked questions</h2>")
        for f in spec['faqs']:
            out.append("<details><summary>%s</summary><p>%s</p></details>" % (esc(f['q']), f['a']))
    if spec.get('sources'):
        lis = ''.join("<li><a href='%s' target='_blank' rel='noopener nofollow'>%s</a></li>" % (esc(s['url']), esc(s['title'])) for s in spec['sources'])
        out.append("<h2 id='references'>References</h2><ol class='small'>%s</ol>" % lis)
    out.append("<div class='callout'>Planning a product? <a href='/product-brief/'>Share your product brief</a> and our R&amp;D team will reply within one working day.</div>")
    return '\n'.join(out)


def check(spec, repo='.'):
    errs, warns = [], []
    req = ['slug', 'date', 'title', 'seo_title', 'description', 'primary_keyword', 'image', 'image_alt', 'body_html']
    for k in req:
        if not spec.get(k):
            errs.append('missing field: ' + k)
    if errs:
        return errs, warns
    kw = spec['primary_keyword'].lower()
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', spec['slug']):
        errs.append('slug must be lowercase words joined by hyphens')
    datetime.date.fromisoformat(spec['date'])
    full_title = spec['seo_title'] + ' | Ecosmetix'
    if len(spec['seo_title']) > 60:
        errs.append('seo_title is %d chars (max 60)' % len(spec['seo_title']))
    if not spec['seo_title'].lower().startswith(kw.split()[0]):
        warns.append('seo_title should start with the primary keyword')
    if kw not in spec['seo_title'].lower():
        errs.append('primary keyword not in seo_title')
    if kw not in spec['title'].lower():
        errs.append('primary keyword not in title (H1)')
    dl = len(spec['description'])
    if not 140 <= dl <= 158:
        errs.append('description is %d chars (need 140-158)' % dl)
    if kw not in spec['description'].lower():
        errs.append('primary keyword not in description')
    if not os.path.exists(os.path.join(repo, spec['image'].lstrip('/'))):
        errs.append('image not found in repo: ' + spec['image'])
    body = spec['body_html']
    first100 = ' '.join(re.sub(r'<[^>]+>', ' ', html.unescape(body)).split()[:100]).lower()
    if kw not in first100:
        errs.append('primary keyword not in the first 100 words')
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', body, re.S)
    if len(h2s) < 4:
        errs.append('need at least 4 H2 sections, found %d' % len(h2s))
    if sum(kw in re.sub(r'<[^>]+>', '', h).lower() for h in h2s) < 2:
        errs.append('primary keyword must appear in at least two H2s')
    internal = set(re.findall(r"href=['\"](/[^'\"#]*)", body))
    if len(internal) < 3:
        errs.append('need at least 3 internal links, found %d' % len(internal))
    for link in internal:
        p = link.lstrip('/')
        if p and not (os.path.exists(os.path.join(repo, p)) or os.path.exists(os.path.join(repo, p, 'index.html'))):
            errs.append('broken internal link: ' + link)
    charts = len(re.findall(r'<svg', body)) + len(re.findall(r'<table', body))
    if charts < 2:
        errs.append('need at least 2 charts/diagrams/tables (inline <svg> or <table>), found %d' % charts)
    nf = len(spec.get('faqs', []))
    if not 6 <= nf <= 8:
        errs.append('need 6-8 FAQs, found %d' % nf)
    ns = len(spec.get('sources', []))
    if not 3 <= ns <= 6:
        errs.append('need 3-6 sources, found %d' % ns)
    wc = words(article_html(spec))
    if not WORD_MIN <= wc <= WORD_MAX:
        errs.append('article is %d words (need %d-%d)' % (wc, WORD_MIN, WORD_MAX))
    banned = ['cureskin', 'bo international', 'maxnova', 'dermat india', 'curehair', 'nature4nature', 'leafon']
    low = (body + json.dumps(spec.get('faqs', []))).lower()
    for b in banned:
        if b in low:
            errs.append('mentions a brand that must not appear: ' + b)
    for s in spec.get('secondary_keywords', []):
        if s.lower() not in low:
            warns.append('secondary keyword not used: ' + s)
    if os.path.exists(os.path.join(repo, 'blog', spec['slug'], 'index.html')):
        warns.append('a post with this slug already exists (build will overwrite it)')
    o_errs, _, _ = originality(spec, repo)
    errs += o_errs
    return errs, warns


# ---------------------------------------------------------------- originality
# Repetition: a new post must not reuse the slug, title or primary keyword of any
# published post or earlier draft, and must not share passages with them.
# Plagiarism: the same passage test is run against the text of the web pages used
# while researching (saved as .txt/.html files in a folder), and the most distinctive
# sentences are printed so they can be searched on Google in quotes.
SHINGLE = 8          # words per shingle
MAX_SHARED = 0.03    # max share of the new post's shingles found in any one other text
MAX_RUN = 16         # max identical run of words with any one other text
BOILER = ["planning a product? share your product brief and our r&d team will reply within one working day."]


def plain_words(h):
    t = re.sub(r'<(script|style|svg|figcaption|caption)[\s\S]*?</\1>', ' ', h)
    t = re.sub(r"<h2 id='references'>[\s\S]*?</ol>", ' ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t).lower()
    for b in BOILER:
        t = t.replace(b, ' ')
    return re.findall(r"[a-z0-9][a-z0-9'%.-]*", t)


def shingles(ws, n=SHINGLE):
    return {' '.join(ws[i:i + n]) for i in range(max(0, len(ws) - n + 1))}


def longest_run(a, b):
    """Longest run of identical consecutive words shared by word lists a and b."""
    idx = {}
    for i in range(len(b) - 5):
        idx.setdefault(tuple(b[i:i + 6]), []).append(i)
    best, best_txt = 0, ''
    for i in range(len(a) - 5):
        for j in idx.get(tuple(a[i:i + 6]), []):
            k = 6
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            if k > best:
                best, best_txt = k, ' '.join(a[i:i + k])
    return best, best_txt


def article_from_page(p):
    s = open(p, encoding='utf-8', errors='ignore').read()
    m = re.search(r"<article class='post'>([\s\S]*?)</article>", s)
    return m.group(1) if m else s


def other_texts(spec, repo='.', extra_dirs=()):
    """Yield (label, meta, text) for every published post, spec and draft except this one."""
    blog = os.path.join(repo, 'blog')
    for d in sorted(os.listdir(blog)):
        p = os.path.join(blog, d, 'index.html')
        if d != spec['slug'] and os.path.isfile(p):
            s = open(p, encoding='utf-8').read()
            h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
            kw = re.search(r'"keywords": "([^",]*)', s)
            yield 'blog/' + d, {'slug': d, 'title': html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))) if h1 else '',
                                'primary_keyword': kw.group(1) if kw else ''}, article_from_page(p)
    spec_files = []
    for d in [os.path.join(repo, 'tools', 'specs')] + list(extra_dirs):
        for root, _, fs in os.walk(d):
            spec_files += [os.path.join(root, f) for f in fs if f.endswith('.json')]
    try:  # drafts live on the drafts branch
        import subprocess
        ls = subprocess.run(['git', '-C', repo, 'ls-tree', '-r', '--name-only', 'origin/drafts'], capture_output=True, text=True).stdout.split()
        for f in ls:
            if f.startswith('drafts/') and f.endswith('spec.json'):
                txt = subprocess.run(['git', '-C', repo, 'show', 'origin/drafts:' + f], capture_output=True, text=True).stdout
                spec_files.append(('origin/drafts:' + f, txt))
    except Exception:
        pass
    seen = set()
    for f in spec_files:
        label, txt = (f, open(f, encoding='utf-8').read()) if isinstance(f, str) else f
        try:
            o = json.loads(txt)
        except Exception:
            continue
        if o.get('slug') == spec['slug'] or o.get('slug') in seen:
            continue
        seen.add(o.get('slug'))
        yield label, o, article_html(o)


def compare(spec_words, label, text):
    ow = plain_words(text)
    a, b = shingles(spec_words), shingles(ow)
    shared = len(a & b) / max(1, len(a))
    run, run_txt = longest_run(spec_words, ow)
    return shared, run, run_txt


def originality(spec, repo='.', source_dir=None):
    errs, warns, report = [], [], []
    mine = plain_words(article_html(spec))
    norm = lambda x: re.sub(r'[^a-z0-9]+', ' ', (x or '').lower()).strip()
    for label, meta, text in other_texts(spec, repo):
        if norm(meta.get('primary_keyword')) and norm(meta.get('primary_keyword')) == norm(spec['primary_keyword']):
            errs.append('primary keyword "%s" already used by %s' % (spec['primary_keyword'], label))
        if norm(meta.get('title')) == norm(spec['title']):
            errs.append('title already used by ' + label)
        shared, run, run_txt = compare(mine, label, text)
        report.append((shared, run, label))
        if shared > MAX_SHARED or run >= MAX_RUN:
            errs.append('repeats text from %s: %.1f%% shared %d-word phrases, longest identical run %d words: "%s"'
                        % (label, shared * 100, SHINGLE, run, run_txt[:160]))
    if source_dir and os.path.isdir(source_dir):
        for f in sorted(os.listdir(source_dir)):
            p = os.path.join(source_dir, f)
            if not os.path.isfile(p):
                continue
            shared, run, run_txt = compare(mine, f, open(p, encoding='utf-8', errors='ignore').read())
            report.append((shared, run, 'source:' + f))
            if shared > MAX_SHARED or run >= MAX_RUN:
                errs.append('too close to research source %s: %.1f%% shared phrases, longest identical run %d words: "%s"'
                            % (f, shared * 100, run, run_txt[:160]))
    elif source_dir:
        warns.append('source folder not found: ' + source_dir)
    else:
        warns.append('no research-source folder given: web plagiarism only covered by the quoted-sentence search below')
    return errs, warns, report


def distinctive_sentences(spec, n=6):
    """Longest plain sentences of the body: search each in quotes on Google; any exact hit = rewrite."""
    t = re.sub(r'<(svg|table|figure)[\s\S]*?</\1>', ' ', spec['body_html'])
    t = re.sub(r'</(h2|h3|p|li)>', '\n', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    sents = [' '.join(s.split()) for s in re.split(r'(?<=[.?!])\s+|\n', t)]
    sents = [s for s in sents if 14 <= len(s.split()) <= 40 and 'Ecosmetix' not in s]
    sents.sort(key=len, reverse=True)
    step = max(1, len(sents) // n)
    return [' '.join(s.split()[:16]) for s in sents[::step][:n]]


def render(spec, repo='.', absolute=False):
    s = open(os.path.join(repo, SHELL), encoding='utf-8').read()
    url = '%s/blog/%s/' % (SITE, spec['slug'])
    title = esc(spec['seo_title'] + ' | Ecosmetix')
    desc = esc(spec['description'])
    img = SITE + spec['image']
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, s, count=1, flags=re.S)
    s = re.sub(r"<meta name='description' content='[^']*'>", "<meta name='description' content='%s'>" % desc, s, count=1)
    s = re.sub(r"<link rel='canonical' href='[^']*'>", "<link rel='canonical' href='%s'>" % url, s, count=1)
    s = re.sub(r"(property='og:title' content=')[^']*", r'\g<1>' + title, s)
    s = re.sub(r"(name='twitter:title' content=')[^']*", r'\g<1>' + title, s)
    s = re.sub(r"(property='og:description' content=')[^']*", r'\g<1>' + desc, s)
    s = re.sub(r"(name='twitter:description' content=')[^']*", r'\g<1>' + desc, s)
    s = re.sub(r"(property='og:url' content=')[^']*", r'\g<1>' + url, s)
    s = re.sub(r"(property='og:image' content=')[^']*", r'\g<1>' + img, s)
    s = re.sub(r"(name='twitter:image' content=')[^']*", r'\g<1>' + img, s)
    # schema: keep site graph, add BlogPosting, BreadcrumbList and FAQPage
    m = re.search(r"<script type='application/ld\+json'>(.*?)</script>", s, re.S)
    g = json.loads(m.group(1))
    g['@graph'] = [n for n in g['@graph'] if n.get('@type') in ('Organization', 'LocalBusiness', 'WebSite')]
    g['@graph'].append({'@type': 'BlogPosting', '@id': url + '#article', 'headline': spec['title'],
                        'description': spec['description'], 'image': img, 'datePublished': spec['date'],
                        'dateModified': spec['date'], 'inLanguage': 'en-IN', 'mainEntityOfPage': url,
                        'keywords': ', '.join([spec['primary_keyword']] + spec.get('secondary_keywords', [])),
                        'author': {'@type': 'Organization', 'name': 'Ecosmetix R&D team', '@id': SITE + '/#org'},
                        'publisher': {'@id': SITE + '/#org'}})
    g['@graph'].append({'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': SITE + '/blog/'},
        {'@type': 'ListItem', 'position': 3, 'name': spec['title'], 'item': url}]})
    if spec.get('faqs'):
        g['@graph'].append({'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', f['a'])}}
            for f in spec['faqs']]})
    s = s[:m.start(1)] + json.dumps(g, ensure_ascii=False).replace('</', '<\\/') + s[m.end(1):]
    # hero + article
    s = re.sub(r"(<span class='eyebrow'>Ecosmetix blog</span><h1[^>]*>).*?(</h1>)", lambda mm: mm.group(1) + esc(spec['title']) + mm.group(2), s, count=1, flags=re.S)
    s = re.sub(r"(<p class='post-meta'[^>]*>).*?(</p>)", lambda mm: mm.group(1) + nice_date(spec['date']) + ' &middot; By the Ecosmetix R&amp;D team' + mm.group(2), s, count=1, flags=re.S)
    hero = "<div class='photo' style='margin-bottom:30px'><img src='%s' alt='%s' width='1200' height='675'></div>" % (spec['image'], esc(spec['image_alt']))
    s = re.sub(r"<article class='post'>.*?</article>", lambda mm: "<article class='post'>" + hero + article_html(spec) + '</article>', s, count=1, flags=re.S)
    if absolute:
        s = re.sub(r"(href|src)='/(?!/)", r"\1='" + SITE + '/', s)
        s = re.sub(r'(href|src)="/(?!/)', r'\1="' + SITE + '/', s)
    return s


def build(spec, repo='.'):
    out_dir = os.path.join(repo, 'blog', spec['slug'])
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(render(spec, repo))
    # blog index: add a card at the top of the grid (replace if present)
    ip = os.path.join(repo, 'blog', 'index.html')
    b = open(ip, encoding='utf-8').read()
    href = '/blog/%s/' % spec['slug']
    b = re.sub(r"<a class='card card-img post-card' href='%s'.*?</a>" % re.escape(href), '', b, flags=re.S)
    card = ("<a class='card card-img post-card' href='%s' style='color:inherit'><img src='%s' alt='' loading='lazy' width='800' height='450'>"
            "<div class='in'><p class='post-meta'>%s &middot; Ecosmetix R&amp;D</p><h3 style='font-family:var(--serif);font-size:24px;margin-top:6px'>%s</h3></div></a>"
            % (href, spec['image'], nice_date(spec['date']), esc(spec.get('card_title') or spec['title'])))
    marker = "<div class='grid g3'>"
    i = b.find(marker)
    if i < 0:
        sys.exit('blog/index.html: post grid not found')
    b = b[:i + len(marker)] + card + b[i + len(marker):]
    open(ip, 'w', encoding='utf-8').write(b)
    # sitemap
    sp = os.path.join(repo, 'sitemap.xml')
    sm = open(sp, encoding='utf-8').read()
    loc = SITE + href
    sm = re.sub(r'<url><loc>%s</loc>.*?</url>\n?' % re.escape(loc), '', sm, flags=re.S)
    entry = '<url><loc>%s</loc><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>\n' % (loc, spec['date'])
    sm = sm.replace('</urlset>', entry + '</urlset>')
    sm = re.sub(r'(<loc>%s/blog/</loc><lastmod>)[^<]*' % re.escape(SITE), r'\g<1>' + spec['date'], sm)
    open(sp, 'w', encoding='utf-8').write(sm)
    print('built', os.path.join(out_dir, 'index.html'))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, spec = sys.argv[1], load(sys.argv[2])
    errs, warns = check(spec)
    for w in warns:
        print('WARN:', w)
    if cmd in ('check', 'build', 'originality') and errs:
        for e in errs:
            print('ERROR:', e)
        sys.exit(1)
    if cmd == 'check':
        print('OK: %d words' % words(article_html(spec)))
    elif cmd == 'preview':
        out = sys.argv[3] if len(sys.argv) > 3 else 'preview.html'
        open(out, 'w', encoding='utf-8').write(render(spec, absolute=True))
        print('preview written to', out, '(%d words)' % words(article_html(spec)))
    elif cmd == 'build':
        build(spec)
    elif cmd == 'originality':
        o_errs, o_warns, report = originality(spec, '.', sys.argv[3] if len(sys.argv) > 3 else None)
        for shared, run, label in sorted(report, reverse=True)[:8]:
            print('  %-60s %5.1f%% shared phrases, longest run %d words' % (label[:60], shared * 100, run))
        for w in o_warns:
            print('WARN:', w)
        print('Search each of these on Google in quotes; any exact match must be rewritten:')
        for s in distinctive_sentences(spec):
            print('  "%s"' % s)
        if o_errs:
            sys.exit(1)
        print('OK: no repetition or copied passages found')
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
