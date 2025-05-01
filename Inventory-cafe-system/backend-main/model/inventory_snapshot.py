from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from model.db import get_db, db_connection
from datetime import datetime, timedelta
import logging
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inventory_snapshot")

InventorySnapshotRouter = APIRouter(tags=["Inventory Snapshot"])

async def create_daily_inventory_snapshot():
    """
    Background task to create a daily snapshot of inventory quantities.
    Records beginning quantity, additions, and current quantity for each product.
    """
    while True:
        try:
            # Get the current time
            now = datetime.now()
            # Calculate time until midnight
            tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_until_midnight = (tomorrow - now).total_seconds()
            
            # Sleep until midnight
            logger.info(f"Scheduling next inventory snapshot in {seconds_until_midnight} seconds")
            await asyncio.sleep(seconds_until_midnight)
            
            # It's now midnight, create the inventory snapshot
            logger.info("Creating daily inventory snapshot")
            
            with db_connection() as db:
                cursor = db.cursor()
                today = datetime.now().date()

                # Calculate beginning quantity (quantity at the start of the day)
                # Additions are calculated as the sum of stock added during the day
                cursor.execute("""
                    INSERT INTO daily_inventory_snapshot 
                    (product_id, product_name, beginning_quantity, current_quantity, additions, snapshot_date, process_type)
                    SELECT 
                        ip.id AS product_id,
                        ip.ProductName AS product_name,
                        COALESCE((
                            SELECT Quantity 
                            FROM stock_details 
                            WHERE ProductID = ip.id 
                            AND DATE(created_at) < %s
                            ORDER BY created_at DESC LIMIT 1
                        ), ip.Quantity) AS beginning_quantity,
                        ip.Quantity AS current_quantity,
                        COALESCE((
                            SELECT SUM(quantity) 
                            FROM stock_details 
                            WHERE ProductID = ip.id 
                            AND DATE(created_at) = %s
                        ), 0) AS additions,
                        %s AS snapshot_date,
                        ip.ProcessType AS process_type
                    FROM inventoryproduct ip
                """, (today, today, today))
                
                records_created = cursor.rowcount
                db.commit()
                cursor.close()
                
                logger.info(f"Created {records_created} inventory snapshot records for {today}")
                
        except Exception as e:
            logger.error(f"Error in create_daily_inventory_snapshot: {str(e)}")
            # If there's an error, wait 15 minutes and try again
            await asyncio.sleep(15 * 60)
            
@InventorySnapshotRouter.get("/snapshot/test")
async def test_snapshot_endpoint():
    """
    Test endpoint to verify that the InventorySnapshotRouter is working.
    """
    return {"message": "Inventory Snapshot Router is working"}