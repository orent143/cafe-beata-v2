import requests

def test_mark_order_completed():
    """Test marking an order as completed and verify stock update"""
    try:
        # 1. Create an order with item ID 85
        print("Creating a test order...")
        order_data = {
            "customer_name": "Test Customer",
            "items": [
                {
                    "name": "Mineral Water",
                    "quantity": 1,
                    "price": 10.00,
                    "image": None
                }
            ],
            "status": "pending"
        }
        
        create_response = requests.post(
            'http://127.0.0.1:8000/orders',
            json=order_data
        )
        
        if create_response.status_code != 200:
            print(f"Failed to create order: {create_response.status_code} - {create_response.text}")
            return
            
        response_data = create_response.json()
        order_id = response_data.get("order_id")
        print(f"Order created with ID: {order_id}")
        
        # 2. Mark the order as completed
        print("Marking order as completed...")
        update_response = requests.put(
            f'http://127.0.0.1:8000/orders/{order_id}',
            json={"status": "completed"}
        )
        
        print(f"Status code: {update_response.status_code}")
        print(f"Response: {update_response.text}")
        
        # 3. Check inventory system stock
        print("Checking inventory system stock...")
        inventory_response = requests.get('http://127.0.0.1:8001/api/inventory/inventoryproduct/85')
        print(f"Inventory status: {inventory_response.status_code}")
        print(f"Inventory data: {inventory_response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mark_order_completed() 