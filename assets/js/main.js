/* Ecosmetix website scripts */
(function () {
  'use strict';
  var WA = '919877404384';
  var API = 'https://ecosmetix.in'; // form handlers stay on GoDaddy hosting

  // mobile menu
  var btn = document.querySelector('.menu-btn'), nav = document.querySelector('nav.main');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', open);
  });

  // footer year
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  // before/after compare sliders
  document.querySelectorAll('.compare').forEach(function (c) {
    var r = c.querySelector('input'), a = c.querySelector('.after-wrap'), h = c.querySelector('.handle');
    function set(v) { a.style.clipPath = 'inset(0 0 0 ' + v + '%)'; h.style.left = v + '%'; }
    r.addEventListener('input', function () { set(r.value); }); set(r.value);
  });

  // dynamic active-ingredient rows on the brief form
  var list = document.getElementById('actives');
  function addRow(name, pct) {
    if (!list) return;
    var row = document.createElement('div'); row.className = 'arow';
    row.innerHTML = '<input name="active_name[]" placeholder="e.g. Niacinamide" aria-label="Active ingredient">' +
      '<input name="active_pct[]" placeholder="% e.g. 5" aria-label="Percentage">' +
      '<button type="button" class="rm" aria-label="Remove">&times;</button>';
    row.querySelector('.rm').onclick = function () { if (list.children.length > 1) row.remove(); };
    if (name) row.children[0].value = name; if (pct) row.children[1].value = pct;
    list.appendChild(row);
  }
  if (list) { addRow(); addRow(); addRow(); document.getElementById('add-active').onclick = function () { addRow(); }; }

  // generic AJAX form handler: <form data-ajax="/api/brief.php">
  document.querySelectorAll('form[data-ajax]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = f.querySelector('.msg'), sb = f.querySelector('[type=submit]');
      if (!f.checkValidity()) { f.reportValidity(); return; }
      sb.disabled = true; var t = sb.textContent; sb.textContent = 'Sending…';
      fetch(f.getAttribute('data-ajax'), { method: 'POST', body: new FormData(f), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          msg.className = 'msg ' + (d.ok ? 'ok' : 'err'); msg.innerHTML = d.message;
          if (d.ok) {
            if (d.download) { msg.innerHTML += ' <a class="btn btn-primary" style="margin-top:12px" href="' + new URL(d.download, API + '/').href + '">Download now</a>'; }
            if (d.redirect) { window.location = d.redirect; }
            if (!d.keep) f.reset();
            if (window.gtag) gtag('event', 'generate_lead', { form: f.id });
          }
        })
        .catch(function () {
          msg.className = 'msg err';
          msg.innerHTML = 'Sorry, the form could not be sent. Please email <a href="mailto:rd@ecosmetix.in">rd@ecosmetix.in</a> or <a href="https://wa.me/' + WA + '">WhatsApp us</a>.';
        })
        .finally(function () { sb.disabled = false; sb.textContent = t; });
    });
  });

  // sample status lookup
  var sf = document.getElementById('status-form');
  if (sf) sf.addEventListener('submit', function (e) {
    e.preventDefault();
    var out = document.getElementById('status-result'), id = sf.sample_id.value.trim().toUpperCase(), ph = sf.phone4.value.trim();
    out.innerHTML = '<p class="small">Checking…</p>';
    fetch(API + '/api/status.php?id=' + encodeURIComponent(id) + '&p=' + encodeURIComponent(ph), { headers: { 'Accept': 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var wa = 'https://wa.me/' + WA + '?text=' + encodeURIComponent('Hello Ecosmetix, please share the latest status of my sample ' + id + '.');
        if (!d.ok) {
          out.innerHTML = '<div class="msg err" style="display:block">' + d.message + '</div><div class="btns"><a class="btn btn-wa" href="' + wa + '" target="_blank" rel="noopener">Ask on WhatsApp</a><a class="btn btn-ghost" href="#ask">Ask by email</a></div>';
          return;
        }
        var s = d.sample, html = '<div class="card ice"><span class="pill">' + s.id + '</span><h3 style="font-family:var(--serif);font-size:28px;margin:10px 0 2px">' + s.product + '</h3><p class="small">Last updated ' + s.updated + (s.eta ? ' &middot; Expected next step: ' + s.eta : '') + '</p><ul class="timeline">';
        d.stages.forEach(function (st, i) {
          var cls = i < d.current ? 'done' : (i === d.current ? 'current' : '');
          html += '<li class="' + cls + '"><span class="dot"></span><b>' + st + '</b>' + (i === d.current && s.note ? '<p class="small">' + s.note + '</p>' : '') + '</li>';
        });
        html += '</ul><div class="btns"><a class="btn btn-wa" href="' + wa + '" target="_blank" rel="noopener">Ask about this sample on WhatsApp</a></div></div>';
        out.innerHTML = html;
      })
      .catch(function () { out.innerHTML = '<div class="msg err" style="display:block">Status service is unavailable right now. Please WhatsApp us on +91 98774 04384.</div>'; });
  });

  // prefill sample ID in the email request form
  var ask = document.getElementById('ask-form');
  if (ask && sf) sf.sample_id.addEventListener('change', function () { ask.sample_id.value = sf.sample_id.value.toUpperCase(); });
})();
