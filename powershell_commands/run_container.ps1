# Extract DB info from your script
$dbUser = "wildfire_user"
$dbPassword = "1234"
$dbHost = "host.docker.internal"  # Special Docker hostname to connect to host machine
$dbPort = "5432"
$dbName = "wildfire_db"
$databaseUrl = "postgresql://${dbUser}:${dbPassword}@${dbHost}:${dbPort}/${dbName}"

# Run the container, mapping ports 80 and 8080 from the container to your host
Write-Host "Starting container with database connection to: $dbHost" -ForegroundColor Green
docker run -d --name wildfire-app -p 80:80 -p 8080:8080 -e DATABASE_URL=$databaseUrl $imageName`:$imageTag