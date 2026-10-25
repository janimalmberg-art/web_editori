# 🌐 Graafinen Web-Editori 4.0

**Tee kotisivuja ilman HTML-osaamista!**

Graafinen web-editori on kokonaan suomeksi tehty WYSIWYG-webeditori
Windowsille. Muokkaat suoraan sivun näkymää (klikkaa ja kirjoita), ja
HTML-koodi päivittyy reaaliajassa vasemmassa ikkunassa. Valmiit sivut
toimivat yleisimmillä selaimilla (Chrome, Firefox, Edge, Safari).

> *A WYSIWYG web page editor for Windows, made in Finnish. Edit visually,
> HTML updates live. No coding skills needed.*

Tehnyt **Jani Malmberg** · GitHub: [janimalmberg-art](https://github.com/janimalmberg-art)

---

## 📥 Lataa ja asenna (suositus)

1. Avaa [**Releases-sivu**](https://github.com/janimalmberg-art/web_editori/releases/latest)
2. Lataa tiedosto **Asenna-WebEditori.exe** (tai **Asenna-WebEditori.zip**)
3. Kaksoisnapsauta ja seuraa ohjattua asennusta

- ✅ Kaikki riippuvuudet mukana — **Pythonia ei tarvitse asentaa**
- ✅ Ei vaadi järjestelmänvalvojan oikeuksia (asentuu omalle käyttäjätilille)
- ✅ Graafinen asennusvelho + hiljainen asennus: `Asenna-WebEditori.exe /hiljainen`
- ✅ Poisto: Asetukset > Sovellukset > Graafinen web-editori

## ✨ Ominaisuudet

- 🖱️ **Klikkaa ja kirjoita** — muokkaus suoraan sivunäkymässä, koodi päivittyy reaaliajassa
- 📝 Tekstin muotoilu: lihavointi, kursivointi, värit, otsikot (H1–H6), linkit
- 🖼️ Kuvat tiedostosta tai verkosta (kuvat upotetaan suoraan sivuun), kuvatekstit
- 📊 Taulukot, galleriat, teksti- ja objektikehykset
- 🎬 Videot: YouTube-upotukset ja suorat .mp4/.webm-tiedostot
- 📅 Valmiit kalenterit
- 🧭 Graafinen ylävalikko + alasivut (osiot) automaattisilla valikkolinkeillä
- ↕️ Alueiden siirto ylös/alas, kopiointi, poisto ja kumoa (Ctrl+Z)
- 🎨 Elementtien tekstin, taustan ja korostuksen väritys
- 🖥️ Kokonäkymä (F8) — koko sivu omassa ikkunassaan, muokattavissa suoraan
- 🪟 Word-tyyliset liukusäätimet ja kelluvat ikkunat
- 💾 Tallennus HTML-, XHTML-, PHP- ja PDF-muotoon
- 📖 Kattavat suomenkieliset ohjeet ohjelman Apua-valikossa

## 🚀 Käynnistys lähdekoodista (kehittäjille)

Vaatii Python 3:n ja PyQt5-kirjastot:

```bat
pip install PyQt5 PyQtWebEngine PyQtWebChannel pillow
Käynnistä-Editori.bat
```

tai suoraan: `python editori.py`

## 🔨 Asennuspaketin rakentaminen

Kansiossa `WebEditori-Asennus` on työkalut, joilla editori paketoidaan
itsenäiseksi Windows-asennusohjelmaksi:

```bat
cd WebEditori-Asennus
python rakenna.py
```

- `rakenna.py` rakentaa editorin PyInstallerilla ja tuottaa
  `Valmis-Asennuspaketti\Asenna-WebEditori.exe` -asennusohjelman
- Asennusvelho (PyQt5): Tervetuloa → Asennuskansio → Valinnat → Asennus → Valmis
- Hiljaisen asennuksen, poiston ja automaattiset testit löydät
  [WebEditori-Asennus/Asennusohjeet.txt](WebEditori-Asennus/Asennusohjeet.txt)

### 🤖 Automaattinen rakennus + GitHub-julkaisu (yhdellä komennolla)

Repon juuressa on valmis automaattikomento, joka tekee kaiken:

```bat
Tee-Asennuspaketti.cmd
```

Tai komentoriviltä: `powershell -NoProfile -ExecutionPolicy Bypass -File WebEditori-Asennus\tee_asennuspaketti.ps1`

Automaatti:
1. **Rakentaa** asennuspaketin `Asenna-WebEditori.exe` + `.zip` (PyInstaller, riippuvuudet mukana)
2. **Tallentaa** muutokset GitHubiin (commit + push `main`-haaraan)
3. **Julkaisee** uuden GitHub Releaseän (tagit kasvatetaan automaattisesti: `v4.0` → `v4.0.1` → …) ja lataa liitteeksi `Asenna-WebEditori.exe`, `Asenna-WebEditori.zip` ja `LUE-TAMA.txt`

Tunnukset luetaan Windowsin git-tunnisteista (credential manager). Valinnaiset liput:
`-EiRakennusta` (käytä olemassa olevaa pakettia), `-EiGitia`, `-EiJulkaisua`, `-Tagi v4.0.1` (pakota versiointi).

## 📁 Kansion sisältö

| Tiedosto/kansio | Kuvaus |
|---|---|
| `editori.py` | Pääohjelma (versio 4.0) |
| `osat/` | Ohjelman lähdekoodin osat (p01–p13) |
| `Ohjeet.txt` | Käyttöohje (löytyy myös Apua-valikosta) |
| `Käynnistä-Editori.bat` | Käynnistys Python-ympäristössä |
| `testaa_ohjelma.py` | Automaattinen testiajo |
| `WebEditori-Asennus/` | Asennuspaketin rakennustyökalut ja ohjeet |

## 🛠️ Tekniset tiedot

- **Kieli:** Python 3 + PyQt5 / PyQtWebEngine
- **Asennuskohde:** `%LOCALAPPDATA%\Programs\WebEditori`
- **Rekisteröinti (valinnainen):** ohjelma näkyy Windowsin "Sovellukset"-luettelossa
- **Lisenssi:** vapaa henkilökohtaiseen käyttöön
- **Versio:** 4.0 (2026)

## 🏷️ Avainsanat

web-editori · kotisivut · HTML-editori · WYSIWYG · sivunmuokkaus ·
Python · PyQt5 · Windows · suomenkielinen · ilmainen ·
website builder · HTML editor · offline