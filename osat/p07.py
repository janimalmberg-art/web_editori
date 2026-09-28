EDITOR_JS_B = r"""    blockInfo: function () {
      var b = getBlockEl();
      if (!b || b === document.body) return '';
      var info = {
        tag: b.tagName.toLowerCase(),
        id: b.id || '',
        cls: (b.className || '').replace(SEL_CLASS, '').trim(),
        text: (b.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60)
      };
      return JSON.stringify(info);
    },
    move: function (dir) {
      var b = getBlockEl();
      if (!b) return 'Ei valittua aluetta';
      var sib = (dir < 0) ? b.previousElementSibling : b.nextElementSibling;
      if (!sib) return 'Alue on jo reunimmaisena';
      if (dir < 0) b.parentNode.insertBefore(b, sib);
      else b.parentNode.insertBefore(sib, b);
      notify();
      return 'ok';
    },
    del: function () {
      var b = getBlockEl();
      if (!b) return 'Ei valittua aluetta';
      b.parentNode.removeChild(b);
      notify();
      return 'ok';
    },
    dup: function () {
      var b = getBlockEl();
      if (!b) return 'Ei valittua aluetta';
      var c = b.cloneNode(true);
      c.classList.remove(SEL_CLASS);
      b.parentNode.insertBefore(c, b.nextSibling);
      notify();
      return 'ok';
    },
    scrollY: function () { return window.scrollY || 0; },
    setScroll: function (y) { try { window.scrollTo(0, y || 0); } catch (e) {} },
    pageSettings: function (data) {
      try {
        var o = (typeof data === 'string') ? JSON.parse(data) : (data || {});
        if (o.bg === '') document.body.style.removeProperty('background-color');
        else if (o.bg) document.body.style.backgroundColor = o.bg;
        if (o.txt === '') document.body.style.removeProperty('color');
        else if (o.txt) document.body.style.color = o.txt;
        var c = document.querySelector('.content');
        if (c && o.maxw) c.style.maxWidth = o.maxw + 'px';
        if (o.title) document.title = o.title;
        notify();
      } catch (e) {}
    },
    getNavbar: function () {
      var n = document.querySelector('.navbar');
      var out = [];
      if (n) {
        var as = n.querySelectorAll('a');
        for (var i = 0; i < as.length; i++) {
          out.push([as[i].textContent.trim(), as[i].getAttribute('href') || '#']);
        }
      }
      return JSON.stringify(out);
    },
    setNavbar: function (data) {
      var items = [];
      try {
        items = (typeof data === 'string') ? (JSON.parse(data) || []) : (data || []);
      } catch (e) { items = []; }
      var n = document.querySelector('.navbar');
      if (!n) {
        n = document.createElement('div');
        n.className = 'navbar';
        var c = document.querySelector('.content');
        if (c && c.parentNode === document.body) document.body.insertBefore(n, c);
        else document.body.insertBefore(n, document.body.firstChild);
      }
      while (n.firstChild) n.removeChild(n.firstChild);
      for (var i = 0; i < items.length; i++) {
        var a = document.createElement('a');
        a.href = items[i][1] || '#';
        a.textContent = items[i][0] || 'Linkki';
        n.appendChild(a);
      }
      notify();
    },
    addNavLink: function (name, url) {
      var n = document.querySelector('.navbar');
      if (!n) {
        n = document.createElement('div');
        n.className = 'navbar';
        var c = document.querySelector('.content');
        if (c && c.parentNode === document.body) document.body.insertBefore(n, c);
        else document.body.insertBefore(n, document.body.firstChild);
      }
      var a = document.createElement('a');
      a.href = url;
      a.textContent = name;
      n.appendChild(a);
      notify();
    },
    ensureGalleryScript: function () {
      if (!window.toggleGallerySize) {
        var sc = document.createElement('script');
        sc.textContent = "function toggleGallerySize(){var imgs=document.querySelectorAll('.gallery img');imgs.forEach(function(img){if(img.classList.contains('small')){img.classList.remove('small');img.classList.add('normal');}else if(img.classList.contains('normal')){img.classList.remove('normal');img.classList.add('small');}else{img.classList.add('small');}});}";
        document.body.appendChild(sc);
      }
    },
    getHtmlNow: function () { sendHtmlNow(); return true; }
  };
  window.editorApi = api;

  function setup() {
    if (window.__edReady) return;
    window.__edReady = true;
    try { document.execCommand('styleWithCSS', false, true); } catch (e) {}
    initChannel();
    var mo = new MutationObserver(function () { sendHtmlSoon(); });
    try { mo.observe(document.body, { childList: true, subtree: true, characterData: true }); } catch (e) {}
    document.addEventListener('selectionchange', function () {
      clearTimeout(selTimer);
      selTimer = setTimeout(function () {
        highlightBlock();
        sendSelectionNow();
      }, 120);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setup);
  } else {
    setup();
  }
})();
"""

EDITOR_JS = EDITOR_JS_A + EDITOR_JS_B