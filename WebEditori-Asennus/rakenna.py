# -*- coding: utf-8 -*-
"""
Rakentaa Graafinen web-editori 4.0 - ohjelmasta Windows-graafisen
asennuspaketin (Asenna-WebEditori.exe).

Aja tässä kansiossa:  python rakenna.py

Rakennusvaiheet:
  1. Luodaan ohjelmatiedosto ikoni.ico (Pillow).
  2. Kääritään editori.py itsenäiseksi WebEditori.exe-paketiksi
     (PyInstaller, kaikki riippuvuudet mukana).
  3. Paketoidaan ohjelma + Ohjeet.txt tiedostoon _build/app.zip.
  4. Kääritään asennusohjelmasta yksi klikattava
     Asenna-WebEditori.exe (asennusvelho + app.zip sisällä).
  5. Valmiit tiedostot kopioidaan kansioon Valmis-Asennuspaketti
     (Asenna-WebEditori.exe + Asenna-WebEditori.zip + LUE-TAMA.txt).
"""
import os
import sys
import shutil
import zipfile
import subprocess

KANSIO = os.path.dirname(os.path.abspath(__file__))
PROJEKTI = os.path.dirname(KANSIO)
EDITORI_PY = os.path.join(PROJEKTI, 'editori.py')
OHJEET_TXT = os.path.join(PROJEKTI, 'Ohjeet.txt')
BUILD = os.path.join(KANSIO, '_build')
VALMIS = os.path.join(KANSIO, 'Valmis-Asennuspaketti')
IKONI = os.path.join(KANSIO, 'ikoni.ico')

LUE_TEKSTI = r"""GRAAFINEN WEB-EDITORI 4.0 - ASENNUSPAKETTI
==========================================
Tehnyt Jani Malmberg

ASENTAMINEN (klikkaa ja asenna)
-------------------------------
1. Kaksoisnapsauta tiedostoa: Asenna-WebEditori.exe
2. Seuraa ohjattua asennusta: valitse asennuskansio ja pikakuvakkeet.
3. Kun asennus on valmis, ohjelma aukeaa tyopoydalta tai
   Kaynnista-valikosta (WebEditori).

Paketti sisaltaa KAIKKI ohjelman riippuvuudet (PyQt5-ymparisto ja
selainymparisto), joten Pythonia ei tarvitse asentaa erikseen.
Asennus ei vaadi jarjestelmanvalvojan oikeuksia (asennus omalle
kayttajatilille).

HILJAINEN ASENNUS (ilman valikoita)
-----------------------------------
Asenna-WebEditori.exe /hiljainen
Valinnaiset liput:
  /kohde=C:\oma\polku   asennuskansio
                        (oletus: %LOCALAPPDATA%\Programs\WebEditori)
  /eipikakuvia          ei pikakuvakkeita eika rekisterimerkintoja

OHJELMAN POISTAMINEN
--------------------
Aja asennuskansiossa: Poista-WebEditori.cmd
tai: Asetukset > Sovellukset > Graafinen web-editori > Poista.

KAYTTOOHJE
----------
Ohjeet.txt (asennuskansiossa, loytyy myos Apua-valikosta).
"""


def _aja(komento):
    print('  ' + ' '.join(komento))
    tulos = subprocess.run(komento, cwd=KANSIO)
    if tulos.returncode != 0:
        raise SystemExit('Komento epaonnistui: ' + ' '.join(komento))
# >>> JATKO <<<


def luo_ikoni():
    """Piirtaa yksinkertaisen ohjelmaikonin (sininen tausta, valkoinen W)."""
    if os.path.exists(IKONI):
        return
    from PIL import Image, ImageDraw, ImageFont
    kuva = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    piirra = ImageDraw.Draw(kuva)
    piirra.rounded_rectangle((10, 10, 246, 246), radius=52,
                             fill=(16, 92, 168, 255))
    piirra.rounded_rectangle((10, 10, 246, 246), radius=52,
                             outline=(10, 60, 115, 255), width=6)
    try:
        fontti = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 148)
    except Exception:
        fontti = ImageFont.load_default()
    piirra.text((128, 126), 'W', font=fontti, fill=(255, 255, 255, 255),
                anchor='mm')
    kuva.save(IKONI, format='ICO',
              sizes=[(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)])
    print('  Ikoni luotu: ' + IKONI)


