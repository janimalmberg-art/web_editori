# -*- coding: utf-8 -*-
r"""
Graafinen web-editori 4.0 - asennusohjelma
==========================================

Ohjattu graafinen asennusvelho (suomeksi). Asentaa ohjelman ja kaikki
sen riippuvuudet (PyQt5- ja selainympäristö ovat mukana paketissa, joten
Pythonia ei tarvita kohdetietokoneella).

Asennettavat osat:
  * WebEditori.exe - itse ohjelma (riippuvuudet mukana)
  * Ohjeet.txt - käyttöohje
  * Poista-WebEditori.cmd + Poista-WebEditori.ps1 - poisto-ohjelma
  * Pikakuvakkeet työpöydälle ja/tai Käynnistä-valikkoon (valittavissa)
  * Ohjelman rekisteröinti Sovellukset-luetteloon (valittavissa)

Hiljainen asennus ilman käyttöliittymää:
    Asenna-WebEditori.exe /hiljainen
Valinnaiset liput:
    /kohde=C:\oma\polku   asennuskansio
    /eipikakuvia          ei pikakuvakkeita eikä rekisterimerkintöjä

Tehnyt Jani Malmberg
"""
import os
import sys
import shutil
import zipfile
import subprocess
import traceback
import threading
import winreg

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWizard, QWizardPage, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFileDialog, QCheckBox, QProgressBar,
    QPlainTextEdit, QMessageBox,
)

APP_NAME = 'Graafinen web-editori'
APP_VERSION = '4.0'
PUBLISHER = 'Jani Malmberg'
APP_EXE = 'WebEditori.exe'
SOVELLUS_KANSIO = 'WebEditori'
POISTO_CMD = 'Poista-WebEditori.cmd'
POISTO_PS1 = 'Poista-WebEditori.ps1'
UNINSTALL_KEY = r'Software\Microsoft\Windows\CurrentVersion\Uninstall\WebEditori'
LOG_POLKU = os.path.join(os.environ.get('TEMP', os.getcwd()),
                         'WebEditori-Asennus.log')
POISTO_PS1_SISALTO = r"""param([switch]$Hiljainen)
$ErrorActionPreference = 'SilentlyContinue'
$asennusKansio = Split-Path -Parent $MyInvocation.MyCommand.Path
Remove-Item -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\WebEditori'
$tyopoyta = [Environment]::GetFolderPath('Desktop')
Remove-Item -LiteralPath (Join-Path $tyopoyta 'WebEditori.lnk')
$alkuvalikko = [Environment]::GetFolderPath('Programs')
Remove-Item -LiteralPath (Join-Path $alkuvalikko 'WebEditori') -Recurse -Force
Set-Location $env:TEMP
Start-Sleep -Milliseconds 400
Remove-Item -LiteralPath $asennusKansio -Recurse -Force
if (-not $Hiljainen) {
  $ws = New-Object -ComObject WScript.Shell
  [void]$ws.Popup('Graafinen web-editori on poistettu tietokoneesta.', 0, 'Poisto valmis', 64)
}
"""

POISTO_CMD_SISALTO = r"""@echo off
rem Poistaa Graafinen web-editori -ohjelman tietokoneelta.
if /i "%~1"=="/hiljainen" goto POISTA
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; if ($ws.Popup('Haluatko varmasti poistaa Graafinen web-editori -ohjelman tietokoneelta?', 0, 'Poista Graafinen web-editori', 4 + 32) -ne 6) { exit 1 }"
if errorlevel 1 goto LOPETUS
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Poista-WebEditori.ps1"
goto LOPETUS
:POISTA
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Poista-WebEditori.ps1" -Hiljainen
:LOPETUS
"""


# ============================================================
# APUFUNKTIOT
# ============================================================

