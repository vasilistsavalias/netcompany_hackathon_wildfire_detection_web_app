# --- Path Resolution Function ---
function Get-ScriptDirectory {
    if ($PSScriptRoot) {
        # Running as PS1
        return $PSScriptRoot
    }
    
    # Running as EXE
    if ($MyInvocation.MyCommand.Path) {
        return Split-Path $MyInvocation.MyCommand.Path -Parent
    }
    
    # Fallback to current directory
    return (Get-Location).Path
}

# --- Create a Dummy File in Project Root (MUST BE DONE MANUALLY ONCE) ---
# Create an empty file named "project_root_marker.txt" in your project root directory.

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    if ($logFile) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logEntry = "$timestamp - $Level - $Message"
        Add-Content -Path $logFile -Value $logEntry -ErrorAction SilentlyContinue
    }
}

# --- Determine Project Root Reliably ---
$currentLocation = Get-Location
$scriptDirectory = Get-ScriptDirectory
Write-Host "Initial Debug:"
Write-Host "  Current Location: $currentLocation"
Write-Host "  Script Directory: $scriptDirectory"

# Try to find project root by looking for marker file
$projectRoot = $currentLocation
$markerFile = "project_root_marker.txt"
$maxLevelsUp = 3
$currentLevel = 0

while ($currentLevel -lt $maxLevelsUp) {
    if (Test-Path (Join-Path $projectRoot $markerFile)) {
        break
    }
    $projectRoot = Split-Path $projectRoot -Parent
    $currentLevel++
}

if (-not (Test-Path (Join-Path $projectRoot $markerFile))) {
    Write-Host "ERROR: Could not find project root marker file within $maxLevelsUp levels up." -ForegroundColor Red
    Write-Host "Please ensure 'project_root_marker.txt' exists in the project root directory." -ForegroundColor Red
    pause
    exit 1
}

# --- Configuration ---
$backendDir = Join-Path $projectRoot "machine_learning"
$frontendDir = Join-Path $projectRoot "front_end"
$logFile = Join-Path $projectRoot "launch_log.txt"

# Validate critical directories
if (-not (Test-Path $backendDir)) {
    Write-Host "ERROR: Backend directory not found at: $backendDir" -ForegroundColor Red
    pause
    exit 1
}

if (-not (Test-Path $frontendDir)) {
    Write-Host "ERROR: Frontend directory not found at: $frontendDir" -ForegroundColor Red
    pause
    exit 1
}

# Database configuration
$dbUser = "wildfire_user"
$dbPassword = "1234"  # !!! CHANGE THIS !!! Store securely!
$dbHost = "localhost"
$dbPort = "5432"
$dbName = "wildfire_db"
$databaseUrl = "postgresql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"
$frontendUrl = "http://localhost:5173"
$backendUrl = "http://localhost:8080"

# --- Start-Backend and Start-Frontend Functions ---
function Start-Backend {
    Write-Log "Initializing Backend..."
    try {
        $activateScript = Join-Path $backendDir ".venv\Scripts\activate.ps1"
        if (Test-Path $activateScript) {
            Write-Log "Attempting to activate: '$activateScript'"
            & $activateScript
        } else {
            Write-Host "WARNING: Virtual environment not found at: $activateScript" -ForegroundColor Yellow
            Write-Host "Attempting to continue without virtual environment..." -ForegroundColor Yellow
        }
    } catch {
        Write-Log "Error activating: $($_.Exception.Message)" -Level "ERROR"
    }
    
    $env:DATABASE_URL = $databaseUrl
    if (Test-Path (Join-Path $backendDir "run.py")) {
        $backendProcess = Start-Process python -ArgumentList "run.py" -NoNewWindow -PassThru -WorkingDirectory $backendDir
        Write-Log "Backend started (PID: $($backendProcess.Id))."
        return $backendProcess.Id
    } else {
        Write-Host "ERROR: Backend run.py not found in: $backendDir" -ForegroundColor Red
        pause
        exit 1
    }
}

function Start-Frontend {
    Write-Log "Initializing Frontend..."
    if (-not (Test-Path (Join-Path $frontendDir "package.json"))) {
        Write-Host "ERROR: package.json not found in: $frontendDir" -ForegroundColor Red
        pause
        exit 1
    }
    
    if (-not (Test-Path "$frontendDir\node_modules")) {
        Write-Host "Installing node modules..." -ForegroundColor Yellow
        try {
            Set-Location $frontendDir
            npm install
            Set-Location $projectRoot
        } catch {
            Write-Log "Error running npm install: $($_.Exception.Message)" -Level "ERROR"
            pause
            exit 1
        }
    }
    
    $frontendProcess = Start-Process npm -ArgumentList "run dev" -NoNewWindow -PassThru -WorkingDirectory $frontendDir
    Write-Log "Frontend started (PID: $($frontendProcess.Id))."
    return $frontendProcess.Id
}

# --- Main Script Execution ---
Clear-Content -Path $logFile -ErrorAction SilentlyContinue

Write-Host "`n-----------------------------------------------------" -ForegroundColor DarkGreen
Write-Host "  Starting Wildfire Detection Web Application..." -ForegroundColor Green
Write-Host "-----------------------------------------------------`n" -ForegroundColor DarkGreen

$backendPID = Start-Backend

Write-Host "`nBackend Initializing..." -ForegroundColor Yellow
Write-Host "Please wait..." -ForegroundColor Gray

$waitSeconds = 30
for ($i = $waitSeconds; $i -gt 0; $i--) {
    Write-Host "Waiting... ($i seconds)" -NoNewline -ForegroundColor DarkGray
    Start-Sleep -Seconds 1
    Write-Host "`r" -NoNewline
}

Write-Host "`nInitializing Frontend..." -ForegroundColor Yellow
$frontendPID = Start-Frontend

Write-Host "`n-----------------------------------------------------" -ForegroundColor DarkCyan
Write-Host "  🎉  Application Ready!  🎉" -ForegroundColor Cyan
Write-Host "  Open your browser and go to:" -ForegroundColor White
Write-Host "  ==>  $frontendUrl  <==" -ForegroundColor Yellow -BackgroundColor DarkBlue
Write-Host "-----------------------------------------------------`n" -ForegroundColor DarkCyan

Write-Host "Press CTRL+C to exit." -ForegroundColor Cyan

# Keep the script running
while ($true) {
    Start-Sleep -Seconds 10
}