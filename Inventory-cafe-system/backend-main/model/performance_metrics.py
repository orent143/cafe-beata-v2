import time
import datetime
import threading
import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
import statistics
from model.db import get_db, db_transaction

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("performance_metrics")

# Create router
PerformanceMetricsRouter = APIRouter(tags=["Performance Metrics"])

# In-memory storage for metrics (will be lost on restart)
# For production, consider adding a database table for persistent storage
metrics_storage = {
    "transaction_times": [],  # List of transaction execution times (ms)
    "stock_update_times": [],  # List of stock update execution times (ms)
    "error_rates": {
        "total_requests": 0,
        "failed_requests": 0,
        "errors_by_type": {}  # Dictionary of error types and counts
    },
    "response_times": [],  # List of API response times (ms)
    "database_connection_times": [],  # List of database connection times (ms)
    "concurrent_users": 0,  # Current number of concurrent users
    "max_concurrent_users": 0,  # Maximum concurrent users observed
    "hourly_metrics": {},  # Hourly aggregated metrics
    "daily_metrics": {},  # Daily aggregated metrics
}

# Lock for thread-safe access to metrics
metrics_lock = threading.RLock()

def record_transaction_time(operation_type: str, execution_time_ms: float):
    """Record transaction execution time"""
    with metrics_lock:
        metrics_storage["transaction_times"].append({
            "timestamp": datetime.datetime.now(),
            "operation_type": operation_type,
            "execution_time_ms": execution_time_ms
        })
        
        # Keep only the last 1000 transaction times to limit memory usage
        if len(metrics_storage["transaction_times"]) > 1000:
            metrics_storage["transaction_times"] = metrics_storage["transaction_times"][-1000:]

def record_stock_update_time(product_id: int, execution_time_ms: float):
    """Record stock update execution time"""
    with metrics_lock:
        metrics_storage["stock_update_times"].append({
            "timestamp": datetime.datetime.now(),
            "product_id": product_id,
            "execution_time_ms": execution_time_ms
        })
        
        # Keep only the last 1000 update times to limit memory usage
        if len(metrics_storage["stock_update_times"]) > 1000:
            metrics_storage["stock_update_times"] = metrics_storage["stock_update_times"][-1000:]

def record_error(error_type: str, endpoint: str, error_message: str):
    """Record an error occurrence"""
    with metrics_lock:
        metrics_storage["error_rates"]["failed_requests"] += 1
        
        if error_type not in metrics_storage["error_rates"]["errors_by_type"]:
            metrics_storage["error_rates"]["errors_by_type"][error_type] = {
                "count": 0,
                "endpoints": {}
            }
        
        metrics_storage["error_rates"]["errors_by_type"][error_type]["count"] += 1
        
        if endpoint not in metrics_storage["error_rates"]["errors_by_type"][error_type]["endpoints"]:
            metrics_storage["error_rates"]["errors_by_type"][error_type]["endpoints"][endpoint] = {
                "count": 0,
                "recent_errors": []
            }
        
        metrics_storage["error_rates"]["errors_by_type"][error_type]["endpoints"][endpoint]["count"] += 1
        
        # Add to recent errors list with timestamp
        recent_error = {
            "timestamp": datetime.datetime.now(),
            "message": error_message
        }
        
        metrics_storage["error_rates"]["errors_by_type"][error_type]["endpoints"][endpoint]["recent_errors"].append(recent_error)
        
        # Keep only the last 10 recent errors per endpoint
        if len(metrics_storage["error_rates"]["errors_by_type"][error_type]["endpoints"][endpoint]["recent_errors"]) > 10:
            metrics_storage["error_rates"]["errors_by_type"][error_type]["endpoints"][endpoint]["recent_errors"] = metrics_storage["error_rates"]["errors_by_type"][error_type]["endpoints"][endpoint]["recent_errors"][-10:]

def record_request():
    """Record a new request for calculating error rates"""
    with metrics_lock:
        metrics_storage["error_rates"]["total_requests"] += 1

def record_response_time(endpoint: str, response_time_ms: float):
    """Record API response time"""
    with metrics_lock:
        metrics_storage["response_times"].append({
            "timestamp": datetime.datetime.now(),
            "endpoint": endpoint,
            "response_time_ms": response_time_ms
        })
        
        # Keep only the last 1000 response times
        if len(metrics_storage["response_times"]) > 1000:
            metrics_storage["response_times"] = metrics_storage["response_times"][-1000:]

def record_db_connection_time(connection_time_ms: float):
    """Record database connection time"""
    with metrics_lock:
        metrics_storage["database_connection_times"].append({
            "timestamp": datetime.datetime.now(),
            "connection_time_ms": connection_time_ms
        })
        
        # Keep only the last 100 connection times
        if len(metrics_storage["database_connection_times"]) > 100:
            metrics_storage["database_connection_times"] = metrics_storage["database_connection_times"][-100:]

