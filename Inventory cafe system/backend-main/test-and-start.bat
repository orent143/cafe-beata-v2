@echo off
echo ================================================
echo    INVENTORY CAFE SYSTEM - TEST AND START
echo ================================================
echo.
echo Step 1: Running Database Test...
echo.

python database_test.py

echo.
echo Step 2: Starting Inventory System...
echo.

python -m uvicorn main:app --reload --port 8001

echo.
echo Inventory System has been stopped.
echo ================================================
pause 