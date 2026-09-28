# -*- coding: utf-8 -*-
"""
Graafinen web-editori (versio 4.0)
=================================

Täysi WYSIWYG-webeditori, joka on tehty ihmiselle, joka ei osaa HTML-koodia:

* Oikea ikkuna on oikea graafinen muokkausnäkymä: klikkaa ja kirjoita suoraan,
  lisää otsikoita, kuvia, linkkejä, taulukoita, gallerioita ja osioita.
* Vasen ikkuna näyttää HTML-koodin ja päivittyy REAALIAJASSA, kun muokkaat
  oikean puolen näkymää. Koodin muokkaaminen päivittyy myös esikatseluun.
* Alueita voi siirtää ylös/alas, kopioida ja poistaa hiirellä valiten.
* Ylävalikkoa voi muokata graafisesti ja alasivuista saa automaattisesti
  linkin valikkoon.
* Tallennus HTML-, XHTML- ja PDF-muotoon.

Tehnyt Jani Malmberg
"""

import sys
import os
import re
import json
import time
import base64
import calendar
import datetime
import traceback
import html as html_mod

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QAction, QFileDialog, QSplitter, QPushButton,
    QColorDialog, QInputDialog, QMessageBox, QLabel, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDialog, QDialogButtonBox,
    QGroupBox, QGridLayout, QListWidget, QCheckBox, QToolBar, QToolButton,
    QShortcut
)
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSlot, pyqtSignal, QEvent
from PyQt5.QtGui import QColor, QFont, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
from PyQt5.QtWebChannel import QWebChannel


# ============================================================
# SIVUN PERUSTAATTI
# ============================================================

BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="fi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@TITLE@</title>
<style>
* {
    box-sizing: border-box;
}
body {
    font-family: Arial, Helvetica, sans-serif;
    margin: 20px;
    background-color: #f9f9f9;
    color: #333;
}
/* ---- Navigointipalkki ---- */
.navbar {
    background-color: #333;
    overflow: hidden;
    border-radius: 4px;
}
.navbar a {
    float: left;
    display: block;
    color: #f2f2f2;
    text-align: center;
    padding: 14px 16px;
    text-decoration: none;
    transition: background 0.2s;
}
.navbar a:hover {
    background-color: #ddd;
    color: black;
}
/* ---- Galleria ---- */
.gallery {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 10px 0;
}
.gallery img {
    transition: transform 0.2s ease-in-out;
    border: 2px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
}
.gallery img.small {
    width: 80px;
    height: 80px;
    object-fit: cover;
}
.gallery img.normal {
    width: 160px;
    height: 160px;
    object-fit: cover;
}
.gallery img:hover {
    transform: scale(2.0);
    z-index: 10;
    border-color: #0078d7;
}
/* ---- Kuvakehys ---- */
.image-frame {
    border: 2px solid #0078d7;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
    display: inline-block;
    background: #fff;
    max-width: 100%;
}
.image-frame img {
    max-width: 100%;
    height: auto;
    display: block;
}
.image-frame .frame-caption {
    text-align: center;
    font-style: italic;
    margin-top: 6px;
    color: #666;
}
"""
BASE_TEMPLATE += """/* ---- Tekstikehys ---- */
.text-frame {
    border: 1px solid #aaa;
    padding: 15px;
    margin: 10px 0;
    border-radius: 4px;
    background: #fff;
    line-height: 1.6;
}
.text-frame .frame-title {
    font-weight: bold;
    font-size: 1.1em;
    margin-bottom: 8px;
    border-bottom: 1px solid #eee;
    padding-bottom: 4px;
}
/* ---- Objektikehys (kaavio / upotettu objekti) ---- */
.object-frame {
    border: 2px dashed #666;
    padding: 15px;
    margin: 10px 0;
    border-radius: 4px;
    background: #fafafa;
}
.object-frame .frame-title {
    font-weight: bold;
    font-size: 1.1em;
    margin-bottom: 8px;
}
/* ---- Kalenteri ---- */
.calendar {
    border: 1px solid #ccc;
    padding: 15px;
    display: inline-block;
    border-radius: 4px;
    background: #fff;
}
.calendar h3 {
    margin-top: 0;
    text-align: center;
}
.calendar table {
    border-collapse: collapse;
}
.calendar th {
    background-color: #0078d7;
    color: white;
    padding: 8px 12px;
    text-align: center;
}
.calendar td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: center;
    width: 50px;
    height: 40px;
}
.calendar td.empty {
    background-color: #f0f0f0;
}
/* ---- Alasivu / osio ---- */
.subpage {
    border-left: 4px solid #0078d7;
    padding: 10px 15px;
    margin: 20px 0;
    background: #fff;
    border-radius: 0 4px 4px 0;
}
/* ---- Taulukko ---- */
.data-table {
    border-collapse: collapse;
    margin: 10px 0;
}
.data-table th,
.data-table td {
    border: 1px solid #999;
    padding: 8px 12px;
}
.data-table th {
    background-color: #0078d7;
    color: #fff;
}
.data-table tr:nth-child(even) td {
    background-color: #f2f7fc;
}
/* ---- Video ---- */
.video-embed {
    margin: 10px 0;
}
.video-embed iframe {
    max-width: 100%;
    border: 0;
    border-radius: 4px;
}
/* ---- Lainaus ---- */
blockquote {
    border-left: 4px solid #0078d7;
    padding: 8px 16px;
    margin: 10px 0;
    background: #eef5fc;
    color: #444;
    font-style: italic;
    border-radius: 0 4px 4px 0;
}
/* ---- Yleiset ---- */
h1, h2, h3 {
    color: #222;
}
.content a {
    color: #0066cc;
}
.center {
    text-align: center;
}
.content {
    max-width: 900px;
    margin: 0 auto;
}
</style>
</head>
<body>

<div class="navbar">
  <a href="#">Etusivu</a>
</div>

<div class="content">
  <h1>Sivun otsikko</h1>
  <p>Klikkaa tätä tekstiä ja kirjoita suoraan – muokkaus onnistuu ilman koodaamista.</p>
@CONTENT@
</div>

</body>
</html>
"""
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
# ============================================================
# MUIOKKAUSNÄKYMÄN TYYLIT JA SILTA (JavaScript) -osa 1
# ============================================================

EDITOR_CSS = """
body { cursor: text; }
.editor-selected {
    outline: 2px solid #0078d7 !important;
    outline-offset: 3px;
    border-radius: 2px;
}
.content > *:hover {
    outline: 1px dashed rgba(0, 120, 215, 0.55);
}
img { max-width: 100%; height: auto; }

