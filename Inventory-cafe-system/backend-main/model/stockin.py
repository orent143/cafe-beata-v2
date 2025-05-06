from fastapi import Depends, HTTPException, APIRouter, Form, UploadFile, File, Request
from typing import List, Optional
from pydantic import BaseModel
from model.db import get_db, db_transaction, db_connection
from model.performance_metrics import record_stock_update_time
from datetime import datetime
import logging
import os
import time
import shutil
import uuid
from model.inventoryproduct import notify_cafe_beata_stock_change, is_ready_made_product

StockRouter = APIRouter(tags=["Stock In"])


class StockItem(BaseModel):
    batch_number: str
    quantity: int
    expiration_date: str
    SupplierID: Optional[int] = None


class StockInRequest(BaseModel):
    ProductName: str
    Stocks: List[StockItem]


logger = logging.getLogger(__name__)


@StockRouter.post("/stockin/")
@db_transaction
async def stock_in(request: StockInRequest, db=Depends(get_db)):
    try:
        cursor = db.cursor()

        # Fetch product by ProductName instead of ProductID
        cursor.execute("SELECT id, ProductName, ProcessType FROM inventoryproduct WHERE ProductName = %s", (request.ProductName,))
        product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product_id = product[0]
        process_type = product[2]
        total_quantity_added = 0

        # Start timing the stock update
        start_time = time.time()

        for stock in request.Stocks:
            original_quantity = stock.quantity if process_type and process_type.lower() == "ready-made" else 0

            cursor.execute("""
                INSERT INTO stock_details (ProductID, batch_number, quantity, expiration_date, SupplierID, original_quantity, created_at, transaction_type)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), 'IN')
            """, (product_id, stock.batch_number, stock.quantity, stock.expiration_date, stock.SupplierID, original_quantity))
            total_quantity_added += stock.quantity

        cursor.execute("UPDATE inventoryproduct SET Quantity = Quantity + %s WHERE id = %s", (total_quantity_added, product_id))

        db.commit()

        # End timing and record it
        execution_time_ms = (time.time() - start_time) * 1000
        record_stock_update_time(product_id, execution_time_ms)

        return {"message": "Stock added successfully", "ProductName": product[1], "TotalQuantityAdded": total_quantity_added}

    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"Error in stock_in: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



