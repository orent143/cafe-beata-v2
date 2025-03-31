"""
Cafe Beata Notification Module for Inventory System

This module is designed to be added to the Inventory cafe system to notify
the cafe-beata system when stock levels change for Ready-Made products.

Installation:
1. Copy this file to your inventory system backend
2. Import the functions in your model/inventoryproduct.py file (already done in this project)
3. Call notify_cafe_beata_stock_change after updating products or adjusting stock
"""

import requests
import logging
from datetime import datetime
import json
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='cafe_beata_notifier.log',
    filemode='a'
)
logger = logging.getLogger("cafe-beata-notifier")

# Define the cafe-beata webhook URL - can be customized via environment variable
CAFE_BEATA_WEBHOOK_URL = os.environ.get(
    "CAFE_BEATA_WEBHOOK_URL", 
    "http://localhost:8000/api/inventory-webhook/stock-update"
)

def is_ready_made_product(product_id, mysql_connection):
    """
    Check if a product is a Ready-Made product
    """
    try:
        cursor = mysql_connection.cursor(dictionary=True)
        cursor.execute("SELECT ProcessType FROM inventoryproduct WHERE id = %s", [product_id])
        product = cursor.fetchone()
        cursor.close()
        
        if not product:
            return False
        
        process_type = product.get('ProcessType', '').lower()
        return process_type in ['ready-made', 'ready made', 'ready_made', 'readymade']
    except Exception as e:
        logger.error(f"Error checking if product {product_id} is Ready-Made: {e}")
        return False

def notify_cafe_beata_stock_change(product_id):
    """
    Notifies the cafe-beata system that a product's stock has changed
    Returns True if successful, False otherwise
    """
    try:
        data = {
            "product_id": product_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Notifying cafe-beata of stock change for product {product_id}")
        
        # Add timeout to prevent hanging if Cafe Beata is down
        response = requests.post(
            CAFE_BEATA_WEBHOOK_URL, 
            json=data, 
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully notified cafe-beata of stock change for product {product_id}")
            return True
        else:
            logger.error(f"Failed to notify cafe-beata: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error notifying cafe-beata: Cafe Beata system might be down")
        return False
    except requests.exceptions.Timeout:
        logger.error(f"Timeout notifying cafe-beata: Request took too long")
        return False
    except Exception as e:
        logger.error(f"Error notifying cafe-beata: {e}")
        return False

def get_product_details(product_id, mysql_connection):
    """
    Get product details from the database
    """
    try:
        cursor = mysql_connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, c.CategoryName 
            FROM inventoryproduct p
            LEFT JOIN category c ON p.CategoryID = c.id
            WHERE p.id = %s
        """, [product_id])
        product = cursor.fetchone()
        cursor.close()
        return product
    except Exception as e:
        logger.error(f"Error getting product details for {product_id}: {e}")
        return None

def send_product_update(product_id, mysql_connection):
    """
    Sends complete product data to Cafe Beata
    More comprehensive than just a stock notification
    """
    try:
        # Get product details
        product = get_product_details(product_id, mysql_connection)
        
        if not product:
            logger.error(f"Cannot find product with ID {product_id}")
            return False
            
        # Prepare data to send
        data = {
            "product_id": product_id,
            "product_data": product,
            "timestamp": datetime.now().isoformat(),
            "update_type": "full_product"
        }
        
        logger.info(f"Sending full product update to cafe-beata for product {product_id}")
        
        # Different endpoint for full product updates
        response = requests.post(
            CAFE_BEATA_WEBHOOK_URL.replace("stock-update", "product-update"), 
            json=data, 
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent product update to cafe-beata for product {product_id}")
            return True
        else:
            logger.error(f"Failed to send product update: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending product update: {e}")
        return False

"""
Example usage in routes/products.py:

from cafe_beata_notifier import notify_cafe_beata_stock_change, is_ready_made_product

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    # [Your existing code to update the product]
    
    # After updating, notify cafe-beata if it's a Ready-Made product
    if is_ready_made_product(product_id, mysql.connection):
        notify_cafe_beata_stock_change(product_id)
    
    return jsonify({"success": True, "message": "Product updated successfully"})

@app.route('/api/stock/adjust', methods=['POST'])
def adjust_stock():
    data = request.get_json()
    product_id = data.get('product_id')
    
    # [Your existing code to adjust stock]
    
    # After adjusting, notify cafe-beata if it's a Ready-Made product
    if is_ready_made_product(product_id, mysql.connection):
        notify_cafe_beata_stock_change(product_id)
    
    return jsonify({"success": True, "message": "Stock adjusted successfully"})
""" 