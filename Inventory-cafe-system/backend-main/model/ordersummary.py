from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from model.db import get_db, db_connection
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ordersummary")

OrderSummaryRouter = APIRouter(tags=["OrderSummary"])

# Models
class OrderSummary(BaseModel):
    history_id: int
    customer_name: str
    total_items: int
    total_amount: float
    payment_method: str
    created_at: Optional[str]  # ✅ Updated to use `created_at`

class OrderHistoryDetail(BaseModel):
    history_id: int
    customer_name: str
    total_items: int
    total_amount: float
    payment_method: str
    created_at: Optional[str]  # ✅ Updated to use `created_at`
    items: List[dict]


@OrderSummaryRouter.get("/orders/history/date", response_model=List[OrderSummary])
async def get_order_history(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    with db_connection() as db:
        cursor = None
        try:
            cursor = db.cursor()
            if start_date or end_date:
                try:
                    # Validate date format
                    if start_date:
                        datetime.strptime(start_date, "%Y-%m-%d")
                    if end_date:
                        datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

                query = """
                    SELECT history_id, customer_name, total_items, 
                           total_amount, payment_method, created_at
                    FROM order_history
                    WHERE 1=1
                """
                params = []

                if start_date:
                    query += " AND DATE(created_at) >= %s"
                    params.append(start_date)
                
                if end_date:
                    query += " AND DATE(created_at) <= %s"
                    params.append(end_date)

                query += " ORDER BY created_at DESC"
                cursor.execute(query, tuple(params))
            else:
                cursor.execute("""
                    SELECT history_id, customer_name, total_items, 
                           total_amount, payment_method, created_at
                    FROM order_history
                    ORDER BY created_at DESC
                """)

            history_orders = cursor.fetchall()

            return [
                {
                    "history_id": row[0],
                    "customer_name": row[1],
                    "total_items": row[2],
                    "total_amount": float(row[3]),
                    "payment_method": row[4],
                    "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None
                }
                for row in history_orders
            ]
        except Exception as e:
            logger.error(f"Error getting order history: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
                
                
# ✅ Get order history summary with `OrderDate`
@OrderSummaryRouter.get("/orders/history", response_model=List[OrderSummary])
async def get_order_history():
    with db_connection() as db:
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("""
                SELECT history_id, customer_name, total_items, 
                       total_amount, payment_method, created_at
                FROM order_history
                ORDER BY created_at DESC
            """)

            history_orders = cursor.fetchall()

            return [
                {
                    "history_id": row[0],
                    "customer_name": row[1],
                    "total_items": row[2],
                    "total_amount": float(row[3]),
                    "payment_method": row[4],
                    "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None
                }
                for row in history_orders
            ]
        except Exception as e:
            logger.error(f"Error getting order history: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()

@OrderSummaryRouter.get("/orders/history/{history_id}", response_model=OrderHistoryDetail)
async def get_order_history_detail(history_id: int):
    with db_connection() as db:
        cursor = None
        try:
            cursor = db.cursor()

            # Fetch order summary
            cursor.execute("""
                SELECT oh.history_id, oh.customer_name, oh.total_items, 
                    oh.total_amount, oh.payment_method, oh.created_at
                FROM order_history oh
                WHERE oh.history_id = %s
            """, (history_id,))

            order = cursor.fetchone()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found in history")

            # Fetch products from `order_history_detail`
            cursor.execute("""
                SELECT od.product_id, od.product_name, od.quantity, od.product_price
                FROM order_history_detail od
                WHERE od.order_id = %s
            """, (history_id,))

            items = [
                {
                    "product_id": row[0],
                    "product_name": row[1],
                    "quantity": row[2],
                    "price": float(row[3])
                }
                for row in cursor.fetchall()
            ]

            return {
                "history_id": order[0],
                "customer_name": order[1],
                "total_items": order[2],
                "total_amount": float(order[3]),
                "payment_method": order[4],
                "created_at": order[5].strftime("%Y-%m-%d %H:%M:%S") if order[5] else None,
                "items": items
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting order history detail: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()