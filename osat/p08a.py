# ============================================================
# PÄÄIKKUNA
# ============================================================

class EditorBridge(QObject):
    """Silta esikatselusivun JavaScriptin ja Pythonin välillä (QWebChannel)."""
    htmlPushed = pyqtSignal(str)
    selectionPushed = pyqtSignal(str)

    @pyqtSlot(str)
    def pushHtml(self, html):
        self.htmlPushed.emit(html)

    @pyqtSlot(str)
    def pushSelection(self, info):
        self.selectionPushed.emit(info)


TAG_NAMES = {
    'div': 'lohko', 'section': 'osio', 'article': 'artikkeli', 'p': 'kappale',
    'h1': 'otsikko (H1)', 'h2': 'otsikko (H2)', 'h3': 'otsikko (H3)',
    'h4': 'otsikko (H4)', 'h5': 'otsikko (H5)', 'h6': 'otsikko (H6)',
    'ul': 'luettelo', 'ol': 'numeroitu luettelo', 'li': 'listakohde',
    'table': 'taulukko', 'img': 'kuva', 'figure': 'kuva',
    'blockquote': 'lainaus', 'pre': 'esimuotoiltu teksti', 'nav': 'valikko',
    'header': 'yläosa', 'footer': 'alaosa', 'aside': 'sivupaneeli',
    'span': 'teksti', 'a': 'linkki', 'form': 'lomake', 'iframe': 'upotettu sisältö',
}


class HtmlEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graafinen web-editori 4.0 – Tehnyt Jani Malmberg")
        self.resize(1500, 900)

        self.current_file = None
        self.modified = False

        # Synkronoinnin tilat
        self._applying_html = False
        self._reloading = False
        self._reload_queued = False
        self._pending_html = ''
        self._restore_scroll = 0
        self._force_code_update = False

        # Ikkunoiden tilat (Word-tyyli): 'normal' | 'max' | 'hidden'
        self._pane_state = {'code': 'normal', 'view': 'normal'}
        self._pane_hdrs = {}
        self._pane_prev = None
        self._pane_sizes = [640, 860]

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # ---- Yläpalkki ----
        top_bar = QHBoxLayout()
        self.info_label = QLabel(
            "🌐 Web-editori – muokkaa oikealla, koodi vasemmalla päivittyy itsestään"
        )
        self.info_label.setStyleSheet("font-weight: bold; padding: 4px;")
        top_bar.addWidget(self.info_label)
        top_bar.addStretch()
        help_btn = QPushButton("❓ Ohje")
        help_btn.clicked.connect(self.show_help)
        top_bar.addWidget(help_btn)
        main_layout.addLayout(top_bar)

        # ---- splitteri: koodi | muokkausnäkymä (raahattava jakaja) ----
        splitter = QSplitter(Qt.Horizontal)
        self.splitter = splitter
        splitter.setHandleWidth(10)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet(
            "QSplitter::handle { background: #c8d4de; border: 1px solid #aab8c4; }"
            "QSplitter::handle:hover { background: #4a90d9; border-color: #4a90d9; }"
        )
        main_layout.addWidget(splitter)

        left_widget = QWidget()
        self.left_widget = left_widget
        left_widget.setMinimumWidth(160)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self._pane_header(
            '📝 HTML-koodi (päivittyy automaattisesti)', 'code', '#e8e8e8'))
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas", 10))
        self.editor.textChanged.connect(self.on_code_changed)
        left_layout.addWidget(self.editor)
        splitter.addWidget(left_widget)