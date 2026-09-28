EDITOR_JS_A3 = r"""
  var api = {
    exec: function (cmd, val) {
      try {
        document.body.focus();
        document.execCommand(cmd, false, val || null);
      } catch (e) {}
      notify();
    },
    insert: function (htmlStr) {
      try {
        document.body.focus();
        var ok = document.execCommand('insertHTML', false, htmlStr);
        if (!ok) {
          var target = document.querySelector('.content') || document.body;
          target.insertAdjacentHTML('beforeend', htmlStr);
        }
      } catch (e) {}
      notify();
    },
    insertHeading: function (level, text) {
      var sel = window.getSelection();
      var hasSel = sel && sel.rangeCount > 0 && !sel.isCollapsed;
      if (hasSel) {
        api.exec('formatBlock', '<' + level + '>');
      } else {
        var t = (text && String(text).trim()) ? esc(String(text).trim()) : 'Kirjoita otsikko tähän';
        api.insert('<' + level + '>' + t + '</' + level + '>');
      }
    },
    insertParagraph: function (text) {
      var t = (text && String(text).trim()) ? esc(String(text).trim()) : 'Kirjoita tekstiä tähän...';
      api.insert('<p>' + t + '</p>');
    },
    insertLink: function (text, url) {
      try { document.body.focus(); } catch (e) {}
      var sel = window.getSelection();
      if (sel && sel.rangeCount > 0 && !sel.isCollapsed) {
        try { document.execCommand('createLink', false, url); } catch (e) {}
      } else {
        var t = (text && String(text).trim()) ? esc(String(text).trim()) : esc(url);
        api.insert('<a href="' + String(url).replace(/"/g, '&quot;') + '">' + t + '</a>');
      }
      notify();
    },
    colorBlock: function (prop, val) {
      var b = getBlockEl();
      if (!b) return;
      b.style[prop] = val;
      notify();
    },
"""

EDITOR_JS_A = EDITOR_JS_A1 + EDITOR_JS_A2 + EDITOR_JS_A3