    # ================== PHP JA SIVUN ASEETUKSET ==================
    def add_php_script(self):
        dlg = PhpScriptDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        code = dlg.get_code().strip()
        if not code:
            return
        php = '<?php\n' + code + '\n?>'
        page = self.editor.toPlainText()
        low = page.lower()
        if '</body>' in low:
            idx = low.rfind('</body>')
            page = page[:idx] + php + '\n' + page[idx:]
        else:
            page += '\n' + php
        self._set_code_text(page)
        self.set_modified(True)
        self.update_preview()
        QMessageBox.information(
            self, 'PHP lisätty',
            'PHP-skripti lisättiin sivun loppuun.\n\n'
            'Tallenna sivu .php-päätteellä (esim. index.php), '
            'jotta skripti toimii web-palvelimella.'
        )

    def page_settings(self):
        current_title = os.path.basename(self.current_file) if self.current_file else 'Oma sivuni'
        dlg = PageSettingsDialog(self, current_title)
        if dlg.exec_() != QDialog.Accepted:
            return
        opts = dlg.get_data()
        self._run_js('editorApi.pageSettings(%s)' % json.dumps(opts))
        self.set_modified(True)
        self.statusBar().showMessage('Sivun asetukset päivitetty', 3000)

    # ================== SIJOTTELU ==================
    def move_up(self):
        self._run_js('editorApi.move(-1)', self._block_op_cb)

    def move_down(self):
        self._run_js('editorApi.move(1)', self._block_op_cb)

    def duplicate_block(self):
        self._run_js('editorApi.dup()', self._block_op_cb)

    def delete_block(self):
        self._run_js('editorApi.del()', self._block_op_cb)
        self.statusBar().showMessage(
            'Alue poistettu – paina ↶ Kumoa, jos haluat sen takaisin', 4000)

    def _block_op_cb(self, result):
        if result and result != 'ok':
            self.statusBar().showMessage(str(result), 3000)

    # ================== OHJE ==================
    def show_info(self):
        QMessageBox.information(
            self, 'Tietoja',
            'Graafinen web-editori – versio 4.0\n\n'
            'Tehnyt Jani Malmberg\n\n'
            'Ohjelmalla luot kotisivuja ja materiaalia ilman HTML-osaamista:\n'
            'muokkaat suoraan oikean puolen näkymää ja koodi päivittyy itsestään.\n\n'
            'Sivut toimivat yleisimmillä selaimilla\n'
            '(Chrome, Firefox, Edge ja Safari).'
        )

    def show_help(self):
        QMessageBox.information(
            self, 'Ohje',
            'GRAAFINEN WEB-EDITORI – OHJE\n\n'
            'PERUSIDEA\n'
            '• Muokkaa aina oikean puolen näkymää: klikkaa tekstiä ja kirjoita.\n'
            '• Vasemman koodi päivittyy automaattisesti – koodia ei tarvitse osata.\n\n'
            'TEKSTI JA MUOTOILU\n'
            '• Valitse teksti hiirellä → Lihavoi/Kursivoi/Väri/Keskitä -napit toimivat.\n'
            '• Otsikko-napista saat otsikkotason; tyhjä kenttä tekee uuden otsikon.\n\n'
            'SISÄLTÖ\n'
            '• Kuva: lisää kuva tiedostosta (upotetaan sivutiedostoon) tai verkosta.\n'
            '• Taulukko, Video, Tekstikehys, Galleria, Kalenteri – omilla painikkeillaan.\n'
            '• Osio: luo uuden alasivualueen JA linkin ylävalikkoon.\n'
            '• Valikko: lisää, muokkaa, poista ja järjestä ylävalikon linkit.\n\n'
            'SIJOTTELU\n'
            '• Klikkaa aluetta (sininen kehys = valittu).\n'
            '• Siirrä ylös/alas -napeilla, kopioi tai poista alue.\n\n'
            'TALLENNUS\n'
            '• Tiedosto → Tallenna (HTML-kotisivutiedosto).\n'
            '• Tiedosto → Tallenna PDF (tulostettava materiaali).\n\n'
            'KUMOA: nappi ↶ tai Ctrl+Z esikatselussa.'
        )