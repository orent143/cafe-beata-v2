from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from model.db import get_db, db_connection
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sales")

SalesRouter = APIRouter(tags=["Sales"])

# Sales Response Model
class SalesResponse(BaseModel):
    name: str
    quantity: int
    unit_price: float
    items_sold: int
    remitted: float
    image_url: str  # Include image URL

# Sales Update Model
class SalesUpdateRequest(BaseModel):
    product_id: int
    quantity_sold: int
    remitted: float

# Fetch sales data
@SalesRouter.get("/sales", response_model=List[SalesResponse])
async def get_sales_data(db=Depends(get_db)):
    try:
        cursor = db.cursor(dictionary=True)
        today = datetime.now().date()  # Get today's date

        # Fetch and aggregate sales per product for today, including product image
        cursor.execute("""
            SELECT 
                ip.ProductName, ip.Quantity, ip.UnitPrice, ip.Image,
                COALESCE(SUM(s.quantity_sold), 0) AS total_items_sold, 
                COALESCE(SUM(s.remitted), 0) AS total_remitted
            FROM inventoryproduct ip
            LEFT JOIN sales s ON ip.id = s.product_id AND DATE(s.created_at) = %s  
            GROUP BY ip.id, ip.ProductName, ip.Quantity, ip.UnitPrice, ip.Image
            ORDER BY ip.id ASC
        """, (today,))

        sales_data = cursor.fetchall()
        cursor.close()

        if not sales_data:
            return []  

        return [
            {
                "name": row["ProductName"],
                "quantity": row["Quantity"],
                "unit_price": float(row["UnitPrice"]),
                "items_sold": row["total_items_sold"],
                "remitted": float(row["total_remitted"]),
                "image_url": row["Image"] if row["Image"] else ""  
            }
            for row in sales_data
        ]
    
    except Exception as e:
        logger.error(f"Error getting sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Fetch historical sales data by date
@SalesRouter.get("/sales/daily", response_model=List[SalesResponse])
async def get_daily_sales_data(date: Optional[str] = None, db=Depends(get_db)):
    try:
        cursor = db.cursor(dictionary=True)
        
        # Parse the date or use today's date
        target_date = datetime.now().date()
        if date:
            try:
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Fetch and aggregate sales per product for the specific date
        cursor.execute("""
            SELECT 
                ip.ProductName, ip.Quantity, ip.UnitPrice, ip.Image,
                COALESCE(SUM(s.quantity_sold), 0) AS total_items_sold, 
                COALESCE(SUM(s.remitted), 0) AS total_remitted,
                MAX(s.created_at) AS created_at
            FROM inventoryproduct ip
            LEFT JOIN sales s ON ip.id = s.product_id AND DATE(s.created_at) = %s  
            GROUP BY ip.id, ip.ProductName, ip.Quantity, ip.UnitPrice, ip.Image
            ORDER BY created_at DESC
        """, (target_date,))

        sales_data = cursor.fetchall()
        cursor.close()

        if not sales_data:
            return []  

        return [
            {
                "name": row["ProductName"],
                "quantity": row["Quantity"],
                "unit_price": float(row["UnitPrice"]),
                "items_sold": row["total_items_sold"],
                "remitted": float(row["total_remitted"]),
                "image_url": row["Image"] if row["Image"] else "",
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
            for row in sales_data
        ]
    
    except Exception as e:
        logger.error(f"Error getting daily sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@SalesRouter.post("/update")
async def update_sales(sales_update: SalesUpdateRequest, db=Depends(get_db)):
    try:
        cursor = db.cursor()

        cursor.execute("SELECT Quantity FROM inventoryproduct WHERE id = %s", (sales_update.product_id,))
        product = cursor.fetchone()

        if not product:
            cursor.close()
            raise HTTPException(status_code=404, detail="Product not found")

        available_stock = product[0]

        if available_stock < sales_update.quantity_sold:
            cursor.close()
            raise HTTPException(status_code=400, detail="Not enough stock available")

        cursor.execute("""
            INSERT INTO sales (product_id, quantity_sold, remitted, created_at)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                quantity_sold = quantity_sold + VALUES(quantity_sold), 
                remitted = remitted + VALUES(remitted)
        """, (sales_update.product_id, sales_update.quantity_sold, sales_update.remitted))

        cursor.execute("""
            UPDATE inventoryproduct 
            SET Quantity = Quantity - %s 
            WHERE id = %s
        """, (sales_update.quantity_sold, sales_update.product_id))

        db.commit()
        cursor.close()
        return {"message": "Sales updated successfully"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating sales: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@SalesRouter.get("/total-sales-revenue", response_model=dict)
async def get_total_sales_revenue():
    """Get the total sales revenue for today"""
    with db_connection() as db:
        cursor = None
        try:
            cursor = db.cursor()
            today = datetime.now().date()  # Get today's date

            # SQL query to calculate total sales revenue for today
            cursor.execute("""
                SELECT COALESCE(SUM(s.remitted), 0) AS total_revenue
                FROM sales s
                WHERE DATE(s.created_at) = %s
            """, (today,))

            total_revenue = cursor.fetchone()[0]
            return {"total_sales_revenue": total_revenue}

        except Exception as e:
            logger.error(f"Error getting total sales revenue: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
