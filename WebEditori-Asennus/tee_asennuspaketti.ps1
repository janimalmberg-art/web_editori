# ============================================================
# TEE-ASENNUSPAKETTI - automaattinen rakennus- ja julkaisuskripti
# Graafinen Web-Editori 4.0 (Jani Malmberg)
#
# Tekee yhdella komennolla:
#   1) Rakentaa asennuspaketin Asenna-WebEditori.exe (+ .zip)
#      (rakenna.py -> PyInstaller, riippuvuudet mukana)
#   2) Tallentaa muutokset GitHub-repoon (commit + push)
#   3) Luo GitHub Releaseen ja lataa asennuspaketin liitteiksi
#
# Kaytto (repon juuressa)
#   powershell -NoProfile -ExecutionPolicy Bypass -File `
#     WebEditori-Asennus\tee_asennuspaketti.ps1
#   ... tai tuplaklikkaa repon juuressa: Tee-Asennuspaketti.cmd
#
# Valinnaiset liput:
#   -EiRakennusta  ei rakenneta uudelleen (ka ytetaan olemassa olevaa)
#   -EiGitia       ei committaa eika puata git
#   -EiJulkaisua   ei luoda GitHub Releasea
#   -Tagi v4.0.1   pakota julkaisutagi (oletus: kasistys taclistauksesta)
# ============================================================
param(
    [switch]$EiRakennusta,
    [switch]$EiGitia,
    [switch]$EiJulkaisua,
    [string]$Tagi
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$AsennusKansio = $PSScriptRoot
if (-not $AsennusKansio) { $AsennusKansio = (Get-Location).Path }
$Projekti = Split-Path $AsennusKansio -Parent
$Valmis   = Join-Path $AsennusKansio 'Valmis-Asennuspaketti'
$OnRepo   = Test-Path (Join-Path $Projekti '.git')

function Aikaleima { '[' + (Get-Date -Format 'HH:mm:ss') + ']' }

Write-Output '============================================================'
Write-Output ('ASENNUSPAKETIN AUTOMAATTINEN RAKENNUS - ' + (Get-Date -Format 'd.M.yyyy HH:mm'))
Write-Output ('Projekti: ' + $Projekti)
Write-Output '============================================================'

# ------------------------------------------------------------
# VAIHE 1/3: Rakenna asennuspaketti (PyInstaller)
# ------------------------------------------------------------
if (-not $EiRakennusta) {
    Write-Output ((Aikaleima) + ' VAIHE 1/3: Rakennetaan asennuspaketti (kestaa muutaman minuutin)...')
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { throw 'Pythonia ei loydy PATH-vakayhteydesta.' }
    & python -c "import PyInstaller" *> $null
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller puuttuu: asenna komennolla  pip install pyinstaller' }
    Push-Location $AsennusKansio
    try {
        & python rakenna.py
        if ($LASTEXITCODE -ne 0) { throw ('rakenna.py palautti virhekoodin ' + $LASTEXITCODE) }
    } finally { Pop-Location }
} else {
    Write-Output ((Aikaleima) + ' VAIHE 1/3: rakennus ohitettiin (-EiRakennusta)')
}

$tiedostoExe = Join-Path $Valmis 'Asenna-WebEditori.exe'
$tiedostoZip = Join-Path $Valmis 'Asenna-WebEditori.zip'
$tiedostoLue = Join-Path $Valmis 'LUE-TAMA.txt'
foreach ($f in @($tiedostoExe, $tiedostoZip, $tiedostoLue)) {
    if (-not (Test-Path $f)) { throw ('Puuttuva valmis tiedosto: ' + $f + '   (aja rakennus ilman -EiRakennusta-lippua)') }
}
foreach ($f in @($tiedostoExe, $tiedostoZip)) {
    $mt = '{0:N1} Mt' -f ((Get-Item $f).Length / 1MB)
    Write-Output ((Aikaleima) + ('   valmis: ' + [System.IO.Path]::GetFileName($f) + '  (' + $mt + ')'))
}

# ------------------------------------------------------------
# VAIHE 2/3: Tallenna muutokset GitHub-repoon
# ------------------------------------------------------------
if ($OnRepo -and -not $EiGitia) {
    Write-Output ((Aikaleima) + ' VAIHE 2/3: Git commit + push...')
    Push-Location $Projekti
    try {
        git add -A | Out-Null
        $muutokset = @(git status --porcelain)
        $haara = git rev-parse --abbrev-ref HEAD
        if ($muutokset.Count -gt 0) {
            git commit -m ('Asennuspaketti rakennettu automaattisesti ' + (Get-Date -Format 'd.M.yyyy HH:mm')) | Out-Null
            Write-Output ((Aikaleima) + '   commit tehty')
        } else {
            Write-Output ((Aikaleima) + '   ei uusia muutoksia commitoitavaksi')
        }
        git push origin $haara
        Write-Output ((Aikaleima) + ('   push ok -> origin/' + $haara))
    } finally { Pop-Location }
} else {
    Write-Output ((Aikaleima) + ' VAIHE 2/3: git-osa ohitettiin')
}

# ------------------------------------------------------------
# VAIHE 3/3: GitHub Release + liitteet
# ------------------------------------------------------------
$releaseHtml = $null
if ($OnRepo -and -not $EiJulkaisua) {
    Write-Output ((Aikaleima) + ' VAIHE 3/3: GitHub-julkaisu (julkaise_githubissa.ps1)...')
    & (Join-Path $AsennusKansio 'julkaise_githubissa.ps1') -Projekti $Projekti -Valmis $Valmis -Tagi $Tagi
    if ($LASTEXITCODE -ne 0) { Write-Warning ('Julkaisusripti palautti koodin ' + $LASTEXITCODE) }
    $urlTiedosto = Join-Path $Valmis '_release_url.txt'
    if (Test-Path $urlTiedosto) { $releaseHtml = (Get-Content $urlTiedosto -Raw).Trim() }
}

# ------------------------------------------------------------
# YHTEENVETO
# ------------------------------------------------------------
Write-Output ''
Write-Output '============================================================'
Write-Output 'ASENNUSPAKETTI-PUTKI VALMIS'
Write-Output ('  Asennuspaketti : ' + $tiedostoExe)
Write-Output ('  Zip-paketti    : ' + $tiedostoZip)
if ($releaseHtml) { Write-Output ('  GitHub Release : ' + $releaseHtml) }
Write-Output '============================================================'
Write-Output 'PIPELINE-VALMIS ok'