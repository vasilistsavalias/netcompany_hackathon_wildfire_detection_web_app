# This script uses PS2EXE to convert test_container.ps1 to an .exe

# --- Configuration ---

# Input file (your test container PowerShell script)
$inputFile = "C:\Users\vtsav\Documents\1.programming_mine\GithubRepos\netcompany_hackathon_wildfire_detection_web_app\test_container.ps1"

# Output file (the .exe) - in the same directory as the input
$outputFile = "C:\Users\vtsav\Documents\1.programming_mine\GithubRepos\netcompany_hackathon_wildfire_detection_web_app\test_container.exe"

# --- Script ---

# Check if PS2EXE is installed. If not, install it.
if (-not (Get-Module -ListAvailable -Name ps2exe)) {
    Write-Host "PS2EXE module not found. Installing..." -ForegroundColor Yellow
    try {
        Install-Module -Name ps2exe -Force -Scope CurrentUser  # Install for current user only
    }
    catch {
        Write-Host "Error installing PS2EXE: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "You may need to run PowerShell as an administrator to install modules." -ForegroundColor Red
        exit 1
    }
    Write-Host "PS2EXE installed successfully." -ForegroundColor Green
}

# Convert the script to an .exe
# IMPORTANT: Remove -NoConsole (or set it to $false) if you want the console to be visible.
try {
    Invoke-ps2exe -InputFile $inputFile -OutputFile $outputFile
    Write-Host "Successfully created: $outputFile" -ForegroundColor Green
}
catch {
    Write-Host "Error creating .exe: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Done." -ForegroundColor Green
