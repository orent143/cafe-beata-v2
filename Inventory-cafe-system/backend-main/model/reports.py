from fastapi import APIRouter, Depends, HTTPException, Query 
from typing import Dict, List, Optional
from datetime import datetime
from model.db import get_db
import traceback
import logging
import mysql.connector

# Set up logger
logger = logging.getLogger("inventory-system-backend")

ReportRouter = APIRouter(tags=["Reports"])

def determine_status(quantity: int) -> str:
    """Determine stock status based on quantity."""
    if quantity == 0:
        return "Out of Stock"
    elif quantity <= 10:
        return "Low Stock"
    else:
        return "In Stock"

def ensure_report_tables_exist(db_conn):
    """Create report tables if they don't exist"""
    try:
        cursor = db_conn.cursor()
        
        # Create inventory reports table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_reports (
            ReportID INT AUTO_INCREMENT PRIMARY KEY,
            ProductID INT,
            ProductName VARCHAR(255),
            Quantity INT,
            UnitPrice DECIMAL(10, 2),
            CategoryID INT,
            Status VARCHAR(50),
            ReportDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Image VARCHAR(255)
        )
        """)
        
        # Create stock reports table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_reports (
            ReportID INT AUTO_INCREMENT PRIMARY KEY,
            StockID INT,
            StockName VARCHAR(255),
            Quantity INT,
            CostPrice DECIMAL(10, 2),
            SupplierID INT,
            Status VARCHAR(50),
            ReportDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Image VARCHAR(255)
        )
        """)
        
        db_conn.commit()
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Error creating report tables: {str(e)}")
        return False

def generate_inventory_report(db_conn, report_date: Optional[str] = None) -> Dict:
    """Fetch all inventory data for a given report date or latest, with category names."""
    logger.info(f"Generating inventory report for: {report_date}")

    try:
        ensure_report_tables_exist(db_conn)
        cursor = db_conn.cursor()

        # Attempt to fetch from reports table with category name join
        try:
            if report_date:
                cursor.execute("""
                    SELECT 
                        ir.ReportID, ir.ProductID, ir.ProductName, ir.Quantity, ir.UnitPrice, 
                        ir.CategoryID, c.CategoryName, ir.Status, ir.ReportDate, ir.Image
                    FROM inventory_reports ir
                    LEFT JOIN categories c ON ir.CategoryID = c.id
                    WHERE DATE(ir.ReportDate) = %s
                    ORDER BY ir.ReportDate DESC
                """, (report_date,))
            else:
                cursor.execute("""
                    SELECT 
                        ir.ReportID, ir.ProductID, ir.ProductName, ir.Quantity, ir.UnitPrice, 
                        ir.CategoryID, c.CategoryName, ir.Status, ir.ReportDate, ir.Image
                    FROM inventory_reports ir
                    LEFT JOIN categories c ON ir.CategoryID = c.id
                    ORDER BY ir.ReportDate DESC
                """)
            products = cursor.fetchall()
        except mysql.connector.Error as e:
            logger.error(f"Error querying inventory_reports: {str(e)}")
            products = []

        # Fallback to inventoryproduct table if no report data
        if not products:
            try:
                cursor.execute("""
                    SELECT 
                        p.id, p.id, p.ProductName, p.Quantity, p.Price, p.CategoryID, 
                        c.CategoryName,
                        CASE 
                            WHEN p.Quantity = 0 THEN 'Out of Stock'
                            WHEN p.Quantity <= 10 THEN 'Low Stock'
                            ELSE 'In Stock'
                        END as Status, 
                        NOW(), p.ProductImage
                    FROM inventoryproduct p
                    LEFT JOIN categories c ON p.CategoryID = c.id
                    ORDER BY p.id
                """)
                products = cursor.fetchall()
            except mysql.connector.Error as e:
                logger.error(f"Error querying inventoryproduct: {str(e)}")
                products = []

        if not products:
            return {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_items": 0,
                "total_value": 0,
                "items": []
            }

        total_value = 0
        items = []
        for product in products:
            try:
                qty = float(product[3]) if product[3] is not None else 0
                price = float(product[4]) if product[4] is not None else 0
                total_value += qty * price

                item = {
                    "ReportID": product[0] or 0,
                    "ProductID": product[1] or 0,
                    "ProductName": product[2] or "Unknown Product",
                    "Quantity": product[3] or 0,
                    "UnitPrice": float(product[4]) or 0,
                    "CategoryID": product[5] or 0,
                    "CategoryName": product[6] or "Unknown Category",
                    "Status": product[7] or "Unknown",
                    "ReportDate": (product[8].strftime("%Y-%m-%d %H:%M:%S") 
                                   if isinstance(product[8], datetime) 
                                   else str(product[8]) or ""),
                    "Image": f"/uploads/products/{product[9]}" if product[9] else None,
                }
                items.append(item)
            except Exception as e:
                logger.error(f"Error processing product: {str(e)}")

        report_date_str = products[0][8].strftime("%Y-%m-%d %H:%M:%S") if isinstance(products[0][8], datetime) else str(products[0][8])
        return {
            "date": report_date_str,
            "total_items": len(items),
            "total_value": total_value,
            "items": items
        }

    except Exception as e:
        logger.error(f"Error generating inventory report: {traceback.format_exc()}")
        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_items": 0,
            "total_value": 0,
            "items": []
        }