def rakenna_sovellus():
    """Kaarittaa editorin itsenaiseksi ohjelmaksi (riippuvuudet mukana)."""
    _aja([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
          '--windowed', '--name', 'WebEditori', '--icon', IKONI,
          '--specpath', BUILD, '--distpath', os.path.join(BUILD, 'dist'),
          '--workpath', os.path.join(BUILD, 'tyo'), EDITORI_PY])


def tee_ohjelmazip():
    """Paketoi WebEditori-sovelluksen ja ohjeet tiedostoon _build/app.zip."""
    juuri = os.path.join(BUILD, 'dist', 'WebEditori')
    kohde = os.path.join(BUILD, 'app.zip')
    if os.path.exists(kohde):
        os.remove(kohde)
    with zipfile.ZipFile(kohde, 'w', zipfile.ZIP_DEFLATED,
                         compresslevel=6) as paketti:
        for juuri_kansio, _kansiot, tiedostot in os.walk(juuri):
            for nimi in tiedostot:
                polku = os.path.join(juuri_kansio, nimi)
                suhde = os.path.relpath(polku, juuri)
                paketti.write(polku, arcname=suhde)
        paketti.write(OHJEET_TXT, arcname='Ohjeet.txt')
    koko = os.path.getsize(kohde) / (1024.0 * 1024.0)
    print('  app.zip valmis (%.1f Mt)' % koko)
    return kohde


def rakenna_asennusohjelma(app_zip):
    """Kartittaa asennusvelhosta yhden klikattavan exe-tiedoston."""
    _aja([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
          '--onefile', '--windowed', '--name', 'Asenna-WebEditori',
          '--icon', IKONI,
          '--specpath', BUILD,
          '--distpath', os.path.join(BUILD, 'dist-asennus'),
          '--workpath', os.path.join(BUILD, 'tyo-asennus'),
          '--add-data', app_zip + ';.',
          '--add-data', IKONI + ';.',
          os.path.join(KANSIO, 'asennusohjelma.py')])


def jarjestele():
    """Kopioi valmiit tiedostot kansioon Valmis-Asennuspaketti."""
    os.makedirs(VALMIS, exist_ok=True)
    lahto = os.path.join(BUILD, 'dist-asennus', 'Asenna-WebEditori.exe')
    kohde = os.path.join(VALMIS, 'Asenna-WebEditori.exe')
    shutil.copyfile(lahto, kohde)
    with zipfile.ZipFile(os.path.join(VALMIS, 'Asenna-WebEditori.zip'),
                         'w', zipfile.ZIP_DEFLATED) as paketti:
        paketti.write(kohde, arcname='Asenna-WebEditori.exe')
    with open(os.path.join(VALMIS, 'LUE-TAMA.txt'), 'w',
              encoding='utf-8-sig', newline='\r\n') as tiedosto:
        tiedosto.write(LUE_TEKSTI)
    return kohde


def main():
    print('=== 1/5 Ikonin luonti ===')
    luo_ikoni()
    print('=== 2/5 Ohjelman paketointi (PyInstaller) ===')
    rakenna_sovellus()
    print('=== 3/5 Ohjelmapaketti app.zip ===')
    app_zip = tee_ohjelmazip()
    print('=== 4/5 Asennusohjelman paketointi (kestaa hetken) ===')
    rakenna_asennusohjelma(app_zip)
    print('=== 5/5 Valmiiden tiedostojen järjestely ===')
    exe = jarjestele()
    print('')
    print('VALMIS. Asennuspaketti:')
    print('  ' + exe)
    print('  ' + os.path.join(VALMIS, 'Asenna-WebEditori.zip'))
    print('  ' + os.path.join(VALMIS, 'LUE-TAMA.txt'))


if __name__ == '__main__':
    main()