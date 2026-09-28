# -*- coding: utf-8 -*-
"""
Automaattinen kaatumistesti graafiselle web-editorille.
=====================================================

Simuloi käyttäjän toimintoja: kaikkien "Lisää"-elementtien lisäämisen
(ml. Valikko), muotoilut, värit, sijoittelun, ikkunoinnin ja tallennuksen.
Jos ohjelma kaatuu (segfault), prosessi kuolee ja poistumiskoodi on
nollasta poikkeava. Python-poikkeukset tulostetaan.

Aja:  python testaa_ohjelma.py
"""

import sys
import os
import traceback

TAMA_KANSIO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TAMA_KANSIO)

from PyQt5.QtCore import Qt, QTimer, QEventLoop, QEvent, pyqtSlot  # noqa: E402
from PyQt5.QtWidgets import (  # noqa: E402
    QApplication, QDialog, QInputDialog, QMessageBox, QFileDialog, QToolButton,
)

# Tuodaan testattava ohjelma
import editori  # noqa: E402
from editori import (  # noqa: E402
    HtmlEditor, NavMenuDialog, TableDialog, CalendarDialog, GalleryDialog,
    PhpScriptDialog, PageSettingsDialog, ColorPaletteDialog,
)

# ------------------------------------------------------------
# Tulosten keruu
# ------------------------------------------------------------
TULOKSET = []
APP = None


def kirjaa(nimi, ok, lisatieto=""):
    TULOKSET.append((nimi, ok, lisatieto))
    merkki = "OK " if ok else "VIRHE"
    print("[%s] %s %s" % (merkki, nimi, ("-- " + lisatieto) if lisatieto else ""))
    sys.stdout.flush()


def pump(ms):
    """Anna Qt-tapahtumasilmukalle aikaa (JS-ajot, takaisinkutsut)."""
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()


# ------------------------------------------------------------
# Automaattiset vastaukset dialogeihin
# ------------------------------------------------------------

# Jono valmiiksi syötettyjä vastauksia QInputDialog-kutsuille.
VASTAUKSET = []


def lisaa_vastaus(*arvot):
    for a in arvot:
        VASTAUKSET.append(a)


def _ota_vastaus(oletus):
    if VASTAUKSET:
        return VASTAUKSET.pop(0)
    return oletus


def fake_getItem(*args, **kwargs):
    return _ota_vastaus(("H1",)), True


def fake_getText(*args, **kwargs):
    return _ota_vastaus("Testiarvo"), True


def fake_getMultiLineText(*args, **kwargs):
    return _ota_vastaus("Testitekstia"), True


QInputDialog.getItem = staticmethod(fake_getItem)
QInputDialog.getText = staticmethod(fake_getText)
QInputDialog.getMultiLineText = staticmethod(fake_getMultiLineText)

# Tiedostovalinta-ikkunat eivat avaudu testeissa
TALLENNUS_POLUT = []


def fake_getSaveFileName(*args, **kwargs):
    if TALLENNUS_POLUT:
        return (TALLENNUS_POLUT.pop(0), "")
    return ("", "")


QFileDialog.getOpenFileName = staticmethod(lambda *a, **k: ("", ""))
QFileDialog.getSaveFileName = staticmethod(fake_getSaveFileName)
QFileDialog.getOpenNames = staticmethod(lambda *a, **k: ([], ""))


def fake_information(*args, **kwargs):
    pass


def fake_warning(*args, **kwargs):
    print("    (QMessageBox.warning: %s)" % (args[2] if len(args) > 2 else ""))


def fake_question(*args, **kwargs):
    # Vastaa aina "Discard" (ala tallenna)
    return QMessageBox.Discard


QMessageBox.information = staticmethod(fake_information)
QMessageBox.warning = staticmethod(fake_warning)
QMessageBox.question = staticmethod(fake_question)


def fake_color_exec(self):
    self.pick_color("#FF0000")
    self.accept()
    return QDialog.Accepted


ColorPaletteDialog.exec_ = fake_color_exec


