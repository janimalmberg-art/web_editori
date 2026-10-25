# ============================================================
# JULKAISE GITHUBISSA - luo Releaseen ja lataa asennuspaketin
# liitteiksi (Asenna-WebEditori.exe / .zip / LUE-TAMA.txt).
# Kaytetaan tee_asennuspaketti.ps1 -skirptista; voi ajaa myos
# erikseen:
#   powershell -File julkaise_githubissa.ps1 `
#     -Projekti <repon juuri> -Valmis <Valmis-Asennuspaketti>
#   ... -Tagi v4.0.1   (pakota tagi)
# Tunnukset luetaan Windowsin git-credential-managerilta;
# salasanaa EI tulosteta milloinkaan.
# ============================================================
param(
    [Parameter(Mandatory = $true)][string]$Projekti,
    [Parameter(Mandatory = $true)][string]$Valmis,
    [string]$Tagi
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

function Aikaleima { '[' + (Get-Date -Format 'HH:mm:ss') + ']' }

# --- owner/repo remotesta ---
Push-Location $Projekti
try {
    $remoteUrl = git remote get-url origin
    $haara = git rev-parse --abbrev-ref HEAD
} finally { Pop-Location }
if ($remoteUrl -notmatch 'github\.com[:/](.+)/(.+?)(?:\.git)?/?$') {
    throw ('Remote URL ei ole GitHub-repon URL: ' + $remoteUrl)
}
$omistaja = $Matches[1]; $reponNimi = $Matches[2]
$api = "https://api.github.com/repos/$omistaja/$reponNimi"

# --- tunnus credential-managerilta (sisaan, ei ulos) ---
$credRaw = ("protocol=https`nhost=github.com`n" | git credential fill) 2>$null
if ($LASTEXITCODE -ne 0 -or -not $credRaw) {
    Write-Warning 'GitHub-tunnuksia ei saatu (git credential fill) - julkaisu ohitetaan.'
    exit 0
}
$token = ($credRaw | Where-Object { $_ -like 'password=*' }) -replace '^password=', ''
if (-not $token) { Write-Warning 'Token puuttuu credential managerista - julkaisu ohitetaan.'; exit 0 }
$ots = @{ Authorization = "Bearer $token"; 'User-Agent' = 'web-editori-autobuild'; Accept = 'application/vnd.github+json' }

# --- olemassa olevat tagit -> seuraava versiotagi ---
$olevat = @()
try { $olevat = @(Invoke-RestMethod -Uri "$api/tags?per_page=100" -Headers $ots).name } catch { $olevat = @() }
$versiot = @($olevat | Where-Object { $_ -match '^v\d+(\.\d+)*$' })
if (-not $Tagi) {
    if ($versiot.Count -gt 0) {
        $viime = $versiot[0]
        if ($viime -match '^v(\d+)\.(\d+)(?:\.(\d+))?$') {
            $a = [int]$Matches[1]; $b = [int]$Matches[2]
            $c = if ($Matches[3]) { [int]$Matches[3] } else { 0 }
            $c++; $Tagi = "v$a.$b.$c"
            while ($versiot -contains $Tagi) { $c++; $Tagi = "v$a.$b.$c" }
        } else { $Tagi = 'v4.0' }
    } else { $Tagi = 'v4.0' }
}
Write-Output ((Aikaleima) + ('   julkaisutagi: ' + $Tagi))

# --- luodaan release ---
$muistiinpanot = @'
Graafinen Web-Editori 4.0 - automaattinen asennuspaketti

Rakennettu ja julkaistu automaattisesti $(d.M.yyyy placeholder).
Kaikki riippuvuudet mukana; Pythonia ei tarvitse asentaa.
Ei vaadi jarjestelmanvalvojan oikeuksia.

ASENTAMINEN
  1. Lataa Asenna-WebEditori.exe (tai .zip ja pura se ensin)
  2. Kaksoisnapsauta ja seuraa ohjattua asennusta
  3. Ohjelma aukeaa tyopoydalta / Kaynnista-valikosta (WebEditori)

HILJAINEN ASENNUS
  Asenna-WebEditori.exe /hiljainen
  Valinnaiset: /kohde=C:\oma\polku  /eipikakuvia

POISTO
  Asetukset > Sovellukset > Graafinen web-editori > Poista
  tai asennuskansion Poista-WebEditori.cmd

Tehnyt Jani Malmberg
'@
$muistiinpanot = $muistiinpanot.Replace('$(d.M.yyyy placeholder)', (Get-Date -Format 'd.M.yyyy'))
$rele = @{
    tag_name    = $Tagi
    name        = "Graafinen Web-Editori 4.0 - asennuspaketti ($Tagi)"
    body        = $muistiinpanot
    draft       = $false
    prerelease  = $false
} | ConvertTo-Json
$uusiRelease = Invoke-RestMethod -Method Post -Uri "$api/releases" -Headers $ots -ContentType 'application/json' -Body $rele
Write-Output ((Aikaleima) + ('   release luotu: ' + $uusiRelease.html_url))

# --- liitteiden lataus (exe viimeksi, isoin) ---
foreach ($nimi in @('LUE-TAMA.txt', 'Asenna-WebEditori.zip', 'Asenna-WebEditori.exe')) {
    $tiedosto = Join-Path $Valmis $nimi
    if (-not (Test-Path $tiedosto)) { Write-Warning ('   liite puuttuu, ohitetaan: ' + $tiedosto); continue }
    $mt = '{0:N1} Mt' -f ((Get-Item $tiedosto).Length / 1MB)
    Write-Output ((Aikaleima) + ('   ladataan: ' + $nimi + ' (' + $mt + ')...'))
    $lataaUrl = ($uusiRelease.upload_url -replace '\{\?name,label\}', ('?name=' + $nimi))
    $yritys = 0
    while ($true) {
        $yritys++
        try {
            Invoke-RestMethod -Method Post -Uri $lataaUrl -Headers $ots -ContentType 'application/octet-stream' -InFile $tiedosto | Out-Null
            break
        } catch {
            if ($yritys -ge 3) { throw ('Liitteen lataus epaonnistui (' + $nimi + '): ' + $_.Exception.Message) }
            Write-Output ((Aikaleima) + '   yritys ' + $yritys + ' epaonnistui, odotetaan ja yritetaan uudelleen...')
            Start-Sleep -Seconds (15 * $yritys)
        }
    }
}

Write-Output ((Aikaleima) + '   kaikki liitteet ladattu')
# Julkaisun URL talteen pakettilaitteelle (ja tarvittaessa yhteenvedon takia)
$ulostiedosto = Join-Path $Valmis '_release_url.txt'
Set-Content -Path $ulostiedosto -Value $uusiRelease.html_url -Encoding UTF8
exit 0