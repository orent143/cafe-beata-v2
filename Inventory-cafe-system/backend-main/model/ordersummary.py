from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from model.db import get_db, db_connection
import logging
from datetime import datetime
import bcrypt
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

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    
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
@OrderSummaryRouter.put("/orders/history/{history_id}/details")
async def edit_order_history_details(
    history_id: int,
    updated_order: OrderHistoryDetail,
    admin_username: str,
    admin_password: str
):
    """
    Edit an existing order history entry and its details. Requires admin credentials (username and password).
    Fetches available products for validation.
    """
    with db_connection() as db:
        cursor = None
        try:
            cursor = db.cursor(dictionary=True)

            # Validate admin credentials
            cursor.execute("""
                SELECT password, role, status 
                FROM users 
                WHERE username = %s AND role = 'admin' AND status = 'Active'
            """, (admin_username,))
            admin_user = cursor.fetchone()

            if not admin_user:
                raise HTTPException(status_code=403, detail="Invalid admin credentials or inactive account")

            # Verify the password
            if not bcrypt.checkpw(admin_password.encode('utf-8'), admin_user['password'].encode('utf-8')):
                raise HTTPException(status_code=403, detail="Invalid admin credentials")

            # Check if the order exists
            cursor.execute("SELECT history_id FROM order_history WHERE history_id = %s", (history_id,))
            existing_order = cursor.fetchone()

            if not existing_order:
                raise HTTPException(status_code=404, detail="Order not found in history")

            # Fetch available products
            cursor.execute("""
                SELECT id, ProductName, Quantity, UnitPrice, ProcessType
                FROM inventoryproduct
            """)
            available_products = cursor.fetchall()
            product_map = {product['id']: product for product in available_products}

            # Validate and update order details
            total_items = 0
            for item in updated_order.items:
                product_id = item["product_id"]
                quantity = item["quantity"]

                if product_id not in product_map:
                    raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found")

                product = product_map[product_id]
                product_name, stock, unit_price, process_type = product["ProductName"], product["Quantity"], product["UnitPrice"], product["ProcessType"]

                if process_type != "To Be Made" and quantity > stock:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for {product_name} (ID {product_id})"
                    )

                total_items += quantity

            # Update the order summary
            cursor.execute("""
                UPDATE order_history
                SET customer_name = %s, total_items = %s, total_amount = %s, 
                    payment_method = %s, created_at = %s
                WHERE history_id = %s
            """, (
                updated_order.customer_name,
                total_items,
                updated_order.total_amount,
                updated_order.payment_method,
                updated_order.created_at,
                history_id,
            ))

            # Delete existing order details
            cursor.execute("DELETE FROM order_history_detail WHERE order_id = %s", (history_id,))

            # Insert updated order details
            for item in updated_order.items:
                product_id = item["product_id"]
                quantity = item["quantity"]
                product = product_map[product_id]
                product_name, unit_price = product["ProductName"], product["UnitPrice"]

                cursor.execute("""
                    INSERT INTO order_history_detail (order_id, product_id, product_name, quantity, product_price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (history_id, product_id, product_name, quantity, unit_price))

            # Log the PUT transaction
            cursor.execute("""
                INSERT INTO order_transaction_logs (history_id, action_type, performed_by, remarks)
                VALUES (%s, %s, %s, %s)
            """, (
                history_id,
                "Updated",
                admin_username,
                f"Updated order with {len(updated_order.items)} items, new total amount: {updated_order.total_amount}"
            ))

            db.commit()

            return {"success": True, "message": "Order history and details updated successfully"}
        except Exception as e:
            logger.error(f"Error updating order history details: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
                
@OrderSummaryRouter.delete("/orders/history/{history_id}/details")
async def delete_order_history_details(
    history_id: int,
    admin_username: str,
    admin_password: str
):
    """
    Delete an existing order history entry and its details. Requires admin credentials (username and password).
    Restores the quantity of used products back to the inventory.
    """
    with db_connection() as db:
        cursor = None
        try:
            cursor = db.cursor(dictionary=True)

            # Validate admin credentials
            cursor.execute("""
                SELECT password, role, status 
                FROM users 
                WHERE username = %s AND role = 'admin' AND status = 'Active'
            """, (admin_username,))
            admin_user = cursor.fetchone()

            if not admin_user:
                raise HTTPException(status_code=403, detail="Invalid admin credentials or inactive account")

            # Verify the password
            if not bcrypt.checkpw(admin_password.encode('utf-8'), admin_user['password'].encode('utf-8')):
                raise HTTPException(status_code=403, detail="Invalid admin credentials")

            # Check if the order exists
            cursor.execute("SELECT history_id FROM order_history WHERE history_id = %s", (history_id,))
            existing_order = cursor.fetchone()

            if not existing_order:
                raise HTTPException(status_code=404, detail="Order not found in history")

            # Fetch the order details to restore product quantities
            cursor.execute("""
                SELECT product_id, quantity 
                FROM order_history_detail 
                WHERE order_id = %s
            """, (history_id,))
            order_details = cursor.fetchall()

            # Restore product quantities
            for detail in order_details:
                product_id = detail["product_id"]
                quantity = detail["quantity"]

                cursor.execute("""
                    UPDATE inventoryproduct
                    SET Quantity = Quantity + %s
                    WHERE id = %s
                """, (quantity, product_id))

            # Delete order details
            cursor.execute("DELETE FROM order_history_detail WHERE order_id = %s", (history_id,))

            # Delete order summary
            cursor.execute("DELETE FROM order_history WHERE history_id = %s", (history_id,))

            # Log the DELETE transaction
            cursor.execute("""
                INSERT INTO order_transaction_logs (history_id, action_type, performed_by, remarks)
                VALUES (%s, %s, %s, %s)
            """, (
                history_id,
                "Deleted",
                admin_username,
                "Deleted order and restored inventory quantities"
            ))

            db.commit()

            return {"success": True, "message": "Order history and details deleted successfully, and product quantities restored"}
        except Exception as e:
            logger.error(f"Error deleting order history details: {str(e)}")
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
                "history_id": history_id,  # <-- Add this line
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
                
@OrderSummaryRouter.get("/orders/history-logs")
async def get_order_transaction_logs():
    with db_connection() as db:
        cursor = None
        try:
            cursor = db.cursor()
            cursor.execute("""
                SELECT log_id, history_id, action_type, performed_by, performed_at, remarks
                FROM order_transaction_logs
                ORDER BY performed_at DESC
            """)
            logs = cursor.fetchall()
            return [
                {
                    "log_id": row[0],
                    "history_id": row[1],
                    "action_type": row[2],
                    "performed_by": row[3],
                    "performed_at": row[4].strftime("%Y-%m-%d %H:%M:%S"),
                    "remarks": row[5]
                }
                for row in logs
            ]
        except Exception as e:
            logger.error(f"Error fetching transaction logs: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
        finally:
            if cursor:
                cursor.close()
