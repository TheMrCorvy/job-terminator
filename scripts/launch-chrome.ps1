<#
.SYNOPSIS
    Launches Google Chrome with Remote Debugging (CDP) and a dedicated user profile.

.DESCRIPTION
    Chrome 136+ prohibits remote debugging on the default user profile for security.
    This script starts an isolated Chrome instance using a persistent automation profile
    at $HOME\.chrome-job-terminator. You can log into LinkedIn, Indeed, etc. once, and
    all cookies/sessions will be permanently preserved for Job Terminator.

.EXAMPLE
    .\scripts\launch-chrome.ps1
#>

param (
    [int]$Port = 9222,
    [string]$ProfileDir = "$HOME\.chrome-job-terminator"
)

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " 🤖 Job Terminator - Chrome CDP Launcher" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Locate Chrome executable
$chromeCandidates = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chromePath = $null
foreach ($path in $chromeCandidates) {
    if (Test-Path $path) {
        $chromePath = $path
        break
    }
}

if (-not $chromePath) {
    Write-Error "Google Chrome was not found at standard installation locations."
    Write-Host "Please install Google Chrome or update the path in this script." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found Chrome at: $chromePath" -ForegroundColor Green

# 2. Check if port is already active
$portCheck = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($portCheck) {
    Write-Host "`nPort $Port is already in use by process ID $($portCheck[0].OwningProcess)." -ForegroundColor Yellow
    Write-Host "Chrome remote debugging appears to already be running on port $Port." -ForegroundColor Green
    Write-Host "You can verify by opening: http://localhost:$Port/json/version" -ForegroundColor Cyan
    exit 0
}

# 3. Create profile directory if missing
if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
    Write-Host "Created dedicated automation profile directory at: $ProfileDir" -ForegroundColor Yellow
} else {
    Write-Host "Using dedicated automation profile directory at: $ProfileDir" -ForegroundColor Yellow
}

# 4. Launch Chrome with CDP
Write-Host "`nLaunching Chrome on port $Port with profile: $ProfileDir..." -ForegroundColor Green
Write-Host "TIP: Log into your job sites (LinkedIn, Indeed, Glassdoor, etc.) in this window." -ForegroundColor Yellow
Write-Host "Your sessions and cookies will be automatically remembered.`n" -ForegroundColor Yellow

$chromeArgs = @(
    "--remote-debugging-port=$Port",
    "--user-data-dir=$ProfileDir",
    "--no-first-run",
    "--no-default-browser-check"
)

Start-Process -FilePath $chromePath -ArgumentList $chromeArgs

# 5. Wait briefly and verify listener
Start-Sleep -Seconds 2
$portVerification = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($portVerification) {
    Write-Host "SUCCESS: Chrome is actively listening for CDP on port $Port!" -ForegroundColor Green
    Write-Host "CDP Endpoint: http://localhost:$Port" -ForegroundColor Cyan
} else {
    Write-Host "Notice: Chrome was launched. Verify CDP connection at http://localhost:$Port/json/version" -ForegroundColor Yellow
}
