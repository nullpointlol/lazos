# Script to stop development backend and frontend on Windows (PowerShell)

$ErrorActionPreference = "Continue"

Write-Host "LAZOS - Stopping development services..." -ForegroundColor Red
Write-Host ""

# Function to stop processes on a port
function Stop-PortProcess {
    param (
        [int]$Port
    )
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections.OwningProcess | Select-Object -Unique
        $stoppedAny = $false
        foreach ($procId in $pids) {
            $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Stopping process on port $Port and its children (PID: $procId - $($proc.Name))..." -ForegroundColor Red
                taskkill.exe /F /PID $procId /T | Out-Null
                $stoppedAny = $true
            }
        }
        if ($stoppedAny) {
            Write-Host "Port $Port freed." -ForegroundColor Green
        }
    } else {
        Write-Host "Port $Port is already free." -ForegroundColor Green
    }
}

# Stop the ports
Stop-PortProcess 8000
Stop-PortProcess 5173

Write-Host ""
Write-Host "All development services have been stopped." -ForegroundColor Green