def fake_table_exec(self):
    self.accept()
    return QDialog.Accepted


TableDialog.exec_ = fake_table_exec


def fake_calendar_exec(self):
    self.accept()
    return QDialog.Accepted


CalendarDialog.exec_ = fake_calendar_exec


def fake_gallery_exec(self):
    self.urls_edit.setPlainText(
        "https://esimerkki.fi/k1.jpg\nhttps://esimerkki.fi/k2.jpg")
    self.accept()
    return QDialog.Accepted


GalleryDialog.exec_ = fake_gallery_exec


def fake_php_exec(self):
    self.code_edit.setPlainText('echo "<p>PHP-testi</p>";')
    self.accept()
    return QDialog.Accepted


PhpScriptDialog.exec_ = fake_php_exec


def fake_page_exec(self):
    self.accept()
    return QDialog.Accepted


PageSettingsDialog.exec_ = fake_page_exec

def fake_navmenu_exec(self):
    """Simuloi kayttajan valikkodialogin kaytto: lisaa linkki, siirra, paivita."""
    self.name_edit.setText("Testivalikko")
    self.url_edit.setText("#testivalikko")
    self.add_link()
    if self.listw.count() >= 2:
        self.listw.setCurrentRow(self.listw.count() - 1)
        self.move_item(-1)
        self.move_item(1)
    if self.listw.count() >= 1:
        self.listw.setCurrentRow(0)
        self.name_edit.setText("Muokattu")
        self.update_selected()
    self.accept()
    return QDialog.Accepted


NavMenuDialog.exec_ = fake_navmenu_exec


