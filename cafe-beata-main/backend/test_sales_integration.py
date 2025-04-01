import requests
import json
import time
import mysql.connector

def get_db_connection():
    """Connect to the database used by both systems"""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Warweapons19",
        database="cafe_beata"
    )
    return connection

def test_sales_record_update():
    """
    Test the sales record update functionality when an order is marked as completed.
    
    This test:
    1. Creates a test order
    2. Marks the order as completed
    3. Checks if the sales records were updated in the database
    """
    print("\n=== Testing Sales Record Update ===\n")
    
    # Step 1: Create a test order
    print("Creating a test order...")
    
    order_data = {
        "customer_name": "Test Customer",
        "status": "pending",
        "items": [
            {
                "name": "Cappuccino", # Make sure this item exists in your database
                "quantity": 2,
                "price": 85.0,
                "image": "/images/cappuccino.jpg"
            }
        ]
    }
    
    try:
        # Create the order
        create_response = requests.post(
            "http://127.0.0.1:8000/orders",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if create_response.status_code != 200:
            print(f"Failed to create order: {create_response.text}")
            return
        
        order_id = create_response.json().get("order_id")
        print(f"Created order with ID: {order_id}")
        
        # Step 2: Mark the order as completed
        print(f"Marking order {order_id} as completed...")
        
        complete_response = requests.put(
            f"http://127.0.0.1:8000/orders/{order_id}",
            json={"status": "completed"},
            headers={"Content-Type": "application/json"}
        )
        
        if complete_response.status_code != 200:
            print(f"Failed to mark order as completed: {complete_response.text}")
            return
        
        print(f"Order {order_id} marked as completed!")
        
        # Give some time for the database to update
        print("Waiting for database updates to complete...")
        time.sleep(2)
        
        # Step 3: Check the sales records in the database
        print("Checking sales records...")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Find the product_id for our item
        cursor.execute("SELECT id, external_source, external_id FROM itemso WHERE name = %s", ("Cappuccino",))
        item_result = cursor.fetchone()
        
        if not item_result:
            print("Error: Test item 'Cappuccino' not found in database")
            cursor.close()
            conn.close()
            return
        
        external_id = item_result.get("external_id")
        
        if not external_id:
            print("Error: Test item 'Cappuccino' does not have an external_id")
            cursor.close()
            conn.close()
            return
        
        # Check for sales record
        cursor.execute("""
            SELECT * FROM sales 
            WHERE product_id = %s AND created_at >= (NOW() - INTERVAL 5 MINUTE)
        """, (external_id,))
        
        sales_records = cursor.fetchall()
        
        if not sales_records:
            print("No recent sales records found for this product")
        else:
            print(f"Found {len(sales_records)} recent sales records:")
            for record in sales_records:
                print(f"  - ID: {record['id']}")
                print(f"    Product ID: {record['product_id']}")
                print(f"    Product Name: {record['product_name'] or 'Not set'}")
                print(f"    Quantity Sold: {record['quantity_sold']}")
                print(f"    Unit Price: {record['unit_price']}")
                print(f"    Remitted: {record['remitted']}")
                print(f"    Created At: {record['created_at']}")
                print()
        
        cursor.close()
        conn.close()
        
        print("Test completed!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_sales_record_update() 