# ============================================================
# MUIOKKAUSNÄKYMÄN TYYLIT JA SILTA (JavaScript) -osa 1
# ============================================================

EDITOR_CSS = """
body { cursor: text; }
.editor-selected {
    outline: 2px solid #0078d7 !important;
    outline-offset: 3px;
    border-radius: 2px;
}
.content > *:hover {
    outline: 1px dashed rgba(0, 120, 215, 0.55);
}
img { max-width: 100%; height: auto; }
"""

EDITOR_JS_A1 = r"""(function () {
  'use strict';
  var SEL_CLASS = 'editor-selected';
  var sendTimer = null, selTimer = null, lastBlock = null;

  function esc(t) {
    return String(t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function initChannel() {
    if (window.__edChanInit) return;
    window.__edChanInit = true;
    var s = document.createElement('script');
    s.src = 'qrc:///qtwebchannel/qwebchannel.js';
    s.onload = function () {
      try {
        new QWebChannel(qt.webChannelTransport, function (ch) {
          window.__edBridge = ch.objects.bridge;
          sendHtmlNow();
          sendSelectionNow();
        });
      } catch (e) {}
    };
    (document.head || document.documentElement).appendChild(s);
  }

  function cleanClone() {
    var root = document.documentElement.cloneNode(true);
    var junk = root.querySelectorAll('[data-editor]');
    for (var i = 0; i < junk.length; i++) {
      if (junk[i].parentNode) junk[i].parentNode.removeChild(junk[i]);
    }
    var marked = root.querySelectorAll('.' + SEL_CLASS);
    for (var j = 0; j < marked.length; j++) {
      marked[j].classList.remove(SEL_CLASS);
    }
    var b = root.querySelector('body');
    if (b) b.removeAttribute('contenteditable');
    return root;
  }

  function sendHtmlNow() {
    var bridge = window.__edBridge;
    if (!bridge) return;
    var dt = document.doctype ? '<!DOCTYPE ' + document.doctype.name + '>\n' : '';
    try { bridge.pushHtml(dt + cleanClone().outerHTML); } catch (e) {}
  }
  function sendHtmlSoon() {
    clearTimeout(sendTimer);
    sendTimer = setTimeout(sendHtmlNow, 300);
  }

  function sendSelectionNow() {
    var bridge = window.__edBridge;
    if (!bridge) return;
    var info = '';
    try { info = window.editorApi.blockInfo(); } catch (e) {}
    try { bridge.pushSelection(info || ''); } catch (e) {}
  }
  function sendSelectionSoon() {
    clearTimeout(selTimer);
    selTimer = setTimeout(sendSelectionNow, 120);
  }
"""

EDITOR_JS_A2 = r"""
  function getBlockEl() {
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return null;
    var node = sel.anchorNode;
    if (!node) return null;
    var el = (node.nodeType === 3) ? node.parentElement : (node.nodeType === 1 ? node : null);
    if (!el || el === document.body) return null;
    while (el && el !== document.body) {
      var p = el.parentElement;
      if (!p) return null;
      if (p === document.body || (p.classList && p.classList.contains('content'))) return el;
      el = p;
    }
    return null;
  }

  function highlightBlock() {
    var b = getBlockEl();
    if (lastBlock && lastBlock !== b) {
      lastBlock.classList.remove(SEL_CLASS);
      lastBlock = null;
    }
    if (b && b !== document.body) {
      b.classList.add(SEL_CLASS);
      lastBlock = b;
    }
    return b || null;
  }

  function notify() {
    sendHtmlSoon();
    sendSelectionSoon();
  }
"""