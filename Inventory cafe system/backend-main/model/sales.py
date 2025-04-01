from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from pydantic import BaseModel
from model.db import get_db, db_connection
from datetime import datetime, timedelta
import logging
import json
import statistics
import asyncio
from fastapi.background import BackgroundTasks

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

# Historical Sales Response Model
class HistoricalSalesResponse(BaseModel):
    date: str
    total_sales: float
    total_items: int
    items: List[Dict]

# Forecast Response Model
class ForecastResponse(BaseModel):
    historical_data: List[Dict]
    forecast_data: List[Dict]
    product_forecasts: List[Dict]
    metrics: Dict

# Global variable to keep track of the background task
background_fix_task = None

# Background task to fix sales records with missing data
async def fix_sales_records_background():
    """
    Background task to fix sales records with missing product information
    This runs every 6 hours and updates any sales records with empty fields
    """
    while True:
        try:
            logger.info("Running background task to fix sales records with missing data")
            with db_connection() as db:
                cursor = db.cursor()
                
                # Update sales records with missing product information
                cursor.execute("""
                    UPDATE sales s
                    JOIN inventoryproduct ip ON s.product_id = ip.id
                    SET 
                        s.product_name = ip.ProductName,
                        s.unit_price = ip.UnitPrice,
                        s.Image = ip.Image
                    WHERE 
                        s.product_name = '' OR s.product_name IS NULL
                        OR s.unit_price = 0 OR s.unit_price IS NULL
                        OR s.Image IS NULL
                """)
                
                records_updated = cursor.rowcount
                db.commit()
                
                logger.info(f"Fixed {records_updated} sales records with missing data")
                cursor.close()
        except Exception as e:
            logger.error(f"Error in fix_sales_records_background: {str(e)}")
        
        # Sleep for 6 hours before running again
        await asyncio.sleep(6 * 60 * 60)  # 6 hours in seconds

# Start the background task when the module is loaded
def start_background_task():
    global background_fix_task
    if background_fix_task is None:
        background_fix_task = asyncio.create_task(fix_sales_records_background())
        logger.info("Started background task to fix sales records")

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
        cursor = db.cursor(dictionary=True)

        # Get product information including name, price, and image
        cursor.execute("""
            SELECT id, ProductName, UnitPrice, Quantity, Image 
            FROM inventoryproduct 
            WHERE id = %s
        """, (sales_update.product_id,))
        
        product = cursor.fetchone()

        if not product:
            cursor.close()
            raise HTTPException(status_code=404, detail="Product not found")

        available_stock = product['Quantity']

        if available_stock < sales_update.quantity_sold:
            cursor.close()
            raise HTTPException(status_code=400, detail="Not enough stock available")

        # Insert into sales with product details
        cursor.execute("""
            INSERT INTO sales (
                product_id, 
                product_name, 
                Image, 
                quantity_sold, 
                unit_price,
                remitted, 
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE 
                quantity_sold = quantity_sold + VALUES(quantity_sold), 
                remitted = remitted + VALUES(remitted)
        """, (
            sales_update.product_id, 
            product['ProductName'], 
            product['Image'], 
            sales_update.quantity_sold, 
            product['UnitPrice'],
            sales_update.remitted
        ))

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

