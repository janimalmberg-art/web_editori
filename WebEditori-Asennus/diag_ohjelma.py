# -*- coding: utf-8 -*-
r"""Diagnoosi: miksi paketoitu WebEditori.exe ei kaynnisty offscreen-tilassa?

  A. Tarkista QtWebEngine-tiedostot paketoidusta sovelluksesta
  B. Uudelleenasenna testikansioon (hiljainen)
  C. Kaynnista paketoitu WebEditori.exe NORMAALITILASSA hetkeksi
  D. Kaynnista lahdetiedosto editori.py offscreen-tilassa hetkeksi
  E. Kaynnista paketoitu WebEditori.exe offscreen-tilassa hetkeksi
  F. Siivoa: hiljainen poisto

Loki: _build/diag.log (aja: python aja_diag.py)
"""
import ctypes
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

KANSIO = os.path.dirname(os.path.abspath(__file__))
PROJEKTI = os.path.dirname(KANSIO)
ASENNA_EXE = os.path.join(KANSIO, 'Valmis-Asennuspaketti', 'Asenna-WebEditori.exe')
TESTIKOHDE = r'C:\Users\PC\Desktop\ASENNUS-TESTI\WebEditori'
PAKETOITU_EXE = os.path.join(TESTIKOHDE, 'WebEditori.exe')
EDITORI_PY = os.path.join(PROJEKTI, 'editori.py')
TARKISTETTAVAT = [
    'icudtl.dat',
    os.path.join('resources', 'qtwebengine_resources.pak'),
    os.path.join('resources', 'qtwebengine_resources_100p.pak'),
    os.path.join('resources', 'qtwebengine_resources_icudata.pak'),
    os.path.join('resources', 'qtwebengine_locales', 'fi.pak'),
    'Qt5WebEngine.dll',
    'Qt5WebEngineCore.dll',
    'Qt5WebEngineWidgets.dll',
]


def kirjaa(viesti):
    print(viesti, flush=True)


def onko_kaynissa(prosessi):
    return prosessi.poll() is None


def testaa_kaynnistysta(komento, tyoskentely, offscreen, sekuntia):
    ymparisto = dict(os.environ)
    if offscreen:
        ymparisto['QT_QPA_PLATFORM'] = 'offscreen'
    prosessi = subprocess.Popen(komento, cwd=tyoskentely, env=ymparisto)
    time.sleep(sekuntia)
    jaljella = onko_kaynissa(prosessi)
    if jaljella:
        prosessi.terminate()
        try:
            prosessi.wait(timeout=10)
        except subprocess.TimeoutExpired:
            prosessi.kill()
    return jaljella, prosessi.returncode


def tapa_webengine_prosessit():
    subprocess.run(['taskkill', '/IM', 'WebEditori.exe', '/F'],
                   capture_output=True)


def main():
    kirjaa('=== DIAGNOOSI: PAKETOIDUN OHJELMAN KAYNNISTYS ===')

    kirjaa('--- A. QtWebEngine-tiedostot paketissa ---')
    juuri = os.path.join(KANSIO, '_build', 'dist', 'WebEditori')
    for suhde in TARKISTETTAVAT:
        polku = os.path.join(juuri, suhde)
        if os.path.exists(polku):
            kirjaa('  [OK] %s (%.1f Mt)'
                   % (suhde, os.path.getsize(polku) / (1024.0 * 1024.0)))
        else:
            kirjaa('  [PUUTTUU] ' + suhde)

    kirjaa('--- B. Uudelleenasennus testikansioon ---')
    if not os.path.exists(PAKETOITU_EXE):
        tulos = subprocess.run([ASENNA_EXE, '/hiljainen',
                                '/kohde=' + TESTIKOHDE],
                               timeout=300, capture_output=True)
        kirjaa('  Hiljainen asennus, lopetuskoodi %d' % tulos.returncode)
    else:
        kirjaa('  Asennus jo olemassa, kaytetaan sita')

    kirjaa('--- C. Paketoitu WebEditori.exe NORMAALITILASSA ---')
    tapa_webengine_prosessit()
    jaljella, koodi = testaa_kaynnistysta([PAKETOITU_EXE], TESTIKOHDE,
                                          False, 15.0)
    kirjaa('  Jalkeilla 15 s: %s' % jaljella)
    tapa_webengine_prosessit()

    kirjaa('--- D. Lahdetiedosto editori.py offscreen ---')
    jaljella, koodi = testaa_kaynnistysta(
        [sys.executable, EDITORI_PY], PROJEKTI, True, 15.0)
    kirjaa('  Jalkeilla 15 s: %s (lopetuskoodi %s)' % (jaljella, koodi))

    kirjaa('--- E. Paketoitu WebEditori.exe offscreen ---')
    jaljella, koodi = testaa_kaynnistysta(
        [PAKETOITU_EXE], TESTIKOHDE, True, 15.0)
    kirjaa('  Jalkeilla 15 s: %s' % jaljella)
    tapa_webengine_prosessit()

    kirjaa('--- F. Siivous: hiljainen poisto ---')
    tulos = subprocess.run(
        ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
         os.path.join(TESTIKOHDE, 'Poista-WebEditori.ps1'), '-Hiljainen'],
        timeout=180, capture_output=True, text=True)
    kirjaa('  Poisto lopetuskoodi %d, kansio poistettu: %s'
           % (tulos.returncode, not os.path.exists(TESTIKOHDE)))
    kirjaa('=== DIAGNOOSI VALMIS ===')


if __name__ == '__main__':
    main()