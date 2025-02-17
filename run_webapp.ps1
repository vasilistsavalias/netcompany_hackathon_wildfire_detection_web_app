# powershell_launch_all.ps1

# --- Configuration ---
$projectRoot = "C:\Users\vtsav\Documents\1.programming_mine\GithubRepos\netcompany_hackathon_wildfire_detection_web_app"
$backendDir = Join-Path $projectRoot "machine_learning"
$frontendDir = Join-Path $projectRoot "front_end"
$dbUser = "wildfire_user"
$dbPassword = "1234"  # !!! CHANGE THIS !!!  Store securely!
$dbHost = "localhost"
$dbPort = "5432"
$dbName = "wildfire_db"
$databaseUrl = "postgresql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"
$frontendUrl = "http://localhost:5173"  # Default for Vite (React) - change if needed
$backendUrl = "http://localhost:8080" # Backend URL
$logFile = Join-Path $projectRoot "launch_log.txt" # Log file

# --- Functions ---

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO" # Default log level
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Level - $Message"
    Add-Content -Path $logFile -Value $logEntry
}

function Start-Backend {
    Write-Log "Initializing Backend..."
    Set-Location $backendDir
    try {
        Invoke-Expression "& '$($backendDir)\.venv\Scripts\activate.ps1'"
    } catch {
        Write-Log "Error activating virtual environment: $($_.Exception.Message)" -Level "ERROR"
        exit 1 # Exit on critical error
    }
    $env:DATABASE_URL = $databaseUrl
    # Start Flask and capture the Process ID (PID)
    $backendProcess = Start-Process python -ArgumentList "run.py" -NoNewWindow -PassThru
    Write-Log "Backend server started (PID: $($backendProcess.Id))."
    return $backendProcess.Id  # Return the PID
}

function Start-Frontend {
    Write-Log "Initializing Frontend..."
    Set-Location $frontendDir
    if (-not (Test-Path "$frontendDir\node_modules")) {
        Write-Log "[!] node_modules not found.  Running npm install..." -Level "WARNING"
        try{
            npm install
        } catch {
            Write-Log "Error running npm install: $($_.Exception.Message)" -Level "ERROR"
            exit 1
        }
    }
    # Start npm and capture the PID
    $frontendProcess = Start-Process npm -ArgumentList "run dev" -NoNewWindow -PassThru
    Write-Log "Frontend server started (PID: $($frontendProcess.Id))."
    return $frontendProcess.Id # Return the PID
}

# --- Main Script Execution ---

# Clear the log file at the start of each run
Clear-Content -Path $logFile -ErrorAction SilentlyContinue

# --- Temporarily Show Console, Display Message, and Wait ---
Write-Host "Waiting 30 seconds for the backend server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# --- Start Backend and Frontend ---
Write-Log "Starting Wildfire Detection Web App..."
$backendPID = Start-Backend
$frontendPID = Start-Frontend

# --- Instructions for the User ---
Write-Host "`n-----------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Open your web browser and go to:" -ForegroundColor White
Write-Host "  ==>  $frontendUrl  <== " -ForegroundColor Yellow -BackgroundColor DarkBlue
Write-Host "  (You can copy and paste the URL)" -ForegroundColor White
Write-Host "-----------------------------------------------------" -ForegroundColor DarkGray
Write-Host "`nPress CTRL+C in this window to shut down the application." -ForegroundColor Cyan

# Keep the script running indefinitely (until Ctrl+C)
while ($true) {
    Start-Sleep -Seconds 10 # Check for Ctrl+C periodically
}