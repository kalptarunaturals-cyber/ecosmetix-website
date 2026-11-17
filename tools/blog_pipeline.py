#!/usr/bin/env python3
"""Ecosmetix daily blog: approval and publishing pipeline (runs in GitHub Actions).

Layout
  main branch     the live website (served by GitHub Pages at www.ecosmetix.in)
  drafts branch   drafts/<id>/spec.json  written each morning by the Claude writing task
                  drafts/<id>/state.json written by this script (sent / feedback / published)

Each run:
  1. notify  - every draft whose spec changed since it was last emailed is sent for approval
               from info@ecosmetix.in to info@ecosmetix.in (subject carries the draft id).
  2. check   - reads replies from info@ecosmetix.in by IMAP.
               "APPROVE" (first line of the reply) -> publish (not before 13:00 IST)
               anything else                      -> saved as feedback for the writing task
Env: MAIL_USER, MAIL_APP_PASSWORD (Google app password for info@ecosmetix.in),
     MAIN_DIR (checkout of main), DRAFTS_DIR (checkout of drafts).
"""
import datetime, email, email.policy, hashlib, html, imaplib, json, os, re, smtplib, subprocess, sys
from email.message import EmailMessage
from email.utils import make_msgid, parseaddr

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
SITE = 'https://www.ecosmetix.in'
APPROVER = 'info@ecosmetix.in'
PUBLISH_FROM_HOUR = 13  # IST

USER = os.environ.get('MAIL_USER', 'info@ecosmetix.in')
PWD = os.environ.get('MAIL_APP_PASSWORD', '')
MAIN = os.environ.get('MAIN_DIR', '.')
DRAFTS = os.environ.get('DRAFTS_DIR', 'drafts-wt')


def now():
    return datetime.datetime.now(IST)


def load(p, default=None):
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(p, data):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def sh(*a, cwd=None):
    print('+', ' '.join(a))
    return subprocess.run(a, cwd=cwd, check=True, text=True, capture_output=True).stdout


def drafts():
    root = os.path.join(DRAFTS, 'drafts')
    if not os.path.isdir(root):
        return []
    out = []
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if os.path.isfile(os.path.join(p, 'spec.json')):
            out.append((d, p))
    return out


def tag(did):
    return '[EBX %s]' % did