def increment_concurrent_users():
    """Increment concurrent user count"""
    with metrics_lock:
        metrics_storage["concurrent_users"] += 1
        metrics_storage["max_concurrent_users"] = max(
            metrics_storage["max_concurrent_users"],
            metrics_storage["concurrent_users"]
        )

def decrement_concurrent_users():
    """Decrement concurrent user count"""
    with metrics_lock:
        metrics_storage["concurrent_users"] = max(0, metrics_storage["concurrent_users"] - 1)

def update_hourly_metrics():
    """Update hourly aggregated metrics"""
    current_hour = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    hour_key = current_hour.strftime("%Y-%m-%d %H:00")
    
    with metrics_lock:
        # Filter metrics for the current hour
        hour_transaction_times = [
            item["execution_time_ms"] 
            for item in metrics_storage["transaction_times"] 
            if item["timestamp"].replace(minute=0, second=0, microsecond=0) == current_hour
        ]
        
        hour_stock_update_times = [
            item["execution_time_ms"] 
            for item in metrics_storage["stock_update_times"] 
            if item["timestamp"].replace(minute=0, second=0, microsecond=0) == current_hour
        ]
        
        hour_response_times = [
            item["response_time_ms"] 
            for item in metrics_storage["response_times"] 
            if item["timestamp"].replace(minute=0, second=0, microsecond=0) == current_hour
        ]
        
        # Calculate aggregated metrics
        metrics_storage["hourly_metrics"][hour_key] = {
            "avg_transaction_time": statistics.mean(hour_transaction_times) if hour_transaction_times else 0,
            "avg_stock_update_time": statistics.mean(hour_stock_update_times) if hour_stock_update_times else 0,
            "avg_response_time": statistics.mean(hour_response_times) if hour_response_times else 0,
            "transaction_count": len(hour_transaction_times),
            "stock_update_count": len(hour_stock_update_times),
            "max_concurrent_users": metrics_storage["max_concurrent_users"]
        }
        
        # Reset max concurrent users for the next hour
        metrics_storage["max_concurrent_users"] = metrics_storage["concurrent_users"]

def start_metrics_aggregation():
    """Start background task for aggregating metrics hourly"""
    def hourly_aggregation():
        while True:
            try:
                update_hourly_metrics()
            except Exception as e:
                logger.error(f"Error in hourly metrics aggregation: {e}")
            
            # Sleep until the start of the next hour
            now = datetime.datetime.now()
            next_hour = (now.replace(minute=0, second=0, microsecond=0) + 
                         datetime.timedelta(hours=1))
            seconds_to_wait = (next_hour - now).total_seconds()
            time.sleep(seconds_to_wait)
    
    aggregation_thread = threading.Thread(target=hourly_aggregation)
    aggregation_thread.daemon = True
    aggregation_thread.start()
    logger.info("Metrics aggregation background task started")

# API Endpoints
@PerformanceMetricsRouter.get("/api/performance/metrics")
async def get_performance_metrics(db=Depends(get_db)):
    """Get current performance metrics"""
    with metrics_lock:
        # Calculate current error rate
        total_requests = metrics_storage["error_rates"]["total_requests"]
        failed_requests = metrics_storage["error_rates"]["failed_requests"]
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0

        # Calculate average transaction times for the last 100 transactions
        recent_transaction_times = [
            item["execution_time_ms"] for item in metrics_storage["transaction_times"][-100:]
        ] if metrics_storage["transaction_times"] else []

        avg_transaction_time = statistics.mean(recent_transaction_times) if recent_transaction_times else 0

        # Calculate average stock update times for the last 100 updates
        recent_stock_update_times = [
            item["execution_time_ms"] for item in metrics_storage["stock_update_times"][-100:]
        ] if metrics_storage["stock_update_times"] else []

        avg_stock_update_time = statistics.mean(recent_stock_update_times) if recent_stock_update_times else 0

        # Calculate average response times for the last 100 requests
        recent_response_times = [
            item["response_time_ms"] for item in metrics_storage["response_times"][-100:]
        ] if metrics_storage["response_times"] else []

        avg_response_time = statistics.mean(recent_response_times) if recent_response_times else 0

        # Get the most recent hourly metrics (last 24 hours)
        hourly_keys = sorted(metrics_storage["hourly_metrics"].keys())[-24:] if metrics_storage["hourly_metrics"] else []
        recent_hourly_metrics = {
            key: metrics_storage["hourly_metrics"][key] for key in hourly_keys
        }

        return {
            "current_metrics": {
                "error_rate": round(error_rate, 2),
                "avg_transaction_time": round(avg_transaction_time, 2),
                "avg_stock_update_time": round(avg_stock_update_time, 2),
                "avg_response_time": round(avg_response_time, 2),
                "concurrent_users": metrics_storage["concurrent_users"],
                "max_concurrent_users": metrics_storage["max_concurrent_users"]
            },
            "hourly_metrics": recent_hourly_metrics,
            "error_details": {
                "total_requests": total_requests,
                "failed_requests": failed_requests,
                "errors_by_type": metrics_storage["error_rates"]["errors_by_type"]
            },
            "transaction_times": [
                {
                    "timestamp": t["timestamp"].isoformat() if hasattr(t["timestamp"], "isoformat") else str(t["timestamp"]),
                    "operation_type": t["operation_type"],
                    "execution_time_ms": t["execution_time_ms"]
                }
                for t in metrics_storage["transaction_times"][-10:]
            ],
            "stock_update_times": [
                {
                    "timestamp": t["timestamp"].isoformat() if hasattr(t["timestamp"], "isoformat") else str(t["timestamp"]),
                    "product_id": t.get("product_id"),
                    "execution_time_ms": t["execution_time_ms"]
                }
                for t in metrics_storage["stock_update_times"][-10:]
            ],
        }
