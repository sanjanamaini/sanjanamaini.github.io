(function () {
  var pg = document.getElementById('pg'), out = document.getElementById('out');
  var base = location.origin && location.origin !== 'null' ? location.origin : 'https://sanjanamaini.github.io';
  var o = document.createElement('option'); o.value = ''; o.textContent = 'Home'; pg.appendChild(o);
  PAGES.forEach(function (p) { var x = document.createElement('option'); x.value = p.slug; x.textContent = p.name; pg.appendChild(x); });
  function clean(s) { return s.trim().replace(/\s+/g, '_'); }
  function build() {
    var cmp = clean(document.getElementById('cmp').value) || pg.value || 'home';
    var u = base + '/' + (pg.value ? pg.value + '/' : '') + '?utm_source=' + document.getElementById('src').value +
      '&utm_medium=' + document.getElementById('med').value + '&utm_campaign=' + encodeURIComponent(cmp);
    out.textContent = u;
  }
  ['pg', 'src', 'med', 'cmp'].forEach(function (id) { document.getElementById(id).addEventListener('input', build); });
  build();
})();
