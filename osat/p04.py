class GalleryDialog(QDialog):
    """Gallerian luonti: URL-kuvat ja omat kuvatiedostot."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Luo galleria")
        self.resize(560, 500)
        self.data_urls = []

        layout = QVBoxLayout(self)

        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Gallerian otsikko:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("esim. Lomakuvat")
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Esikatselukoko:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["Normaali (160px)", "Pieni (80px)"])
        size_layout.addWidget(self.size_combo)
        size_layout.addStretch()
        layout.addLayout(size_layout)

        group = QGroupBox("Kuvat")
        group_layout = QVBoxLayout(group)

        group_layout.addWidget(QLabel("Internetosoitteet (yksi per rivi):"))
        self.urls_edit = QPlainTextEdit()
        self.urls_edit.setPlaceholderText(
            "https://esimerkki.fi/kuva1.jpg\n"
            "https://esimerkki.fi/kuva2.jpg"
        )
        self.urls_edit.setMaximumHeight(110)
        group_layout.addWidget(self.urls_edit)

        file_btn = QPushButton("📂 Lisää kuvia omalta tietokoneelta...")
        file_btn.clicked.connect(self.add_files)
        group_layout.addWidget(file_btn)

        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(110)
        group_layout.addWidget(self.file_list)

        remove_btn = QPushButton("🗑 Poista valittu tiedosto listasta")
        remove_btn.clicked.connect(self.remove_selected_file)
        group_layout.addWidget(remove_btn)

        layout.addWidget(group)

        info = QLabel(
            "ℹ Omat kuvatiedostot upotetaan suoraan sivutiedostoon "
            "(ei tarvitse erillistä kuvakansiota). Gallerian kuvat isontuvat, "
            "kun hiiri viedään kuvan päälle."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def add_files(self):
        paths, _ = QFileDialog.getOpenNames(
            self, "Valitse kuvat", "",
            "Kuvat (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.svg)"
        )
        for path in paths:
            try:
                with open(path, "rb") as f:
                    data = f.read()
            except Exception as e:
                QMessageBox.warning(self, "Virhe", "Kuvan lukeminen epäonnistui:\n%s" % e)
                continue
            ext = os.path.splitext(path)[1].lower().lstrip(".")
            if ext == "jpg":
                ext = "jpeg"
            mime = {
                "png": "image/png", "jpeg": "image/jpeg", "gif": "image/gif",
                "bmp": "image/bmp", "webp": "image/webp", "svg": "image/svg+xml",
            }.get(ext, "image/png")
            data_url = "data:%s;base64,%s" % (mime, base64.b64encode(data).decode("ascii"))
            self.data_urls.append(data_url)
            self.file_list.addItem(os.path.basename(path))

    def remove_selected_file(self):
        row = self.file_list.currentRow()
        if row >= 0 and row < len(self.data_urls):
            self.data_urls.pop(row)
            self.file_list.takeItem(row)

    def get_data(self):
        title = self.title_input.text().strip()
        size = "small" if self.size_combo.currentIndex() == 1 else "normal"
        urls = [
            line.strip()
            for line in self.urls_edit.toPlainText().splitlines()
            if line.strip()
        ] + self.data_urls
        return title, size, urls


class TableDialog(QDialog):
    """Taulukon luonti."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Luo taulukko")
        self.resize(340, 220)

        form = QFormLayout(self)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 50)
        self.rows_spin.setValue(3)
        form.addRow("Rivit:", self.rows_spin)

        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 10)
        self.cols_spin.setValue(3)
        form.addRow("Sarakkeet:", self.cols_spin)

        self.header_check = QCheckBox("Ensimmäinen rivi on otsikkorivi")
        self.header_check.setChecked(True)
        form.addRow(self.header_check)

        self.caption_edit = QLineEdit()
        self.caption_edit.setPlaceholderText("valinnainen")
        form.addRow("Taulukon otsikko:", self.caption_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        form.addRow(btn_box)

    def get_data(self):
        return (
            self.rows_spin.value(),
            self.cols_spin.value(),
            self.header_check.isChecked(),
            self.caption_edit.text().strip(),
        )