def _kanta():
    """Resurssikansio (PyInstallerin purkupolku tai skriptin kansio)."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _resurssi(nimi):
    return os.path.join(_kanta(), nimi)


def _oletuskohde():
    kanta = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    return os.path.join(kanta, 'Programs', SOVELLUS_KANSIO)


def _kirjaa(viesti):
    """Kirjaa asennuksen vaiheet lokitiedostoon."""
    try:
        with open(LOG_POLKU, 'a', encoding='utf-8') as tiedosto:
            tiedosto.write(viesti + '\n')
    except Exception:
        pass


def _kansion_kilo(kansio):
    """Laskee kansion sisällön koon kilotavuina."""
    yhteensa = 0
    for juuri, _kansiot, tiedostot in os.walk(kansio):
        for nimi in tiedostot:
            try:
                yhteensa += os.path.getsize(os.path.join(juuri, nimi))
            except OSError:
                pass
    return yhteensa // 1024

# ============================================================
# PIKAKUVAKKEET JA REKISTERI
# ============================================================

def _aja_powershell(teksti):
    subprocess.run(
        ['powershell', '-NoProfile', '-Command', teksti],
        check=True, capture_output=True, text=True,
    )


def luo_pikakuvakkeet(kohde, tyopoyta, alkuvalikko):
    """Luo pikakuvakkeet WScript.Shell-COM:illa PowerShellin kautta."""
    exe = os.path.join(kohde, APP_EXE)
    ohjeet = os.path.join(kohde, 'Ohjeet.txt')
    poisto = os.path.join(kohde, POISTO_CMD)
    rivit = [
        "$ErrorActionPreference = 'Stop'",
        "$ws = New-Object -ComObject WScript.Shell",
    ]

    def kuvake(sijainti, kohde_tiedosto, ikoni=None):
        rivit.append("$lnk = $ws.CreateShortcut(%s)" % sijainti)
        rivit.append("$lnk.TargetPath = '%s'" % kohde_tiedosto)
        if ikoni:
            rivit.append("$lnk.IconLocation = '%s,0'" % ikoni)
        rivit.append("$lnk.WorkingDirectory = '%s'" % kohde)
        rivit.append("$lnk.Save()")

    if tyopoyta:
        kuvake(
            "(Join-Path ([Environment]::GetFolderPath('Desktop')) "
            "'WebEditori.lnk')", exe, ikoni=exe,
        )
    if alkuvalikko:
        rivit.append(
            "$valikko = Join-Path ([Environment]::GetFolderPath('Programs')) "
            "'%s'" % SOVELLUS_KANSIO)
        rivit.append(
            "New-Item -ItemType Directory -Force -Path $valikko | Out-Null")
        kuvake("(Join-Path $valikko 'WebEditori.lnk')", exe, ikoni=exe)
        if os.path.exists(ohjeet):
            kuvake("(Join-Path $valikko 'Ohjeet.lnk')", ohjeet)
        kuvake("(Join-Path $valikko 'Poista-ohjelma.lnk')", poisto, ikoni=poisto)

    _aja_powershell('\n'.join(rivit))


def rekisteroi_uninstall(kohde):
    """Rekisteröi ohjelman Sovellukset-luetteloon (per-käyttäjä, HKCU)."""
    avain = winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
    try:
        winreg.SetValueEx(avain, 'DisplayName', 0, winreg.REG_SZ,
                          '%s %s' % (APP_NAME, APP_VERSION))
        winreg.SetValueEx(avain, 'DisplayVersion', 0, winreg.REG_SZ,
                          APP_VERSION)
        winreg.SetValueEx(avain, 'Publisher', 0, winreg.REG_SZ, PUBLISHER)
        winreg.SetValueEx(avain, 'InstallLocation', 0, winreg.REG_SZ, kohde)
        winreg.SetValueEx(avain, 'UninstallString', 0, winreg.REG_SZ,
                          '"%s"' % os.path.join(kohde, POISTO_CMD))
        winreg.SetValueEx(avain, 'DisplayIcon', 0, winreg.REG_SZ,
                          '%s,0' % os.path.join(kohde, APP_EXE))
        winreg.SetValueEx(avain, 'EstimatedSize', 0, winreg.REG_DWORD,
                          _kansion_kilo(kohde))
        winreg.SetValueEx(avain, 'NoModify', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(avain, 'NoRepair', 0, winreg.REG_DWORD, 1)
    finally:
        winreg.CloseKey(avain)

# ============================================================
# ASENNUSTYÖLÄINEN (taustasäie)
# ============================================================

class Tyolainen(QObject):
    """Tekee varsinaisen asennuksen ja raportoi etenemisen signaaleilla."""
    etene = pyqtSignal(int, str)
    valmis = pyqtSignal(bool, str)

    def __init__(self, kohde, valinnat):
        super().__init__()
        self.kohde = os.path.abspath(kohde)
        self.valinnat = valinnat

    def aja(self):
        try:
            self._asenna()
            self.valmis.emit(True, 'Asennus valmis.')
        except Exception:
            self.valmis.emit(False, traceback.format_exc())

    def _asenna(self):
        kohde = self.kohde
        _kirjaa('Asennus alkaa: ' + kohde)
        self.etene.emit(2, 'Valmistellaan kansiota ' + kohde)
        if os.path.isdir(kohde):
            if os.path.exists(os.path.join(kohde, APP_EXE)):
                self.etene.emit(5, 'Poistetaan aiempi asennus...')
                try:
                    shutil.rmtree(kohde)
                except Exception:
                    raise RuntimeError(
                        'Aiemman asennuksen poistaminen ei onnistunut. '
                        'Sulje ohjelma ja yritä asennusta uudelleen.')
            elif os.listdir(kohde):
                raise RuntimeError(
                    'Kansio ei ole tyhjä: ' + kohde +
                    ' - valitse tyhjä kansio.')
        os.makedirs(kohde, exist_ok=True)

        self.etene.emit(5, 'Puretaan ohjelmapakettia...')
        with zipfile.ZipFile(_resurssi('app.zip')) as paketti:
            jasenet = paketti.infolist()
            yhteensa = len(jasenet)
            for i, jasen in enumerate(jasenet):
                paketti.extract(jasen, kohde)
                if i % 50 == 0 or i == yhteensa - 1:
                    self.etene.emit(
                        5 + int(72 * (i + 1) / yhteensa),
                        'Asennetaan: ' + jasen.filename)
        if not os.path.exists(os.path.join(kohde, APP_EXE)):
            raise RuntimeError(
                'Ohjelmapaketti oli viallinen: ' + APP_EXE + ' puuttuu.')

        self.etene.emit(80, 'Luodaan poisto-ohjelmaa...')
        with open(os.path.join(kohde, POISTO_PS1), 'w',
                  encoding='utf-8', newline='\r\n') as tiedosto:
            tiedosto.write(POISTO_PS1_SISALTO)
        with open(os.path.join(kohde, POISTO_CMD), 'w',
                  encoding='utf-8', newline='\r\n') as tiedosto:
            tiedosto.write(POISTO_CMD_SISALTO)

        if self.valinnat.get('rekisteri'):
            self.etene.emit(86, 'Rekisteröidään ohjelma Sovellukset-luetteloon...')
            rekisteroi_uninstall(kohde)

        if self.valinnat.get('tyopoyta') or self.valinnat.get('alkuvalikko'):
            self.etene.emit(92, 'Luodaan pikakuvakkeita...')
            luo_pikakuvakkeet(kohde, self.valinnat.get('tyopoyta'),
                              self.valinnat.get('alkuvalikko'))

        self.etene.emit(100, 'Kaikki tiedostot asennettu.')
        _kirjaa('Asennus onnistui kohteeseen: ' + kohde)
# ============================================================
# ASENNUSVELHO
# ============================================================

class TervetuloaSivu(QWizardPage):
    """Ensimmäinen sivu: tiedot asennettavasta ohjelmasta."""

    def __init__(self):
        super().__init__()
        self.setTitle('Tervetuloa')
        self.setSubTitle('Asennetaan %s %s tietokoneellesi.'
                         % (APP_NAME, APP_VERSION))
        teksti = QLabel(
            '<h3>%s %s</h3>'
            '<p>Tämä ohjattu asennus asentaa <b>%s</b>-verkkosivueditorin '
            'sekä <b>kaikki sen riippuvuudet</b> (PyQt5- ja selainympäristö '
            'sisältyvät pakettiin - Pythonia ei tarvita).</p>'
            '<p><b>Asennettavat osat:</b><br>'
            '&bull; %s - itse ohjelma<br>'
            '&bull; Ohjeet.txt - käyttöohje<br>'
            '&bull; Poisto-ohjelma<br>'
            '&bull; Pikakuvakkeet (valitset kohteet seuraavissa vaiheissa)</p>'
            '<p>Asennus ei vaadi järjestelmänvalvojan oikeuksia.</p>'
            '<p><i>Tehnyt %s</i></p>'
            % (APP_NAME, APP_VERSION, APP_NAME, APP_NAME, PUBLISHER))
        teksti.setWordWrap(True)
        asettelu = QVBoxLayout(self)
        asettelu.addWidget(teksti)
        self.vanha = QLabel('')
        self.vanha.setStyleSheet('color: #a05a00; font-weight: bold;')
        asettelu.addWidget(self.vanha)

    def initializePage(self):
        aiempi = os.path.join(_oletuskohde(), APP_EXE)
        if os.path.exists(aiempi):
            self.vanha.setText(
                'Huom: aiempi asennus löytyi kansiosta %s - se päivitetään.'
                % _oletuskohde())
        else:
            self.vanha.setText('')


class KansioSivu(QWizardPage):
    """Sivu, jossa valitaan asennuskansio."""

    def __init__(self):
        super().__init__()
        self.setTitle('Asennuskansio')
        self.setSubTitle('Valitse kansio, johon ohjelma asennetaan.')
        self.asennuskohde = QLineEdit(_oletuskohde())
        selaa = QPushButton('Selaa...')
        selaa.clicked.connect(self._selaa)
        rivi = QHBoxLayout()
        rivi.addWidget(self.asennuskohde, 1)
        rivi.addWidget(selaa)
        self.vinkki = QLabel('')
        self.vinkki.setWordWrap(True)
        asettelu = QVBoxLayout(self)
        asettelu.addLayout(rivi)
        asettelu.addWidget(self.vinkki)
        self.registerField('kohde*', self.asennuskohde)
        self.asennuskohde.textChanged.connect(self.completeChanged)
        self._tarvitaan = 300 * 1024 * 1024
        try:
            with zipfile.ZipFile(_resurssi('app.zip')) as paketti:
                self._tarvitaan = sum(jasen.file_size
                                      for jasen in paketti.infolist())
        except Exception:
            pass

    def _selaa(self):
        polku = QFileDialog.getExistingDirectory(
            self, 'Valitse asennuskansio', self.asennuskohde.text())
        if polku:
            self.asennuskohde.setText(os.path.normpath(polku))

    def isComplete(self):
        polku = self.asennuskohde.text().strip()
        if not polku:
            self.vinkki.setText('Kirjoita tai valitse asennuskansio.')
            return False
        ajuri = os.path.splitdrive(polku)[0]
        tarvitaan = int(self._tarvitaan * 2.5)
        if ajuri:
            try:
                vapaa = shutil.disk_usage(ajuri + os.sep).free
                if vapaa < tarvitaan:
                    self.vinkki.setText(
                        'Levytilaa ei riitä: tarvitaan noin %s, vapaana %s.'
                        % (_asennuksen_kilo(tarvitaan // 1024),
                           _asennuksen_kilo(vapaa // 1024)))
                    return False
            except OSError:
                pass
        if (os.path.isdir(polku) and os.listdir(polku)
                and not os.path.exists(os.path.join(polku, APP_EXE))):
            self.vinkki.setText(
                'Kansio ei ole tyhjä eikä siinä ole aiempaa asennusta. '
                'Valitse toinen kansio.')
            return False
        self.vinkki.setText('Ohjelma asennetaan kansioon: ' + polku)
        return True


class ValinnatSivu(QWizardPage):
    """Sivu, jossa valitaan pikakuvakkeet ja lisätoiminnot."""

    def __init__(self):
        super().__init__()
        self.setTitle('Valinnat')
        self.setSubTitle('Valitse, mitä pikakuvakkeita ja lisätoimintoja tehdään.')
        self.tyopoyta = QCheckBox('Pikakuvake työpöydälle (WebEditori)')
        self.tyopoyta.setChecked(True)
        self.alkuvalikko = QCheckBox(
            'Pikakuvakkeet Käynnistä-valikkoon (ohjelma, ohjeet, poisto)')
        self.alkuvalikko.setChecked(True)
        self.rekisteri = QCheckBox(
            'Näytä ohjelma kohdassa Sovellukset - mahdollistaa poiston '
            'Windowsin asetusten kautta')
        self.rekisteri.setChecked(True)
        self.kaynnista = QCheckBox('Käynnistä ohjelma asennuksen päätyttyä')
        self.kaynnista.setChecked(True)
        self.avaa_ohjeet = QCheckBox(
            'Avaa käyttöohjeet (Ohjeet.txt) asennuksen päätyttyä')
        self.avaa_ohjeet.setChecked(True)
        asettelu = QVBoxLayout(self)
        for valinta in (self.tyopoyta, self.alkuvalikko, self.rekisteri):
            asettelu.addWidget(valinta)
        asettelu.addSpacing(12)
        asettelu.addWidget(QLabel('Asennuksen jälkeen:'))
        asettelu.addWidget(self.kaynnista)
        asettelu.addWidget(self.avaa_ohjeet)
        asettelu.addStretch(1)


class AsennusSivu(QWizardPage):
    """Sivu, jossa asennus suoritetaan (edistymispalkki ja loki)."""

    def __init__(self):
        super().__init__()
        self.setTitle('Asennus')
        self.setSubTitle('Ohjelmaa asennetaan - odota hetki.')
        self._ok = False
        self._tyolainen = None
        self._lanka = None
        self.palkki = QProgressBar()
        self.loki = QPlainTextEdit()
        self.loki.setReadOnly(True)
        asettelu = QVBoxLayout(self)
        asettelu.addWidget(self.palkki)
        asettelu.addWidget(self.loki)

    def isComplete(self):
        return self._ok

    def initializePage(self):
        velho = self.wizard()
        velho.button(QWizard.BackButton).setEnabled(False)
        velho.button(QWizard.CancelButton).setEnabled(False)
        self._ok = False
        self.palkki.setValue(0)
        self.loki.clear()
        self._tyolainen = Tyolainen(velho.field('kohde'), velho.valinnat())
        self._tyolainen.etene.connect(self._edisty)
        self._tyolainen.valmis.connect(self._tulos)
        self._lanka = threading.Thread(target=self._tyolainen.aja, daemon=True)
        self._lanka.start()

    def _edisty(self, prosentti, viesti):
        self.palkki.setValue(prosentti)
        self.loki.appendPlainText(viesti)

    def _tulos(self, ok, viesti):
        velho = self.wizard()
        if ok:
            self._ok = True
            self.loki.appendPlainText('Asennus onnistui!')
            self.completeChanged()
            velho.next()
        else:
            self.loki.appendPlainText(viesti)
            velho.button(QWizard.BackButton).setEnabled(True)
            velho.button(QWizard.CancelButton).setEnabled(True)
            QMessageBox.critical(
                self, 'Asennus epäonnistui',
                'Asennuksessa tapahtui virhe:\n\n' + viesti[-1500:])


class ValmisSivu(QWizardPage):
    """Viimeinen sivu: asennus valmis, valinnaiset päätöstot."""

    def __init__(self):
        super().__init__()
        self.setTitle('Valmis')
        self.setSubTitle('%s %s on asennettu.' % (APP_NAME, APP_VERSION))
        self.kaynnista = QCheckBox('Käynnistä ohjelma nyt')
        self.ohjeet = QCheckBox('Avaa käyttöohje')
        asettelu = QVBoxLayout(self)
        asettelu.addWidget(QLabel(
            'Asennus onnistui. Ohjelma on käynnistettävissä työpöydän '
            'pikakuvakkeesta tai Käynnistä-valikosta.'))
        asettelu.addSpacing(10)
        asettelu.addWidget(self.kaynnista)
        asettelu.addWidget(self.ohjeet)
        asettelu.addStretch(1)

    def initializePage(self):
        self.wizard().button(QWizard.BackButton).setEnabled(False)
        valinnat = self.wizard().valinnat()
        self.kaynnista.setChecked(valinnat['kaynnista'])
        self.ohjeet.setChecked(valinnat['ohjeet'])

    def validatePage(self):
        kohde = self.wizard().field('kohde')
        if self.ohjeet.isChecked():
            try:
                os.startfile(os.path.join(kohde, 'Ohjeet.txt'))
            except Exception:
                pass
        if self.kaynnista.isChecked():
            try:
                subprocess.Popen([os.path.join(kohde, APP_EXE)], cwd=kohde)
            except Exception:
                pass
        return True


class AsennusVelho(QWizard):
    """Pääikkuna: ohjattu asennus neljällä vaiheella."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Asennus - %s %s' % (APP_NAME, APP_VERSION))
        ikoni = _resurssi('ikoni.ico')
        if os.path.exists(ikoni):
            self.setWindowIcon(QIcon(ikoni))
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        self.setButtonText(QWizard.NextButton, 'Seuraava >')
        self.setButtonText(QWizard.BackButton, '< Takaisin')
        self.setButtonText(QWizard.CancelButton, 'Peruuta')
        self.setButtonText(QWizard.FinishButton, 'Valmis')
        self.addPage(TervetuloaSivu())
        self.addPage(KansioSivu())
        self.addPage(ValinnatSivu())
        self.addPage(AsennusSivu())
        self.addPage(ValmisSivu())
        self.resize(620, 520)

    def valinnat(self):
        sivu = self.page(2)
        return {
            'tyopoyta': sivu.tyopoyta.isChecked(),
            'alkuvalikko': sivu.alkuvalikko.isChecked(),
            'rekisteri': sivu.rekisteri.isChecked(),
            'kaynnista': sivu.kaynnista.isChecked(),
            'ohjeet': sivu.avaa_ohjeet.isChecked(),
        }
