class NavMenuDialog(QDialog):
    """Ylävalikon linkkien muokkaus: lisää, muokkaa, poista ja järjestä."""
    def __init__(self, parent=None, links=None):
        super().__init__(parent)
        self.setWindowTitle("Muokkaa ylävalikkoa")
        self.resize(540, 400)

        layout = QVBoxLayout(self)
        info = QLabel(
            "Hallitse sivun ylävalikon linkkejä. Nimi näkyy valikossa. "
            "Osoite voi olla esim. https://... tai #-alkuinen kohta samalla sivulla."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        middle = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(QLabel("Valikon linkit:"))
        self.listw = QListWidget()
        self.listw.currentRowChanged.connect(self.load_selected)
        left.addWidget(self.listw)
        middle.addLayout(left, 1)

        right = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("esim. Etusivu")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https:// tai #kohta")
        right.addRow("Nimi:", self.name_edit)
        right.addRow("Osoite:", self.url_edit)

        btn_col = QVBoxLayout()
        self.btn_add = QPushButton("➕ Lisää uusi")
        self.btn_add.clicked.connect(self.add_link)
        btn_col.addWidget(self.btn_add)
        self.btn_update = QPushButton("💾 Päivitä valittu")
        self.btn_update.clicked.connect(self.update_selected)
        btn_col.addWidget(self.btn_update)
        self.btn_remove = QPushButton("🗑 Poista valittu")
        self.btn_remove.clicked.connect(self.remove_selected)
        btn_col.addWidget(self.btn_remove)
        self.btn_up = QPushButton("⬆ Siirrä ylös")
        self.btn_up.clicked.connect(lambda: self.move_item(-1))
        btn_col.addWidget(self.btn_up)
        self.btn_down = QPushButton("⬇ Siirrä alas")
        self.btn_down.clicked.connect(lambda: self.move_item(1))
        btn_col.addWidget(self.btn_down)
        btn_col.addStretch()
        right.addRow(btn_col)
        middle.addLayout(right, 1)

        layout.addLayout(middle)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self._names = []
        self._urls = []
        for name, url in (links or []):
            self._names.append(name)
            self._urls.append(url)
            self.listw.addItem("%s  →  %s" % (name, url))

    def load_selected(self, row):
        if 0 <= row < len(self._names):
            self.name_edit.setText(self._names[row])
            self.url_edit.setText(self._urls[row])

    def add_link(self):
        name = self.name_edit.text().strip() or "Linkki"
        url = self.url_edit.text().strip() or "#"
        self._names.append(name)
        self._urls.append(url)
        self.listw.addItem("%s  →  %s" % (name, url))
        self.name_edit.clear()
        self.url_edit.clear()

    def update_selected(self):
        row = self.listw.currentRow()
        if row < 0:
            return
        name = self.name_edit.text().strip() or "Linkki"
        url = self.url_edit.text().strip() or "#"
        self._names[row] = name
        self._urls[row] = url
        self.listw.item(row).setText("%s  →  %s" % (name, url))

    def remove_selected(self):
        row = self.listw.currentRow()
        if row < 0:
            return
        self._names.pop(row)
        self._urls.pop(row)
        self.listw.takeItem(row)

    def move_item(self, direction):
        row = self.listw.currentRow()
        new_row = row + direction
        if row < 0 or not (0 <= new_row < self.listw.count()):
            return
        item = self.listw.takeItem(row)
        self.listw.insertItem(new_row, item)
        self.listw.setCurrentRow(new_row)
        self._names[row], self._names[new_row] = self._names[new_row], self._names[row]
        self._urls[row], self._urls[new_row] = self._urls[new_row], self._urls[row]

    def get_links(self):
        return list(zip(self._names, self._urls))