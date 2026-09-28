# ============================================================
# OSA 13b – KOKONÄKYMÄ: koko nettisivu omassa ikkunassaan
# ============================================================
# Tämä osa on viitekopio editori.py:n uudesta ominaisuudesta:
#
#   1. Luokka KokosivuIkkuna sijaitsee editori.py:ssä heti TAG_NAMES-
#      sanakirjan jälkeen, ennen luokkaa HtmlEditor.
#   2. HtmlEditor-luokkaan lisätyt metodit: avaa_kokosivu,
#      paivita_kokosivu, toggle_kokosivu, kokonakyma_suljettu,
#      _push_kokosivuun, on_kokosivu_html, _on_app_focus_changed
#      (löytyvät editori.py:stä otsikon "KOKONÄKYMÄ" alta) sekä
#      _odota_raikas-portti.
#   3. Kytkennät: create_actions (toiminto 'kokonakyma', F8),
#      työkalurivi tb3, Näkymä-valikko, __init__ (self.kokosivu,
#      focusChanged-kytkentä), _cb_scroll, on_preview_html,
#      on_code_changed ja closeEvent.
#
# Toiminta:
#   - "🖥 Kokonäkymä (koko sivu)" / Näkymä-valikko / F8 avaa koko
#     nettisivun omaan ikkunaansa ruudun keskelle.
#   - Sivua voi muokata suoraan kokonäkymässä; muutokset synkronoituvat
#     koodiin ja pääikkunaan, ja pääohjelma jää taustalle toimimaan.
#   - Välillä liikkutaan tehtäväpalkilla tai Alt+Tab:lla;
#     "✔ Valmis" / ESC palaa pääohjelmaan ja virkistää sen esikatselun.
#
# Liittyvät lisäykset muualla editori.py:ssä:
#   4. Vierintäpalkki: EDITOR_CSS sisältää aina näkyvän, tyylitelty
#      vierityspalkin (html { overflow-y: scroll } + ::-webkit-scrollbar)
#      – näkyy muokkausnäkymässä ja kokonäkymässä.
#   5. Hiirivaihto kelluvien ikkunoiden välillä: HtmlEditor.eventFilter /
#      _hover_nosta / set_hiirivaihto – hiiri ikkunan päälle nostaa sen
#      esiin ja vasen napsautus avaa ikkunan (katkaisija Näkymä-valikossa,
#      toiminto 'hiirivaihto'). Paneelin otsikkopalkissa on 🖥-nappi
#      (_pane_header), joka avaa muokkausnäkymän isoksi kelluvaksi.

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QShortcut
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
from PyQt5.QtWebChannel import QWebChannel

import time


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