    # ================== SYNKRONOINTI ==================
    def _default_doc(self):
        return BASE_TEMPLATE.replace('@TITLE@', 'Oma sivuni').replace('@CONTENT@', '')

    def render_preview(self, code):
        html = code

        def php_to_placeholder(m):
            b64 = base64.b64encode(m.group(0).encode('utf-8')).decode('ascii')
            return (
                '<div data-php-b64="' + b64 + '" style="display:none;">'
                '<span style="color:#888;">🐘 PHP-skripti (muokataan koodipuolella)</span></div>'
            )

        html = re.sub(r'<\?php.*?\?>', php_to_placeholder, html, flags=re.S | re.I)

        if '<body' in html.lower() and 'contenteditable' not in html.lower():
            html = re.sub(r'<body\b', '<body contenteditable="true"', html, count=1, flags=re.I)

        css = '<style data-editor="1">' + EDITOR_CSS + '</style>'
        head_idx = html.lower().find('</head>')
        if head_idx != -1:
            html = html[:head_idx] + css + html[head_idx:]
        else:
            html = css + html

        js = '<script data-editor="1">' + EDITOR_JS + '</script>'
        body_idx = html.lower().rfind('</body>')
        if body_idx != -1:
            html = html[:body_idx] + js + html[body_idx:]
        else:
            html = html + js

        return html

    def restore_php(self, html):
        def from_placeholder(m):
            try:
                return base64.b64decode(m.group(1).encode('ascii')).decode('utf-8', 'replace')
            except Exception:
                return ''

        html = re.sub(
            r'<div[^>]*\bdata-php-b64="([^"]*)"[^>]*>.*?</div>',
            from_placeholder, html, flags=re.S
        )
        html = re.sub(r'\s*contenteditable="(?:true|)"', '', html)
        return html

    def on_preview_html(self, raw_html):
        if self._reloading:
            return
        if self.editor.hasFocus() and not self._force_code_update:
            return
        if self._force_code_update:
            self._force_code_update = False
        html = self.restore_php(raw_html)
        if html == self.editor.toPlainText():
            return
        self._set_code_text(html)
        self.set_modified(True)
        self.statusBar().showMessage('Koodi päivittyi esikatselun muutoksista', 2000)

    def _set_code_text(self, text):
        self._applying_html = True
        cursor = self.editor.textCursor()
        pos = cursor.position()
        self.editor.setPlainText(text)
        try:
            pos = max(0, min(pos, len(self.editor.toPlainText())))
            c = self.editor.textCursor()
            c.setPosition(pos)
            self.editor.setTextCursor(c)
        except Exception:
            pass
        self._applying_html = False

    def on_code_changed(self):
        if self._applying_html:
            return
        self.set_modified(True)
        self._code_timer.start()