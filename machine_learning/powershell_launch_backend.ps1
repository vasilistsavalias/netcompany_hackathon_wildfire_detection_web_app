# powershell_launch_backend.ps1

# --- Configuration ---
# Change this to your *actual* project directory if it's different
$projectDir = "C:\Users\vtsav\Documents\1.programming_mine\GithubRepos\netcompany_hackathon_wildfire_detection_web_app\machine_learning"

# --- Database Connection (PostgreSQL) ---
# Replace with your *actual* PostgreSQL credentials
$dbUser = "wildfire_user"
$dbPassword = "1234"  # !!! CHANGE THIS !!!
$dbHost = "localhost"
$dbPort = "5432"
$dbName = "wildfire_db"

# Construct the DATABASE_URL
$databaseUrl = "postgresql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"

# --- Script ---

# Change to the project directory
Set-Location $projectDir

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Set the DATABASE_URL environment variable
$env:DATABASE_URL = $databaseUrl

# Run the Flask application
python run.py