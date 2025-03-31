#!/usr/bin/env python3
"""
Test script for the Inventory System to Cafe Beata webhook integration.
This script can be used to simulate webhook calls without modifying the actual
inventory system code.

Usage:
  python test_webhook.py --type stock --product-id 1
  python test_webhook.py --type product --product-id 1
"""

import requests
import json
import argparse
import sys
from datetime import datetime

def test_stock_update_webhook(product_id):
    """
    Test the stock update webhook by sending a notification to Cafe Beata
    that a product's stock has changed
    """
    # Webhook URL for stock updates
    webhook_url = "http://localhost:8000/api/inventory-webhook/stock-update"
    
    # Prepare the webhook data
    data = {
        "product_id": product_id,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\nSending stock update webhook for product ID {product_id}...")
    print(f"Webhook URL: {webhook_url}")
    print(f"Payload: {json.dumps(data, indent=2)}")
    
    try:
        # Send the webhook notification
        response = requests.post(
            webhook_url, 
            json=data,
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        
        # Print the response
        print("\nResponse:")
        print(f"Status code: {response.status_code}")
        try:
            print(f"Response body: {json.dumps(response.json(), indent=2)}")
        except json.JSONDecodeError:
            print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Success! Webhook notification was received by Cafe Beata.")
            return True
        else:
            print("\n❌ Error: Webhook notification failed.")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the Cafe Beata system.")
        print("Make sure the Cafe Beata backend is running at http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def test_product_update_webhook(product_id):
    """
    Test the full product update webhook by sending complete product 
    information to Cafe Beata
    """
    # Webhook URL for product updates
    webhook_url = "http://localhost:8000/api/inventory-webhook/product-update"
    
    # Generate mock product data
    product_data = {
        "id": product_id,
        "ProductName": f"Test Product {product_id}",
        "ItemCode": f"TP-{product_id}",
        "Description": "This is a test product for webhook testing",
        "Price": 9.99,
        "Quantity": 50,
        "Threshold": 10,
        "InStock": "Yes",
        "ProcessType": "Ready-Made",
        "CategoryID": 1,
        "CategoryName": "Ready Made",
        "ProductImage": "uploads/products/test.jpg"
    }
    
    # Prepare the webhook data
    data = {
        "product_id": product_id,
        "product_data": product_data,
        "timestamp": datetime.now().isoformat(),
        "update_type": "full_product"
    }
    
    print(f"\nSending product update webhook for product ID {product_id}...")
    print(f"Webhook URL: {webhook_url}")
    print(f"Payload: {json.dumps(data, indent=2)}")
    
    try:
        # Send the webhook notification
        response = requests.post(
            webhook_url, 
            json=data,
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        
        # Print the response
        print("\nResponse:")
        print(f"Status code: {response.status_code}")
        try:
            print(f"Response body: {json.dumps(response.json(), indent=2)}")
        except json.JSONDecodeError:
            print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Success! Product update webhook was received by Cafe Beata.")
            return True
        else:
            print("\n❌ Error: Product update webhook failed.")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the Cafe Beata system.")
        print("Make sure the Cafe Beata backend is running at http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the Cafe Beata webhook integration')
    parser.add_argument('--type', choices=['stock', 'product'], default='stock',
                        help='Type of webhook to test (stock or product)')
    parser.add_argument('--product-id', type=int, default=1,
                        help='Product ID to use in the test (default: 1)')
    
    args = parser.parse_args()
    
    print("=================================================================")
    print("      CAFE BEATA WEBHOOK INTEGRATION TEST")
    print("=================================================================")
    print(f"Testing {args.type} webhook with product ID: {args.product_id}")
    
    # Run the appropriate test
    if args.type == 'stock':
        success = test_stock_update_webhook(args.product_id)
    else:  # product
        success = test_product_update_webhook(args.product_id)
    
    print("\n=================================================================")
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed. See error messages above.")
    print("=================================================================")
    
    # Return non-zero exit code if the test failed
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 