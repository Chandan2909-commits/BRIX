# Gmail Auto-Reply PowerShell Script

# Parameters
param(
    [int]$MessageCount = 10
)

# Display header
Write-Host "`n=== BRIX Gmail Auto-Reply (PowerShell) ===`n" -ForegroundColor Cyan
Write-Host "Will process up to $MessageCount unread messages`n"

# Create temp directory
$tempDir = "$env:TEMP\brix_gmail_ps"
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir | Out-Null
}

# Copy credentials
Write-Host "Preparing credentials..."
Copy-Item -Path "credentials.json" -Destination "$tempDir\credentials.json" -Force

# Change to temp directory
Push-Location $tempDir

# Run Python script
Write-Host "Running Gmail automation..."
try {
    & python "S:\BRIX\brix-tkinter\gmail_auto_reply.py" $MessageCount
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python script failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
}
catch {
    Write-Host "Error running Python script: $_" -ForegroundColor Red
}

# Copy token back if created
if (Test-Path "$tempDir\gmail_token.json") {
    Copy-Item -Path "$tempDir\gmail_token.json" -Destination "S:\BRIX\brix-tkinter\gmail_token.json" -Force
}

# Return to original directory
Pop-Location

Write-Host "`nPress Enter to exit..."
Read-Host