# ============================================================
# HILJAINEN ASENNUS JA KÄYNNISTYS
# ============================================================

def _lue_liput(argv):
    """Lukee komentorivin liput (/hiljainen, /kohde=..., /eipikakuvia)."""
    optiot = {'hiljainen': False, 'kohde': None, 'eipikakuvia': False}
    for lippu in argv[1:]:
        pieni = lippu.lower()
        if pieni in ('/hiljainen', '-hiljainen', '/s', '/silent'):
            optiot['hiljainen'] = True
        elif pieni in ('/eipikakuvia', '-eipikakuvia'):
            optiot['eipikakuvia'] = True
        elif '=' in pieni:
            nimi, arvo = pieni.split('=', 1)
            if nimi.lstrip('/-') == 'kohde':
                optiot['kohde'] = lippu.split('=', 1)[1].strip().strip('"')
    return optiot


def _hiljainen_asennus(optiot):
    """Asentaa oletusvalinnoilla ilman käyttöliittymää. Palauttaa 0/1."""
    kohde = optiot['kohde'] or _oletuskohde()
    _kirjaa('Hiljainen asennus: kohde=%s eipikakuvia=%s'
            % (kohde, optiot['eipikakuvia']))
    valinnat = {
        'tyopoyta': not optiot['eipikakuvia'],
        'alkuvalikko': not optiot['eipikakuvia'],
        'rekisteri': not optiot['eipikakuvia'],
        'kaynnista': False,
        'ohjeet': False,
    }
    tyolainen = Tyolainen(kohde, valinnat)
    tyolainen.etene.connect(
        lambda prosentti, viesti: _kirjaa('[%3d%%] %s' % (prosentti, viesti)))
    tulos = {}

    def _valmis(ok, viesti):
        tulos['ok'] = ok
        tulos['viesti'] = viesti

    tyolainen.valmis.connect(_valmis)
    tyolainen.aja()
    if tulos.get('ok'):
        _kirjaa('Hiljainen asennus valmis.')
        return 0
    _kirjaa('Hiljainen asennus epäonnistui: %s' % tulos.get('viesti', ''))
    return 1


def main():
    optiot = _lue_liput(sys.argv)
    if optiot['hiljainen']:
        try:
            return _hiljainen_asennus(optiot)
        except Exception:
            _kirjaa(traceback.format_exc())
            return 1
    sovellus = QApplication(sys.argv)
    velho = AsennusVelho()
    velho.show()
    return sovellus.exec_()


if __name__ == '__main__':
    sys.exit(main())