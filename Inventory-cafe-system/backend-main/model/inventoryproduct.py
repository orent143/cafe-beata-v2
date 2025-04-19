from fastapi import Depends, HTTPException, APIRouter, Form, UploadFile, File, Request, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from model.db import get_db
import os
import shutil
from datetime import datetime
from uuid import uuid4
import mysql.connector
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inventory")

UPLOAD_DIR = "uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)

InventoryRouter = APIRouter(tags=["Inventory"])

class ProductUpdate(BaseModel):
    ProductName: Optional[str] = None
    Quantity: Optional[int] = None
    UnitPrice: Optional[float] = None
    CategoryID: Optional[int] = None
    Threshold: Optional[int] = None  # ✅ Added threshold field

class StockItem(BaseModel):
    stock_location: str
    batch_number: str
    quantity: int
    expiration_date: str
    cost_price: float
    SupplierID: Optional[int] = None  # Add SupplierID

class StockInRequest(BaseModel):
    ProductID: str
    Stocks: List[StockItem]

def determine_status(quantity: Optional[int], process_type: str, threshold: Optional[int] = None) -> str:
    """Determine the product status based on process type and threshold."""
    # Default None quantity to 0 for consistent status evaluation
    quantity = quantity if quantity is not None else 0
    
    if process_type == "To Be Made":
        return "Available"  # Always available for "To Be Made"

    if process_type == "Ready-Made":
        if quantity == 0:
            return "Out of Stock"
        elif threshold is not None and quantity <= threshold:
            return "Low Stock"
        else:
            return "In Stock"
    
    return "Unknown"


def generate_unique_id():
    return str(uuid4())

def log_activity(db, icon: str, title: str, status: str):
    """Log an activity with proper connection handling"""
    try:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO activity_logs (icon, title, time, status) VALUES (%s, %s, NOW(), %s)",
            (icon, title, status),
        )
        db.commit()
        cursor.close()
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")

def log_product_transaction(db, product_id: str, product_name: str, transaction_type: str, 
                          process_type: str, unit_price: float, category_id: Optional[int] = None):
    """Log a product transaction with proper connection handling"""
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO product_transactions 
            (product_id, product_name, transaction_type, process_type, unit_price, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (product_id, product_name, transaction_type, process_type, unit_price, category_id))
        db.commit()
        cursor.close()
    except Exception as e:
        logger.error(f"Failed to log product transaction: {e}")
        raise

