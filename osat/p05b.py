class CalendarDialog(QDialog):
    """Kalenterin luonti valitulle kuukaudelle."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Luo kalenteri")
        self.resize(320, 180)

        form = QFormLayout(self)

        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2100)
        self.year_input.setValue(datetime.date.today().year)
        form.addRow("Vuosi:", self.year_input)

        self.month_input = QComboBox()
        for kuukausi in ("Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu",
                         "Toukokuu", "Kesäkuu", "Heinäkuu", "Elokuu",
                         "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"):
            self.month_input.addItem(kuukausi)
        self.month_input.setCurrentIndex(datetime.date.today().month - 1)
        form.addRow("Kuukausi:", self.month_input)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        form.addRow(btn_box)

    def get_year_month(self):
        return self.year_input.value(), self.month_input.currentIndex() + 1


class PageSettingsDialog(QDialog):
    """Sivun perusasetukset: otsikko, värit ja leveys."""
    def __init__(self, parent=None, current_title=""):
        super().__init__(parent)
        self.setWindowTitle("Sivun asetukset")
        self.resize(420, 260)
        self.bg_color = None
        self.txt_color = None

        form = QFormLayout(self)

        self.title_edit = QLineEdit(current_title)
        self.title_edit.setPlaceholderText("esim. Janin kotisivut")
        form.addRow("Sivun otsikko (selaimen välilehti):", self.title_edit)

        bg_row = QHBoxLayout()
        self.bg_preview = QLabel("   ")
        self.bg_preview.setFixedSize(60, 24)
        self.bg_preview.setStyleSheet("border: 1px solid #666; background: white;")
        bg_btn = QPushButton("🎨 Valitse taustaväri...")
        bg_btn.clicked.connect(self.choose_bg)
        bg_row.addWidget(self.bg_preview)
        bg_row.addWidget(bg_btn)
        bg_row.addStretch()
        form.addRow(bg_row)

        txt_row = QHBoxLayout()
        self.txt_preview = QLabel("   ")
        self.txt_preview.setFixedSize(60, 24)
        self.txt_preview.setStyleSheet("border: 1px solid #666; background: white;")
        txt_btn = QPushButton("🎨 Valitse tekstin väri...")
        txt_btn.clicked.connect(self.choose_txt)
        txt_row.addWidget(self.txt_preview)
        txt_row.addWidget(txt_btn)
        txt_row.addStretch()
        form.addRow(txt_row)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 1400)
        self.width_spin.setValue(900)
        self.width_spin.setSuffix(" px")
        form.addRow("Sisällön leveys:", self.width_spin)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        form.addRow(btn_box)

    def choose_bg(self):
        dlg = ColorPaletteDialog(self, "Taustaväri")
        if dlg.exec_() == QDialog.Accepted:
            c = dlg.get_color()
            if c:
                self.bg_color = c
                self.bg_preview.setStyleSheet(
                    "border: 1px solid #666; background: %s;" % c)

    def choose_txt(self):
        dlg = ColorPaletteDialog(self, "Tekstin väri")
        if dlg.exec_() == QDialog.Accepted:
            c = dlg.get_color()
            if c:
                self.txt_color = c
                self.txt_preview.setStyleSheet(
                    "border: 1px solid #666; background: %s;" % c)

    def get_data(self):
        return {
            "title": self.title_edit.text().strip(),
            "bg": self.bg_color or "",
            "txt": self.txt_color or "",
            "maxw": self.width_spin.value(),
        }