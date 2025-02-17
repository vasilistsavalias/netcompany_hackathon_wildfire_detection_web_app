# powershell_launch_all_docker.ps1

# --- Configuration ---
$projectRoot        = "C:\Users\vtsav\Documents\1.programming_mine\GithubRepos\netcompany_hackathon_wildfire_detection_web_app"
$backendDir         = Join-Path $projectRoot "machine_learning"
$frontendDir        = Join-Path $projectRoot "front_end"
$dbUser             = "wildfire_user"
$dbPassword         = "1234"  # !!! CHANGE THIS !!!  Store securely!
$dbHost             = "localhost"
$dbPort             = "5432"
$dbName             = "wildfire_db"
$databaseUrl        = "postgresql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"
$frontendUrl        = "http://localhost:5173"   # Port mapping for frontend container
$backendUrl         = "http://localhost:8080"     # Port mapping for backend container
$logFile            = Join-Path $projectRoot "launch_log.txt"  # Log file

# Docker image names
$backendImageName   = "wildfire-backend"
$frontendImageName  = "wildfire-frontend"

# --- Functions ---

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry  = "$timestamp - $Level - $Message"
    Add-Content -Path $logFile -Value $logEntry
}

function Build-BackendImage {
    Write-Host "Building backend Docker image..." -ForegroundColor Cyan
    Write-Log "Building backend Docker image from $backendDir."
    try {
        docker build -t $backendImageName $backendDir
        Write-Host "Backend image built successfully." -ForegroundColor Green
        Write-Log "Backend Docker image built successfully."
    }
    catch {
        Write-Host "Error building backend Docker image: $($_.Exception.Message)" -ForegroundColor Red
        Write-Log "Error building backend Docker image: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}

function Build-FrontendImage {
    Write-Host "Building frontend Docker image..." -ForegroundColor Cyan
    Write-Log "Building frontend Docker image from $frontendDir."
    try {
        docker build -t $frontendImageName $frontendDir
        Write-Host "Frontend image built successfully." -ForegroundColor Green
        Write-Log "Frontend Docker image built successfully."
    }
    catch {
        Write-Host "Error building frontend Docker image: $($_.Exception.Message)" -ForegroundColor Red
        Write-Log "Error building frontend Docker image: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}

function Remove-ContainerIfExists {
    param(
        [string]$ContainerName
    )
    $existing = docker ps -a --format "{{.Names}}" | Select-String -Pattern "^$ContainerName$"
    if ($existing) {
        Write-Host "Removing existing container '$ContainerName'..." -ForegroundColor Yellow
        Write-Log "Removing existing container '$ContainerName'."
        docker rm -f $ContainerName | Out-Null
    }
}

function Start-BackendContainer {
    Write-Host "Starting backend container..." -ForegroundColor Cyan
    Write-Log "Starting backend container."
    Remove-ContainerIfExists -ContainerName "wildfire-backend"
    try {
        # Run container in detached mode, mapping port 8080 and setting DATABASE_URL
        docker run -d --rm --name wildfire-backend -e DATABASE_URL=$databaseUrl -p 8080:8080 $backendImageName | Out-Null
        Write-Host "Backend container started." -ForegroundColor Green
        Write-Log "Backend container started."
    }
    catch {
        Write-Host "Error starting backend container: $($_.Exception.Message)" -ForegroundColor Red
        Write-Log "Error starting backend container: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}

function Start-FrontendContainer {
    Write-Host "Starting frontend container..." -ForegroundColor Cyan
    Write-Log "Starting frontend container."
    Remove-ContainerIfExists -ContainerName "wildfire-frontend"
    try {
        # Run container in detached mode, mapping port 5173
        docker run -d --rm --name wildfire-frontend -p 5173:5173 $frontendImageName | Out-Null
        Write-Host "Frontend container started." -ForegroundColor Green
        Write-Log "Frontend container started."
    }
    catch {
        Write-Host "Error starting frontend container: $($_.Exception.Message)" -ForegroundColor Red
        Write-Log "Error starting frontend container: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}

function Test-Backend {
    Write-Host "`nTesting the backend API health check endpoint..." -ForegroundColor Cyan
    $healthEndpoint = "$backendUrl/api/health-check"
    try {
        $response = Invoke-WebRequest -Uri $healthEndpoint -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Backend API is healthy!" -ForegroundColor Green
            Write-Log "Backend API is healthy."
        }
        else {
            Write-Host "Warning: Backend API returned status code $($response.StatusCode)." -ForegroundColor Yellow
            Write-Log "Warning: Backend API returned status code $($response.StatusCode)." -Level "WARNING"
        }
    }
    catch {
        Write-Host "Error: Could not reach backend API." -ForegroundColor Red
        Write-Log "Error: Could not reach backend API. Exception: $($_.Exception.Message)" -Level "ERROR"
    }
}

# --- Main Script Execution ---

# Clear the log file at the start of each run
Clear-Content -Path $logFile -ErrorAction SilentlyContinue

Write-Log "Starting containerized Wildfire Detection Web App..."

# Build Docker images for backend and frontend
Build-BackendImage
Build-FrontendImage

# Start the backend container
Start-BackendContainer

# Wait for the backend container to initialize (adjust delay as needed)
Write-Host "Waiting 30 seconds for the backend container to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test the backend API health check endpoint
Test-Backend

# Start the frontend container
Start-FrontendContainer

# --- Instructions for the User ---
Write-Host "`n-----------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Open your web browser and go to:" -ForegroundColor White
Write-Host "  ==>  $frontendUrl  <== " -ForegroundColor Yellow -BackgroundColor DarkBlue
Write-Host "  (You can copy and paste the URL)" -ForegroundColor White
Write-Host "-----------------------------------------------------" -ForegroundColor DarkGray
Write-Host "`nPress CTRL+C in this window to shut down the application." -ForegroundColor Cyan

# Keep the script running indefinitely (until Ctrl+C)
while ($true) {
    Start-Sleep -Seconds 10
}
