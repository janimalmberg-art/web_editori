# ============================================================
# LATAA RELELIITTEET - curl-pohjainen luotettava lataaja.
# PS 5.1:n Invoke-RestMethod jumittaa isot tiedostot GitHubin
# uploads-pisteeseen (- ~10 kt/s), curl paastelee ne lapi oikein.
#
# Kaytto: powershell -File lataa_liitteet_curl.ps1 `
#          -Valmis <Valmis-Asennuspaketti> [-Tagi v4.0.1]
# Tunnukset git-credential-managerilta; token ei tallennu levylle.
# ============================================================
param(
    [Parameter(Mandatory = $true)][string]$Valmis,
    [string]$Tagi = 'v4.0.1',
    [string[]]$Nimet = @('Asenna-WebEditori.exe', 'Asenna-WebEditori.zip')
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
function Aikaleima { '[' + (Get-Date -Format 'HH:mm:ss') + ']' }
$api = 'https://api.github.com/repos/janimalmberg-art/web_editori'

# tunnus
$credRaw = ("protocol=https`nhost=github.com`n" | git credential fill) 2>$null
if ($LASTEXITCODE -ne 0 -or -not $credRaw) { throw 'GitHub-tunnuksia ei saatu credential managerilta.' }
$token = ($credRaw | Where-Object { $_ -like 'password=*' }) -replace '^password=', ''
if (-not $token) { throw 'Token puuttuu.' }

# releen upload_url
$kierros = @{ Authorization = "Bearer $token"; 'User-Agent' = 'web-editori-autobuild'; Accept = 'application/vnd.github+json' }
$relet = @(Invoke-RestMethod -Uri "$api/releases?per_page=30" -Headers $kierros)
$rele = $relet | Where-Object { $_.tag_name -eq $Tagi } | Select-Object -First 1
if (-not $rele) { throw ('Relea ' + $Tagi + ' ei loytynyt.') }
Write-Output ((Aikaleima) + (' rele loytyi: ' + $rele.html_url))

# jo ladatut liitteet ohi
$olevatAssets = @{}; foreach ($a in $rele.assets) { $olevatAssets[$a.name] = $a.size }

# curl-otsikkotiedosto (poistetaan aina lopussa)
$otsTiedosto = Join-Path $env:TEMP ('curl-otsikot-' + [Guid]::NewGuid().ToString('N') + '.txt')
@(
    'Authorization: Bearer ' + $token
    'Content-Type: application/octet-stream'
) | Set-Content -Path $otsTiedosto -Encoding ASCII

try {
    foreach ($nimi in $Nimet) {
        $tiedosto = Join-Path $Valmis $nimi
        if (-not (Test-Path $tiedosto)) { Write-Warning ('   ohitetaan, puuttuu: ' + $tiedosto); continue }
        $pituus = (Get-Item $tiedosto).Length
        if ($olevatAssets.ContainsKey($nimi) -and $olevatAssets[$nimi] -eq $pituus) {
            Write-Output ((Aikaleima) + ('   jo valmis, ohitetaan: ' + $nimi)); continue
        }
        $uplUrl = ($rele.upload_url -replace '\{\?name,label\}', ('?name=' + $nimi))
        $mt = '{0:N1} Mt' -f ($pituus / 1MB)
        Write-Output ((Aikaleima) + ('   curl lahettaa: ' + $nimi + ' (' + $mt + ')...'))
        $alku = Get-Date
        & curl.exe -s -S -X POST -H ("@{0}" -f $otsTiedosto) `
            --data-binary ("@{0}" -f $tiedosto) `
            --max-time 7200 --connect-timeout 30 `
            --speed-limit 10240 --speed-time 90 `
            --retry 5 --retry-delay 10 `
            $uplUrl > $null
        if ($LASTEXITCODE -ne 0) { throw ("curl epaonnistui ($nimi), koodi $LASTEXITCODE") }
        $kesto = [int]((Get-Date) - $alku).TotalSeconds
        Write-Output ((Aikaleima) + ('   valmis ' + $nimi + ' kesti ' + $kesto + ' s'))

        # todenna koko API:sta
        $asset = Invoke-RestMethod -Uri "$api/releases/$($rele.id)/assets" -Headers $kierros |
                 Where-Object { $_.name -eq $nimi }
        if (-not $asset -or $asset.size -ne $pituus) { throw ($nimi + ': liitteen koko ei tasmaa palvelimella!') }
        Write-Output ((Aikaleima) + ('   api-vahvistus ok (' + [int]($asset.size / 1MB) + ' Mt)'))
    }
    Write-Output ((Aikaleima) + ' KAIKKI LIITTEET VALMIIT')
} finally {
    Remove-Item $otsTiedosto -Force -ErrorAction SilentlyContinue
}
exit 0