def strip_tags(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()


def send(msg):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
        s.login(USER, PWD)
        s.send_message(msg)


def approval_email(did, spec, preview_path, check_out):
    url = '%s/blog/%s/' % (SITE, spec['slug'])
    body = re.sub(r'<svg[\s\S]*?</svg>', '<p><i>[chart: see attached preview]</i></p>', spec['body_html'])
    faqs = ''.join('<p><b>%s</b><br>%s</p>' % (html.escape(f['q']), f['a']) for f in spec.get('faqs', []))
    seo = ('<table cellpadding="6" style="border-collapse:collapse;font-size:14px">'
           + ''.join('<tr><td style="border:1px solid #ddd"><b>%s</b></td><td style="border:1px solid #ddd">%s</td></tr>' % (k, html.escape(str(v))) for k, v in [
               ('Primary keyword', spec.get('primary_keyword', '')),
               ('Secondary keywords', ', '.join(spec.get('secondary_keywords', []))),
               ('SEO title', spec['seo_title'] + ' | Ecosmetix'),
               ('Meta description (%d chars)' % len(spec['description']), spec['description']),
               ('Live URL after approval', url),
               ('Checks', check_out.strip().splitlines()[-1] if check_out.strip() else ''),
           ]) + '</table>')
    notes = ''.join('<li>%s</li>' % html.escape(n) for n in spec.get('notes_for_approver', []))
    m = EmailMessage()
    m['From'] = 'Ecosmetix Blog <%s>' % USER
    m['To'] = APPROVER
    m['Subject'] = '[Approval needed] Ecosmetix blog: %s %s' % (spec['title'], tag(did))
    m['Message-ID'] = make_msgid(domain='ecosmetix.in')
    m.set_content('Reply APPROVE to publish at about 1 PM IST, or reply with the changes you want.\n\n'
                  + spec['title'] + '\n' + url + '\n\n' + strip_tags(spec['body_html'])[:4000])
    m.add_alternative(
        '<div style="font-family:Arial,sans-serif;max-width:760px">'
        '<p style="font-size:16px"><b>Reply <span style="color:#0a7">APPROVE</span> to publish at about 1 PM IST, or reply with the changes you want.</b></p>'
        + ('<p><b>Notes:</b></p><ul>%s</ul>' % notes if notes else '')
        + '<h3>SEO summary</h3>' + seo
        + '<p>The full page preview (with charts) is attached as an HTML file. Open it in a browser.</p><hr>'
        + '<h1>%s</h1>' % html.escape(spec['title']) + body
        + ('<h2>FAQs</h2>' + faqs if faqs else '') + '</div>', subtype='html')
    with open(preview_path, 'rb') as f:
        m.add_attachment(f.read(), maintype='text', subtype='html', filename='preview-%s.html' % spec['slug'])
    return m


def notify():
    changed = False
    for did, p in drafts():
        spec_path = os.path.join(p, 'spec.json')
        st = load(os.path.join(p, 'state.json'), {})
        if st.get('published'):
            continue
        h = hashlib.sha256(open(spec_path, 'rb').read()).hexdigest()
        if st.get('sent_hash') == h or st.get('check_error_hash') == h:
            continue
        spec = load(spec_path)
        chk = subprocess.run([sys.executable, 'tools/blog_tool.py', 'check', os.path.abspath(spec_path)], cwd=MAIN, text=True, capture_output=True)
        if chk.returncode != 0:
            print('draft %s fails checks, not sent:\n%s' % (did, chk.stdout))
            st.update(check_error=chk.stdout, check_error_hash=h)
            save(os.path.join(p, 'state.json'), st)
            changed = True
            continue
        prev = os.path.abspath(os.path.join(p, 'preview.html'))
        sh(sys.executable, 'tools/blog_tool.py', 'preview', os.path.abspath(spec_path), prev, cwd=MAIN)
        m = approval_email(did, spec, prev, chk.stdout)
        send(m)
        st.update(sent_hash=h, sent_at=now().isoformat(), message_id=m['Message-ID'], subject=str(m['Subject']))
        st.pop('check_error', None)
        save(os.path.join(p, 'state.json'), st)
        changed = True
        print('sent approval email for', did)
    return changed


def reply_text(msg):
    part = msg.get_body(preferencelist=('plain', 'html'))
    if part is None:
        return ''
    t = part.get_content()
    if part.get_content_type() == 'text/html':
        t = strip_tags(re.sub(r'<(br|/p|/div)[^>]*>', '\n', t))
    lines = []
    for ln in t.splitlines():
        if ln.strip().startswith('>') or re.match(r'^\s*On .+wrote:\s*$', ln) or re.match(r'^-{2,}\s*Original Message', ln):
            break
        lines.append(ln)
    return '\n'.join(lines).strip()


def replies(did):
    """Replies from the approver to this draft, oldest first: (datetime, text)."""
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    M.login(USER, PWD)
    M.select('"[Gmail]/All Mail"', readonly=True)
    q = 'subject:"EBX %s" from:%s newer_than:10d' % (did, APPROVER)
    typ, data = M.search(None, 'X-GM-RAW', '"%s"' % q.replace('"', '\\"'))
    out = []
    for num in (data[0].split() if data and data[0] else []):
        typ, msgdata = M.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(msgdata[0][1], policy=email.policy.default)
        subj = str(msg.get('Subject', ''))
        if not re.match(r'^\s*(re|aw|fwd?)\s*:', subj, re.I):
            continue  # the approval request itself
        if parseaddr(str(msg.get('From', '')))[1].lower() != APPROVER:
            continue
        dt = email.utils.parsedate_to_datetime(msg['Date']).astimezone(IST)
        out.append((dt, reply_text(msg), str(msg.get('Message-ID', ''))))
    M.logout()
    return sorted(out)


def publish(did, p, spec, st):
    spec_name = '%s-%s.json' % (spec['date'], spec['slug'])
    dst = os.path.join(MAIN, 'tools', 'specs', spec_name)
    with open(os.path.join(p, 'spec.json'), encoding='utf-8') as f:
        data = f.read()
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(data)
    sh(sys.executable, 'tools/blog_tool.py', 'build', 'tools/specs/' + spec_name, cwd=MAIN)
    sh('git', 'add', '-A', cwd=MAIN)
    sh('git', 'commit', '-m', 'Publish blog: %s' % spec['title'], cwd=MAIN)
    sh('git', 'push', 'origin', 'HEAD:main', cwd=MAIN)
    url = '%s/blog/%s/' % (SITE, spec['slug'])
    st.update(published=True, published_at=now().isoformat(), url=url)
    m = EmailMessage()
    m['From'] = 'Ecosmetix Blog <%s>' % USER
    m['To'] = APPROVER
    m['Subject'] = 'Re: ' + st.get('subject', 'Ecosmetix blog %s' % tag(did))
    if st.get('message_id'):
        m['In-Reply-To'] = st['message_id']
        m['References'] = st['message_id']
    m.set_content('Published: %s\n\nIt will be live within about 2 minutes. It has been added to the blog page and the sitemap.' % url)
    try:
        send(m)
    except Exception as e:
        print('confirmation email failed:', e)
    print('published', url)


def check():
    changed = False
    for did, p in drafts():
        sp = os.path.join(p, 'state.json')
        st = load(sp, {})
        if st.get('published') or not st.get('sent_at'):
            continue
        spec = load(os.path.join(p, 'spec.json'))
        sent_at = datetime.datetime.fromisoformat(st['sent_at'])
        rs = [r for r in replies(did) if r[0] >= sent_at]
        if not rs:
            continue
        dt, text, mid = rs[-1]
        first = (text.strip().splitlines() or [''])[0].strip().upper()
        if re.match(r'^(APPROVE|APPROVED|OK PUBLISH|PUBLISH)\b', first):
            st.update(approved_at=dt.isoformat())
            if now().hour >= PUBLISH_FROM_HOUR or now().date() > dt.date():
                publish(did, p, spec, st)
            else:
                print('approved, waiting until %d:00 IST to publish' % PUBLISH_FROM_HOUR)
            save(sp, st)
            changed = True
        elif st.get('feedback_id') != mid:
            st.update(feedback=text, feedback_at=dt.isoformat(), feedback_id=mid)
            save(sp, st)
            changed = True
            print('feedback saved for', did)
    return changed


def main():
    if not PWD:
        sys.exit('MAIL_APP_PASSWORD secret is not set; add it in the repository settings (Secrets and variables > Actions).')
    sys.path.insert(0, MAIN)
    a = notify()
    b = check()
    print('changed' if (a or b) else 'nothing to do')


if __name__ == '__main__':
    main()
