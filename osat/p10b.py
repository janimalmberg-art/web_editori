    def _reload_preview_now(self):
        if self._reloading:
            self._reload_queued = True
            return
        self._reloading = True
        self._pending_html = self.render_preview(self.editor.toPlainText())
        self.preview.page().runJavaScript('window.scrollY || 0', self._cb_scroll)

    def _cb_scroll(self, y):
        self._restore_scroll = int(y or 0)
        self.preview.setHtml(self._pending_html)

    def on_load_finished(self, ok):
        self._reloading = False
        if self._restore_scroll:
            self.preview.page().runJavaScript(
                'editorApi.setScroll(%d)' % self._restore_scroll
            )
        if self._reload_queued:
            self._reload_queued = False
            QTimer.singleShot(50, self._reload_preview_now)

    def on_selection_info(self, info):
        has = bool(info)
        for key in ('move_up', 'move_down', 'dup', 'del'):
            self.actions[key].setEnabled(has)
        if not has:
            self.sel_label.setText('Ei valintaa – klikkaa kohdetta esikatselussa')
            return
        try:
            d = json.loads(info)
        except Exception:
            d = {}
        name = TAG_NAMES.get(d.get('tag', ''), d.get('tag', ''))
        label = 'Valittu: %s' % (name or 'kohde')
        if d.get('id'):
            label += ' (id=%s)' % d['id']
        if d.get('text'):
            label += ' – "%s"' % d['text'][:40]
        self.sel_label.setText(label)

    def update_preview(self):
        self._code_timer.stop()
        self._reload_preview_now()

    def update_code_from_preview(self):
        self._force_code_update = True
        self.preview.page().runJavaScript('editorApi.getHtmlNow()')

    def set_modified(self, m=True):
        self.modified = m
        title = 'Graafinen web-editori 4.0 – Tehnyt Jani Malmberg'
        if self.current_file:
            title += ' – ' + os.path.basename(self.current_file)
        if self.modified:
            title += ' •'
        self.setWindowTitle(title)

    def _confirm_discard(self):
        btn = QMessageBox.question(
            self, 'Tallentamattomia muutoksia',
            'Sivulla on tallentamattomia muutoksia.\nTallennetaanko ennen jatkamista?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        if btn == QMessageBox.Save:
            return 'save'
        if btn == QMessageBox.Discard:
            return 'discard'
        return 'cancel'