/* ---- Aina näkyvä vierintäpalkki (kuten koodi-ikkunassa) ----
   Näkyy muokkausnäkymässä ja kokonäkymässä silloinkin, kun sivu
   mahtuu ikkunaan – palkkia voi raahata hiirellä. */
html { overflow-y: scroll; }
::-webkit-scrollbar { width: 14px; height: 14px; }
::-webkit-scrollbar-track {
    background: #e9e9e9;
    border-left: 1px solid #d3d3d3;
}
::-webkit-scrollbar-thumb {
    background: #8fa0b3;
    border: 2px solid #e9e9e9;
    border-radius: 7px;
}
::-webkit-scrollbar-thumb:hover { background: #5f7186; }
::-webkit-scrollbar-corner { background: #e9e9e9; }
"""

EDITOR_JS_A1 = r"""(function () {
  'use strict';
  var SEL_CLASS = 'editor-selected';
  var sendTimer = null, selTimer = null, lastBlock = null;

  function esc(t) {
    return String(t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function initChannel() {
    if (window.__edChanInit) return;
    window.__edChanInit = true;
    var s = document.createElement('script');
    s.src = 'qrc:///qtwebchannel/qwebchannel.js';
    s.onload = function () {
      try {
        new QWebChannel(qt.webChannelTransport, function (ch) {
          window.__edBridge = ch.objects.bridge;
          sendHtmlNow();
          sendSelectionNow();
        });
      } catch (e) {}
    };
    (document.head || document.documentElement).appendChild(s);
  }

  function cleanClone() {
    var root = document.documentElement.cloneNode(true);
    var junk = root.querySelectorAll('[data-editor]');
    for (var i = 0; i < junk.length; i++) {
      if (junk[i].parentNode) junk[i].parentNode.removeChild(junk[i]);
    }
    var marked = root.querySelectorAll('.' + SEL_CLASS);
    for (var j = 0; j < marked.length; j++) {
      marked[j].classList.remove(SEL_CLASS);
    }
    var b = root.querySelector('body');
    if (b) b.removeAttribute('contenteditable');
    return root;
  }

  function sendHtmlNow() {
    var bridge = window.__edBridge;
    if (!bridge) return;
    var dt = document.doctype ? '<!DOCTYPE ' + document.doctype.name + '>\n' : '';
    try { bridge.pushHtml(dt + cleanClone().outerHTML); } catch (e) {}
  }
  function sendHtmlSoon() {
    clearTimeout(sendTimer);
    sendTimer = setTimeout(sendHtmlNow, 300);
  }

  function sendSelectionNow() {
    var bridge = window.__edBridge;
    if (!bridge) return;
    var info = '';
    try { info = window.editorApi.blockInfo(); } catch (e) {}
    try { bridge.pushSelection(info || ''); } catch (e) {}
  }
  function sendSelectionSoon() {
    clearTimeout(selTimer);
    selTimer = setTimeout(sendSelectionNow, 120);
  }
"""

EDITOR_JS_A2 = r"""
  function getBlockEl() {
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return null;
    var node = sel.anchorNode;
    if (!node) return null;
    var el = (node.nodeType === 3) ? node.parentElement : (node.nodeType === 1 ? node : null);
    if (!el || el === document.body) return null;
    while (el && el !== document.body) {
      var p = el.parentElement;
      if (!p) return null;
      if (p === document.body || (p.classList && p.classList.contains('content'))) return el;
      el = p;
    }
    return null;
  }

  function highlightBlock() {
    var b = getBlockEl();
    if (lastBlock && lastBlock !== b) {
      lastBlock.classList.remove(SEL_CLASS);
      lastBlock = null;
    }
    if (b && b !== document.body) {
      b.classList.add(SEL_CLASS);
      lastBlock = b;
    }
    return b || null;
  }

  function notify() {
    sendHtmlSoon();
    sendSelectionSoon();
  }
"""
EDITOR_JS_A3 = r"""
  var api = {
    exec: function (cmd, val) {
      try {
        document.body.focus();
        document.execCommand(cmd, false, val || null);
      } catch (e) {}
      notify();
    },
    insert: function (htmlStr) {
      try {
        document.body.focus();
        var ok = document.execCommand('insertHTML', false, htmlStr);
        if (!ok) {
          var target = document.querySelector('.content') || document.body;
          target.insertAdjacentHTML('beforeend', htmlStr);
        }
      } catch (e) {}
      notify();
    },
    insertHeading: function (level, text) {
      var sel = window.getSelection();
      var hasSel = sel && sel.rangeCount > 0 && !sel.isCollapsed;
      if (hasSel) {
        api.exec('formatBlock', '<' + level + '>');
      } else {
        var t = (text && String(text).trim()) ? esc(String(text).trim()) : 'Kirjoita otsikko tähän';
        api.insert('<' + level + '>' + t + '</' + level + '>');
      }
    },
    insertParagraph: function (text) {
      var t = (text && String(text).trim()) ? esc(String(text).trim()) : 'Kirjoita tekstiä tähän...';
      api.insert('<p>' + t + '</p>');
    },
    insertLink: function (text, url) {
      try { document.body.focus(); } catch (e) {}
      var sel = window.getSelection();
      if (sel && sel.rangeCount > 0 && !sel.isCollapsed) {
        try { document.execCommand('createLink', false, url); } catch (e) {}
      } else {
        var t = (text && String(text).trim()) ? esc(String(text).trim()) : esc(url);
        api.insert('<a href="' + String(url).replace(/"/g, '&quot;') + '">' + t + '</a>');
      }
      notify();
    },
    colorBlock: function (prop, val) {
      var b = getBlockEl();
      if (!b) return;
      b.style[prop] = val;
      notify();
    },
"""

EDITOR_JS_A = EDITOR_JS_A1 + EDITOR_JS_A2 + EDITOR_JS_A3
EDITOR_JS_B = r"""    blockInfo: function () {
      var b = getBlockEl();
      if (!b || b === document.body) return '';
      var info = {
        tag: b.tagName.toLowerCase(),
        id: b.id || '',
        cls: (b.className || '').replace(SEL_CLASS, '').trim(),
        text: (b.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60)
      };
      return JSON.stringify(info);
    },
    move: function (dir) {
      var b = getBlockEl();
      if (!b) return 'Ei valittua aluetta';
      var sib = (dir < 0) ? b.previousElementSibling : b.nextElementSibling;
      if (!sib) return 'Alue on jo reunimmaisena';
      if (dir < 0) b.parentNode.insertBefore(b, sib);
      else b.parentNode.insertBefore(sib, b);
      notify();
      return 'ok';
    },
    del: function () {
      var b = getBlockEl();
      if (!b) return 'Ei valittua aluetta';
      b.parentNode.removeChild(b);
      notify();
      return 'ok';
    },
    dup: function () {
      var b = getBlockEl();
      if (!b) return 'Ei valittua aluetta';
      var c = b.cloneNode(true);
      c.classList.remove(SEL_CLASS);
      b.parentNode.insertBefore(c, b.nextSibling);
      notify();
      return 'ok';
    },
    scrollY: function () { return window.scrollY || 0; },
    setScroll: function (y) { try { window.scrollTo(0, y || 0); } catch (e) {} },
    pageSettings: function (data) {
      try {
        var o = (typeof data === 'string') ? JSON.parse(data) : (data || {});
        if (o.bg === '') document.body.style.removeProperty('background-color');
        else if (o.bg) document.body.style.backgroundColor = o.bg;
        if (o.txt === '') document.body.style.removeProperty('color');
        else if (o.txt) document.body.style.color = o.txt;
        var c = document.querySelector('.content');
        if (c && o.maxw) c.style.maxWidth = o.maxw + 'px';
        if (o.title) document.title = o.title;
        notify();
      } catch (e) {}
    },
    getNavbar: function () {
      var n = document.querySelector('.navbar');
      var out = [];
      if (n) {
        var as = n.querySelectorAll('a');
        for (var i = 0; i < as.length; i++) {
          out.push([as[i].textContent.trim(), as[i].getAttribute('href') || '#']);
        }
      }
      return JSON.stringify(out);
    },
    setNavbar: function (data) {
      var items = [];
      try {
        items = (typeof data === 'string') ? (JSON.parse(data) || []) : (data || []);
      } catch (e) { items = []; }
      var n = document.querySelector('.navbar');
      if (!n) {
        n = document.createElement('div');
        n.className = 'navbar';
        var c = document.querySelector('.content');
        if (c && c.parentNode === document.body) document.body.insertBefore(n, c);
        else document.body.insertBefore(n, document.body.firstChild);
      }
      while (n.firstChild) n.removeChild(n.firstChild);
      for (var i = 0; i < items.length; i++) {
        var a = document.createElement('a');
        a.href = items[i][1] || '#';
        a.textContent = items[i][0] || 'Linkki';
        n.appendChild(a);
      }
      notify();
    },
    addNavLink: function (name, url) {
      var n = document.querySelector('.navbar');
      if (!n) {
        n = document.createElement('div');
        n.className = 'navbar';
        var c = document.querySelector('.content');
        if (c && c.parentNode === document.body) document.body.insertBefore(n, c);
        else document.body.insertBefore(n, document.body.firstChild);
      }
      var a = document.createElement('a');
      a.href = url;
      a.textContent = name;
      n.appendChild(a);
      notify();
    },
    ensureGalleryScript: function () {
      if (!window.toggleGallerySize) {
        var sc = document.createElement('script');
        sc.textContent = "function toggleGallerySize(){var imgs=document.querySelectorAll('.gallery img');imgs.forEach(function(img){if(img.classList.contains('small')){img.classList.remove('small');img.classList.add('normal');}else if(img.classList.contains('normal')){img.classList.remove('normal');img.classList.add('small');}else{img.classList.add('small');}});}";
        document.body.appendChild(sc);
      }
    },
    getHtmlNow: function () { sendHtmlNow(); return true; }
  };
  window.editorApi = api;

  function setup() {
    if (window.__edReady) return;
    window.__edReady = true;
    try { document.execCommand('styleWithCSS', false, true); } catch (e) {}
    initChannel();
    var mo = new MutationObserver(function () { sendHtmlSoon(); });
    try { mo.observe(document.body, { childList: true, subtree: true, characterData: true }); } catch (e) {}
    document.addEventListener('selectionchange', function () {
      clearTimeout(selTimer);
      selTimer = setTimeout(function () {
        highlightBlock();
        sendSelectionNow();
      }, 120);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setup);
  } else {
    setup();
  }
})();
"""

EDITOR_JS = EDITOR_JS_A + EDITOR_JS_B
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


class KokosivuIkkuna(QMainWindow):
    """Koko nettisivu omassa ikkunassaan ruudun keskellä.

    Pääohjelma jää taustalle toimimaan tavallisena ikkunana. Ikkunoiden
    välillä voi liikkua vapaasti tehtäväpalkin tai Alt+Tab:n avulla, ja
    ESC tai "Valmis"-painike palauttaa pääohjelman muokkausnäkymään.
    Muokkaukset tässä ikkunassa tallentuvat samaan sivuun kuin
    pääikkunassa (synkronointi molempiin suuntiin).
    """

    def __init__(self, editori):
        super().__init__(None)  # itsenäinen ikkuna: oma tehtäväpalkkimerkki
        self.editori = editori
        self.setWindowTitle('Koko sivu – kokonäkymä')
        self.resize(1100, 820)
        self.setMinimumSize(480, 360)

        self._reloading = False
        self._reload_queued = False
        self._pending_html = ''
        self._restore_scroll = 0
        self._viime_lataus = 0.0

        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        palkki = QHBoxLayout()
        palkki.setContentsMargins(8, 4, 8, 4)
        info = QLabel(
            '🖥 Koko nettisivu – muokkaa suoraan sivulla. '
            'Pääohjelma jatkaa taustalla (Alt+Tab tai tehtäväpalkki).')
        palkki.addWidget(info)
        palkki.addStretch()
        btn_paivita = QPushButton('🔄 Päivitä')
        btn_paivita.clicked.connect(lambda: self.editori.paivita_kokosivu())
        palkki.addWidget(btn_paivita)
        btn_valmis = QPushButton('✔ Valmis – takaisin pääohjelmaan')
        btn_valmis.setStyleSheet('font-weight: bold;')
        btn_valmis.clicked.connect(self.sulje_ja_palaa)
        palkki.addWidget(btn_valmis)
        lay.addLayout(palkki)

        self.view = QWebEngineView()
        lay.addWidget(self.view, 1)

        # Oma silta ja kanava tälle ikkunalle
        self.bridge = EditorBridge(self)
        self.bridge.htmlPushed.connect(self.editori.on_kokosivu_html)
        self.bridge.selectionPushed.connect(self._nayta_valinta)
        self.web_channel = QWebChannel(self.view.page())
        self.web_channel.registerObject('bridge', self.bridge)
        self.view.page().setWebChannel(self.web_channel)

        script = QWebEngineScript()
        script.setName('editor_init_koko')
        script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(False)
        script.setSourceCode(EDITOR_JS)
        self.view.page().scripts().insert(script)

        self.view.loadFinished.connect(self.on_load_finished)

        esc = QShortcut(QKeySequence('Escape'), self)
        esc.activated.connect(self.sulje_ja_palaa)

        self.statusBar().showMessage(
            'Vinkki: ESC tai "Valmis" palaa pääohjelmaan.')

    # ---- sisällön lataus (säilyttää vierityspaikan) ----
    def lataa(self, html):
        if self._reloading:
            self._reload_queued = True
            self._pending_html = html
            return
        self._reloading = True
        self._pending_html = html
        self.view.page().runJavaScript('window.scrollY || 0', self._cb_scroll)

    def _cb_scroll(self, y):
        self._restore_scroll = int(y or 0)
        self.view.setHtml(self._pending_html)

    def on_load_finished(self, ok):
        self._reloading = False
        self._viime_lataus = time.perf_counter()
        if self._restore_scroll:
            self.view.page().runJavaScript(
                'editorApi.setScroll(%d)' % self._restore_scroll)
        if self._reload_queued:
            self._reload_queued = False
            QTimer.singleShot(50, lambda: self.lataa(self._pending_html))

    def _nayta_valinta(self, info):
        try:
            d = json.loads(info) if info else {}
        except Exception:
            d = {}
        if not d:
            return
        nimi = TAG_NAMES.get(d.get('tag', ''), d.get('tag', ''))
        teksti = 'Valittu kokonäkymässä: %s' % (nimi or 'kohde')
        if d.get('text'):
            teksti += ' – "%s"' % d['text'][:40]
        self.statusBar().showMessage(teksti, 4000)

    def sulje_ja_palaa(self):
        self.hide()
        self.editori.kokonakyma_suljettu()

    def closeEvent(self, event):
        event.accept()
        self.editori.kokonakyma_suljettu()


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

        # Kokonäkymäikkuna (koko nettisivu omassa ikkunassaan)
        self.kokosivu = None
        self._koko_muokkaus_aika = 0.0

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
        # kun käyttäjä palaa pääikkunaan kokonäkymän ollessa auki,
        # esikatselu virkistetään kokonäkymän muutoksilla
        QApplication.instance().focusChanged.connect(self._on_app_focus_changed)

        # ---- Kelluvat ikkunat: vaihto hiirellä ----
        # Hiiri kelluvan ikkunan päälle nostaa sen muiden joukosta
        # päällimmäiseksi (pieni viive, näppäimistöfokus ei siirry);
        # vasen hiirinäppäin avaa (aktivoi) ikkunan tavalliseen tapaan.
        self._hiirivaihto = True
        self._hover_kohde = None
        self._hover_ajastin = QTimer(self)
        self._hover_ajastin.setSingleShot(True)
        self._hover_ajastin.setInterval(350)
        self._hover_ajastin.timeout.connect(self._hover_nosta)
        QApplication.instance().installEventFilter(self)

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
    # ================== TOIMINNOT ==================
    def create_actions(self):
        A = {}

        def mk(key, text, slot, shortcut=None):
            action = QAction(text, self)
            action.triggered.connect(slot)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            A[key] = action
            return action

        mk('new', '🆕 Uusi', self.new_page, 'Ctrl+N')
        mk('open', '📂 Avaa', self.open_file, 'Ctrl+O')
        mk('save', '💾 Tallenna', self.save_html, 'Ctrl+S')
        mk('save_xhtml', '💾 XHTML', self.save_xhtml, 'Ctrl+Shift+S')
        mk('save_pdf', '📄 PDF', self.save_pdf, 'Ctrl+P')
        mk('exit', '❌ Sulje', self.close, 'Ctrl+Q')

        mk('undo', '↶ Kumoa', lambda: self.fmt('undo'))
        mk('redo', '↷ Uudelleen', lambda: self.fmt('redo'))
        mk('clear_format', '🧹 Muotoilu pois', lambda: self.fmt('removeFormat'))

        mk('heading', '📝 Otsikko', self.add_heading, 'Ctrl+H')
        mk('paragraph', '¶ Kappale', self.add_paragraph)
        mk('bold', '𝐁 Lihavoi', lambda: self.fmt('bold'))
        mk('italic', '𝐼 Kursivoi', lambda: self.fmt('italic'))
        mk('underline', 'U Alleviivaa', lambda: self.fmt('underline'))
        mk('strike', 'S̶ Yliviivaa', lambda: self.fmt('strikeThrough'))
        mk('ul', '• Luettelo', lambda: self.fmt('insertUnorderedList'))
        mk('ol', '1. Numeroitu', lambda: self.fmt('insertOrderedList'))
        mk('align_left', '⬅ Vasen', lambda: self.fmt('justifyLeft'))
        mk('align_center', '⬌ Keskitä', lambda: self.fmt('justifyCenter'))
        mk('align_right', '➡ Oikea', lambda: self.fmt('justifyRight'))
        mk('align_justify', '≡ Molemmat', lambda: self.fmt('justifyFull'))

        mk('link', '🔗 Linkki', self.add_link)
        mk('unlink', '🔗✂ Ei linkkiä', lambda: self.fmt('unlink'))
        mk('image_file', '🖼 Kuva', self.add_image_file)
        mk('image_web', '🌐 Kuva verkosta', self.add_image_web)
        mk('table', '▦ Taulukko', self.add_table)
        mk('video', '▶ Video', self.add_video)
        mk('hr', '― Viiva', lambda: self._insert_html('<hr>'))
        mk('text_frame', '🗒 Tekstikehys', self.add_text_frame)
        mk('object_frame', '📊 Objektikehys', self.add_object_frame)
        mk('gallery', '🖼 Galleria', self.add_gallery)
        mk('calendar', '📅 Kalenteri', self.add_calendar)
        mk('nav_menu', '☰ Valikko', self.edit_nav_menu)
        mk('section', '📄 Osio', self.add_section)
        mk('php', '🐘 PHP', self.add_php_script)

        mk('color_text', '🎨 Tekstin väri', self.color_text)
        mk('color_bg', '🖍 Korostus', self.color_hilite)
        mk('color_elem', '🎨 Elementin väri', self.color_element)
        mk('color_elem_bg', '🎨 Elementin tausta', self.color_element_background)

        mk('move_up', '⬆ Ylös', self.move_up)
        mk('move_down', '⬇ Alas', self.move_down)
        mk('dup', '⧉ Kopioi', self.duplicate_block)
        mk('del', '🗑 Poista', self.delete_block)

        mk('settings', '⚙ Asetukset', self.page_settings)
        mk('update_preview', '➡ Päivitä esikatselu', self.update_preview)
        mk('update_code', '⬅ Päivitä koodi', self.update_code_from_preview)
        mk('kokonakyma', '🖥 Kokonäkymä (koko sivu)', self.toggle_kokosivu, 'F8')
        mk('muokkaus_isoksi',
           '🖥 Muokkausnäkymä isoksi ikkunaksi (kelluva)',
           self.avaa_kokosivu)
        hiiri_v = mk('hiirivaihto',
                     '🖱 Ikkunan vaihto hiirellä (vie päälle + napsauta)',
                     self.toggle_hiirivaihto)
        hiiri_v.setCheckable(True)
        hiiri_v.setChecked(True)

        mk('help', '❓ Ohje', self.show_help)
        mk('info', 'ℹ Tietoja', self.show_info)

        for key in ('move_up', 'move_down', 'dup', 'del'):
            A[key].setEnabled(False)

        self.actions = A

        # ================== TYÖKALURIVIT ==================
        def bar(title):
            tb = QToolBar(title, self)
            tb.setMovable(False)
            self.addToolBar(tb)
            return tb

        tb1 = bar('Tiedosto ja muotoilu')
        for key in ('new', 'open', 'save', 'save_pdf'):
            tb1.addAction(A[key])
        tb1.addSeparator()
        for key in ('undo', 'redo', 'clear_format'):
            tb1.addAction(A[key])
        tb1.addSeparator()
        for key in ('heading', 'paragraph', 'bold', 'italic', 'underline', 'strike'):
            tb1.addAction(A[key])
        tb1.addSeparator()
        for key in ('ul', 'ol', 'align_left', 'align_center', 'align_right', 'align_justify'):
            tb1.addAction(A[key])

        tb2 = bar('Lisää sisältöä')
        for key in ('link', 'unlink', 'image_file', 'image_web', 'table', 'video', 'hr',
                    'text_frame', 'object_frame', 'gallery', 'calendar', 'section',
                    'nav_menu', 'php'):
            tb2.addAction(A[key])
        tb2.addSeparator()
        for key in ('color_text', 'color_bg', 'color_elem', 'color_elem_bg'):
            tb2.addAction(A[key])

        tb3 = bar('Sijoittelu ja sivu')
        for key in ('move_up', 'move_down', 'dup', 'del'):
            tb3.addAction(A[key])
        tb3.addSeparator()
        for key in ('settings', 'update_preview', 'update_code', 'kokonakyma'):
            tb3.addAction(A[key])
    # ================== VALIKOT ==================
    def create_menus(self):
        A = self.actions
        mb = self.menuBar()

        m_file = mb.addMenu('&Tiedosto')
        m_file.addAction(A['new'])
        m_file.addAction(A['open'])
        m_file.addSeparator()
        m_file.addAction(A['save'])
        m_file.addAction(A['save_xhtml'])
        m_file.addAction(A['save_pdf'])
        m_file.addSeparator()
        m_file.addAction(A['exit'])

        m_fmt = mb.addMenu('&Muotoilu')
        m_fmt.addAction(A['heading'])
        m_fmt.addAction(A['paragraph'])
        m_fmt.addSeparator()
        for key in ('bold', 'italic', 'underline', 'strike'):
            m_fmt.addAction(A[key])
        m_fmt.addSeparator()
        for key in ('ul', 'ol', 'align_left', 'align_center', 'align_right', 'align_justify'):
            m_fmt.addAction(A[key])
        m_fmt.addSeparator()
        m_fmt.addAction(A['clear_format'])
        m_fmt.addAction(A['color_text'])
        m_fmt.addAction(A['color_bg'])

        m_add = mb.addMenu('&Lisää')
        m_add.addAction(A['link'])
        m_add.addAction(A['unlink'])
        m_add.addSeparator()
        m_add.addAction(A['image_file'])
        m_add.addAction(A['image_web'])
        m_add.addSeparator()
        m_add.addAction(A['table'])
        m_add.addAction(A['video'])
        m_add.addAction(A['hr'])
        m_add.addSeparator()
        m_add.addAction(A['text_frame'])
        m_add.addAction(A['object_frame'])
        m_add.addSeparator()
        m_add.addAction(A['gallery'])
        m_add.addAction(A['calendar'])
        m_add.addSeparator()
        m_add.addAction(A['section'])
        m_add.addAction(A['nav_menu'])
        m_add.addSeparator()
        m_add.addAction(A['php'])

        m_layout = mb.addMenu('&Sijoittelu')
        for key in ('move_up', 'move_down', 'dup', 'del'):
            m_layout.addAction(A[key])

        m_colors = mb.addMenu('&Värit')
        for key in ('color_text', 'color_bg', 'color_elem', 'color_elem_bg'):
            m_colors.addAction(A[key])

        m_page = mb.addMenu('&Sivu')
        for key in ('settings', 'update_preview', 'update_code'):
            m_page.addAction(A[key])

        m_help = mb.addMenu('&Apua')
        m_help.addAction(A['help'])
        m_help.addAction(A['info'])
    # ================== SYNKRONOINTI ==================
    def _default_doc(self):
        return BASE_TEMPLATE.replace('@TITLE@', 'Oma sivuni').replace('@CONTENT@', '')

    def render_preview(self, code):
        html = code

        def php_to_placeholder(m):
            b64 = base64.b64encode(m.group(0).encode('utf-8')).decode('ascii')
            return (
                '<div data-php-b64="' + b64 + '" style="display:none;">'
                '<span style="color:#888;">🐘 PHP-skripti (muokataan koodipuolella)</span></div>'
            )

        html = re.sub(r'<\?php.*?\?>', php_to_placeholder, html, flags=re.S | re.I)

        if '<body' in html.lower() and 'contenteditable' not in html.lower():
            html = re.sub(r'<body\b', '<body contenteditable="true"', html, count=1, flags=re.I)

        css = '<style data-editor="1">' + EDITOR_CSS + '</style>'
        head_idx = html.lower().find('</head>')
        if head_idx != -1:
            html = html[:head_idx] + css + html[head_idx:]
        else:
            html = css + html

        js = '<script data-editor="1">' + EDITOR_JS + '</script>'
        body_idx = html.lower().rfind('</body>')
        if body_idx != -1:
            html = html[:body_idx] + js + html[body_idx:]
        else:
            html = html + js

        return html

    def restore_php(self, html):
        def from_placeholder(m):
            try:
                return base64.b64decode(m.group(1).encode('ascii')).decode('utf-8', 'replace')
            except Exception:
                return ''

        html = re.sub(
            r'<div[^>]*\bdata-php-b64="([^"]*)"[^>]*>.*?</div>',
            from_placeholder, html, flags=re.S
        )
        html = re.sub(r'\s*contenteditable="(?:true|)"', '', html)
        return html

    def on_preview_html(self, raw_html):
        if self._reloading:
            return
        if self.editor.hasFocus() and not self._force_code_update:
            return
        if self._force_code_update:
            self._force_code_update = False
        html = self.restore_php(raw_html)
        if html == self.editor.toPlainText():
            return
        self._set_code_text(html)
        self.set_modified(True)
        self.statusBar().showMessage('Koodi päivittyi esikatselun muutoksista', 2000)
        self._push_kokosivuun(raw_html)

    def _set_code_text(self, text):
        self._applying_html = True
        cursor = self.editor.textCursor()
        pos = cursor.position()
        self.editor.setPlainText(text)
        try:
            pos = max(0, min(pos, len(self.editor.toPlainText())))
            c = self.editor.textCursor()
            c.setPosition(pos)
            self.editor.setTextCursor(c)
        except Exception:
            pass
        self._applying_html = False

    # ================== KOKONÄKYMÄ (koko sivu omassa ikkunassaan) ==================
    def avaa_kokosivu(self):
        """Avaa koko nettisivun omaan ikkunaansa ruudun keskelle.

        Pääohjelma jää taustalle toimimaan tavallisena ikkunana. Välillä
        voi liikkua tehtäväpalkin tai Alt+Tab:n avulla; ESC tai
        "Valmis"-painike palauttaa pääohjelmaan.
        """
        if self.kokosivu is None:
            self.kokosivu = KokosivuIkkuna(self)
        nimi = os.path.basename(self.current_file) if self.current_file else 'Oma sivuni'
        self.kokosivu.setWindowTitle('Koko sivu – %s' % nimi)
        self.kokosivu.lataa(self.render_preview(self.editor.toPlainText()))
        # keskitä ikkuna ruudun keskelle (sama näyttö kuin pääikkunassa)
        ruutu = self.screen() or QApplication.primaryScreen()
        alue = ruutu.availableGeometry()
        kehys = self.kokosivu.frameGeometry()
        kehys.moveCenter(alue.center())
        self.kokosivu.move(kehys.topLeft())
        self.kokosivu.show()
        self.kokosivu.raise_()
        self.kokosivu.activateWindow()
        self.statusBar().showMessage(
            'Kokonäkymä avattu ruudun keskelle – pääohjelma jatkaa taustalla', 4000)

    def paivita_kokosivu(self):
        """Lataa kokonäkymään koodin mukainen tuore sisältö."""
        if self.kokosivu is not None:
            self.kokosivu.lataa(self.render_preview(self.editor.toPlainText()))

    def toggle_kokosivu(self):
        if self.kokosivu is not None and self.kokosivu.isVisible():
            self.kokosivu.sulje_ja_palaa()
        else:
            self.avaa_kokosivu()

    def kokonakyma_suljettu(self):
        """Kokonäkymä suljettiin – virkistä pääesikatselu ja palauta fokus."""
        if self.kokosivu is not None and self.kokosivu.isVisible():
            return
        self.update_preview()
        self.raise_()
        self.activateWindow()
        self.statusBar().showMessage('Palattiin pääohjelman muokkausnäkymään', 3000)

    def _push_kokosivuun(self, html_dokumentti):
        """Vie esikatselun sisältö kokonäkymäikkunaan, jos se on auki."""
        if self.kokosivu is None or not self.kokosivu.isVisible():
            return
        if time.perf_counter() - self._koko_muokkaus_aika < 2.0:
            # käyttäjä on juuri muokannut kokonäkymässä – älä lataa sivua
            # uudelleen hänen kirjoittaessaan (kohdistin säilyy)
            return
        dok = html_dokumentti
        if 'contenteditable' not in dok.lower():
            # cleanClone poistaa muokattavuuden – lisätään se takaisin
            m = re.search(r'<body\b', dok, flags=re.I)
            if m:
                dok = dok[:m.end()] + ' contenteditable="true"' + dok[m.end():]
        self.kokosivu.lataa(dok)

    def on_kokosivu_html(self, raw_html, _yrityksia=8):
        """Kokonäkymässä tehty muokkaus -> koodi päivittyy.

        Pääesikatselu päivitetään vasta, kun käyttäjä palaa pääikkunaan
        (kokonakyma_suljettu / focusChanged), jotta kokonäkymää ei ladata
        uudelleen kirjoittamisen keskellä.
        """
        if self._reloading:
            if _yrityksia > 0:
                QTimer.singleShot(
                    120, lambda: self.on_kokosivu_html(raw_html, _yrityksia - 1))
            return
        html = self.restore_php(raw_html)
        if html == self.editor.toPlainText():
            return
        self._set_code_text(html)
        self.set_modified(True)
        # merkitse aidon muokkauksen ajankohta (sivun latauksen jälkeinen
        # alkusynkronointi ei ole käyttäjän muokkaus)
        if self.kokosivu is not None and (
                time.perf_counter() - self.kokosivu._viime_lataus) > 0.6:
            self._koko_muokkaus_aika = time.perf_counter()
        self.statusBar().showMessage('Koodi päivittyi kokonäkymän muutoksista', 2000)

    def _on_app_focus_changed(self, vanha, uusi):
        """Kun käyttäjä palaa pääikkunaan kokonäkymän ollessa auki,
        virkistetään pääesikatselu, jotta työkalut toimivat tuoreella
        sisällöllä eivätkä ylikirjoita kokonäkymän muutoksia."""
        if self.kokosivu is None or not self.kokosivu.isVisible():
            return
        if uusi is None:
            return
        try:
            ikkuna = uusi.window()
        except Exception:
            return
        if ikkuna is self:
            self._code_timer.start()

    # ---- Kelluvat ikkunat: vaihto hiirellä ----
    def set_hiirivaihto(self, paalla):
        """Kytkee hiirivaihdon (hiiri ikkunan päälle nostaa sen esiin)."""
        self._hiirivaihto = bool(paalla)
        self._hover_ajastin.stop()
        self._hover_kohde = None

    def toggle_hiirivaihto(self):
        self.set_hiirivaihto(self.actions['hiirivaihto'].isChecked())

    def eventFilter(self, obj, event):
        """Nostaa kelluvan ikkunan päällimmäiseksi, kun hiiri viedään
        sen päälle (noin 0,35 s viive eikä näppäimistöfokusta siirretä).
        Vasen hiirinäppäin avaa ikkunan Qt:n oletuksen mukaisesti."""
        try:
            tyyppi = event.type()
            if tyyppi == QEvent.Enter and self._hiirivaihto \
                    and isinstance(obj, QWidget):
                ikk = obj.window()
                if ikk is self or (self.kokosivu is not None
                                   and ikk is self.kokosivu):
                    if self.kokosivu is not None and self.kokosivu.isVisible():
                        self._hover_kohde = ikk
                        self._hover_ajastin.start()
            elif tyyppi == QEvent.Leave and self._hover_ajastin.isActive() \
                    and isinstance(obj, QWidget) \
                    and obj.window() is self._hover_kohde:
                # hiiri liukui vain ohi – peruu kesken olevan nostoajastimen
                self._hover_ajastin.stop()
                self._hover_kohde = None
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def _hover_nosta(self):
        kohde = self._hover_kohde
        self._hover_kohde = None
        if kohde is None or not self._hiirivaihto:
            return
        if not kohde.isVisible():
            return
        app = QApplication.instance()
        aktiivinen = app.activeWindow()
        # ei nosteta, jos avoimen dialogin takana tai toisessa ohjelmassa
        if aktiivinen is not self and aktiivinen is not self.kokosivu:
            return
        if not kohde.isActiveWindow():
            kohde.raise_()  # ei vie fokusta – vasen napsautus avaa ikkunan

    def on_code_changed(self):
        if self._applying_html:
            return
        self.set_modified(True)
        self._code_timer.start()
    def _reload_preview_now(self):
        if self._reloading:
            self._reload_queued = True
            return
        self._reloading = True
        self._pending_html = self.render_preview(self.editor.toPlainText())
        self.preview.page().runJavaScript('window.scrollY || 0', self._cb_scroll)

    def _cb_scroll(self, y):
        self._restore_scroll = int(y or 0)
        self.preview.setHtml(self._pending_html)
        # vie sama sisältö kokonäkymäikkunaan (jos se on auki)
        self._push_kokosivuun(self._pending_html)

    def on_load_finished(self, ok):
        self._reloading = False
        if self._restore_scroll:
            self.preview.page().runJavaScript(
                'editorApi.setScroll(%d)' % self._restore_scroll
            )
        if self._reload_queued:
            self._reload_queued = False
            QTimer.singleShot(50, self._reload_preview_now)

    def on_selection_info(self, info):
        has = bool(info)
        for key in ('move_up', 'move_down', 'dup', 'del'):
            self.actions[key].setEnabled(has)
        if not has:
            self.sel_label.setText('Ei valintaa – klikkaa kohdetta esikatselussa')
            return
        try:
            d = json.loads(info)
        except Exception:
            d = {}
        name = TAG_NAMES.get(d.get('tag', ''), d.get('tag', ''))
        label = 'Valittu: %s' % (name or 'kohde')
        if d.get('id'):
            label += ' (id=%s)' % d['id']
        if d.get('text'):
            label += ' – "%s"' % d['text'][:40]
        self.sel_label.setText(label)

    def update_preview(self):
        self._code_timer.stop()
        self._reload_preview_now()

    def update_code_from_preview(self):
        self._force_code_update = True
        self._odota_raikas(lambda: self.preview.page().runJavaScript(
            'editorApi.getHtmlNow()'))

    def set_modified(self, m=True):
        self.modified = m
        title = 'Graafinen web-editori 4.0 – Tehnyt Jani Malmberg'
        if self.current_file:
            title += ' – ' + os.path.basename(self.current_file)
        if self.modified:
            title += ' •'
        self.setWindowTitle(title)

    def _confirm_discard(self):
        btn = QMessageBox.question(
            self, 'Tallentamattomia muutoksia',
            'Sivulla on tallentamattomia muutoksia.\nTallennetaanko ennen jatkamista?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        if btn == QMessageBox.Save:
            return 'save'
        if btn == QMessageBox.Discard:
            return 'discard'
        return 'cancel'
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
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        if self.kokosivu is not None:
            self.kokosivu.hide()
    # ================== MUIOKKAUSOPERAATIOT ==================
    def _odota_raikas(self, toiminto, _yrityksia=20):
        """Suorita toiminto vasta, kun esikatselu ei ole latautumassa.

        Estää tilanteen, jossa työkalu (esim. Valikko) lukee tai kirjoittaa
        vanhentunutta esikatselua sen päivittymisen keskellä.
        """
        if self._reloading and _yrityksia > 0:
            QTimer.singleShot(120, lambda: self._odota_raikas(toiminto, _yrityksia - 1))
            return
        toiminto()

    def _run_js(self, expression, callback=None, _attempts=10):
        js = (
            '(function(){function go(){ return ( ' + expression + ' ); } '
            'if (window.editorApi) { return go(); } '
            'setTimeout(function(){ try { go(); } catch (e) {} }, 200); return null; })()'
        )

        def suorita():
            if callback is None:
                self.preview.page().runJavaScript(js)
                return

            def _wrapped(result):
                # Jos editorApi ei ollut vielä valmis (tulos null), yritetään
                # uudelleen hetken kuluttua, jotta esim. Valikko-ikkuna avautuu
                # varmasti myös heti käynnistyksen jälkeen.
                if (result is None or result == 'null') and _attempts > 0:
                    QTimer.singleShot(
                        150, lambda: self._run_js(expression, callback, _attempts - 1))
                    return
                callback(result)

            self.preview.page().runJavaScript(js, _wrapped)

        self._odota_raikas(suorita)

    def _insert_html(self, html_str):
        self._run_js('editorApi.insert(%s)' % json.dumps(html_str))

    def fmt(self, cmd, val=None):
        if val is None:
            self._run_js("editorApi.exec('%s')" % cmd)
        else:
            self._run_js("editorApi.exec('%s', %s)" % (cmd, json.dumps(val)))

    def add_heading(self):
        level, ok = QInputDialog.getItem(
            self, 'Otsikko', 'Valitse otsikon taso:',
            ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'], 1, False
        )
        if not ok:
            return
        text, ok2 = QInputDialog.getText(
            self, 'Otsikko',
            'Otsikon teksti (tyhjä = uusi otsikko kohdistimen kohdalle):'
        )
        if not ok2:
            return
        self._run_js('editorApi.insertHeading(%s, %s)' %
                     (json.dumps(level.lower()), json.dumps(text)))

    def add_paragraph(self):
        text, ok = QInputDialog.getMultiLineText(
            self, 'Kappale', 'Kappaleen teksti (tyhjä = tyhjä kappale):', ''
        )
        if not ok:
            return
        self._run_js('editorApi.insertParagraph(%s)' % json.dumps(text))

    def add_link(self):
        text, ok = QInputDialog.getText(
            self, 'Linkki', 'Linkin teksti (tyhjä = käytä esikatselussa valittua tekstiä):'
        )
        if not ok:
            return
        url, ok2 = QInputDialog.getText(
            self, 'Linkki', 'Osoite, johon linkki vie:', text='https://'
        )
        if not ok2 or not url.strip():
            return
        self._run_js('editorApi.insertLink(%s, %s)' %
                     (json.dumps(text), json.dumps(url.strip())))

    def color_text(self):
        dlg = ColorPaletteDialog(self, 'Tekstin väri')
        if dlg.exec_() != QDialog.Accepted:
            return
        color = dlg.get_color()
        if color:
            self.fmt('foreColor', color)

    def color_hilite(self):
        dlg = ColorPaletteDialog(self, 'Tekstin korostusväri')
        if dlg.exec_() != QDialog.Accepted:
            return
        color = dlg.get_color()
        if color:
            self.fmt('hiliteColor', color)

    def color_element(self):
        dlg = ColorPaletteDialog(self, 'Elementin väri')
        if dlg.exec_() != QDialog.Accepted:
            return
        color = dlg.get_color()
        if color:
            self._run_js('editorApi.colorBlock("color", %s)' % json.dumps(color))

    def color_element_background(self):
        dlg = ColorPaletteDialog(self, 'Elementin taustaväri')
        if dlg.exec_() != QDialog.Accepted:
            return
        color = dlg.get_color()
        if color:
            self._run_js('editorApi.colorBlock("backgroundColor", %s)' % json.dumps(color))
    # ================== SISÄLLÖN LISÄÄMINEN ==================
    def _image_frame_html(self, src, alt, caption):
        alt = html_mod.escape(alt or '', quote=True)
        src = str(src).replace('"', '&quot;')
        out = '<div class="image-frame">\n  <img src="%s" alt="%s">\n' % (src, alt)
        if caption:
            out += '  <div class="frame-caption">%s</div>\n' % html_mod.escape(caption)
        out += '</div>'
        return out

    def add_image_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Valitse kuva', '',
            'Kuvat (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.svg)'
        )
        if not path:
            return
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except Exception as e:
            QMessageBox.warning(self, 'Virhe', 'Kuvan lukeminen epäonnistui:\n%s' % e)
            return
        ext = os.path.splitext(path)[1].lower().lstrip('.')
        if ext == 'jpg':
            ext = 'jpeg'
        mime = {
            'png': 'image/png', 'jpeg': 'image/jpeg', 'gif': 'image/gif',
            'bmp': 'image/bmp', 'webp': 'image/webp', 'svg': 'image/svg+xml',
        }.get(ext, 'image/png')
        src = 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode('ascii'))
        alt, _ = QInputDialog.getText(
            self, 'Kuva', 'Kuvaus (näkyy kuvan tilalla):', text=os.path.basename(path))
        caption, _ = QInputDialog.getText(self, 'Kuva', 'Kuvateksti (valinnainen):')
        self._insert_html(self._image_frame_html(src, alt or '', caption or ''))
        self.statusBar().showMessage('Kuva lisätty (upotettu sivutiedostoon)', 4000)

    def add_image_web(self):
        url, ok = QInputDialog.getText(
            self, 'Kuva verkosta', 'Kuvan osoite (URL):', text='https://'
        )
        if not ok or not url.strip():
            return
        alt, _ = QInputDialog.getText(self, 'Kuva verkosta', 'Kuvaus (alt-teksti):')
        caption, _ = QInputDialog.getText(
            self, 'Kuva verkosta', 'Kuvateksti (valinnainen):')
        self._insert_html(self._image_frame_html(url.strip(), alt or '', caption or ''))

    def add_table(self):
        dlg = TableDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return
        rows, cols, header, caption = dlg.get_data()
        out = ['<table class="data-table">']
        if caption:
            out.append('  <caption>%s</caption>' % html_mod.escape(caption))
        if header:
            out.append('  <tr>' +
                       ''.join('<th>Otsikko %d</th>' % (i + 1) for i in range(cols)) +
                       '</tr>')
            rows -= 1
        for _ in range(max(rows, 0)):
            out.append('  <tr>' + ''.join('<td>&nbsp;</td>' for _ in range(cols)) + '</tr>')
        out.append('</table>')
        self._insert_html('\n'.join(out))

    def add_video(self):
        url, ok = QInputDialog.getText(
            self, 'Video',
            'Videon osoite (YouTube-linkki tai suora .mp4/.webm-tiedosto):',
            text='https://'
        )
        if not ok or not url.strip():
            return
        url = url.strip()
        m = (re.search(r'youtube\.com/watch\?v=([\w-]{6,})', url)
             or re.search(r'youtu\.be/([\w-]{6,})', url))
        if m:
            vid = (
                '<div class="video-embed">\n'
                '  <iframe width="560" height="315" '
                'src="https://www.youtube.com/embed/%s" title="Video" frameborder="0" '
                'allow="accelerometer; autoplay; encrypted-media; gyroscope" '
                'allowfullscreen></iframe>\n</div>' % m.group(1)
            )
        elif re.search(r'\.(mp4|webm|ogv)(\?.*)?$', url, re.I):
            vid = (
                '<video controls style="max-width:100%%;">\n'
                '  <source src="%s">\n'
                '  Selaimesi ei tue videosoitinta.\n'
                '</video>'
            ) % url
        else:
            vid = (
                '<div class="video-embed">\n'
                '  <iframe width="560" height="315" src="%s" '
                'title="Upotettu sisältö" frameborder="0" allowfullscreen></iframe>\n</div>'
            ) % url
        self._insert_html(vid)
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

        if key == 'view':
            make_btn('🖥', 'Avaa muokkausnäkymän isoksi kelluvaksi ikkunaksi '
                           '(muut ikkunat jäävät taakse kellumaan)',
                     self.avaa_kokosivu)
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
        A = self.actions
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
        m.addSeparator()
        m.addAction(A['kokonakyma'])
        m.addAction(A['muokkaus_isoksi'])
        m.addAction(A['hiirivaihto'])

def _poikkeus_kasittelija(tp, val, tb):
    """Estää PyQt5:n oletuksen mukaisen äkillisen keskeytyksen (abort).

    PyQt5 keskeyttää koko ohjelman, jos slotissa tai takaisinkutsussa
    tapahtuu käsittelemätön Python-poikkeus. Näytetään virhe viestinä
    sen sijaan, että ohjelma kaatuisi – käyttäjä voi jatkaa työtään.
    """
    try:
        traceback.print_exception(tp, val, tb)
        teksti = ''.join(traceback.format_exception_only(tp, val)).strip()
        QMessageBox.warning(
            None, 'Odottamaton virhe',
            'Ohjelmassa tapahtui odottamaton virhe, mutta se ei kaatunut.\n'
            'Voit jatkaa käyttöä. Jos virhe toistuu, käynnistä ohjelma '
            'uudelleen.\n\n%s' % teksti)
    except Exception:
        pass


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Graafinen web-editori')
    sys.excepthook = _poikkeus_kasittelija
    win = HtmlEditor()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
