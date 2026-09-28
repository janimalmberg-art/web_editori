    def add_text_frame(self):
        title, ok = QInputDialog.getText(self, 'Tekstikehys', 'Kehyksen otsikko:')
        if not ok:
            return
        content, ok2 = QInputDialog.getMultiLineText(
            self, 'Tekstikehys', 'Kehyksen teksti:', 'Kirjoita teksti tähän...'
        )
        if not ok2:
            return
        out = '<div class="text-frame">\n'
        if title.strip():
            out += '  <div class="frame-title">%s</div>\n' % html_mod.escape(title)
        body = html_mod.escape(content).replace('\n', '<br>')
        out += '  <p>%s</p>\n</div>' % body
        self._insert_html(out)

    def add_object_frame(self):
        title, ok = QInputDialog.getText(
            self, 'Objektikehys', 'Kehyksen otsikko (esim. Kaavio tai esitys):'
        )
        if not ok:
            title = ''
        out = '<div class="object-frame">\n'
        out += '  <div class="frame-title">%s</div>\n' % html_mod.escape(
            title or 'Kaavio / upotettu objekti')
        out += '  <p>Tähän kohtaan voi upottaa kaavion, videon tai muun objektin.</p>\n</div>'
        self._insert_html(out)

    def add_gallery(self):
        dlg = GalleryDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        title, size, urls = dlg.get_data()
        if not urls:
            QMessageBox.information(self, 'Huom', 'Valitse tai syötä vähintään yksi kuva.')
            return
        out = ''
        if title:
            out += '<h3>%s</h3>\n' % html_mod.escape(title)
        out += '<div class="gallery">\n'
        for u in urls:
            u = str(u).strip().replace('"', '&quot;')
            out += ('  <img src="%s" class="%s" alt="Kuva" '
                    'title="Vie hiiri päälle isontaaksesi">\n' % (u, size))
        out += '</div>'
        self._run_js('editorApi.ensureGalleryScript()')
        self._insert_html(out)
        self.statusBar().showMessage('Galleria lisätty – kuvat isontuvat hiiren päällä', 4000)

    def add_calendar(self):
        dlg = CalendarDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        year, month = dlg.get_year_month()
        self._insert_html(self._calendar_html(year, month))

    def _calendar_html(self, year, month):
        months_fi = ['Tammikuu', 'Helmikuu', 'Maaliskuu', 'Huhtikuu', 'Toukokuu',
                     'Kesäkuu', 'Heinäkuu', 'Elokuu', 'Syyskuu', 'Lokakuu',
                     'Marraskuu', 'Joulukuu']
        days = ['Ma', 'Ti', 'Ke', 'To', 'Pe', 'La', 'Su']
        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
        out = ['<div class="calendar">',
               '  <h3>%s %d</h3>' % (months_fi[month - 1], year),
               '  <table>',
               '    <tr>%s</tr>' % ''.join('<th>%s</th>' % d for d in days)]
        for week in weeks:
            cells = ''.join(
                '<td class="empty">&nbsp;</td>' if day == 0 else '<td>&nbsp;</td>'
                for day in week
            )
            out.append('    <tr>%s</tr>' % cells)
        out.append('  </table>')
        out.append('</div>')
        return '\n'.join(out)

    def add_section(self):
        name, ok = QInputDialog.getText(
            self, 'Osio (alasivu)', 'Osion nimi (esim. Tietoja minusta):'
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        base = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'osio'
        anchor, ok2 = QInputDialog.getText(
            self, 'Osio (alasivu)', 'Osion tunniste (näkyy osoitteessa #...):', text=base
        )
        if not ok2 or not anchor.strip():
            return
        anchor = re.sub(r'[^a-zA-Z0-9_-]', '', anchor.strip()) or 'osio'
        out = (
            '<section class="subpage" id="%s">\n'
            '  <h2>%s</h2>\n'
            '  <p>Kirjoita osion sisältö tähän...</p>\n'
            '</section>' % (anchor, html_mod.escape(name))
        )
        self._insert_html(out)
        self._run_js('editorApi.addNavLink(%s, %s)' %
                     (json.dumps(name), json.dumps('#' + anchor)))
        self.statusBar().showMessage('Osio lisätty ja linkki valikkoon', 4000)

    def edit_nav_menu(self):
        def got_links(result):
            try:
                links = json.loads(result) if result else []
            except Exception:
                links = []
            dlg = NavMenuDialog(self, links)
            if dlg.exec_() == QDialog.Accepted:
                items = [[n, u] for n, u in dlg.get_links()]
                self._run_js('editorApi.setNavbar(%s)' % json.dumps(items))
                self.statusBar().showMessage('Valikko päivitetty', 3000)
        self._run_js('editorApi.getNavbar()', got_links)