@echo off
echo Starting Inventory Cafe System backend on port 8001...

:: Ask if user wants to update API URLs first
echo.
echo Do you want to update all API URLs to use port 8001? (y/n)
set /p update_urls=

if /i "%update_urls%"=="y" (
    echo.
    echo Running URL update script...
    cd "../Inventory cafe system/BeataIMS-main/IMS"
    node update-api-urls.js
    echo.
    echo URL updates complete!
    echo.
    cd "../../.."
)

cd "../Inventory cafe system/backend-main"
python -m uvicorn main:app --reload --port 8001
pause 