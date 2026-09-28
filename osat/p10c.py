    # ================== TIEDOSTOTOIMINNOT ==================
    def new_page(self):
        if self.modified:
            r = self._confirm_discard()
            if r == 'cancel':
                return
            if r == 'save' and not self._do_save('html'):
                return
        self._set_code_text(self._default_doc())
        self.current_file = None
        self.set_modified(False)
        self.update_preview()
        self.statusBar().showMessage('Uusi sivu luotu', 3000)

    def open_file(self):
        if self.modified:
            r = self._confirm_discard()
            if r == 'cancel':
                return
            if r == 'save' and not self._do_save('html'):
                return
        path, _ = QFileDialog.getOpenFileName(
            self, 'Avaa web-sivu', '',
            'Web-sivut (*.html *.htm *.xhtml *.php);;Kaikki tiedostot (*.*)'
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        except Exception as e:
            QMessageBox.warning(self, 'Virhe', 'Tiedoston avaus epäonnistui:\n%s' % e)
            return
        self._set_code_text(text)
        self.current_file = path
        self.set_modified(False)
        self.update_preview()
        self.statusBar().showMessage('Avattu: %s' % path, 5000)

    def _do_save(self, fmt):
        default = self.current_file or ('sivu.html' if fmt == 'html' else 'sivu.xhtml')
        if fmt == 'html':
            filt = 'HTML-sivu (*.html *.htm)'
        else:
            filt = 'XHTML-sivu (*.xhtml)'
        path, _ = QFileDialog.getSaveFileName(self, 'Tallenna sivu', default, filt)
        if not path:
            return False
        code = self.editor.toPlainText()
        if fmt == 'xhtml':
            code = re.sub(
                r'<(br|hr|img|input|meta|link|source)\b([^>]*?)\s*/?>',
                lambda m: '<%s%s />' % (m.group(1), m.group(2)),
                code
            )
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            QMessageBox.warning(self, 'Virhe', 'Tallennus epäonnistui:\n%s' % e)
            return False
        self.current_file = path
        self.set_modified(False)
        self.statusBar().showMessage('Tallennettu: %s' % path, 5000)
        return True

    def save_html(self):
        self._do_save('html')

    def save_xhtml(self):
        self._do_save('xhtml')

    def save_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Tallenna PDF', 'sivu.pdf', 'PDF-tiedosto (*.pdf)'
        )
        if not path:
            return
        self.statusBar().showMessage('Luodaan PDF-tiedostoa...', 5000)
        self.preview.page().printToPdf(path)

    def on_pdf_finished(self, file_path, ok):
        if ok:
            self.statusBar().showMessage('PDF tallennettu', 5000)
            QMessageBox.information(self, 'PDF valmis',
                                    'PDF-tiedosto tallennettiin:\n%s' % file_path)
        else:
            QMessageBox.warning(self, 'Virhe', 'PDF:n luonti epäonnistui.')

    def closeEvent(self, event):
        if self.modified:
            r = self._confirm_discard()
            if r == 'cancel':
                event.ignore()
                return
            if r == 'save' and not self._do_save('html'):
                event.ignore()
                return
        event.accept()