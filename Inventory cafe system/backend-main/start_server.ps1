# PowerShell script to start the FastAPI server
Write-Host "Starting Inventory Cafe System API server..."
Write-Host "Press Ctrl+C to stop the server"
Write-Host "" 

# Set the current working directory to the script's directory
Set-Location $PSScriptRoot

# Start the server using python -m uvicorn
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload

# This will execute after the server is stopped
Write-Host "Server stopped." 