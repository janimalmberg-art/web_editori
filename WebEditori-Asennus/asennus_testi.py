# -*- coding: utf-8 -*-
r"""Testaa valmiin asennuspaketin toimivuus paikallisesti.

Vaiheet:
  1. Hiljainen asennus kansioon C:\Users\PC\Desktop\ASENNUS-TESTI\WebEditori
  2. Tarkista asennetut tiedostot, rekisterimerkinta ja pikakuvakkeet
  3. Kaynnista asennettu ohjelma (offscreen-tilassa) hetkeksi
  4. Kaynnista asennusvelho (offscreen-tilassa) hetkeksi
  5. Suorita poisto hiljaisesti ja tarkista etta kaikki siivottiin

Aja taustalla:  python aja_testi.py     (loki: _build/testi.log)
Nayta tila:     python polla.py _build/testi.log _build/testi.pid
"""
import ctypes
import os
import subprocess
import sys
import time
import winreg

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

KANSIO = os.path.dirname(os.path.abspath(__file__))
VALMIS = os.path.join(KANSIO, 'Valmis-Asennuspaketti')
ASENNA_EXE = os.path.join(VALMIS, 'Asenna-WebEditori.exe')
TESTIKOHDE = r'C:\Users\PC\Desktop\ASENNUS-TESTI\WebEditori'
UNINSTALL_KEY = (r'Software\Microsoft\Windows\CurrentVersion\Uninstall'
                 r'\WebEditori')
TULOKSET = []


def kirjaa(viesti):
    print(viesti, flush=True)


def hylly(sana, ok):
    TULOKSET.append(ok)
    kirjaa(('  [ONNISTUI] ' if ok else '  [EPÄONNISTUI] ') + sana)


def tiedosto_olemassa(nimi):
    return os.path.exists(os.path.join(TESTIKOHDE, nimi))


def rekisteri_olemassa():
    try:
        avain = winreg.OpenKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
        winreg.CloseKey(avain)
        return True
    except OSError:
        return False


def desktop_polku():
    ulos = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "[Environment]::GetFolderPath('Desktop')"],
        capture_output=True, text=True, timeout=30)
    return ulos.stdout.strip()


def kaynnista_hetkeksi(exe, sekuntia, imagnosto):
    """Kaynnistaa exen offscreen-tilassa ja katsoa pysyyko se jalkeilla."""
    ymparisto = dict(os.environ)
    ymparisto['QT_QPA_PLATFORM'] = 'offscreen'
    prosessi = subprocess.Popen([exe], cwd=os.path.dirname(exe),
                                env=ymparisto)
    time.sleep(sekuntia)
    jaljella = prosessi.poll() is None
    subprocess.run(['taskkill', '/IM', imagnosto, '/F'],
                   capture_output=True, timeout=30)
    time.sleep(1.0)
    return jaljella


def main():
    kirjaa('=== WEB-EDITORI ASENNUSPAKETIN TESTI ===')
    alkuaika = time.time()

    # --- 0. Esitarkistus ---
    kirjaa('--- 0/6 Esitarkistus ---')
    if not os.path.exists(ASENNA_EXE):
        kirjaa('  [EPÄONNISTUI] Asenna-WebEditori.exe puuttuu: ' + ASENNA_EXE)
        sys.exit(1)
    koko = os.path.getsize(ASENNA_EXE) / (1024.0 * 1024.0)
    kirjaa('  Asenna-WebEditori.exe %.1f Mt' % koko)
    hylly('Asennusohjelma olemassa', True)

    # --- 1. Hiljainen asennus ---
    kirjaa('--- 1/6 Hiljainen asennus kohteeseen ' + TESTIKOHDE + ' ---')
    tulos = subprocess.run(
        [ASENNA_EXE, '/hiljainen', '/kohde=' + TESTIKOHDE],
        timeout=300, capture_output=True)
    kirjaa('  Lopetuskoodi: %d' % tulos.returncode)
    hylly('Hiljainen asennus (lopetuskoodi 0)', tulos.returncode == 0)

    # --- 2. Tarkistukset ---
    kirjaa('--- 2/6 Asennettujen tiedostojen tarkistus ---')
    odotetut = ['WebEditori.exe', 'Ohjeet.txt', 'Poista-WebEditori.cmd',
                'Poista-WebEditori.ps1']
    puuttuvat = [nimi for nimi in odotetut if not tiedosto_olemassa(nimi)]
    if puuttuvat:
        kirjaa('  Puuttuvat: ' + ', '.join(puuttuvat))
    hylly('Asennustiedostot paikallaan', not puuttuvat)
    ohjelman_koko = 0
    for juuri, _kansiot, tiedostot in os.walk(TESTIKOHDE):
        for nimi in tiedostot:
            ohjelman_koko += os.path.getsize(os.path.join(juuri, nimi))
    kirjaa('  Asennettu yhteensa %.1f Mt, %d tiedostoa'
           % (ohjelman_koko / (1024.0 * 1024.0),
              sum(len(t) for _r, _k, t in os.walk(TESTIKOHDE))))
    hylly('Rekisterimerkinta (HKCU Uninstall)', rekisteri_olemassa())
    tyopoyta = desktop_polku()
    lnk = os.path.join(tyopoyta, 'WebEditori.lnk')
    kirjaa('  Tyopoyta: ' + tyopoyta)
    hylly('Tyopoydan pikakuvake WebEditori.lnk', os.path.exists(lnk))

    # --- 3. Ohjelman kaynnistys ---
    kirjaa('--- 3/6 Asennetun ohjelman kaynnistys ---')
    ok = kaynnista_hetkeksi(os.path.join(TESTIKOHDE, 'WebEditori.exe'),
                            14.0, 'WebEditori.exe')
    hylly('WebEditori.exe kaynnistyi ja pysyi jalkeilla', ok)

    # --- 4. Asennusvelhon kaynnistys ---
    kirjaa('--- 4/6 Asennusvelhon kaynnistys ---')
    ok = kaynnista_hetkeksi(ASENNA_EXE, 9.0, 'Asenna-WebEditori.exe')
    hylly('Asenna-WebEditori.exe avaa velhon (ei kaadu)', ok)

    # --- 5. Poisto ---
    kirjaa('--- 5/6 Poisto ---')
    tulos = subprocess.run(
        ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
         os.path.join(TESTIKOHDE, 'Poista-WebEditori.ps1'), '-Hiljainen'],
        timeout=180, capture_output=True, text=True)
    kirjaa('  Lopetuskoodi: %d' % tulos.returncode)
    time.sleep(2.0)
    hylly('Poistoskripti suoritettiin', tulos.returncode == 0)
    hylly('Asennuskansio poistettiin', not os.path.exists(TESTIKOHDE))
    hylly('Rekisterimerkinta poistettiin', not rekisteri_olemassa())
    hylly('Pikakuvake poistettiin', not os.path.exists(lnk))

    kirjaa('--- 6/6 YHTEENVETO ---')
    onnistuivat = sum(1 for ok in TULOKSET if ok)
    kirjaa('  %d/%d tarkistusta onnistui (%.1f s)'
           % (onnistuivat, len(TULOKSET), time.time() - alkuaika))
    if all(TULOKSET):
        kirjaa('  KAIKKI TESTIT MENIVAT LAPI')
        sys.exit(0)
    kirjaa('  OSISSA HUOMIOITA - tarkista ylla olevat rivit')
    sys.exit(1)


if __name__ == '__main__':
    main()