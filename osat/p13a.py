    # ================== IKKUNOINTI (Word-tyyli) ==================
    def _pane_title(self, key):
        return 'HTML-koodi-ikkuna' if key == 'code' else 'Muokkausnäkymä-ikkuna'

    def _pane_widget(self, key):
        return self.left_widget if key == 'code' else self.right_widget

    def _pane_header(self, text, key, bg):
        """Ikkunan otsikkopalkki Word-tyylisillä painikkeilla: ▲ isontaa, _ piilottaa, ✕ sulkee."""
        bar = QWidget()
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: bold; padding: 4px; background: %s;" % bg)
        lay.addWidget(lbl, 1)

        def make_btn(sym, tip, slot):
            b = QToolButton()
            b.setText(sym)
            b.setToolTip(tip)
            b.setAutoRaise(True)
            b.setFixedSize(24, 22)
            b.setStyleSheet("font-weight: bold; background: %s; border: none;" % bg)
            b.clicked.connect(slot)
            lay.addWidget(b)
            return b

        b_max = make_btn(
            '▲', 'Isonta täyteen näkymän (kuten Wordin keskinäppäin)',
            lambda: self.maximize_pane(key))
        b_min = make_btn('_', 'Piilottaa ikkunan taustalle', lambda: self.minimize_pane(key))
        b_cls = make_btn('✕', 'Sulkee ikkunan – avaa uudelleen Näkymä-valikosta',
                         lambda: self.close_pane(key))
        self._pane_hdrs[key] = {'max': b_max}
        return bar

    def _visible_count(self):
        return sum(1 for v in self._pane_state.values() if v != 'hidden')

    def _apply_panes(self):
        st = self._pane_state
        for key in ('code', 'view'):
            w = self._pane_widget(key)
            visible = st[key] != 'hidden'
            if w.isVisible() != visible:
                w.setVisible(visible)
        for key in ('code', 'view'):
            hdr = self._pane_hdrs.get(key)
            if hdr:
                if st[key] == 'max':
                    hdr['max'].setText('▼')
                    hdr['max'].setToolTip('Palauta ikkuna normaaliin kokoon')
                else:
                    hdr['max'].setText('▲')
                    hdr['max'].setToolTip('Isonta täyteen näkymän (kuten Wordin keskinäppäin)')
        if st['code'] == 'max':
            self.splitter.setSizes([99999, 0])
        elif st['view'] == 'max':
            self.splitter.setSizes([0, 99999])
        elif st['code'] != 'hidden' and st['view'] != 'hidden':
            self.splitter.setSizes(self._pane_sizes)

    def maximize_pane(self, key):
        other = 'view' if key == 'code' else 'code'
        st = self._pane_state
        if st[key] == 'max':
            st[key] = 'normal'
            st[other] = self._pane_prev or 'normal'
            self._pane_prev = None
            self.statusBar().showMessage('%s palautettu' % self._pane_title(key), 3000)
        else:
            self._pane_prev = st[other]
            st[key] = 'max'
            st[other] = 'hidden'
            self.statusBar().showMessage('%s iso näytölle – ▼ palauttaa' % self._pane_title(key), 4000)
        self._apply_panes()

    def minimize_pane(self, key):
        self._hide_pane(key, 'piilotettu taustalle')

    def close_pane(self, key):
        self._hide_pane(key, 'suljettu')

    def _hide_pane(self, key, word):
        st = self._pane_state
        if st[key] == 'hidden':
            return
        if self._visible_count() == 1:
            QMessageBox.information(
                self, 'Ikkuna pysyy näkyvissä',
                'Vähintään yhden ikkunan on pysyttävä näkyvissä.\n\n'
                'Avaa piilotettu ikkuna uudelleen Näkymä-valikosta.')
            return
        st[key] = 'hidden'
        self._apply_panes()
        self.statusBar().showMessage(
            '%s %s – avaa uudelleen: Näkymä-valikko' % (self._pane_title(key), word), 5000)

    def show_pane(self, key):
        st = self._pane_state
        other = 'view' if key == 'code' else 'code'
        if st[other] == 'max':
            st[other] = 'normal'
            self._pane_prev = None
        st[key] = 'normal'
        self._apply_panes()
        self.statusBar().showMessage('%s avattu näytölle' % self._pane_title(key), 3000)

    def reset_panes(self):
        self._pane_state = {'code': 'normal', 'view': 'normal'}
        self._pane_prev = None
        self._apply_panes()
        self.statusBar().showMessage('Molemmat ikkunat näkyvät alkuperäisissä koissaan', 4000)

    def _on_splitter_moved(self, pos, index):
        if (self.left_widget.isVisible() and self.right_widget.isVisible()
                and self._pane_state['code'] != 'max' and self._pane_state['view'] != 'max'):
            self._pane_sizes = self.splitter.sizes()

    def create_view_menu(self):
        m = self.menuBar().addMenu('&Näkymä')
        act = m.addAction('Näytä HTML-koodi-ikkuna')
        act.triggered.connect(lambda: self.show_pane('code'))
        act = m.addAction('Näytä muokkausnäkymä-ikkuna')
        act.triggered.connect(lambda: self.show_pane('view'))
        m.addSeparator()
        act = m.addAction('HTML-koodi täyteen näkymän')
        act.triggered.connect(lambda: self.maximize_pane('code'))
        act = m.addAction('Muokkausnäkymä täyteen näkymän')
        act.triggered.connect(lambda: self.maximize_pane('view'))
        m.addSeparator()
        act = m.addAction('Molemmat ikkunat näkyviin (palauta)')
        act.triggered.connect(self.reset_panes)