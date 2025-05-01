import os
from fastapi import FastAPI, Request, HTTPException, Depends, Form, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import uvicorn
from typing import List

# Import routers
from model.auth import AuthRouter
from model.activity_logs import ActivityLogsRouter
from model.users import UsersRouter
from model.inventoryproduct import InventoryRouter
from model.inventory_snapshot import InventorySnapshotRouter
from model.stockin import StockRouter
from model.createorder import CreateOrderRouter
from model.ordersummary import OrderSummaryRouter
from model.sales import SalesRouter, start_background_task
from model.reports import ReportRouter
from model.categories import CategoryRouter
from model.suppliers import SupplierRouter
from model.db import ensure_tables_exist, init_connection_pool, start_connection_pool_cleanup, test_connection, get_db, db_transaction

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Cafe Beata Inventory Management System")

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:5173",  # Vue dev server
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    # Add any other origins that need access
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the uploads directories exist
os.makedirs("uploads/profile_pics", exist_ok=True)
os.makedirs("uploads/products", exist_ok=True)  # Ensure product uploads directory exists
os.makedirs("uploads/stocks", exist_ok=True)  # Ensure stock images directory exists
os.makedirs("static", exist_ok=True)  # Ensure static directory exists for HTML files

# Mount static files for serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# Make sure the profile_pics directory is directly mounted
app.mount("/uploads/profile_pics", StaticFiles(directory="uploads/profile_pics"), name="profile_pics")
app.mount("/products", StaticFiles(directory="uploads/products"), name="products")  # Direct access to product images
app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static HTML files

# WebSocket Manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            if conn in self.active_connections:
                self.disconnect(conn)

# Create the connection manager instance
manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws/inventory")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and wait for any messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

# Export the manager for use in other modules
def get_websocket_manager():
    return manager

# Include CRUD routes from modules
app.include_router(AuthRouter, prefix="/Auth")
app.include_router(ActivityLogsRouter, tags=["Activity Logs"])
app.include_router(UsersRouter, prefix="/api/users", tags=["Users"])
app.include_router(InventoryRouter, prefix="/api/inventory", tags=["Inventory"])
app.include_router(InventorySnapshotRouter, prefix="/api/inventory_snapshot", tags=["Inventory Snapshot"])
app.include_router(StockRouter, prefix="/api/stock", tags=["Stock In"])
app.include_router(CategoryRouter, prefix="/api/categories", tags=["Categories"])
app.include_router(SupplierRouter, prefix="/api/suppliers", tags=["Suppliers"])
app.include_router(SalesRouter, prefix="/api/sales", tags=["Sales"])
app.include_router(ReportRouter, prefix="/api/reports", tags=["Reports"])
app.include_router(CreateOrderRouter, prefix="/api/orders", tags=["CreateOrders"])
app.include_router(OrderSummaryRouter, prefix="/api/ordersummary", tags=["OrderSummary"])

# Test database connection at startup
@app.on_event("startup")
async def startup_db_client():
    try:
        test_connection()
        logger.info("Successfully connected to the database")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run when the application starts up
    """
    # Log startup information
    logger.info("=== Inventory System Starting ===")
    logger.info(f"Server running on port 8001")
    logger.info(f"Static files served from: {os.path.abspath('uploads')}")
    
    # Ensure all necessary database tables exist
    try:
        ensure_tables_exist()
    except Exception as e:
        logger.error(f"Error during table setup: {e}")
        logger.info("Continuing startup despite table setup errors")
    
    # Initialize database connection pool
    try:
        logger.info("Initializing database connection pool...")
        init_connection_pool()
        
        # Start connection pool cleanup scheduler
        logger.info("Starting connection pool cleanup scheduler...")
        start_connection_pool_cleanup()
    except Exception as e:
        logger.error(f"Error initializing database services: {e}")
    
    logger.info("Inventory System API is ready")
    
    # Start background task
    try:
        logger.info("Starting background task...")
        start_background_task()
    except Exception as e:
        logger.error(f"Error starting background task: {e}")
    
# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run when the application is shutting down
    """
    # Log shutdown information
    logger.info("=== Inventory System Shutting Down ===")
    
    # Clean up database connections
    from model.db import connection_pool
    try:
        if connection_pool is not None:
            logger.info("Cleaning up database connection pool...")
            connection_pool._remove_connections()
            logger.info("Database connection pool cleaned up")
    except Exception as e:
        logger.error(f"Error cleaning up database connection pool: {e}")
    
    logger.info("Inventory System API shutdown complete")
    
# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Cafe Beata Inventory Management System API"}

# Profile page endpoint
@app.get("/profile")
async def profile_page():
    return FileResponse("static/profile.html")

# Redirect for user profile with ID
@app.get("/profile/{user_id}")
async def profile_redirect(user_id: int):
    return RedirectResponse(f"/profile?user_id={user_id}")

# Log all incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests for debugging"""
    logger.info(f"Request: {request.method} {request.url}")
    # Log headers
    for header, value in request.headers.items():
        logger.info(f"Header: {header}: {value}")
    
    # Process the request
    response = await call_next(request)
    
    # Get the origin from the request
    origin = request.headers.get("Origin", "*")
    
    # Add CORS headers to response
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Origin"
    
    # Log response status
    logger.info(f"Response status: {response.status_code}")
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the app
if __name__ == "__main__":
    if not os.path.exists("uploads/products"):
        os.makedirs("uploads/products", exist_ok=True)
    
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)

