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
import base64
import calendar
import datetime
import html as html_mod

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QAction, QFileDialog, QSplitter, QPushButton,
    QColorDialog, QInputDialog, QMessageBox, QLabel, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDialog, QDialogButtonBox,
    QGroupBox, QGridLayout, QListWidget, QCheckBox, QToolBar, QToolButton
)
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSlot, pyqtSignal
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