# ==============================
# launch_app.ps1
# ==============================

[CmdletBinding()]
param()

# --- Function: Get-ScriptDirectory ---
function Get-ScriptDirectory {
    if ($PSScriptRoot) {
        return $PSScriptRoot
    }
    if ($MyInvocation.MyCommand.Path) {
        return Split-Path $MyInvocation.MyCommand.Path -Parent
    }
    return (Get-Location).Path
}

# --- Determine Project Root using Marker File ---
$initialLocation = Get-ScriptDirectory
Write-Host "Initializing Application..." -ForegroundColor Cyan
$markerFile = "project_root_marker.txt"
$projectRoot = $initialLocation
while ($projectRoot -and -not (Test-Path (Join-Path $projectRoot $markerFile))) {
    $parent = Split-Path $projectRoot -Parent
    if ($parent -eq $projectRoot) { break }
    $projectRoot = $parent
}
if (-not (Test-Path (Join-Path $projectRoot $markerFile))) {
    Write-Host "ERROR: Project root marker '$markerFile' not found. Ensure it exists in the project root." -ForegroundColor Red
    exit 1
}
Write-Host "Project root detected at:" -ForegroundColor Green
Write-Host "    $projectRoot" -ForegroundColor Green

# --- Configuration ---
$backendDir = Join-Path $projectRoot "machine_learning"
$frontendDir = Join-Path $projectRoot "front_end"

if (-not (Test-Path $backendDir)) {
    Write-Host "ERROR: Backend directory not found at: $backendDir" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $frontendDir)) {
    Write-Host "ERROR: Frontend directory not found at: $frontendDir" -ForegroundColor Red
    exit 1
}

# --- Database and URL Settings ---
$dbUser = "wildfire_user"
$dbPassword = "1234"  # !!! CHANGE THIS !!! in production, store securely!
$dbHost = "localhost"
$dbPort = "5432"
$dbName = "wildfire_db"
$databaseUrl = "postgresql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"
$frontendUrl = "http://localhost:5173"
$backendUrl = "http://localhost:8080"

# --- Install Backend Requirements ---
function Install-BackendRequirements {
    $requirementsFile = Join-Path $backendDir "requirements.txt"
    if (Test-Path $requirementsFile) {
        Write-Host "Installing backend requirements..." -ForegroundColor Cyan
        try {
            & python -m pip install -r $requirementsFile
            Write-Host "Backend requirements installed successfully." -ForegroundColor Green
        } catch {
            Write-Host "ERROR: Failed to install backend requirements." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "WARNING: requirements.txt not found in $backendDir" -ForegroundColor Yellow
    }
}
Install-BackendRequirements

# --- Start Backend ---
function Start-Backend {
    Write-Host "Starting Backend..." -ForegroundColor Cyan
    $activateScript = Join-Path $backendDir ".venv\Scripts\activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    } else {
        Write-Host "Note: Virtual environment not found. Continuing without activation." -ForegroundColor Yellow
    }
    $env:DATABASE_URL = $databaseUrl
    $runPy = Join-Path $backendDir "run.py"
    if (Test-Path $runPy) {
        $backendProcess = Start-Process python -ArgumentList "run.py" -NoNewWindow -PassThru -WorkingDirectory $backendDir
        return $backendProcess.Id
    } else {
        Write-Host "ERROR: run.py not found in backend directory." -ForegroundColor Red
        exit 1
    }
}

# --- Start Frontend ---
function Start-Frontend {
    Write-Host "Starting Frontend..." -ForegroundColor Cyan
    $packageJson = Join-Path $frontendDir "package.json"
    if (-not (Test-Path $packageJson)) {
        Write-Host "ERROR: package.json not found in frontend directory." -ForegroundColor Red
        exit 1
    }
    $nodeModules = Join-Path $frontendDir "node_modules"
    if (-not (Test-Path $nodeModules)) {
        Write-Host "Installing node modules..." -ForegroundColor Cyan
        try {
            Set-Location $frontendDir
            npm install
            Set-Location $projectRoot
        } catch {
            Write-Host "ERROR: npm install failed." -ForegroundColor Red
            exit 1
        }
    }
    $frontendProcess = Start-Process npm -ArgumentList "run dev" -NoNewWindow -PassThru -WorkingDirectory $frontendDir
    return $frontendProcess.Id
}

# --- Wait for Backend with Countdown ---
function Wait-ForBackend {
    param(
        [string]$backendUrl = "http://localhost:8080",
        [int]$timeoutSeconds = 60
    )
    $startTime = Get-Date
    $endTime = $startTime.AddSeconds($timeoutSeconds)
    $backendReady = $false
    while ((Get-Date) -lt $endTime) {
        try {
            $response = Invoke-WebRequest -Uri $backendUrl -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                $backendReady = $true
                break
            }
        } catch {
            # Backend not yet ready
        }
        $remaining = [math]::Ceiling(($endTime - (Get-Date)).TotalSeconds)
        $elapsed = $timeoutSeconds - $remaining
        $percent = [math]::Round(($elapsed / $timeoutSeconds) * 100)
        Write-Progress -Activity "Initializing Backend" `
                       -Status "Please wait... $remaining seconds remaining" `
                       -PercentComplete $percent
        Start-Sleep -Seconds 1
    }
    Write-Progress -Activity "Initializing Backend" -Completed
    return $backendReady
}

# --- Main Execution ---

Write-Host "`n=====================================================" -ForegroundColor DarkGreen
Write-Host "        Starting Wildfire Detection Application" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor DarkGreen

# Launch Backend
$backendPID = Start-Backend
Write-Host "`nBackend is launching. Please wait..." -ForegroundColor Yellow
$backendReady = Wait-ForBackend -backendUrl $backendUrl -timeoutSeconds 100
if (-not $backendReady) {
    Write-Host "WARNING: Backend did not become fully ready within the timeout period." -ForegroundColor Red
} else {
    Write-Host "Backend is ready!" -ForegroundColor Green
}

# Launch Frontend
Write-Host "`nLaunching Frontend..." -ForegroundColor Yellow
$frontendPID = Start-Frontend

Write-Host "`n=====================================================" -ForegroundColor DarkCyan
Write-Host "        🎉  Application Ready!  🎉" -ForegroundColor Cyan
Write-Host "        Open your browser and go to:" -ForegroundColor White
Write-Host "            ==>  $frontendUrl  <==" -ForegroundColor Yellow
Write-Host "=====================================================" -ForegroundColor DarkCyan
Write-Host "Press CTRL+C to exit." -ForegroundColor Cyan

# Keep the script running
while ($true) {
    Start-Sleep -Seconds 10
}
