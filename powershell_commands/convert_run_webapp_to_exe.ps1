# powershell_commands\convert_run_webapp_to_exe_with_icon.ps1 (Output to Project Root - Robust Path Construction)

# --- Configuration ---

# Input file (your main PowerShell script)
$inputFile = Join-Path $PSScriptRoot "run_webapp.ps1"

# Output file (the .exe) - SAVE TO PROJECT ROOT DIRECTORY
$projectRootDir = Join-Path $PSScriptRoot ".."
$outputFile = Join-Path $projectRootDir "run_webapp.exe"

# Icon file (.ico) - Relative path to favicon.ico
$iconPathPart1 = Join-Path $PSScriptRoot ".."
$iconPathPart2 = Join-Path $iconPathPart1 "front_end"
$iconPathPart3 = Join-Path $iconPathPart2 "public"
$iconFile = Join-Path $iconPathPart3 "favicon.ico"

# --- Script ---

# Check if PS2EXE is installed.  If not, install it.
if (-not (Get-Module -ListAvailable -Name ps2exe)) {
    Write-Host "PS2EXE module not found. Installing..." -ForegroundColor Yellow
    try {
        Install-Module -Name ps2exe -Force -Scope CurrentUser
    }
    catch {
        Write-Host "Error installing PS2EXE: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Check if the icon file exists
if (-not (Test-Path $iconFile)) {
    Write-Host "Error: Icon file not found: '$iconFile'" -ForegroundColor Red
    exit 1
}

# Convert the script to an .exe WITH ICON
try {
    Invoke-ps2exe -InputFile $inputFile -OutputFile $outputFile -IconFile $iconFile
    Write-Host "Successfully created: $outputFile with icon" -ForegroundColor Green
}
catch {
    Write-Host "Error creating .exe with icon: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Done. .exe with icon created in project root." -ForegroundColor Green