@PerformanceMetricsRouter.get("/api/performance/database_stats")
async def get_database_stats(db=Depends(get_db)):  # Remove @db_transaction decorator
    """Get database performance statistics"""
    try:
        # Get active connections count
        cursor = db.cursor()
        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        threads_connected = cursor.fetchone()
        
        try:
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            threads_connected = cursor.fetchone()
        except Exception as e:
            threads_connected = (None, 0)
            logger.error(f"Error fetching threads_connected: {e}")
            
        try:
            cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
            max_connections = cursor.fetchone()
        except Exception as e:
            max_connections = (None, 100)  # Default fallback
            logger.error(f"Error fetching max_connections: {e}")

        
        # Get max connections
        cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
        max_connections = cursor.fetchone()
        
        # Get database uptime
        cursor.execute("SHOW STATUS LIKE 'Uptime'")
        uptime = cursor.fetchone()
        
        # Get table statistics
        cursor.execute("""
            SELECT table_name, table_rows, data_length, index_length
            FROM information_schema.tables
            WHERE table_schema = 'cafe_beata'
            ORDER BY data_length DESC
        """)
        tables = cursor.fetchall()
        
        # Get query cache statistics
        cursor.execute("SHOW STATUS LIKE 'Qcache%'")
        query_cache = cursor.fetchall()
        
        cursor.close()
        
        # Format the results
        return {
            "connection_stats": {
                "active_connections": int(threads_connected[1]) if threads_connected else 0,
                "max_connections": int(max_connections[1]) if max_connections else 0,
                "connection_usage_percent": (int(threads_connected[1]) / int(max_connections[1]) * 100) 
                                          if threads_connected and max_connections else 0
            },
            "uptime": {
                "seconds": int(uptime[1]) if uptime else 0,
                "readable": str(datetime.timedelta(seconds=int(uptime[1]))) if uptime else "0:00:00"
            },
            "table_stats": [
                {
                    "table_name": table[0],
                    "rows": table[1],
                    "data_size_mb": round(table[2] / (1024 * 1024), 2),
                    "index_size_mb": round(table[3] / (1024 * 1024), 2),
                    "total_size_mb": round((table[2] + table[3]) / (1024 * 1024), 2)
                }
                for table in tables
            ],
            "query_cache": {
                key[0].replace("Qcache_", ""): int(key[1])
                for key in query_cache
            }
        }
    except Exception as e:
        logger.error(f"Error fetching database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@PerformanceMetricsRouter.get("/api/performance/backup_status")
async def get_backup_status(db=Depends(get_db)):
    """Get database backup status"""
    try:
        # This would typically connect to your backup system
        # For demonstration, we'll return mock data
        return {
            "last_backup": {
                "timestamp": datetime.datetime.now() - datetime.timedelta(days=1),
                "status": "success",
                "size_mb": 42.5,
                "duration_seconds": 35
            },
            "next_scheduled_backup": datetime.datetime.now() + datetime.timedelta(hours=23),
            "backup_history": [
                {
                    "timestamp": datetime.datetime.now() - datetime.timedelta(days=1),
                    "status": "success",
                    "size_mb": 42.5,
                    "duration_seconds": 35
                },
                {
                    "timestamp": datetime.datetime.now() - datetime.timedelta(days=2),
                    "status": "success",
                    "size_mb": 41.8,
                    "duration_seconds": 33
                },
                {
                    "timestamp": datetime.datetime.now() - datetime.timedelta(days=3),
                    "status": "success",
                    "size_mb": 41.2,
                    "duration_seconds": 32
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching backup status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Middleware decorator for measuring response times
def measure_response_time(original_function):
    """Decorator to measure API response time"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            response = await original_function(*args, **kwargs)
            return response
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            # Extract endpoint name from function name or path
            endpoint = original_function.__name__
            record_response_time(endpoint, execution_time)
    
    return wrapper

# Initialize metrics tracking on startup
def init_performance_metrics():
    """Initialize performance metrics tracking"""
    logger.info("Initializing performance metrics tracking")
    start_metrics_aggregation() 