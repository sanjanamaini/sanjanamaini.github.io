/* Theme toggle and click tracking. The site reads fine without this file. */
(function () {
  var r = document.documentElement, b = document.getElementById('t');
  try { var s = localStorage.getItem('theme'); if (s) r.setAttribute('data-theme', s); } catch (e) {}
  if (b) b.addEventListener('click', function () {
    var dark = getComputedStyle(r).getPropertyValue('--bg').trim() === '#0F1316';
    var d = dark ? 'light' : 'dark';
    r.setAttribute('data-theme', d);
    try { localStorage.setItem('theme', d); } catch (e) {}
  });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-track]');
    if (!a || typeof gtag !== 'function') return;
    gtag('event', 'link_click', {
      link_type: a.getAttribute('data-track'),
      project: a.getAttribute('data-project') || '',
      link_url: a.href,
      page_path: location.pathname
    });
  });
  var pdfs = document.querySelectorAll('a[href$=".pdf"]');
  for (var i = 0; i < pdfs.length; i++) pdfs[i].setAttribute('data-track', 'pdf');
})();