@StockRouter.get("/stockin/{product_id}", response_model=dict)
@db_transaction
async def get_product_details(product_id: str, request = None, db=Depends(get_db)):
    """Get product details with consistent remaining quantity."""
    cursor = None
    try:
        base_url = "http://127.0.0.1:8001/"
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                ip.id, 
                ip.ProductName, 
                ip.Quantity,    -- ✅ Pulling the quantity directly from inventoryproduct
                ip.ProcessType, 
                ip.Image, 
                ip.Threshold,  -- Fetch the threshold value for the product
                COALESCE(s.SupplierName, 'N/A') AS SupplierName
            FROM inventoryproduct ip
            LEFT JOIN stock_details sd ON ip.id = sd.ProductID
            LEFT JOIN suppliers s ON sd.SupplierID = s.id
            WHERE ip.id = %s
            ORDER BY sd.created_at DESC LIMIT 1
        """, (product_id,))

        product = cursor.fetchone()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Extract values
        remaining_quantity = product["Quantity"]
        threshold = product["Threshold"] if product["Threshold"] is not None else 5  # Default threshold to 5 if not set

        # Determine stock status based on threshold and remaining quantity
        if remaining_quantity <= 0:
            status = "Out of Stock"
        elif remaining_quantity <= threshold:
            status = "Low Stock"
        else:
            status = "In Stock"

        return {
            "ProductID": product["id"],
            "ProductName": product["ProductName"],
            "Quantity": remaining_quantity,
            "ProcessType": product["ProcessType"],
            "Image": f"{base_url}uploads/products/{product['Image']}" if product["Image"] else None,
            "CurrentSupplier": product["SupplierName"],
            "Threshold": threshold,  # Return Threshold in the response
            "Status": status
        }

    except Exception as e:
        logger.error(f"Error in get_product_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        if cursor and cursor != db.cursor():
            cursor.close()

@StockRouter.get("/stockdetails/{product_id}", response_model=dict)
@db_transaction
async def get_stock_details(product_id: str, db=Depends(get_db)):
    """Get detailed stock info with remaining quantity and basic product details."""
    try:
        cursor = db.cursor()
        logger.info(f"Getting stock details for product ID: {product_id}")

        # Fetch product details from the inventoryproduct table
        cursor.execute("""
            SELECT id, ProductName, Quantity, ProcessType, Image, Threshold, UnitPrice
            FROM inventoryproduct 
            WHERE id = %s
        """, (product_id,))
        
        product = cursor.fetchone()
        
        if not product:
            logger.warning(f"Product not found: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
            
        # Get supplier info in a separate query to avoid GROUP BY issues
        cursor.execute("""
            SELECT COALESCE(s.SupplierName, 'N/A') AS SupplierName
            FROM stock_details sd
            LEFT JOIN suppliers s ON sd.SupplierID = s.id
            WHERE sd.ProductID = %s
            ORDER BY sd.created_at DESC
            LIMIT 1
        """, (product_id,))
        
        supplier_info = cursor.fetchone()
        supplier_name = supplier_info[0] if supplier_info else "Unknown"

        # Extract values with proper null handling
        product_id_value = product[0]
        product_name = product[1] or "Unknown Product"
        remaining_quantity = product[2] if product[2] is not None else 0
        process_type = product[3] or "Standard"
        image = product[4]
        threshold = product[5] if product[5] is not None else 5  
        unit_price = product[6] if product[6] is not None else 0.00

        base_url = "http://127.0.0.1:8001/uploads/products/"

        # Fetch current stock details from stock_details table
        cursor.execute("""
            SELECT 
                sd.id,
                sd.batch_number,
                sd.quantity,
                sd.expiration_date,
                sd.created_at,
                COALESCE(s.SupplierName, 'Unknown') AS SupplierName,
                sd.original_quantity
            FROM stock_details sd
            LEFT JOIN suppliers s ON sd.SupplierID = s.id
            WHERE sd.ProductID = %s
            ORDER BY sd.created_at DESC
        """, (product_id,))

        stocks = cursor.fetchall()

        # Prepare stock list with safe error handling
        stock_list = []
        for stock in stocks:
            try:
                stock_item = {
                    "id": stock[0],
                    "batch_number": stock[1] or "Unknown",
                    "quantity": stock[2] if stock[2] is not None else 0,
                    "expiration_date": stock[3].strftime('%Y-%m-%d') if stock[3] else None,
                    "created_at": stock[4].strftime('%Y-%m-%d %H:%M:%S') if stock[4] else None,
                    "SupplierName": stock[5] or "Unknown",
                    "original_quantity": stock[6] if stock[6] is not None else 0
                }
                stock_list.append(stock_item)
            except Exception as date_error:
                logger.error(f"Error formatting stock data: {date_error}")
                stock_list.append({
                    "id": stock[0] if stock[0] is not None else 0,
                    "batch_number": str(stock[1]) if stock[1] else "Unknown",
                    "quantity": stock[2] if stock[2] is not None else 0,
                    "expiration_date": None,
                    "created_at": None,
                    "SupplierName": str(stock[5]) if stock[5] else "Unknown",
                    "original_quantity": stock[6] if len(stock) > 6 and stock[6] is not None else 0
                })

        # Fetch unique deducted transactions from inventory_transactions table
        cursor.execute("""
            SELECT 
                MIN(it.id) AS TransactionID,  -- Use MIN(id) to ensure unique rows
                it.quantity AS QuantityDeducted,
                it.created_at AS TransactionDate
            FROM inventory_transactions it
            WHERE it.ProductID = %s
            AND it.transaction_type = 'Deduct'
            GROUP BY it.quantity, it.created_at  -- Group by quantity and created_at to remove duplicates
            ORDER BY it.created_at DESC
        """, (product_id,))

        deducted_transactions = cursor.fetchall()
        deducted_list = []
        
        for trans in deducted_transactions:
            try:
                deducted_item = {
                    "TransactionID": trans[0],
                    "QuantityDeducted": trans[1] if trans[1] is not None else 0,
                    "TransactionDate": trans[2].strftime('%Y-%m-%d %H:%M:%S') if trans[2] else None
                }
                deducted_list.append(deducted_item)
            except Exception as date_error:
                logger.error(f"Error formatting transaction data: {date_error}")
                # Add a transaction item with safer values
                deducted_list.append({
                    "TransactionID": trans[0] if trans[0] is not None else 0,
                    "QuantityDeducted": trans[1] if trans[1] is not None else 0,
                    "TransactionDate": None
                })

        # Determine stock status based on threshold and remaining quantity
        if remaining_quantity <= 0:
            status = "Out of Stock"
        elif remaining_quantity <= threshold:
            status = "Low Stock"
        else:
            status = "In Stock"

        # Prepare and return the result with complete null safety
        result = {
            "ProductID": product_id_value,
            "ProductName": product_name,
            "UnitPrice": unit_price,
            "Quantity": remaining_quantity,
            "ProcessType": process_type,
            "Image": f"{base_url}{image}" if image else None,
            "CurrentSupplier": supplier_name,
            "Status": status,
            "StockDetails": stock_list,
            "DeductedTransactions": deducted_list
        }
        
        logger.info(f"Successfully fetched stock details for product {product_id}")
        return result

    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        logger.error(f"Error in get_stock_details for product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@StockRouter.delete("/stockdetails/{product_id}/{TransactionID}")
@db_transaction
async def delete_stock_transaction(product_id: str, TransactionID: int, db=Depends(get_db)):
    """
    Delete a stock-in transaction and revert inventory quantity.
    """
    try:
        cursor = db.cursor(dictionary=True)

        # Step 1: Verify the transaction exists
        cursor.execute("""
            SELECT id, ProductID, transaction_type, quantity
            FROM stock_details
            WHERE id = %s AND ProductID = %s
        """, (TransactionID, product_id))
        transaction = cursor.fetchone()

        if not transaction:
            raise HTTPException(status_code=404, detail=f"Transaction with ID {TransactionID} for product {product_id} not found")

        transaction_type = transaction["transaction_type"]
        quantity = transaction["quantity"]

        # Step 2: Only allow deleting IN transactions
        if transaction_type != "IN":
            raise HTTPException(status_code=400, detail="Only stock-in transactions can be deleted")

        # Step 3: Update inventory quantity (revert added stock)
        cursor.execute("""
            UPDATE inventoryproduct
            SET Quantity = CASE 
                WHEN Quantity - %s < 0 THEN 0 
                ELSE Quantity - %s 
            END
            WHERE id = %s
        """, (quantity, quantity, product_id))

        # Step 4: Delete the stock-in record
        cursor.execute("DELETE FROM stock_details WHERE id = %s", (TransactionID,))

        db.commit()

        return {
            "message": f"Stock-in transaction {TransactionID} deleted successfully.",
            "RevertedQuantity": quantity,
            "ProductID": product_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting stock-in transaction {TransactionID}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@StockRouter.delete("/stockout/{TransactionID}")
@db_transaction
async def delete_stock_out_transaction(TransactionID: int, db=Depends(get_db)):
    """
    Delete a stock out/deducted transaction by its ID and update the product quantity.
    """
    try:
        cursor = db.cursor(dictionary=True)

        # Fetch the transaction details to determine its type
        cursor.execute("""
            SELECT id, ProductID, quantity, transaction_type
            FROM inventory_transactions
            WHERE id = %s AND transaction_type = 'Deduct'
        """, (TransactionID,))
        transaction = cursor.fetchone()

        if not transaction:
            raise HTTPException(status_code=404, detail=f"Transaction with ID {TransactionID} not found or is not a 'Deduct' transaction")

        product_id = transaction["ProductID"]
        quantity = transaction["quantity"]

        # Delete the transaction
        cursor.execute("DELETE FROM inventory_transactions WHERE id = %s", (TransactionID,))

        # Update the product quantity by adding back the deducted quantity
        cursor.execute("""
            UPDATE inventoryproduct
            SET Quantity = Quantity + %s
            WHERE id = %s
        """, (quantity, product_id))

        db.commit()

        return {
            "message": f"Stock out transaction {TransactionID} deleted successfully",
            "ProductID": product_id,
            "RestoredQuantity": quantity
        }

    except HTTPException:
        raise
    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"Error deleting stock out transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@StockRouter.get("/inventory-transactions", response_model=list)
@db_transaction
async def get_inventory_transactions(db=Depends(get_db)):
    """Fetch all inventory transactions, including stock-in and deducted."""
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, product_name, transaction_type, quantity, created_at
            FROM inventory_transactions
            WHERE transaction_type IN ('Add', 'StockIn', 'Deduct')  -- Include all transaction types
            ORDER BY created_at DESC LIMIT 100
        """)
        
        transactions = cursor.fetchall()
        
        # Format the transactions data
        return [
            {
                "id": t["id"],
                "product_name": t["product_name"],
                "transaction_type": t["transaction_type"],
                "quantity": t["quantity"],
                "created_at": t["created_at"].strftime("%Y-%m-%d %H:%M:%S") if t["created_at"] else None
            }
            for t in transactions
        ]

    except Exception as e:
        logger.error(f"Error fetching inventory transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")
    finally:
        if cursor and cursor != db.cursor():
            cursor.close()