@pyqtSlot()
def suorita_testit():
    win = APP._test_window

    # 0) Odota etta esikatselu on ladattu
    for _ in range(50):
        pump(100)
        if win.editor.toPlainText().strip():
            break
    kirjaa("Esikatselun alkulataus", True)

    # Varmista ettei koodieditorilla ole fokusta (pushien synkronointi)
    win.preview.setFocus()
    pump(200)

    koodeksti = lambda: win.editor.toPlainText()

    # 1) VALIKKO (kayttajan ilmoittama kaatava toiminto)
    try:
        win.edit_nav_menu()
        pump(800)
        ok = ("Testivalikko" in koodeksti()) and ("#testivalikko" in koodeksti())
        kirjaa("Lisaavalikko (edit_nav_menu)", ok)
    except Exception:
        kirjaa("Lisaavalikko (edit_nav_menu)", False, traceback.format_exc())

    # 2) VALIKKO uudelleen (muokkaus olemassa olevaan)
    try:
        win.edit_nav_menu()
        pump(800)
        ok = "Muokattu" in koodeksti()
        kirjaa("Valikon uudelleenmuokkaus", ok)
    except Exception:
        kirjaa("Valikon uudelleenmuokkaus", False, traceback.format_exc())

    # 3) Osio (alasivu + automaattinen valikkolinkki)
    try:
        VASTAUKSET.clear()
        lisaa_vastaus("Tietoja minusta", "tietoja-minusta")
        win.add_section()
        pump(800)
        ok = 'id="tietoja-minusta"' in koodeksti()
        kirjaa("Lisaa osio (add_section)", ok)
    except Exception:
        kirjaa("Lisaa osio", False, traceback.format_exc())

    # 4) Otsikko, kappale, linkki
    try:
        VASTAUKSET.clear()
        lisaa_vastaus("H2", "Testiotsikko")
        win.add_heading()
        pump(600)
        VASTAUKSET.clear()
        lisaa_vastaus("Uusi kappale tekstia")
        win.add_paragraph()
        pump(600)
        VASTAUKSET.clear()
        lisaa_vastaus("Testilinkki", "https://esimerkki.fi")
        win.add_link()
        pump(600)
        ok = ("Testiotsikko" in koodeksti() and "Testilinkki" in koodeksti())
        kirjaa("Lisaa otsikko/kappale/linkki", ok)
    except Exception:
        kirjaa("Lisaa otsikko/kappale/linkki", False, traceback.format_exc())

    # 5) Kuva verkosta, taulukko, video
    try:
        VASTAUKSET.clear()
        lisaa_vastaus("https://esimerkki.fi/kuva.jpg", "alt-teksti", "kuvateksti")
        win.add_image_web()
        pump(600)
        win.add_table()
        pump(600)
        VASTAUKSET.clear()
        lisaa_vastaus("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        win.add_video()
        pump(600)
        ok = ("image-frame" in koodeksti() and "data-table" in koodeksti()
              and "video-embed" in koodeksti())
        kirjaa("Lisaa kuva verkosta / taulukko / video", ok)
    except Exception:
        kirjaa("Lisaa kuva/taulukko/video", False, traceback.format_exc())

    # 6) Tekstikehys, objektikehys, galleria, kalenteri
    try:
        VASTAUKSET.clear()
        lisaa_vastaus("Kehyksen otsikko", "Kehyksen sisalto")
        win.add_text_frame()
        pump(600)
        win.add_object_frame()
        pump(600)
        win.add_gallery()
        pump(600)
        win.add_calendar()
        pump(600)
        ok = ("text-frame" in koodeksti() and "object-frame" in koodeksti()
              and "gallery" in koodeksti() and "calendar" in koodeksti())
        kirjaa("Lisaa kehykset/galleria/kalenteri", ok)
    except Exception:
        kirjaa("Lisaa kehykset/galleria/kalenteri", False, traceback.format_exc())

    # 7) Muotoilukomennot ilman valintaa
    try:
        for cmd in ("bold", "italic", "underline", "strikeThrough",
                    "insertUnorderedList", "insertOrderedList",
                    "justifyLeft", "justifyCenter", "justifyRight",
                    "justifyFull", "removeFormat", "undo", "redo"):
            win.fmt(cmd)
            pump(60)
        kirjaa("Muotoilukomennot (fmt)", True)
    except Exception:
        kirjaa("Muotoilukomennot", False, traceback.format_exc())

    # 8) Varit
    try:
        win.color_text(); pump(300)
        win.color_hilite(); pump(300)
        win.color_element(); pump(300)
        win.color_element_background(); pump(300)
        kirjaa("Varit", True)
    except Exception:
        kirjaa("Varit", False, traceback.format_exc())

    # 9) Sijoittelu: valitse lohko JS:lla ja siirra/kopioi/poista
    try:
        win._run_js(
            "var p = document.querySelector('.content p');"
            "if (p) { var r = document.createRange();"
            "r.selectNodeContents(p); var s = window.getSelection();"
            "s.removeAllRanges(); s.addRange(r); } true"
        )
        pump(500)  # selectionchange -> pushSelection
        win.move_up(); pump(500)
        win.move_down(); pump(500)
        win.duplicate_block(); pump(500)
        win.delete_block(); pump(500)
        kirjaa("Sijoittelu (siirra/kopioi/poista)", True)
    except Exception:
        kirjaa("Sijoittelu", False, traceback.format_exc())

    # 10) Sivun asetukset
    try:
        win.page_settings()
        pump(600)
        kirjaa("Sivun asetukset", True)
    except Exception:
        kirjaa("Sivun asetukset", False, traceback.format_exc())

    # 11) Ikkunoiden hallinta (Word-tyyli)
    try:
        win.maximize_pane('code'); pump(200)
        win.maximize_pane('code'); pump(200)  # palautus
        win.maximize_pane('view'); pump(200)
        win.show_pane('code'); pump(200)
        win.minimize_pane('code'); pump(200)
        win.show_pane('code'); pump(200)
        win.reset_panes(); pump(200)
        kirjaa("Ikkunoiden hallinta", True)
    except Exception:
        kirjaa("Ikkunoiden hallinta", False, traceback.format_exc())

    # 12) Koodimuokkaus -> esikatselu (synkronointi toiseen suuntaan)
    try:
        uusi = koodeksti().replace(
            "Sivun otsikko", "Koodista muokattu otsikko")
        win.editor.setPlainText(uusi)
        pump(1200)  # 700 ms ajastin + setHtml + loadFinished
        kirjaa("Koodimuokkaus paivittaa esikatselun", True)
    except Exception:
        kirjaa("Koodimuokkaus -> esikatselu", False, traceback.format_exc())

    # 13) PHP-skriptin lisays
    try:
        win.add_php_script()
        pump(800)
        ok = "<?php" in koodeksti()
        kirjaa("Lisaa PHP-skripti", ok)
    except Exception:
        kirjaa("Lisaa PHP-skripti", False, traceback.format_exc())

    # 14) Tallennus suoralla polulla
    try:
        polku = os.path.join(TAMA_KANSIO, "testitulos.html")
        TALLENNUS_POLUT.append(polku)
        win.current_file = polku
        onnistui = win._do_save('html')
        with open(polku, "r", encoding="utf-8") as f:
            sisalto = f.read()
        kirjaa("Tallenna HTML", onnistui and ("Testiotsikko" in sisalto or "muokattu" in sisalto.lower()))
    except Exception:
        kirjaa("Tallenna HTML", False, traceback.format_exc())

    # 15) Uusi sivu
    try:
        win.new_page()
        pump(800)
        kirjaa("Uusi sivu", "Sivun otsikko" in koodeksti())
    except Exception:
        kirjaa("Uusi sivu", False, traceback.format_exc())

    # 16) Kokonakyma: koko sivu omassa ikkunassaan ruudun keskella
    try:
        win.avaa_kokosivu()
        pump(1500)
        nakyy = win.kokosivu.isVisible()
        ruutu = QApplication.primaryScreen().availableGeometry()
        kc = win.kokosivu.frameGeometry().center()
        keskella = (abs(kc.x() - ruutu.center().x()) < 120
                    and abs(kc.y() - ruutu.center().y()) < 120)
        tulos = {}

        def _ota(r):
            tulos['v'] = r

        win.kokosivu.view.page().runJavaScript(
            "document.querySelector('.navbar') ? 'navbar-ok' : 'ei-navbaria'", _ota)
        pump(700)

        # koodimuutos siirtyy kokonakymaan
        koodi = koodeksti().replace('Sivun otsikko', 'Sivun otsikko KOKOTESTI', 1)
        win.editor.setPlainText(koodi)
        win.update_preview()
        pump(1500)

        def _ota2(r):
            tulos['k'] = r

        win.kokosivu.view.page().runJavaScript(
            "document.body.innerHTML.indexOf('KOKOTESTI') >= 0 ? 'siirtyi' : 'ei-siirtynyt'",
            _ota2)
        pump(700)

        # kokonakymassa tehty muokkaus siirtyy koodiin
        win.kokosivu.view.page().runJavaScript(
            "try { editorApi.insert('<p data-testi=\"1\">KOKOMUOKKAUS</p>'); } catch (e) {}")
        pump(2200)
        koodissa = 'KOKOMUOKKAUS' in koodeksti()

        # sulje ja palaa paaojkelmaan
        win.kokosivu.sulje_ja_palaa()
        pump(900)
        paluu = not win.kokosivu.isVisible()
        ok = (nakyy and keskella and tulos.get('v') == 'navbar-ok'
              and tulos.get('k') == 'siirtyi' and koodissa and paluu)
        kirjaa("Kokonakyma (koko sivu omassa ikkunassaan)", ok,
               '' if ok else 'nakyy=%s keskella=%s navbar=%s koodi-siirtyi=%s muokkaus=%s paluu=%s'
               % (nakyy, keskella, tulos.get('v'), tulos.get('k'), koodissa, paluu))
    except Exception:
        kirjaa("Kokonakyma", False, traceback.format_exc())

    # 17) Kelluvat ikkunat: vierintapalkki + hiirivaihto ikkunoiden valilla
    try:
        # a) aina nakyyva tyylitelty vierintapalkki muokkausnakymassa
        css = editori.EDITOR_CSS
        palkki_css = ('::-webkit-scrollbar' in css
                      and 'overflow-y: scroll' in css)
        tulos = {}

        def _ota(r):
            tulos['v'] = r

        win.preview.page().runJavaScript(
            "getComputedStyle(document.documentElement).overflowY", _ota)
        pump(600)

        # b) hiiri paakikkunan paalle (kokosivu aktiivisena) -> se nostetaan
        #    esiin ilman nakpaimistofokuksen siirtoa
        win.avaa_kokosivu()
        pump(1200)
        kutsut = []
        win.raise_ = lambda: kutsut.append('paa')
        QApplication.sendEvent(win.editor, QEvent(QEvent.Enter))
        pump(600)
        nostettu = kutsut == ['paa']
        fokus_jai = not win.isActiveWindow()

        # c) hiiren poistuminen peruu kesken olevan nostoajastimen
        kutsut2 = []
        win.raise_ = lambda: kutsut2.append('paa')
        QApplication.sendEvent(win.editor, QEvent(QEvent.Enter))
        QApplication.sendEvent(win.editor, QEvent(QEvent.Leave))
        pump(600)
        ei_nostoa = kutsut2 == []
        del win.raise_

        # d) kytkin pois -> hiirivaihto ei enaa nosta
        win.actions['hiirivaihto'].setChecked(False)
        win.toggle_hiirivaihto()
        kutsut3 = []
        win.raise_ = lambda: kutsut3.append('paa')
        QApplication.sendEvent(win.editor, QEvent(QEvent.Enter))
        pump(600)
        pois = kutsut3 == []
        del win.raise_
        win.actions['hiirivaihto'].setChecked(True)
        win.toggle_hiirivaihto()

        # e) muokkausnakymän otsikkopalkin isonna-avausnappi loytyy
        napit = [b.toolTip() for b in win.findChildren(QToolButton)]
        isonappi = any('isoksi kelluvaksi' in t for t in napit)

        win.kokosivu.sulje_ja_palaa()
        pump(900)
        paluu = not win.kokosivu.isVisible()

        ok = (palkki_css and tulos.get('v') == 'scroll' and nostettu
              and fokus_jai and ei_nostoa and pois and isonappi and paluu)
        kirjaa("Kelluvat ikkunat (vierintapalkki + hiirivaihto)", ok,
               '' if ok else 'css=%s overflowY=%s nostettu=%s fokus-jai=%s '
                             'leave-peruu=%s pois=%s isonappi=%s paluu=%s'
               % (palkki_css, tulos.get('v'), nostettu, fokus_jai,
                  ei_nostoa, pois, isonappi, paluu))
    except Exception:
        kirjaa("Kelluvat ikkunat", False, traceback.format_exc())

    # 18) Yhteenveto
    epaonnistuneet = [t for t in TULOKSET if not t[1]]
    print("")
    print("=" * 60)
    if epaonnistuneet:
        print("TESTIT EPAONNISTIVAT: %d/%d" % (len(epaonnistuneet), len(TULOKSET)))
        for nimi, _ok, info in epaonnistuneet:
            print("  - %s: %s" % (nimi, info.splitlines()[-1] if info else ""))
    else:
        print("KAIKKI %d TESTIA LAPI - EI KAATUMISTA." % len(TULOKSET))
    QTimer.singleShot(150, APP.quit)


def main():
    global APP
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    APP = app
    app.setApplicationName('Graafinen web-editori - testi')

    def poikkeus_hook(t, v, tb):
        print("PYTHON-POIKKEUS:", "".join(traceback.format_exception(t, v, tb)))
        sys.stdout.flush()

    sys.excepthook = poikkeus_hook

    win = HtmlEditor()
    APP._test_window = win
    win.show()

    QTimer.singleShot(1500, suorita_testit)
    app.exec_()
    epaonnistuneet = [t for t in TULOKSET if not t[1]]
    koodi = 1 if epaonnistuneet else 0
    print("POISTUMISKOODI:", koodi)
    sys.exit(koodi)


if __name__ == '__main__':
    main()
