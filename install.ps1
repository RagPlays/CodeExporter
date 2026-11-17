<#
.SYNOPSIS
    Installs (or removes) the "exportcode" command for the current user.

.DESCRIPTION
    Creates %LOCALAPPDATA%\ExportCode\bin\exportcode.cmd, which runs
    ExportCode.py from this folder, and adds that folder to your user PATH.
    No administrator rights needed. Keep this folder where it is, or run the
    script again after moving it. Open a NEW terminal afterwards.

.PARAMETER Uninstall
    Remove the launcher and the PATH entry.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall
#>
param([switch]$Uninstall)

$ErrorActionPreference = 'Stop'

$Name     = 'exportcode'
$Here     = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script   = Join-Path $Here 'ExportCode.py'
$BinDir   = Join-Path $env:LOCALAPPDATA 'ExportCode\bin'
$Launcher = Join-Path $BinDir "$Name.cmd"

function Get-UserPathEntries {
    $value = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($value) { @($value -split ';' | Where-Object { $_ }) } else { @() }
}

function Set-UserPathEntries([string[]]$Entries) {
    [Environment]::SetEnvironmentVariable('Path', ($Entries -join ';'), 'User')
}

function Find-Python {
    # Try the Windows "py" launcher first, then python / python3. Each candidate
    # is actually run, which skips the Microsoft Store stub that has no Python.
    foreach ($candidate in @('py -3', 'python', 'python3')) {
        $parts = $candidate -split ' '
        $exe   = $parts[0]
        $extra = @($parts | Select-Object -Skip 1)
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
        try {
            & $exe @extra -c 'import sys; sys.exit(sys.version_info < (3, 8))' 2>$null
            if ($LASTEXITCODE -eq 0) { return $candidate }
        } catch { }
    }
    return $null
}

if ($Uninstall) {
    if (Test-Path $Launcher) {
        Remove-Item $Launcher -Force
        Write-Host "Removed $Launcher"
    }
    $remaining = @(Get-UserPathEntries | Where-Object { $_ -ne $BinDir })
    Set-UserPathEntries $remaining
    if ((Test-Path $BinDir) -and -not (Get-ChildItem $BinDir)) { Remove-Item $BinDir -Force }
    Write-Host 'Done. Open a new terminal for the PATH change to apply.'
    return
}

if (-not (Test-Path $Script)) {
    throw "Cannot find $Script. Run this script from the project folder."
}

$python = Find-Python
if (-not $python) {
    throw 'Python 3.8 or newer was not found. Install it from https://www.python.org/downloads/ (tick "Add python.exe to PATH"), then run this script again.'
}

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

$lines = @(
    '@echo off',
    'setlocal',
    "set `"EXPORTCODE_PROG=$Name`"",
    "$python `"$Script`" %*",
    'exit /b %ERRORLEVEL%'
)
Set-Content -Path $Launcher -Value $lines -Encoding OEM
Write-Host "Installed command: $Launcher"
Write-Host "It runs: $python `"$Script`""

$entries = Get-UserPathEntries
if ($entries -notcontains $BinDir) {
    Set-UserPathEntries ($entries + $BinDir)
    Write-Host "Added $BinDir to your user PATH."
}

Write-Host ''
Write-Host "Ready. Open a NEW terminal and try:  $Name --help"