# Get all stock records
@StockRouter.get("/records")
@db_transaction
async def get_stock_records(db=Depends(get_db)):
    """
    Get all stock records
    """
    try:
        cursor = db.cursor(dictionary=True)
        
        query = """
        SELECT s.*, p.ProductName, p.ItemCode
        FROM stockin s
        JOIN inventoryproduct p ON s.ProductID = p.id
        ORDER BY s.DateStocked DESC
        LIMIT 100
        """
        
        cursor.execute(query)
        records = cursor.fetchall()
        
        # Process the results
        for record in records:
            if 'DateStocked' in record and record['DateStocked']:
                record['DateStocked'] = record['DateStocked'].strftime('%Y-%m-%d %H:%M:%S')
            if 'ExpiryDate' in record and record['ExpiryDate']:
                record['ExpiryDate'] = record['ExpiryDate'].strftime('%Y-%m-%d')
                
        return records
        
    except Exception as e:
        logger.error(f"Error fetching stock records: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock records: {str(e)}")

# Add new stock record
@StockRouter.post("/add")
async def add_stock(
    ProductID: int = Form(...),
    Quantity: int = Form(...),
    UnitCost: float = Form(...),
    TotalCost: float = Form(...),
    ExpiryDate: Optional[str] = Form(None),
    InvoiceNumber: str = Form(...),
    StockImage: Optional[UploadFile] = File(None),
    Notes: Optional[str] = Form(None)
):
    """
    Add a new stock record and update product quantity
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Handle image upload if provided
        image_path = None
        if StockImage:
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads/stocks", exist_ok=True)
            
            # Generate a unique filename
            file_extension = os.path.splitext(StockImage.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            image_path = f"uploads/stocks/{unique_filename}"
            
            # Save the file
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(StockImage.file, buffer)
        
        # Insert new stock record
        insert_query = """
        INSERT INTO stockin 
        (ProductID, Quantity, UnitCost, TotalCost, ExpiryDate, InvoiceNumber, StockImage, Notes, DateStocked)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        cursor.execute(insert_query, [
            ProductID, Quantity, UnitCost, TotalCost, ExpiryDate, InvoiceNumber, image_path, Notes
        ])
        
        # Update product quantity
        update_query = """
        UPDATE inventoryproduct 
        SET Quantity = Quantity + %s, UpdatedAt = NOW()
        WHERE id = %s
        """
        
        cursor.execute(update_query, [Quantity, ProductID])
        
        # Set product status to in stock if it wasn't
        cursor.execute("""
        UPDATE inventoryproduct
        SET InStock = 'Yes'
        WHERE id = %s AND InStock = 'No'
        """, [ProductID])
        
        connection.commit()
        
        # Check if this is a Ready-Made product and notify cafe-beata
        if is_ready_made_product(ProductID, connection):
            notify_cafe_beata_stock_change(ProductID)
        
        cursor.close()
        connection.close()
        
        return {"success": True, "message": "Stock added successfully"}
    
    except Exception as e:
        print(f"Error adding stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Adjust stock (increase or decrease)
@StockRouter.post("/adjust/{product_id}")
@db_transaction
async def adjust_stock(
    product_id: int,
    action: str = Form(None),  # Make Form parameters optional
    quantity: int = Form(None),
    reason: str = Form(None),
    request: Request = None,  # Add request parameter to handle JSON
    db=Depends(get_db)  # Add db dependency
):
    """
    Adjust stock level for a product
    """
    try:
        # Handle both Form and JSON data
        if request and request.headers.get("content-type") == "application/json":
            body = await request.json()
            action = body.get("action")
            quantity = body.get("quantity")
            reason = body.get("reason")
            logger.info(f"Received JSON stock adjustment: product_id={product_id}, action={action}, quantity={quantity}, reason={reason}")
        else:
            logger.info(f"Received Form stock adjustment: product_id={product_id}, action={action}, quantity={quantity}, reason={reason}")
        
        if not all([action, quantity, reason]):
            logger.error(f"Missing required parameters: action={action}, quantity={quantity}, reason={reason}")
            raise HTTPException(status_code=400, detail="Missing required parameters")
            
        cursor = db.cursor(dictionary=True)
        
        # Check if product exists
        cursor.execute("SELECT * FROM inventoryproduct WHERE id = %s", [product_id])
        product = cursor.fetchone()
        
        if not product:
            logger.error(f"Product not found: product_id={product_id}")
            raise HTTPException(status_code=404, detail="Product not found")
        
        current_quantity = product.get('Quantity', 0)
        new_quantity = current_quantity
        
        # Calculate new quantity based on action
        if action == 'add':
            new_quantity = current_quantity + quantity
        elif action == 'subtract':
            new_quantity = max(0, current_quantity - quantity)  # Prevent negative quantity
        elif action == 'set':
            new_quantity = quantity
        else:
            logger.error(f"Invalid action: {action}")
            raise HTTPException(status_code=400, detail="Invalid action. Use 'add', 'subtract', or 'set'")
        
        logger.info(f"Adjusting stock: product_id={product_id}, current_quantity={current_quantity}, new_quantity={new_quantity}, action={action}")
        
        # Update product quantity
        cursor.execute("""
        UPDATE inventoryproduct
        SET Quantity = %s
        WHERE id = %s
        """, [new_quantity, product_id])
        
        # Log the number of rows affected
        rows_affected = cursor.rowcount
        logger.info(f"Database update complete: rows_affected={rows_affected}")
        
        if rows_affected == 0:
            logger.warning(f"No rows were updated in the database for product_id={product_id}")
        
        # Add stock adjustment record
        cursor.execute("""
        INSERT INTO stock_adjustments
        (product_id, previous_quantity, new_quantity, action, reason, adjustment_date)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """, [product_id, current_quantity, new_quantity, action, reason])
        
        # Send real-time WebSocket notification
        try:
            import asyncio
            import sys
            import os
            
            # Add the parent directory to sys.path to import main
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from main import get_websocket_manager
            
            # Get the WebSocket manager
            manager = get_websocket_manager()
            
            # Prepare the WebSocket message
            stock_status = "Out of Stock" if new_quantity <= 0 else "Low Stock" if new_quantity <= product.get('Threshold', 5) else "In Stock"
            
            ws_message = {
                "type": "stock_update",
                "data": {
                    "product_id": product_id,
                    "product_name": product.get('ProductName', 'Unknown'),
                    "quantity": new_quantity,
                    "previous_quantity": current_quantity,
                    "status": stock_status,
                    "action": action,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Broadcast the message via WebSocket asynchronously
            asyncio.create_task(manager.broadcast(ws_message))
            logger.info(f"WebSocket notification sent for product {product_id}")
        except Exception as ws_error:
            logger.error(f"Error sending WebSocket notification: {ws_error}")
            # Continue with the regular process
        
        # Check if this is a Ready-Made product and notify cafe-beata
        is_ready = is_ready_made_product(product_id, db)
        logger.info(f"Product is_ready_made: {is_ready}")
        
        if is_ready:
            notify_result = notify_cafe_beata_stock_change(product_id)
            logger.info(f"Notification to cafe-beata result: {notify_result}")
        
        # Verify that the update was successful by querying the database again
        cursor.execute("SELECT Quantity FROM inventoryproduct WHERE id = %s", [product_id])
        verification = cursor.fetchone()
        logger.info(f"Verification query result: {verification}")
        
        return {
            "success": True, 
            "message": f"Stock {action}ed successfully",
            "previous_quantity": current_quantity,
            "new_quantity": new_quantity,
            "verification_quantity": verification['Quantity'] if verification else None
        }
    
    except Exception as e:
        logger.error(f"Error adjusting stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get stock movement history for a product
@StockRouter.get("/history/{product_id}")
async def get_stock_history(product_id: int):
    """
    Get stock movement history for a specific product
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if product exists
        cursor.execute("SELECT * FROM inventoryproduct WHERE id = %s", [product_id])
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get stock in records
        cursor.execute("""
        SELECT 'stockin' as type, DateStocked as date, Quantity, UnitCost, TotalCost, 
               InvoiceNumber, Notes
        FROM stockin
        WHERE ProductID = %s
        """, [product_id])
        
        stock_in = cursor.fetchall()
        
        # Get stock adjustment records
        cursor.execute("""
        SELECT 'adjustment' as type, adjustment_date as date, 
               previous_quantity, new_quantity, action, reason
        FROM stock_adjustments
        WHERE product_id = %s
        """, [product_id])
        
        adjustments = cursor.fetchall()
        
        # Combine and sort records by date
        history = stock_in + adjustments
        history.sort(key=lambda x: x['date'], reverse=True)
        
        cursor.close()
        connection.close()
        
        return {"success": True, "product": product, "history": history}
    
    except Exception as e:
        print(f"Error getting stock history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Set minimum stock level for a product
@StockRouter.put("/min-level/{product_id}")
async def update_min_stock_level(
    product_id: int,
    min_stock_level: int = Form(...)
):
    """
    Update the minimum stock level (threshold) for a product
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Update threshold
        cursor.execute("""
        UPDATE inventoryproduct
        SET Threshold = %s, UpdatedAt = NOW()
        WHERE id = %s
        """, [min_stock_level, product_id])
        
        affected_rows = cursor.rowcount
        connection.commit()
        
        cursor.close()
        connection.close()
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"success": True, "message": "Minimum stock level updated successfully"}
    
    except Exception as e:
        print(f"Error updating minimum stock level: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get low stock alerts
@StockRouter.get("/alerts")
async def get_low_stock_alerts():
    """
    Get products that are below their threshold levels
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
        SELECT p.*, c.CategoryName
        FROM inventoryproduct p
        LEFT JOIN category c ON p.CategoryID = c.id
        WHERE p.Quantity <= p.Threshold
        ORDER BY (p.Threshold - p.Quantity) DESC
        """)
        
        low_stock_products = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {"success": True, "low_stock_products": low_stock_products}
    
    except Exception as e:
        print(f"Error getting low stock alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Handle stock updates from cafe system
@StockRouter.put("/inventoryproduct/{product_id}/stock")
async def update_stock_from_cafe(
    product_id: int,
    action: str = Form(...),  # 'add', 'subtract', or 'set'
    quantity: int = Form(...),
    reason: str = Form(...)
):
    """
    Handle stock updates from the cafe system
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if product exists
        cursor.execute("SELECT * FROM inventoryproduct WHERE id = %s", [product_id])
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        current_quantity = product.get('Quantity', 0)
        new_quantity = current_quantity
        
        # Calculate new quantity based on action
        if action == 'add':
            new_quantity = current_quantity + quantity
        elif action == 'subtract':
            new_quantity = max(0, current_quantity - quantity)  # Prevent negative quantity
        elif action == 'set':
            new_quantity = quantity
        else:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=400, detail="Invalid action. Use 'add', 'subtract', or 'set'")
        
        # Update product quantity
        cursor.execute("""
        UPDATE inventoryproduct
        SET Quantity = %s,
            InStock = CASE WHEN %s > 0 THEN 'Yes' ELSE 'No' END
        WHERE id = %s
        """, [new_quantity, new_quantity, product_id])
        
        # Add stock adjustment record
        cursor.execute("""
        INSERT INTO stock_adjustments
        (product_id, previous_quantity, new_quantity, action, reason, adjustment_date)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """, [product_id, current_quantity, new_quantity, action, reason])
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "success": True, 
            "message": f"Stock {action}ed successfully",
            "previous_quantity": current_quantity,
            "new_quantity": new_quantity
        }
    
    except Exception as e:
        print(f"Error updating stock from cafe: {e}")
        raise HTTPException(status_code=500, detail=str(e))
