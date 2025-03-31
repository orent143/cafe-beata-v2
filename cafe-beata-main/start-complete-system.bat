@echo off
echo ===========================================
echo COMPLETE SYSTEM STARTUP
echo ===========================================
echo This will start:
echo  1. Cafe Beata Backend (Port 8000)
echo  2. Inventory System Backend (Port 8001)
echo  3. Inventory System Frontend (Port 5173)
echo.

:: Ask if user wants to update API URLs first
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

:: Start the Cafe Beata backend
start cmd /k "title Cafe Beata Backend && cd backend && python -m uvicorn main:app --reload --port 8000"

:: Wait for a moment
timeout /t 3

:: Start the Inventory System backend
start cmd /k "title Inventory System Backend && cd ../Inventory cafe system/backend-main && python -m uvicorn main:app --reload --port 8001"

:: Wait for a moment
timeout /t 3

:: Start the Inventory System frontend
start cmd /k "title Inventory System Frontend && cd ../Inventory cafe system/BeataIMS-main/IMS && npm run dev"

echo.
echo All systems have been started in separate windows:
echo  - Cafe Beata Backend: http://localhost:8000
echo  - Inventory System Backend: http://localhost:8001
echo  - Inventory System Frontend: http://localhost:5173 (once it finishes starting)
echo.
echo Press any key to close this window...
pause > nul 