@ReportRouter.get("/inventory_report", response_model=Dict)
async def get_inventory_report(
    date: Optional[str] = Query(None, description="Filter reports by date (YYYY-MM-DD)"),
    db = Depends(get_db)
):
    try:
        return generate_inventory_report(db, date)
    except Exception as e:
        logger.error(f"Error in inventory report: {traceback.format_exc()}")
        # Return empty response rather than error
        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_items": 0,
            "total_value": 0,
            "items": []
        }

@ReportRouter.get("/low_stock_report", response_model=Dict)
async def get_low_stock_report(
    date: Optional[str] = Query(None, description="Filter reports by date (YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """Get a report of all products with low stock or out of stock"""
    try:
        logger.info(f"Generating low stock report")
        
        # Query inventory products directly
        cursor = db.cursor()
        
        try:
            # First check if SupplierID exists in the table
            cursor.execute("SHOW COLUMNS FROM inventoryproduct LIKE 'SupplierID'")
            supplierID_exists = cursor.fetchone() is not None
            
            # Check if ProductImage exists in the table
            cursor.execute("SHOW COLUMNS FROM inventoryproduct LIKE 'ProductImage'")
            productImage_exists = cursor.fetchone() is not None
            
            # Build the query fields based on columns that exist
            if supplierID_exists:
                supplier_field = "SupplierID"
            else:
                supplier_field = "NULL as SupplierID"
                
            if productImage_exists:
                image_field = "ProductImage"
            else:
                image_field = "NULL as ProductImage"
            
            # First try to get items with zero quantity (out of stock)
            cursor.execute(f"""
                SELECT 
                    id, id, ProductName, Quantity, 
                    CASE WHEN UnitPrice IS NULL OR UnitPrice = 0 THEN Price ELSE UnitPrice END as Price,
                    {supplier_field}, 
                    'Out of Stock' as Status,
                    NOW(), {image_field},
                    Threshold
                FROM inventoryproduct
                WHERE Quantity <= 0 AND ProcessType = 'Ready-Made'
                ORDER BY id
            """)
            zero_stock_items = cursor.fetchall()
            
            # Then get items with low stock (based on threshold)
            cursor.execute(f"""
                SELECT 
                    id, id, ProductName, Quantity, 
                    CASE WHEN UnitPrice IS NULL OR UnitPrice = 0 THEN Price ELSE UnitPrice END as Price,
                    {supplier_field}, 
                    'Low Stock' as Status,
                    NOW(), {image_field},
                    Threshold
                FROM inventoryproduct
                WHERE ProcessType = 'Ready-Made' AND Quantity > 0 AND Quantity <= Threshold AND Threshold > 0
                ORDER BY Quantity ASC
            """)
            low_stock_items = cursor.fetchall()
            
            # Combine the results
            all_low_stock_items = zero_stock_items + low_stock_items
            
            # If no items found through threshold, use a default threshold of 10
            if not all_low_stock_items:
                cursor.execute(f"""
                    SELECT 
                        id, id, ProductName, Quantity, 
                        CASE WHEN UnitPrice IS NULL OR UnitPrice = 0 THEN Price ELSE UnitPrice END as Price,
                        {supplier_field},
                        CASE 
                            WHEN Quantity <= 0 THEN 'Out of Stock'
                            WHEN Quantity <= 10 THEN 'Low Stock'
                            ELSE 'In Stock'
                        END as Status,
                        NOW(), {image_field},
                        10 as Threshold
                    FROM inventoryproduct
                    WHERE ProcessType = 'Ready-Made' AND Quantity <= 10
                    ORDER BY 
                        CASE 
                            WHEN Quantity <= 0 THEN 0  
                            ELSE 1
                        END,
                        Quantity ASC
                """)
                all_low_stock_items = cursor.fetchall()
                
        except mysql.connector.Error as e:
            logger.error(f"Error querying inventoryproduct for low stock: {str(e)}")
            all_low_stock_items = []
            
        # If still no data, return empty response
        if not all_low_stock_items:
            return {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_items": 0,
                "total_value": 0,
                "items": []
            }

        # Calculate total value
        total_value = 0
        for item in all_low_stock_items:
            try:
                if item[3] is not None and item[4] is not None:
                    total_value += float(item[3]) * float(item[4])
            except (ValueError, TypeError):
                pass

        # Format items with all necessary fields
        items = []
        for item in all_low_stock_items:
            try:
                threshold = item[9] if len(item) > 9 and item[9] is not None else 10
                
                # Ensure price is a valid number (defaulting to 0 if not)
                unit_price = 0
                try:
                    if item[4] is not None:
                        unit_price = float(item[4])
                except (ValueError, TypeError):
                    pass
                
                formatted_item = {
                    "ProductID": item[0] if item[0] is not None else 0,
                    "StockID": item[1] if item[1] is not None else 0,
                    "ProductName": item[2] if item[2] is not None else "Unknown Product",
                    "StockName": item[2] if item[2] is not None else "Unknown Product",
                    "Quantity": item[3] if item[3] is not None else 0,
                    "UnitPrice": unit_price,
                    "CostPrice": unit_price,
                    "SupplierID": item[5] if item[5] is not None else "N/A",
                    "Status": item[6] if item[6] is not None else "Unknown",
                    "ReportDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Image": f"/uploads/products/{item[8]}" if item[8] else None,
                    "Threshold": threshold
                }
                items.append(formatted_item)
            except Exception as e:
                logger.error(f"Error formatting low stock item: {str(e)}")
                # Log the actual item data for debugging
                logger.error(f"Item data: {str(item)}")

        cursor.close()
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_items": len(items),
            "total_value": total_value,
            "items": items
        }

    except Exception as e:
        logger.error(f"Error in low stock report: {traceback.format_exc()}")
        # Return empty data instead of an error
        return {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_items": 0,
            "total_value": 0,
            "items": []
        }

@ReportRouter.get("/debug_zero_stock", response_model=Dict)
async def get_debug_zero_stock(db = Depends(get_db)):
    """Get detailed diagnostic information about zero quantity items"""
    try:
        cursor = db.cursor(dictionary=True)
        
        # Check if SupplierID exists in the table
        cursor.execute("SHOW COLUMNS FROM inventoryproduct LIKE 'SupplierID'")
        supplierID_exists = cursor.fetchone() is not None
        
        # Check if ProductImage exists in the table
        cursor.execute("SHOW COLUMNS FROM inventoryproduct LIKE 'ProductImage'")
        productImage_exists = cursor.fetchone() is not None
        
        # Build the query based on whether SupplierID exists
        if supplierID_exists:
            supplier_field = "SupplierID"
        else:
            supplier_field = "NULL as SupplierID"
            
        # Build image field based on whether ProductImage exists
        if productImage_exists:
            image_field = "ProductImage"
        else:
            image_field = "NULL as ProductImage"
        
        # Get detailed information about zero quantity items
        cursor.execute(f"""
            SELECT 
                id, ProductName, Quantity, 
                CASE WHEN UnitPrice IS NULL OR UnitPrice = 0 THEN Price ELSE UnitPrice END as UnitPrice, 
                {supplier_field}, 
                CASE 
                    WHEN Quantity <= 0 THEN 'Out of Stock'
                    WHEN Quantity <= Threshold THEN 'Low Stock'
                    ELSE 'In Stock'
                END as Status,
                {image_field}, Threshold
            FROM inventoryproduct
            WHERE ProcessType = 'Ready-Made' AND Quantity <= 0
            ORDER BY id
        """)
        zero_items = cursor.fetchall()
        
        # Get all items for comparison
        cursor.execute("""
            SELECT 
                id, ProductName, Quantity, 
                CASE 
                    WHEN Quantity <= 0 THEN 'Out of Stock'
                    WHEN Quantity <= Threshold THEN 'Low Stock'
                    ELSE 'In Stock'
                END as Status,
                Threshold
            FROM inventoryproduct
            LIMIT 50
        """)
        all_items = cursor.fetchall()
        
        cursor.close()
        
        return {
            "zero_items_count": len(zero_items),
            "zero_items": zero_items,
            "all_items_sample": all_items
        }
    except Exception as e:
        logger.error(f"Error in debug zero stock: {str(e)}")
        return {
            "error": str(e),
            "zero_items_count": 0,
            "zero_items": [],
            "all_items_sample": []
        }
