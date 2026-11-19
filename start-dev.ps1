# Script to start development backend and frontend on Windows (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "LAZOS - Starting development environment on Windows" -ForegroundColor Green
Write-Host ""

# Verify directories
if (-not (Test-Path "lazos-api") -or -not (Test-Path "lazos-web")) {
    Write-Error "Error: Please run from the project root directory (lazos/)"
    exit 1
}

# Function to stop processes on a port
function Stop-PortProcess {
    param (
        [int]$Port
    )
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections.OwningProcess | Select-Object -Unique
        foreach ($procId in $pids) {
            $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Stopping existing process on port $Port and its children (PID: $procId - $($proc.Name))..." -ForegroundColor Yellow
                taskkill.exe /F /PID $procId /T | Out-Null
            }
        }
    }
}

# Stop old instances
Write-Host "Checking ports..." -ForegroundColor Cyan
Stop-PortProcess 8000
Stop-PortProcess 5173

# Start Backend
Write-Host "Starting Backend (API)..." -ForegroundColor Blue
Push-Location lazos-api

# Check .env
if (-not (Test-Path ".env")) {
    Write-Host "No .env found, copying from .env.example" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please configure credentials in lazos-api/.env" -ForegroundColor Yellow
}

# Check virtual environment
if (Test-Path "venv") {
    Write-Host "Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found. Creating venv..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Virtual environment created. Installing requirements..." -ForegroundColor Green
    & "venv/Scripts/pip.exe" install -r requirements.txt
}

$backendLog = Resolve-Path "..\backend.log" -ErrorAction SilentlyContinue
if (-not $backendLog) { $backendLog = Join-Path (Get-Location).Path "..\backend.log" }
$backendErrLog = Resolve-Path "..\backend.err.log" -ErrorAction SilentlyContinue
if (-not $backendErrLog) { $backendErrLog = Join-Path (Get-Location).Path "..\backend.err.log" }

# Clear old logs if they exist
if (Test-Path $backendLog) { Remove-Item $backendLog -ErrorAction SilentlyContinue }
if (Test-Path $backendErrLog) { Remove-Item $backendErrLog -ErrorAction SilentlyContinue }

# Start backend in background and redirect output directly
Write-Host "Starting API on port 8000..." -ForegroundColor Cyan
Start-Process -FilePath "venv\Scripts\python.exe" -ArgumentList "-u", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000" -RedirectStandardOutput $backendLog -RedirectStandardError $backendErrLog -WindowStyle Hidden
Write-Host "Backend started in background. Logs in backend.log" -ForegroundColor Green

Pop-Location

# Wait for backend to start
Start-Sleep -Seconds 3

# Check if API responds
$apiHealthy = $false
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($response) {
        Write-Host "API responding on http://localhost:8000" -ForegroundColor Green
        $apiHealthy = $true
    }
} catch {
    # Ignore error
}

if (-not $apiHealthy) {
    Write-Host "API not responding yet, it may take a few seconds to start up" -ForegroundColor Yellow
}

# Start Frontend
Write-Host ""
Write-Host "Starting Frontend (Web)..." -ForegroundColor Blue
Push-Location lazos-web

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Cyan
    npm install
}

$frontendLog = Resolve-Path "..\frontend.log" -ErrorAction SilentlyContinue
if (-not $frontendLog) { $frontendLog = Join-Path (Get-Location).Path "..\frontend.log" }
$frontendErrLog = Resolve-Path "..\frontend.err.log" -ErrorAction SilentlyContinue
if (-not $frontendErrLog) { $frontendErrLog = Join-Path (Get-Location).Path "..\frontend.err.log" }

# Clear old logs if they exist
if (Test-Path $frontendLog) { Remove-Item $frontendLog -ErrorAction SilentlyContinue }
if (Test-Path $frontendErrLog) { Remove-Item $frontendErrLog -ErrorAction SilentlyContinue }

# Start frontend in background and redirect output directly
Write-Host "Starting web app on port 5173..." -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendErrLog -WindowStyle Hidden
Write-Host "Frontend started in background. Logs in frontend.log" -ForegroundColor Green

Pop-Location

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "Development environment started successfully" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend:    http://localhost:5173" -ForegroundColor Blue
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Blue
Write-Host "API Docs:    http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "To stop all services, run: .\stop-dev.ps1" -ForegroundColor Yellow
Write-Host "Showing frontend logs (Press Ctrl+C to exit log tailing, servers will keep running)..." -ForegroundColor Cyan
Write-Host ""

# Ensure the log file exists before tailing
$logPath = "frontend.log"
$timeout = 10 # seconds
$elapsed = 0
while (-not (Test-Path $logPath) -and $elapsed -lt $timeout) {
    Start-Sleep -Seconds 1
    $elapsed++
}

if (Test-Path $logPath) {
    # Wait and tail logs
    Get-Content -Path $logPath -Wait -Tail 20
} else {
    Write-Host "Could not find frontend.log. You can view logs manually in frontend.log" -ForegroundColor Yellow
}
