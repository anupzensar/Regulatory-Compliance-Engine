# PowerShell script for the unified Regulatory Compliance Engine

Write-Host "Building and running Regulatory Compliance Engine (Unified Architecture)..." -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Building React app..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Step 2: Starting Electron app..." -ForegroundColor Yellow
npm run electron

Read-Host "Press Enter to exit"
