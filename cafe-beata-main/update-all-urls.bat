@echo off
echo This script will update all API URLs in the Inventory System from port 8000 to port 8001.
echo.
echo Working directory: %CD%
echo.

:: Navigate to the IMS directory
cd "../Inventory cafe system/BeataIMS-main/IMS"

:: Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed or not in the PATH. Please install Node.js.
    exit /b 1
)

:: Run the URL update script
echo Running URL update script...
node update-api-urls.js

echo.
echo URL updates completed!
echo.

:: Return to the original directory
cd "../../../cafe-beata-main"

echo Press any key to close...
pause > nul 