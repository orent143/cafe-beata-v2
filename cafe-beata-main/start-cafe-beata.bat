@echo off
echo Starting Cafe Beata backend on port 8000...
cd backend
python -m uvicorn main:app --reload --port 8000
pause 