@InventoryRouter.get("/inventoryproducts/all", response_model=list)
async def get_all_inventory_products(request: Request, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        base_url = str(request.base_url)

        cursor.execute("SELECT id, ProductName, Quantity, UnitPrice, `CategoryID (FK)`, ProcessType, Threshold, Image FROM inventoryproduct ORDER BY id")
        products = cursor.fetchall()
        cursor.close()

        return [
            {
                "ProductID": product[0],
                "ProductName": product[1],
                "Quantity": product[2],
                "UnitPrice": product[3],
                "CategoryID": product[4],
                "ProcessType": product[5],
                "Threshold": product[6],
                "Status": determine_status(product[2], product[5], product[6]),
                "Image": f"{base_url}uploads/products/{product[7]}" if product[7] else None
            }
            for product in products
        ]
    except Exception as e:
        logger.error(f"Error fetching all inventory products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@InventoryRouter.get("/inventoryproducts/filter", response_model=list)
async def filter_inventory_products(
    request: Request,
    process_type: Optional[str] = None,
    threshold: Optional[int] = None,  # Optional threshold filter
    db=Depends(get_db)
):
    try:
        # Validate process type
        if process_type not in ["Ready-Made", "To Be Made"]:
            raise HTTPException(status_code=400, detail="Invalid Process Type")

        cursor = db.cursor()
        # Base URL for image paths
        base_url = str(request.base_url)

        # Construct the SQL query
        query = "SELECT id, ProductName, Quantity, UnitPrice, `CategoryID (FK)`, ProcessType, Threshold, Image FROM inventoryproduct WHERE ProcessType = %s"
        params = [process_type]

        # Add threshold filter if provided
        if threshold is not None:
            query += " AND Threshold <= %s"
            params.append(threshold)

        cursor.execute(query, tuple(params))
        products = cursor.fetchall()
        cursor.close()

        return [
            {
                "id": product[0],
                "ProductName": product[1],
                "Quantity": float('inf') if product[5] == "To Be Made" else product[2],
                "UnitPrice": product[3],
                "CategoryID": product[4],
                "ProcessType": product[5],
                "Threshold": product[6],
                "Status": "Available" if product[5] == "To Be Made" else determine_status(product[2], product[5], product[6]),
                "Image": f"{base_url}uploads/products/{product[7]}" if product[7] else None
            }
            for product in products
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering inventory products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@InventoryRouter.get("/inventoryproduct/{product_id}", response_model=dict)
async def read_inventory_product(product_id: str, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, ProductName, Quantity, UnitPrice, `CategoryID (FK)`, ProcessType, Threshold FROM inventoryproduct WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()

        if product:
            return {
                "ProductID": product[0],
                "ProductName": product[1],
                "Quantity": float('inf') if product[5] == "To Be Made" else product[2],
                "UnitPrice": product[3],
                "CategoryID": product[4],
                "ProcessType": product[5],
                "Threshold": product[6],
                "Status": "Available" if product[5] == "To Be Made" else determine_status(product[2], product[5], product[6])
            }
        
        raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        logger.error(f"Error reading inventory product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@InventoryRouter.post("/inventoryproduct/")
async def create_inventory_product(
    request: Request,
    ProductID: str = Form(...),
    ProductName: str = Form(...),
    UnitPrice: float = Form(...),
    CategoryID: Optional[int] = Form(None),
    ProcessType: str = Form(...),
    Threshold: Optional[int] = Form(None),  # ✅ Threshold parameter only
    Image: Optional[UploadFile] = File(None),
    db=Depends(get_db),
):
    try:
        if ProcessType == "Ready-Made" and Threshold is None:
            raise HTTPException(status_code=400, detail="Threshold required for Ready-Made products")

        image_filename = None

        if ProcessType not in ["Ready-Made", "To Be Made"]:
            raise HTTPException(status_code=400, detail="Invalid Process Type")

        if Image:
            file_extension = Image.filename.split(".")[-1]
            image_filename = f"{ProductID}_{ProductName.replace(' ', '_').replace('/', '_')}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, image_filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(Image.file, buffer)

        # Set status based on ProcessType and Threshold
        status = determine_status(None, ProcessType, Threshold)

        # Get cursor from the connection
        cursor = db.cursor()

        # Insert product into the database with threshold
        cursor.execute(
            """INSERT INTO inventoryproduct 
            (id, ProductName, UnitPrice, `CategoryID (FK)`, ProcessType, Threshold, Image, Status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (ProductID, ProductName, UnitPrice, CategoryID, ProcessType, Threshold, image_filename, status)
        )
        
        # Commit the transaction
        db.commit()
        
        # Close the cursor
        cursor.close()

        base_url = str(request.base_url)
        image_url = f"{base_url}uploads/products/{image_filename}" if image_filename else None

        return {
            "ProductID": ProductID,
            "ProductName": ProductName,
            "UnitPrice": UnitPrice,
            "CategoryID": CategoryID,
            "ProcessType": ProcessType,
            "Threshold": Threshold,
            "Status": status,
            "Image": image_url,
            "message": "Product created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating inventory product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

        
@InventoryRouter.put("/inventoryproduct/{product_id}", response_model=dict)
async def update_inventory_product(
    product_id: str,
    ProductName: Optional[str] = Form(None),
    UnitPrice: Optional[float] = Form(None),
    CategoryID: Optional[int] = Form(None),
    Threshold: Optional[int] = Form(None),  # ✅ Threshold only
    Image: Optional[UploadFile] = File(None),
    db=Depends(get_db),
):
    try:
        cursor = db.cursor()
        
        cursor.execute(
            "SELECT ProductName, UnitPrice, `CategoryID (FK)`, Threshold, ProcessType, Image FROM inventoryproduct WHERE id = %s",
            (product_id,),
        )
        product = cursor.fetchone()

        if not product:
            cursor.close()
            raise HTTPException(status_code=404, detail="Product not found")

        update_fields = []
        update_values = []
        image_filename = product[5]

        if ProductName is not None:
            update_fields.append("ProductName = %s")
            update_values.append(ProductName)

        if UnitPrice is not None:
            update_fields.append("UnitPrice = %s")
            update_values.append(UnitPrice)

        if CategoryID is not None:
            update_fields.append("`CategoryID (FK)` = %s")
            update_values.append(CategoryID)

        if Threshold is not None:
            update_fields.append("Threshold = %s")
            update_values.append(Threshold)

        if Image:
            file_extension = Image.filename.split(".")[-1]
            image_filename = f"{ProductName.replace(' ', '_')}_{int(datetime.utcnow().timestamp())}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, image_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(Image.file, buffer)

            if product[5]:
                old_image_path = os.path.join(UPLOAD_DIR, product[5])
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            update_fields.append("Image = %s")
            update_values.append(image_filename)

        if not update_fields:
            cursor.close()
            raise HTTPException(status_code=400, detail="No fields provided for update")

        # Update status based on process type and threshold
        status = determine_status(None, product[4], Threshold)
        update_fields.append("Status = %s")
        update_values.append(status)

        update_query = f"UPDATE inventoryproduct SET {', '.join(update_fields)} WHERE id = %s"
        update_values.append(product_id)

        cursor.execute(update_query, tuple(update_values))
        db.commit()

        # Update log in a safer way
        try:
            log_activity_safe(
                cursor=cursor, 
                db=db, 
                icon="pi pi-pencil", 
                title=f"Product updated: {ProductName or product[0]}", 
                status="Updated"
            )
        except Exception as log_error:
            logger.warning(f"Failed to log activity: {log_error}")
        
        cursor.close()

        return {
            "message": "Product updated successfully",
            "Image": f"/uploads/products/{image_filename}" if image_filename else None,
        }

    except Exception as e:
        logger.error(f"Error updating inventory product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Helper function for safe activity logging
def log_activity_safe(cursor, db, icon: str, title: str, status: str):
    """Log activity with proper cursor handling"""
    try:
        cursor.execute(
            "INSERT INTO activity_logs (icon, title, time, status) VALUES (%s, %s, NOW(), %s)",
            (icon, title, status),
        )
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")
        # Don't raise exception since logging failure shouldn't affect the main operation

@InventoryRouter.delete("/inventoryproduct/{product_id}", response_model=dict)
async def delete_inventory_product(product_id: str, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        
        # Get product details before deletion
        cursor.execute("""
            SELECT ProductName, ProcessType, UnitPrice, `CategoryID (FK)` 
            FROM inventoryproduct 
            WHERE id = %s
        """, (product_id,))
        product = cursor.fetchone()

        if not product:
            cursor.close()
            raise HTTPException(status_code=404, detail="Product not found")

        # Delete related records
        cursor.execute("DELETE FROM stock_details WHERE ProductID = %s", (product_id,))
        cursor.execute("DELETE FROM inventoryproduct WHERE id = %s", (product_id,))

        # Log the transaction - use an updated approach
        try:
            cursor.execute(
                """
                INSERT INTO product_transactions 
                (product_id, product_name, transaction_type, process_type, unit_price, category_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, 
                (product_id, product[0], "Delete", product[1], product[2], product[3])
            )
        except Exception as log_error:
            logger.warning(f"Failed to log product transaction: {log_error}")

        db.commit()
        
        # Log activity using the new helper function
        try:
            log_activity_safe(
                cursor=cursor, 
                db=db, 
                icon="pi pi-trash", 
                title=f"Product deleted: {product[0]}", 
                status="Deleted"
            )
        except Exception as log_error:
            logger.warning(f"Failed to log activity: {log_error}")
        
        cursor.close()
        
        return {"message": "Product deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting inventory product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@InventoryRouter.post("/inventorysummary", response_model=list)
async def post_inventory_summary(db=Depends(get_db)):
    try:
        cursor = db.cursor()
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  

        cursor.execute(
            "INSERT INTO reports (ReportType, ReportName, ReportDate) VALUES (%s, %s, %s)",
            ("Daily", "Inventory Summary", report_date)
        )
        db.commit()

        cursor.execute("SELECT LAST_INSERT_ID()")
        report_id = cursor.fetchone()[0]  

        cursor.execute("SELECT id, ProductName, Quantity, UnitPrice, `CategoryID (FK)`, Image FROM inventoryproduct")
        products = cursor.fetchall()

        for product in products:
            product_id, product_name, quantity, unit_price, category_id, image = product
            quantity = quantity if quantity is not None else 0
            unit_price = unit_price if unit_price is not None else 0.0
            
            # Need to get the process_type for each product
            cursor.execute("SELECT ProcessType, Threshold FROM inventoryproduct WHERE id = %s", (product_id,))
            proc_info = cursor.fetchone()
            process_type = proc_info[0] if proc_info else "Ready-Made"  # Default to Ready-Made if not found
            threshold = proc_info[1] if proc_info else None
            
            status = determine_status(quantity, process_type, threshold)

            cursor.execute(
                """
                INSERT INTO inventory_reports 
                (ReportDate, ProductID, ProductName, Quantity, UnitPrice, CategoryID, Status, Image) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (report_date, product_id, product_name, quantity, unit_price, category_id, status, image)
            )

        db.commit()

        # Log activity safely
        try:
            log_activity_safe(
                cursor=cursor, 
                db=db, 
                icon="pi pi-chart-line", 
                title="Inventory summary generated", 
                status="Success"
            )
        except Exception as log_error:
            logger.warning(f"Failed to log activity: {log_error}")

        # Format the response
        result = []
        for product in products:
            # We need to get the process_type here as well
            product_id = product[0]
            cursor.execute("SELECT ProcessType, Threshold FROM inventoryproduct WHERE id = %s", (product_id,))
            proc_info = cursor.fetchone()
            process_type = proc_info[0] if proc_info else "Ready-Made"
            threshold = proc_info[1] if proc_info else None
            
            result.append({
                "id": product[0],
                "ProductName": product[1],
                "Quantity": product[2] if product[2] is not None else 0,
                "UnitPrice": product[3] if product[3] is not None else 0.0,
                "CategoryID": product[4],
                "Status": determine_status(product[2] if product[2] is not None else 0, process_type, threshold),
                "Image": f"/uploads/products/{product[5]}" if product[5] else None
            })
        
        cursor.close()
        return result
        
    except Exception as e:
        logger.error(f"Error generating inventory summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating inventory summary: {str(e)}")

@InventoryRouter.get("/activity_logs", response_model=list)
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
        raise HTTPException(status_code=500, detail=f"Error fetching activity logs: {str(e)}")

@InventoryRouter.get("/product_transactions", response_model=list)
async def get_product_transactions(db=Depends(get_db)):
    """Fetch all product transactions."""
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT pt.id, pt.product_id, pt.product_name, pt.transaction_type, 
                   pt.process_type, pt.unit_price, pt.category_id, pt.created_at
            FROM product_transactions pt
            ORDER BY pt.created_at DESC
        """)
        
        transactions = cursor.fetchall()
        cursor.close()
        
        return [
            {
                "id": t[0],
                "product_id": t[1],
                "product_name": t[2],
                "transaction_type": t[3],
                "process_type": t[4],
                "unit_price": float(t[5]),
                "category_id": t[6],
                "created_at": t[7].strftime("%Y-%m-%d %H:%M:%S")
            }
            for t in transactions
        ]

    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")
    
@InventoryRouter.get("/total-products", response_model=dict)
async def get_total_products(db=Depends(get_db)):
    """Fetch total count of products in the inventory."""
    try:
        # Get the cursor from the connection
        cursor = db.cursor()
        
        # SQL query to count all products in the inventory
        cursor.execute("""SELECT COUNT(*) FROM inventoryproduct""")
        
        # Fetch the count
        total_products = cursor.fetchone()[0]
        
        # Close the cursor
        cursor.close()

        # Return the result as a dictionary
        return {"total_products": total_products}

    except Exception as e:
        # Log and raise an error in case of any issues
        logger.error(f"Error fetching total product count: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@InventoryRouter.get("/low-stock-total", response_model=dict)
async def get_total_low_stock(db=Depends(get_db)):
    """Fetch total count of products that are in low stock, excluding 'To Be Made' products."""
    try:
        # Get the cursor from the connection
        cursor = db.cursor()
        
        # SQL query to count low stock products (not zero quantity)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM inventoryproduct
            WHERE ProcessType = 'Ready-Made' 
            AND Quantity > 0 AND Quantity <= COALESCE(Threshold, 5) AND COALESCE(Threshold, 5) > 0
        """)
        
        # Fetch the count
        low_stock_count = cursor.fetchone()[0] or 0
        
        # SQL query to count out of stock products (zero quantity)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM inventoryproduct
            WHERE ProcessType = 'Ready-Made' 
            AND (Quantity <= 0 OR Quantity IS NULL)
        """)
        
        # Fetch the count
        out_of_stock_count = cursor.fetchone()[0] or 0
        
        # Close the cursor
        cursor.close()

        # Return the result as a dictionary - make the out_of_stock_count the main alert count
        return {
            "total_low_stock": low_stock_count,
            "total_out_of_stock": out_of_stock_count,
            "total_alert": out_of_stock_count, 
            "total_attention_needed": low_stock_count + out_of_stock_count
        }

    except Exception as e:
        # Log and raise an error in case of any issues
        logger.error(f"Error fetching total low stock count: {str(e)}")
        # Return zeros instead of failing completely
        return {
            "total_low_stock": 0,
            "total_out_of_stock": 0,
            "total_alert": 0,
            "total_attention_needed": 0,
            "error": str(e)
        }

# Database connection function
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Warweapons19",  # Match password from cafe-beata-main
        database="cafe_beata"
    )
    return connection

# Function to notify Cafe Beata of stock changes for Ready-Made products
def notify_cafe_beata_stock_change(product_id: int) -> bool:
    """
    Notifies the cafe-beata system that a product's stock has changed
    Returns True if successful, False otherwise
    """
    try:
        # Get the current product details to include in the notification
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Fetch current product details
        cursor.execute("""
            SELECT id, ProductName, Quantity, ProcessType, Threshold 
            FROM inventoryproduct 
            WHERE id = %s
        """, [product_id])
        
        product = cursor.fetchone()
        if not product:
            logger.error(f"Product not found when trying to notify cafe-beata: product_id={product_id}")
            cursor.close()
            connection.close()
            return False
        
        # Only notify if this is a Ready-Made product
        if product['ProcessType'] != 'Ready-Made':
            logger.info(f"Not notifying cafe-beata for non-Ready-Made product: product_id={product_id}")
            cursor.close()
            connection.close()
            return True
        
        # Prepare the data to send
        data = {
            "product_id": product_id,
            "product_name": product['ProductName'],
            "quantity": product['Quantity'],
            "status": determine_status(product['Quantity'], product['ProcessType'], product['Threshold']),
            "timestamp": datetime.now().isoformat()
        }
        
        # Log what we're about to send
        logger.info(f"Notifying cafe-beata of stock change: {data}")
        
        # Send real-time WebSocket notification
        try:
            import asyncio
            from main import get_websocket_manager
            
            # Get the WebSocket manager
            manager = get_websocket_manager()
            
            # Prepare the WebSocket message
            ws_message = {
                "type": "stock_update",
                "data": data
            }
            
            # Broadcast the message via WebSocket asynchronously
            asyncio.create_task(manager.broadcast(ws_message))
            logger.info(f"WebSocket notification sent for product {product_id}")
        except Exception as ws_error:
            logger.error(f"Error sending WebSocket notification: {ws_error}")
            # Continue with webhook anyway
        
        # Cafe Beata webhook URL - make sure this is exactly right
        cafe_beata_webhook_url = "http://127.0.0.1:8000/api/inventory-webhook/stock-update"
        
        # Send the notification with timeout
        response = requests.post(
            cafe_beata_webhook_url, 
            json=data, 
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        
        cursor.close()
        connection.close()
        
        if response.status_code == 200:
            logger.info(f"Successfully notified cafe-beata of stock change for product {product_id}")
            return True
        else:
            logger.error(f"Failed to notify cafe-beata: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to cafe-beata webhook for product {product_id}")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error notifying cafe-beata webhook for product {product_id}")
        return False
    except Exception as e:
        logger.error(f"Error notifying cafe-beata: {e}")
        return False

# Function to check if a product is ready-made
def is_ready_made_product(product_id: int, connection) -> bool:
    """
    Check if a product is a Ready-Made product
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT ProcessType FROM inventoryproduct WHERE id = %s", [product_id])
        product = cursor.fetchone()
        cursor.close()
        
        if not product:
            return False
        
        process_type = product.get('ProcessType', '').lower()
        return process_type in ['ready-made', 'ready made', 'ready_made', 'readymade']
    except Exception as e:
        print(f"Error checking if product {product_id} is Ready-Made: {e}")
        return False

# Get all products
@InventoryRouter.get("/products")
async def get_products(process_type: Optional[str] = None):
    """
    Get all products or filter by process type
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Build the query based on the process_type filter
        query = "SELECT * FROM inventoryproduct"
        params = []
        
        if process_type:
            query += " WHERE ProcessType = %s"
            params.append(process_type)
            
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {"success": True, "products": products}
    
    except Exception as e:
        print(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get product by ID
@InventoryRouter.get("/products/{product_id}")
async def get_product(product_id: int):
    """
    Get a specific product by ID
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM inventoryproduct WHERE id = %s", [product_id])
        product = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        return {"success": True, "product": product}
    
    except Exception as e:
        print(f"Error getting product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create a new product
@InventoryRouter.post("/products")
async def create_product(
    ProductName: str = Form(...),
    ItemCode: str = Form(...),
    Description: str = Form(None),
    Price: float = Form(...),
    Quantity: int = Form(...),
    Threshold: int = Form(...),
    InStock: str = Form(...),
    SupplierID: int = Form(...),
    CategoryID: int = Form(...),
    ProcessType: str = Form(...),
    ProductImage: UploadFile = File(None)
):
    """
    Create a new inventory product
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Handle image upload if provided
        image_path = None
        if ProductImage:
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads/products", exist_ok=True)
            
            # Generate a unique filename
            file_extension = os.path.splitext(ProductImage.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            image_path = f"uploads/products/{unique_filename}"
            
            # Save the file
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(ProductImage.file, buffer)
        
        # Insert the new product
        query = """
        INSERT INTO inventoryproduct 
        (ProductName, ItemCode, Description, Price, Quantity, Threshold, 
        InStock, SupplierID, CategoryID, ProcessType, ProductImage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, [
            ProductName, ItemCode, Description, Price, Quantity, Threshold,
            InStock, SupplierID, CategoryID, ProcessType, image_path
        ])
        
        product_id = cursor.lastrowid
        connection.commit()
        
        cursor.close()
        
        # Notify Cafe Beata if this is a Ready-Made product
        if ProcessType.lower() in ['ready-made', 'ready made', 'ready_made', 'readymade']:
            notify_cafe_beata_stock_change(product_id)
        
        connection.close()
        
        return {"success": True, "message": "Product created successfully", "product_id": product_id}
    
    except Exception as e:
        print(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Update a product
@InventoryRouter.put("/products/{product_id}")
async def update_product(
    product_id: int,
    ProductName: str = Form(...),
    ItemCode: str = Form(...),
    Description: str = Form(None),
    Price: float = Form(...),
    Quantity: int = Form(...),
    Threshold: int = Form(...),
    InStock: str = Form(...),
    SupplierID: int = Form(...),
    CategoryID: int = Form(...),
    ProcessType: str = Form(...),
    ProductImage: UploadFile = File(None)
):
    """
    Update an existing product
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if product exists
        cursor.execute("SELECT * FROM inventoryproduct WHERE id = %s", [product_id])
        existing_product = cursor.fetchone()
        
        if not existing_product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Handle image upload if provided
        image_path = existing_product.get('ProductImage')
        if ProductImage:
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads/products", exist_ok=True)
            
            # Generate a unique filename
            file_extension = os.path.splitext(ProductImage.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            image_path = f"uploads/products/{unique_filename}"
            
            # Save the file
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(ProductImage.file, buffer)
        
        # Update the product
        query = """
        UPDATE inventoryproduct SET
        ProductName = %s, ItemCode = %s, Description = %s, Price = %s, Quantity = %s,
        Threshold = %s, InStock = %s, SupplierID = %s, CategoryID = %s, ProcessType = %s,
        ProductImage = %s, UpdatedAt = NOW()
        WHERE id = %s
        """
        
        cursor.execute(query, [
            ProductName, ItemCode, Description, Price, Quantity, Threshold,
            InStock, SupplierID, CategoryID, ProcessType, image_path, product_id
        ])
        
        connection.commit()
        
        # Check if this is a Ready-Made product or if process type changed to Ready-Made
        if (ProcessType.lower() in ['ready-made', 'ready made', 'ready_made', 'readymade'] or
            (existing_product.get('ProcessType', '').lower() in ['ready-made', 'ready made', 'ready_made', 'readymade'])):
            notify_cafe_beata_stock_change(product_id)
        
        cursor.close()
        connection.close()
        
        return {"success": True, "message": "Product updated successfully"}
    
    except Exception as e:
        print(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Delete a product
@InventoryRouter.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """
    Delete a product
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if product exists
        cursor.execute("SELECT * FROM inventoryproduct WHERE id = %s", [product_id])
        existing_product = cursor.fetchone()
        
        if not existing_product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Delete the product
        cursor.execute("DELETE FROM inventoryproduct WHERE id = %s", [product_id])
        connection.commit()
        
        # Notify Cafe Beata if this was a Ready-Made product
        if existing_product.get('ProcessType', '').lower() in ['ready-made', 'ready made', 'ready_made', 'readymade']:
            notify_cafe_beata_stock_change(product_id)
        
        cursor.close()
        connection.close()
        
        return {"success": True, "message": "Product deleted successfully"}
    
    except Exception as e:
        print(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@InventoryRouter.get("/inventory-status", response_model=dict)
async def get_inventory_status(db=Depends(get_db)):
    """Get a breakdown of inventory status with details"""
    try:
        # Get the cursor from the connection
        cursor = db.cursor(dictionary=True)
        
        # Get all Ready-Made products
        cursor.execute("""
            SELECT id, ProductName, Quantity, Price, UnitPrice, Threshold, ProcessType,
            CASE 
                WHEN Quantity <= 0 THEN 'Out of Stock'
                WHEN Quantity <= Threshold THEN 'Low Stock'
                ELSE 'In Stock'
            END as Status
            FROM inventoryproduct
            WHERE ProcessType = 'Ready-Made'
            ORDER BY 
                CASE 
                    WHEN Quantity <= 0 THEN 1
                    WHEN Quantity <= Threshold THEN 2
                    ELSE 3
                END,
                ProductName
        """)
        
        products = cursor.fetchall()
        
        # Process products into categories
        out_of_stock = []
        low_stock = []
        in_stock = []
        
        for product in products:
            # Make sure price is properly set
            price = product.get('UnitPrice') if product.get('UnitPrice') else product.get('Price', 0)
            if price is None:
                price = 0
                
            product_data = {
                "id": product.get('id'),
                "name": product.get('ProductName'),
                "quantity": product.get('Quantity', 0),
                "price": float(price),
                "threshold": product.get('Threshold', 0)
            }
            
            if product.get('Status') == 'Out of Stock':
                out_of_stock.append(product_data)
            elif product.get('Status') == 'Low Stock':
                low_stock.append(product_data)
            else:
                in_stock.append(product_data)
        
        # Close the cursor
        cursor.close()
        
        return {
            "out_of_stock": {
                "count": len(out_of_stock),
                "items": out_of_stock
            },
            "low_stock": {
                "count": len(low_stock),
                "items": low_stock
            },
            "in_stock": {
                "count": len(in_stock),
                "items": in_stock
            },
            "total_products": len(products)
        }
        
    except Exception as e:
        logger.error(f"Error getting inventory status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