@SalesRouter.get("/forecasting/historical", response_model=List[HistoricalSalesResponse])
async def get_historical_sales_data(days: int = Query(30, ge=1, le=90), db=Depends(get_db)):
    """
    Get historical sales data for forecasting (last N days)
    """
    try:
        cursor = db.cursor(dictionary=True)
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Fetching historical sales data from {start_date} to {end_date}")
        
        # Get inventory system sales by day - simplify query to avoid JSON functions
        cursor.execute("""
            SELECT 
                DATE(created_at) as sale_date,
                SUM(remitted) as daily_total,
                SUM(quantity_sold) as items_sold
            FROM sales
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY sale_date ASC
        """, (start_date, end_date))
        
        inventory_sales = cursor.fetchall()
        
        # Close db cursor
        cursor.close()
        
        # Format the response
        result = []
        for day in inventory_sales:
            if day['sale_date']:
                result.append({
                    "date": day['sale_date'].strftime('%Y-%m-%d'),
                    "total_sales": float(day['daily_total'] if day['daily_total'] else 0),
                    "total_items": int(day['items_sold'] if day['items_sold'] else 0),
                    "items": []  # Simplified - we're not using the detailed items
                })
            
        return result
        
    except Exception as e:
        logger.error(f"Error getting historical sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@SalesRouter.get("/forecasting/predict", response_model=ForecastResponse)
async def generate_sales_forecast(days_ahead: int = Query(7, ge=1, le=30), db=Depends(get_db)):
    """
    Generate sales forecast for next N days
    """
    try:
        # First, get historical data
        cursor = db.cursor(dictionary=True)
        
        # Last 30 days for historical data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Get inventory system daily sales totals - this query doesn't depend on product names
        cursor.execute("""
            SELECT 
                DATE(created_at) as sale_date,
                SUM(remitted) as daily_total,
                SUM(quantity_sold) as items_sold
            FROM sales
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY sale_date ASC
        """, (start_date, end_date))
        
        daily_sales = cursor.fetchall()
        
        # Modified query to handle missing product data by using LEFT JOIN
        # and COALESCE to handle NULL values
        cursor.execute("""
            SELECT 
                s.product_id,
                COALESCE(p.ProductName, CONCAT('Product ID: ', s.product_id)) as product_name,
                p.Image as image_url,
                SUM(s.quantity_sold) as total_quantity,
                SUM(s.remitted) as total_sales,
                COUNT(DISTINCT DATE(s.created_at)) as days_with_sales
            FROM sales s
            LEFT JOIN inventoryproduct p ON s.product_id = p.id
            WHERE DATE(s.created_at) BETWEEN %s AND %s AND s.quantity_sold > 0
            GROUP BY s.product_id, product_name, image_url
            ORDER BY total_sales DESC
        """, (start_date, end_date))
        
        product_sales = cursor.fetchall()
        
        # Close cursor
        cursor.close()
        
        # Format historical data
        historical_data = []
        for day in daily_sales:
            if day['sale_date']:
                historical_data.append({
                    "date": day['sale_date'].strftime('%Y-%m-%d'),
                    "sales": float(day['daily_total'] if day['daily_total'] else 0),
                    "items": int(day['items_sold'] if day['items_sold'] else 0)
                })
        
        # If we have no historical data, return empty forecast
        if len(historical_data) == 0:
            return {
                "historical_data": [],
                "forecast_data": [],
                "product_forecasts": [],
                "metrics": {
                    "predicted_sales_total": 0,
                    "sales_growth_rate": 0,
                    "predicted_orders": 0,
                    "orders_growth_rate": 0,
                    "top_category": "",
                    "top_category_items": 0
                }
            }
        
        # Simple forecasting based on moving average and trend analysis
        forecast_data = []
        
        # If we have enough historical data
        if len(historical_data) >= 7:
            # Calculate average daily sales
            daily_amounts = [day['sales'] for day in historical_data[-7:]]  # Last 7 days
            avg_daily_sales = sum(daily_amounts) / len(daily_amounts)
            
            # Calculate trend (average day-to-day change)
            daily_changes = []
            for i in range(1, len(daily_amounts)):
                daily_changes.append(daily_amounts[i] - daily_amounts[i-1])
            
            trend = sum(daily_changes) / len(daily_changes) if daily_changes else 0
            
            # Forecast next N days
            for i in range(1, days_ahead + 1):
                forecast_date = end_date + timedelta(days=i)
                
                # Apply seasonality (weekday effect - weekend sales are higher)
                weekday_factor = 1.15 if forecast_date.weekday() >= 5 else 1.0
                
                # Predicted sales with trend and seasonality
                predicted_sales = (avg_daily_sales + (trend * i)) * weekday_factor
                
                # Ensure prediction is not negative
                predicted_sales = max(0, predicted_sales)
                
                forecast_data.append({
                    "date": forecast_date.strftime('%Y-%m-%d'),
                    "sales": round(predicted_sales, 2),
                    "items": round(predicted_sales / 100, 0)  # Estimated items based on average item price
                })
        else:
            # Not enough data, use simple average
            avg_daily_sales = sum(day['sales'] for day in historical_data) / len(historical_data) if historical_data else 0
            
            for i in range(1, days_ahead + 1):
                forecast_date = end_date + timedelta(days=i)
                forecast_data.append({
                    "date": forecast_date.strftime('%Y-%m-%d'),
                    "sales": round(avg_daily_sales, 2),
                    "items": round(avg_daily_sales / 100, 0)
                })
        
        # Generate product-level forecasts
        product_forecasts = []
        for product in product_sales:
            # Only forecast products with enough sales data
            if product['total_quantity'] > 0:
                # Calculate daily average
                daily_avg = product['total_sales'] / 30  # Simplified - assumes all days
                
                # Calculate average sales when there are sales
                sales_day_avg = product['total_sales'] / product['days_with_sales'] if product['days_with_sales'] > 0 else 0
                
                # Probability of sales on any given day
                sale_probability = product['days_with_sales'] / 30
                
                # Estimated growth rate (simplified model)
                growth_rate = ((daily_avg * 7) / (daily_avg * 5)) - 1 if daily_avg > 0 else 0
                
                # Forecasted sales (7 day outlook)
                forecast_sales = daily_avg * 7 * (1 + growth_rate) if daily_avg > 0 else 0
                
                # Confidence level (based on consistency of sales)
                confidence = min(95, (product['days_with_sales'] / 30) * 100)
                
                product_forecasts.append({
                    "id": product['product_id'],
                    "name": product['product_name'],
                    "image": f"/uploads/products/{product['image_url']}" if product['image_url'] else None,
                    "current_sales": float(product['total_sales']),
                    "predicted_sales": round(forecast_sales, 2),
                    "growth_rate": round(growth_rate * 100, 1),
                    "confidence": round(confidence, 0)
                })
        
        # Sort by predicted sales (highest first)
        product_forecasts.sort(key=lambda x: x['predicted_sales'], reverse=True)
        
        # Calculate overall metrics
        current_total = sum(p['current_sales'] for p in product_forecasts)
        predicted_total = sum(p['predicted_sales'] for p in product_forecasts)
        growth_rate = ((predicted_total / current_total) - 1) * 100 if current_total > 0 else 0
        
        # Top category (simplified - using product name as category)
        top_category = product_forecasts[0]['name'].split()[0] if product_forecasts else "Coffee"
        
        metrics = {
            "predicted_sales_total": round(predicted_total, 2),
            "sales_growth_rate": round(growth_rate, 1),
            "predicted_orders": len(historical_data) * 7,  # Simplified estimate
            "orders_growth_rate": 5.0,  # Placeholder
            "top_category": top_category,
            "top_category_items": len([p for p in product_forecasts if top_category in p['name']])
        }
        
        return {
            "historical_data": historical_data,
            "forecast_data": forecast_data,
            "product_forecasts": product_forecasts,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error generating sales forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@SalesRouter.get("/forecasting/historical-sales", response_model=List[dict])
async def get_historical_sales_for_forecasting(days: int = Query(30, ge=7, le=90), db=Depends(get_db)):
    """
    Get historical sales data specifically for forecasting chart
    Returns daily sales data from the sales table for the specified number of days
    """
    try:
        cursor = db.cursor(dictionary=True)
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Fetching historical sales data for forecasting from {start_date} to {end_date}")
        
        # Modified query to handle all cases - even if database is empty or has no data in the range
        cursor.execute("""
            SELECT 
                DATE(created_at) as sale_date,
                SUM(remitted) as daily_total,
                SUM(quantity_sold) as items_sold
            FROM sales
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY sale_date ASC
        """, (start_date, end_date))
        
        sales_data = cursor.fetchall()
        cursor.close()
        
        # Format the response
        result = []
        for day in sales_data:
            if day['sale_date']:
                result.append({
                    "date": day['sale_date'].strftime('%Y-%m-%d'),
                    "sales": float(day['daily_total'] if day['daily_total'] else 0),
                    "items": int(day['items_sold'] if day['items_sold'] else 0)
                })
        
        # If no data found, return at least one data point to prevent frontend errors
        if not result:
            today = datetime.now().date()
            result.append({
                "date": today.strftime('%Y-%m-%d'),
                "sales": 0.0,
                "items": 0
            })
            
        return result
        
    except Exception as e:
        logger.error(f"Error getting historical sales data for forecasting: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Add new endpoint to update existing sales records with missing product information
@SalesRouter.post("/update-product-details")
async def update_sales_product_details(db=Depends(get_db)):
    """
    Update existing sales records to include product names and details if they're missing.
    This helps fix old sales records that don't have product information.
    """
    try:
        cursor = db.cursor(dictionary=True)
        records_updated = 0
        
        # Find sales records with missing product names
        cursor.execute("""
            SELECT s.id, s.product_id 
            FROM sales s 
            WHERE s.product_name IS NULL OR s.product_name = ''
        """)
        
        sales_to_update = cursor.fetchall()
        
        if not sales_to_update:
            return {"message": "No sales records need updating", "updated": 0}
            
        # Update each record with missing product information
        for sale in sales_to_update:
            # Get product information
            cursor.execute("""
                SELECT ProductName, UnitPrice, Image 
                FROM inventoryproduct 
                WHERE id = %s
            """, (sale["product_id"],))
            
            product = cursor.fetchone()
            
            if product:
                # Update the sales record with product details
                cursor.execute("""
                    UPDATE sales 
                    SET 
                        product_name = %s,
                        unit_price = %s,
                        Image = %s
                    WHERE id = %s
                """, (
                    product["ProductName"],
                    product["UnitPrice"],
                    product["Image"],
                    sale["id"]
                ))
                records_updated += 1
        
        db.commit()
        cursor.close()
        
        return {
            "message": "Sales records updated successfully",
            "updated": records_updated
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating sales product details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
