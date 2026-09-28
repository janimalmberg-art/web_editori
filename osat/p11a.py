    # ================== MUIOKKAUSOPERAATIOT ==================
    def _run_js(self, expression, callback=None):
        js = (
            '(function(){function go(){ return ( ' + expression + ' ); } '
            'if (window.editorApi) { return go(); } '
            'setTimeout(function(){ try { go(); } catch (e) {} }, 200); return null; })()'
        )
        if callback is None:
            self.preview.page().runJavaScript(js)
        else:
            self.preview.page().runJavaScript(js, callback)

    def _insert_html(self, html_str):
        self._run_js('editorApi.insert(%s)' % json.dumps(html_str))

    def fmt(self, cmd, val=None):
        if val is None:
            self._run_js("editorApi.exec('%s')" % cmd)
        else:
            self._run_js("editorApi.exec('%s', %s)" % (cmd, json.dumps(val)))

    def add_heading(self):
        level, ok = QInputDialog.getItem(
            self, 'Otsikko', 'Valitse otsikon taso:',
            ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'], 1, False
        )
        if not ok:
            return
        text, ok2 = QInputDialog.getText(
            self, 'Otsikko',
            'Otsikon teksti (tyhjä = uusi otsikko kohdistimen kohdalle):'
        )
        if not ok2:
            return
        self._run_js('editorApi.insertHeading(%s, %s)' %
                     (json.dumps(level.lower()), json.dumps(text)))

    def add_paragraph(self):
        text, ok = QInputDialog.getMultiLineText(
            self, 'Kappale', 'Kappaleen teksti (tyhjä = tyhjä kappale):', ''
        )
        if not ok:
            return
        self._run_js('editorApi.insertParagraph(%s)' % json.dumps(text))

    def add_link(self):
        text, ok = QInputDialog.getText(
            self, 'Linkki', 'Linkin teksti (tyhjä = käytä esikatselussa valittua tekstiä):'
        )
        if not ok:
            return
        url, ok2 = QInputDialog.getText(
            self, 'Linkki', 'Osoite, johon linkki vie:', text='https://'
        )
        if not ok2 or not url.strip():
            return
        self._run_js('editorApi.insertLink(%s, %s)' %
                     (json.dumps(text), json.dumps(url.strip())))

    def color_text(self):
        dlg = ColorPaletteDialog(self, 'Tekstin väri')
        if dlg.exec_() != QDialog.Accepted:
            return
        color = dlg.get_color()
        if color:
            self.fmt('foreColor', color)

    def color_hilite(self):
        dlg = ColorPaletteDialog(self, 'Tekstin korostusväri')
        if dlg.exec_() != QDialog.Accepted:
            return
        color = dlg.get_color()
        if color:
            self.fmt('hiliteColor', color)

    def color_element(self):
        dlg = ColorPaletteDialog(self, 'Elementin väri')
        if dlg.exec_() != QDialog.Accepted:
            return
        color = dlg.get_color()
        if color:
            self._run_js('editorApi.colorBlock("color", %s)' % json.dumps(color))

    def color_element_background(self):
        dlg = ColorPaletteDialog(self, 'Elementin taustaväri')
        if dlg.exec_() != QDialog.Accepted:
            return
        color = dlg.get_color()
        if color:
            self._run_js('editorApi.colorBlock("backgroundColor", %s)' % json.dumps(color))