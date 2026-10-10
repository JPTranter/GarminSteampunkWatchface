<#
push_watch.ps1 — sideload the built watch face onto a connected Garmin watch, then verify it landed.

WHY: Garmin watches (Venu Sq 2 family) present as an MTP/WPD device, not a drive letter, so `cp` and
Explorer-by-path do not work and a copy cannot be trusted without reading it back. This script finds
the device under "This PC" by name, walks into <Internal Storage>\GARMIN\APPS, copies the .prg, then
pulls it back and compares SHA-256 with the local file — so "it's on the watch" is a verified claim.

Usage (from ciq\, PowerShell):
    powershell -ExecutionPolicy Bypass -File push_watch.ps1
    powershell -ExecutionPolicy Bypass -File push_watch.ps1 -Device 'Venu Sq 2' -Prg .\SteampunkNixie.prg

If it reports "device not found": the watch must be plugged in AND awake, and Windows must show it in
This PC. If This PC shows it but the script cannot walk into it, unplug/replug the cable — a watch
that drops MTP leaves a USB device that the shell can no longer bind to (visible only via
Get-PnpDevice, class WPD).

Build first, for the watch's own device id:
    monkeyc.bat -d venusq2m -f monkey.jungle -o SteampunkNixie.prg -y keys/developer_key.der
(venusq2m = Venu Sq 2 Music, part 006-B4116-00; venusq2 = Venu Sq 2, part 006-B4115-00. Read
GARMIN\GarminDevice.xml on the watch to be sure.)
#>
param(
    [string]$Device = 'Venu Sq 2',
    [string]$Prg = (Join-Path $PSScriptRoot 'SteampunkNixie.prg'),
    [string]$Dest = 'GARMIN\APPS',
    [switch]$SkipVerify
)

$ErrorActionPreference = 'Stop'
$sh = New-Object -ComObject Shell.Application

if (-not (Test-Path -LiteralPath $Prg)) { Write-Error "not found: $Prg (build first)"; exit 1 }
$localHash = (Get-FileHash -LiteralPath $Prg -Algorithm SHA256).Hash
Write-Output ("local:  {0}  {1} bytes  sha256 {2}" -f (Split-Path $Prg -Leaf), (Get-Item $Prg).Length, $localHash.Substring(0, 16))

# --- find the device under This PC
$dev = $sh.NameSpace(17).Items() | Where-Object { $_.Name -like "$Device*" } | Select-Object -First 1
if (-not $dev) {
    Write-Output "device '$Device' not found under This PC. Currently: $(($sh.NameSpace(17).Items() | ForEach-Object { $_.Name }) -join ', ')"
    $pnp = Get-PnpDevice -Class WPD -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'Garmin|Venu' }
    # ASCII only inside strings: Windows PowerShell 5.1 reads a BOM-less UTF-8 script as ANSI, and an
    # em-dash here broke the quoting of the whole file (parse error at line 82).
    if ($pnp) { Write-Output "but it IS on the USB bus ($($pnp.FriendlyName)) - unplug/replug the cable so Windows re-presents it"; }
    exit 1
}

# --- walk to <storage>\GARMIN\APPS
$cur = $dev.GetFolder
$inner = $cur.ParseName('Internal Storage')
if ($inner) { $cur = $inner.GetFolder }
foreach ($part in $Dest.Split('\')) {
    $next = $cur.ParseName($part)
    if (-not $next) {
        Write-Output "creating $part"
        $cur.NewFolder($part) | Out-Null
        Start-Sleep -Seconds 1
        $next = $cur.ParseName($part)
    }
    $cur = $next.GetFolder
}
Write-Output ("device: {0}\{1}" -f $Device, $Dest)

# --- copy, then verify by reading it back
$cur.CopyHere($Prg, 16)                       # 16 = "Yes to all" (silent overwrite)
# Read back into a private folder. Shell CopyHere keeps the SOURCE file name, so the readback lands
# as <dir>\<leaf> - looking for any other name (this script used to expect 'ciq_verify_<leaf>')
# reports a failed verify on a push that actually succeeded.
$vdir = Join-Path $env:TEMP 'ciq_verify'
New-Item -ItemType Directory -Force -Path $vdir | Out-Null
$temp = Join-Path $vdir (Split-Path $Prg -Leaf)
Remove-Item -LiteralPath $temp -ErrorAction SilentlyContinue
for ($i = 0; $i -lt 90; $i++) { Start-Sleep -Seconds 1; if ($cur.ParseName((Split-Path $Prg -Leaf))) { Start-Sleep -Seconds 2; break } }
$item = $cur.ParseName((Split-Path $Prg -Leaf))
if (-not $item) { Write-Output 'PUSH FAILED: the .prg is not present on the device'; exit 1 }
Write-Output ("on device: {0}  modified {1}" -f $item.Name, $item.ModifyDate)

if ($SkipVerify) { Write-Output 'pushed (unverified)'; exit 0 }

# Read back until the device copy matches, for up to ~2 minutes. When the .prg is OVERWRITING an
# earlier build, "the file is present" is true immediately - it is the OLD file - so a single
# readback right after CopyHere returns the previous build's hash and reports a false MISMATCH
# while the MTP copy is still in flight.
$devHash = $null
for ($attempt = 1; $attempt -le 12; $attempt++) {
    Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
    $item = $cur.ParseName((Split-Path $Prg -Leaf))
    $sh.NameSpace($vdir).CopyHere($item, 16)
    for ($i = 0; $i -lt 90; $i++) { if ((Test-Path -LiteralPath $temp) -and (Get-Item $temp).Length -gt 0) { break }; Start-Sleep -Seconds 1 }
    if (-not (Test-Path -LiteralPath $temp)) { Write-Output 'VERIFY FAILED: could not read the file back (device dropped?)'; exit 1 }
    Start-Sleep -Seconds 1
    $devHash = (Get-FileHash -LiteralPath $temp -Algorithm SHA256).Hash
    if ($devHash -eq $localHash) { break }
    Write-Output ("  readback {0}: device still has {1}, waiting for the copy to land" -f $attempt, $devHash.Substring(0, 16))
    Start-Sleep -Seconds 10
}
Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
if ($devHash -eq $localHash) {
    Write-Output ("VERIFIED: the copy on the watch is identical (sha256 {0})" -f $devHash.Substring(0, 16))
    Write-Output 'Now switch to it on the watch: long-press the watch face -> Watch Face -> Steampunk Nixie'
} else {
    Write-Output ("MISMATCH: local {0} vs device {1}" -f $localHash.Substring(0, 16), $devHash.Substring(0, 16))
    exit 1
}
