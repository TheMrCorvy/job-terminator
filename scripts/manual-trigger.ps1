<#
.SYNOPSIS
    Convenient PowerShell wrapper for Job Terminator manual trigger.

.EXAMPLE
    # Test Strapi integration
    .\scripts\manual-trigger.ps1 -TestStrapi

    # Test Chrome CDP connection
    .\scripts\manual-trigger.ps1 -TestBrowser

    # Apply to latest job in Strapi
    .\scripts\manual-trigger.ps1 -LatestStrapi

    # Apply to a custom URL
    .\scripts\manual-trigger.ps1 -Url "https://linkedin.com/jobs/view/..."
#>

param (
    [switch]$TestBrowser,
    [switch]$TestStrapi,
    [switch]$LatestStrapi,
    [string]$Url,
    [string]$Title = "Software Engineer",
    [string]$Company = "",
    [string]$Mode = "semi-autonomous"
)

$pythonExe = Join-Path $PSScriptRoot "..\venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Error "Virtual environment not found at .\venv. Please run python -m venv venv first."
    exit 1
}

$scriptPath = Join-Path $PSScriptRoot "..\run_manual.py"

if ($TestBrowser) {
    & $pythonExe $scriptPath --test-browser
} elseif ($TestStrapi) {
    & $pythonExe $scriptPath --test-strapi
} elseif ($LatestStrapi) {
    & $pythonExe $scriptPath --latest-strapi --mode $Mode
} elseif ($Url) {
    & $pythonExe $scriptPath --url $Url --title $Title --company $Company --mode $Mode
} else {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\scripts\manual-trigger.ps1 -TestBrowser"
    Write-Host "  .\scripts\manual-trigger.ps1 -TestStrapi"
    Write-Host "  .\scripts\manual-trigger.ps1 -LatestStrapi"
    Write-Host "  .\scripts\manual-trigger.ps1 -Url 'https://...'`n"
    & $pythonExe $scriptPath --help
}
