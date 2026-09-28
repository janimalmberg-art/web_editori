        right_widget = QWidget()
        self.right_widget = right_widget
        right_widget.setMinimumWidth(200)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self._pane_header(
            '👁 Muokkausnäkymä – klikkaa ja kirjoita suoraan! '
            'Klikkaa aluetta valitaksesi sen.', 'view', '#d6e8f8'))
        self.preview = QWebEngineView()
        right_layout.addWidget(self.preview)
        splitter.addWidget(right_widget)
        splitter.setSizes(self._pane_sizes)
        splitter.splitterMoved.connect(self._on_splitter_moved)

        # ---- Tilarivi ----
        self.sel_label = QLabel("Klikkaa kohdetta esikatselusta")
        self.statusBar().addPermanentWidget(self.sel_label)

        # ---- Ajastimet ----
        self._code_timer = QTimer(self)
        self._code_timer.setSingleShot(True)
        self._code_timer.setInterval(700)
        self._code_timer.timeout.connect(self._reload_preview_now)

        # ---- QWebChannel-silta ----
        self.bridge = EditorBridge(self)
        self.bridge.htmlPushed.connect(self.on_preview_html)
        self.bridge.selectionPushed.connect(self.on_selection_info)

        self.web_channel = QWebChannel(self.preview.page())
        self.web_channel.registerObject('bridge', self.bridge)
        self.preview.page().setWebChannel(self.web_channel)

        script = QWebEngineScript()
        script.setName('editor_init')
        script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(False)
        script.setSourceCode(EDITOR_JS)
        self.preview.page().scripts().insert(script)

        self.preview.loadFinished.connect(self.on_load_finished)
        self.preview.page().pdfPrintingFinished.connect(self.on_pdf_finished)

        # ---- Työkalut ja alkusisältö ----
        self.create_actions()
        self.create_menus()
        self.create_view_menu()

        self.editor.setPlainText(self._default_doc())
        self.set_modified(False)
        QTimer.singleShot(300, self.update_preview)