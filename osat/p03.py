# ============================================================
# DIALOGIT
# ============================================================

class PhpScriptDialog(QDialog):
    """PHP-skriptin syöttöikkuna."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PHP-skriptityökalu")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        info = QLabel(
            "Kirjoita PHP-koodi tähän (ilman <?php ja ?> -tageja).\n"
            "Koodi lisätään sivulle ja se toimii, kun sivu ajetaan PHP-palvelimella."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.code_edit = QPlainTextEdit()
        self.code_edit.setPlaceholderText(
            "esim:\n"
            "echo \"<p>Terve maailma!</p>\";\n"
            "$muuttuja = date('Y-m-d');\n"
            "echo \"<p>Tänään on $muuttuja</p>\";"
        )
        layout.addWidget(self.code_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_code(self):
        return self.code_edit.toPlainText()


class ColorPaletteDialog(QDialog):
    """Värikartta tekstin ja elementtien värjäämiseen."""
    PRESET_COLORS = [
        "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#FFFFFF",
        "#FF0000", "#E80000", "#CC0000", "#FF3333", "#FF6666", "#FF9999",
        "#FF6600", "#FF9900", "#FFCC00", "#FFFF00", "#FFFF99", "#FFCC66",
        "#00FF00", "#33CC33", "#009900", "#66CC66", "#99CC99", "#CCFFCC",
        "#0066FF", "#0033CC", "#0099FF", "#6699FF", "#99CCFF", "#CCFFFF",
        "#9900FF", "#6600CC", "#CC00FF", "#9933FF", "#CC66FF", "#FFCCFF",
        "#FF00FF", "#CC00CC", "#990099", "#663366", "#FF3399", "#FF66CC",
        "#8B4513", "#A0522D", "#D2691E", "#CD853F", "#DEB887", "#F5DEB3",
        "#0078D7", "#00B7C3", "#107C10", "#5D5A58", "#444791", "#0099BC",
    ]

    def __init__(self, parent=None, title="Valitse väri"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(470, 400)
        self.selected_color = None

        layout = QVBoxLayout(self)

        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Valittu väri:"))
        self.preview_label = QLabel("     ")
        self.preview_label.setFixedSize(80, 28)
        self.preview_label.setStyleSheet("border: 1px solid #333; background: white;")
        preview_layout.addWidget(self.preview_label)
        self.hex_edit = QLineEdit()
        self.hex_edit.setPlaceholderText("esim. #FF6600")
        preview_layout.addWidget(self.hex_edit)
        layout.addLayout(preview_layout)

        grid_group = QGroupBox("Valmiit värit")
        grid = QGridLayout(grid_group)
        grid.setSpacing(4)
        cols = 9
        for i, color in enumerate(self.PRESET_COLORS):
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setToolTip(color)
            btn.setStyleSheet(
                "QPushButton { background: %s; border: 1px solid #666; border-radius: 2px; }"
                "QPushButton:hover { border: 2px solid #000; }" % color
            )
            btn.clicked.connect(lambda _=False, c=color: self.pick_color(c))
            grid.addWidget(btn, i // cols, i % cols)
        layout.addWidget(grid_group)

        custom_btn = QPushButton("🎨 Mukautettu väri...")
        custom_btn.clicked.connect(self.choose_custom)
        layout.addWidget(custom_btn)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def pick_color(self, color):
        self.selected_color = color
        self.hex_edit.setText(color)
        self.preview_label.setStyleSheet(
            "border: 1px solid #333; background: %s;" % color
        )

    def choose_custom(self):
        color = QColorDialog.getColor(QColor("#0078D7"), self, "Valitse väri")
        if color.isValid():
            self.pick_color(color.name())

    def get_color(self):
        text = self.hex_edit.text().strip()
        if text:
            if not text.startswith("#"):
                text = "#" + text
            if re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", text):
                return text
            return None
        return self.selected_color