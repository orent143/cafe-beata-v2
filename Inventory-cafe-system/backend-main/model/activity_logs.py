from fastapi import APIRouter, Depends, HTTPException
from model.db import get_db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("activity_logs")

ActivityLogsRouter = APIRouter(tags=["Activity Logs"])

@ActivityLogsRouter.get("/api/activity_logs", tags=["Activity Logs"])
async def get_activity_logs(db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, icon, title, time, status FROM activity_logs ORDER BY time DESC LIMIT 10")
        logs = cursor.fetchall()
        cursor.close()

        return [
            {
                "id": log[0],
                "icon": log[1],
                "title": log[2],
                "time": log[3].strftime("%Y-%m-%d %H:%M:%S") if log[3] else None,
                "status": log[4]
            }
            for log in logs
        ]
    except Exception as e:
        logger.error(f"Error fetching activity logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
