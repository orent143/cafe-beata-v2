@echo off
echo Starting both Cafe Beata and Inventory Cafe Systems...

:: Ask if user wants to update API URLs first
echo.
echo Do you want to update all API URLs in the Inventory System to use port 8001? (y/n)
set /p update_urls=

if /i "%update_urls%"=="y" (
    echo.
    echo Running URL update script...
    cd "../Inventory cafe system/BeataIMS-main/IMS"
    node update-api-urls.js
    echo.
    echo URL updates complete!
    echo.
    cd "../../../cafe-beata-main"
)

:: Start the first backend
start cmd /k "title Cafe Beata Backend && cd backend && python -m uvicorn main:app --reload --port 8000"

:: Wait for a moment
timeout /t 3

:: Start the second backend
start cmd /k "title Inventory Cafe System Backend && cd ../Inventory cafe system/backend-main && python -m uvicorn main:app --reload --port 8001"

echo Both systems have been started in separate windows.
echo Cafe Beata running on port 8000
echo Inventory System running on port 8001
echo.
echo Press any key to close this window...
pause > nul 
