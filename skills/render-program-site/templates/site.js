/* render-program-site shared behaviors (lifted from the frozen comps).
 * Deterministic chrome JS: nav shadow on scroll, scroll-spy active nav link,
 * and the portfolio-map hover/focus trace that draws edge lines between a node
 * and the nodes it expresses (solid) or influences (dashed). Data-driven from
 * the data-exp / data-inf / data-exp-by / data-inf-by attributes the generator
 * emits on each map node. No client content, no analytics. */
(function () {
  var nav = document.querySelector('nav');
  if (nav) { window.addEventListener('scroll', function () { nav.classList.toggle('scrolled', window.scrollY > 8); }); }

  var secs = Array.prototype.slice.call(document.querySelectorAll('section[id]'));
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
  if (links.length) {
    window.addEventListener('scroll', function () {
      var cur = '';
      secs.forEach(function (s) { if (window.scrollY >= s.offsetTop - 130) cur = s.id; });
      links.forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + cur); });
    });
  }

  var svg = document.getElementById('pf-map');
  if (svg) {
    var linkG = document.getElementById('pf-links');
    var nodes = Array.prototype.slice.call(svg.querySelectorAll('.pf-node'));
    var map = {};
    nodes.forEach(function (n) {
      var dot = n.querySelector('.pf-dot');
      map[n.dataset.node] = { el: n, cx: +dot.getAttribute('cx'), cy: +dot.getAttribute('cy') };
    });
    function rel(n) {
      function g(k) { return n.dataset[k] ? n.dataset[k].split(' ').filter(Boolean) : []; }
      return { solid: g('exp').concat(g('expBy')), dashed: g('inf').concat(g('infBy')) };
    }
    function draw(here, id, cls) {
      var t = map[id]; if (!t) return;
      t.el.classList.add('lit');
      var ln = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      ln.setAttribute('x1', here.cx); ln.setAttribute('y1', here.cy);
      ln.setAttribute('x2', t.cx); ln.setAttribute('y2', t.cy);
      ln.setAttribute('class', cls);
      linkG.appendChild(ln);
    }
    function enter(n) {
      svg.classList.add('pf-focus');
      n.classList.add('lit');
      var here = map[n.dataset.node];
      var r = rel(n);
      r.solid.forEach(function (id) { draw(here, id, 'pf-link'); });
      r.dashed.forEach(function (id) { draw(here, id, 'pf-link-soft'); });
    }
    function leave() {
      svg.classList.remove('pf-focus');
      nodes.forEach(function (n) { n.classList.remove('lit'); });
      while (linkG.firstChild) linkG.removeChild(linkG.firstChild);
    }
    var active = null;
    function refresh(node) {
      if (node === active) return;
      if (active) { leave(); }
      active = node;
      if (node) { enter(node); }
    }
    function nodeFrom(e) {
      var t = e.target;
      var n = (t && t.closest) ? t.closest('.pf-node') : null;
      return (n && svg.contains(n)) ? n : null;
    }
    svg.addEventListener('pointermove', function (e) { refresh(nodeFrom(e)); });
    svg.addEventListener('pointerleave', function () { refresh(null); });
    svg.addEventListener('focusin', function (e) { refresh(nodeFrom(e)); });
    svg.addEventListener('focusout', function () { refresh(null); });
  }
})();
