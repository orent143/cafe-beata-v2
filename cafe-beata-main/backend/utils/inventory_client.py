"""
Inventory System Client Utilities
This module provides functions to communicate with the inventory system
"""
import requests
import logging
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger("cafe-beata-backend")

INVENTORY_BASE_URL = "http://localhost:8001/api"
INVENTORY_WS_URL = "ws://localhost:8001/ws/inventory"

# WebSocket connection to inventory system
inventory_ws_connection = None
inventory_ws_reconnect_task = None

async def connect_to_inventory_websocket():
    """
    Connect to the inventory system WebSocket
    Handles reconnection automatically
    """
    global inventory_ws_connection, inventory_ws_reconnect_task
    
    if inventory_ws_reconnect_task is not None:
        # Cancel any existing reconnect task
        inventory_ws_reconnect_task.cancel()
        inventory_ws_reconnect_task = None
    
    try:
        logger.info("Connecting to inventory WebSocket...")
        inventory_ws_connection = await websockets.connect(INVENTORY_WS_URL)
        logger.info("Connected to inventory WebSocket successfully")
        
        # Start a task to handle messages
        asyncio.create_task(handle_inventory_messages())
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to inventory WebSocket: {e}")
        # Schedule reconnection after 5 seconds
        inventory_ws_reconnect_task = asyncio.create_task(schedule_reconnect())
        return False

async def schedule_reconnect():
    """Schedule a reconnection attempt after delay"""
    await asyncio.sleep(5)  # Wait 5 seconds before reconnecting
    await connect_to_inventory_websocket()

async def handle_inventory_messages():
    """Handle incoming messages from inventory WebSocket"""
    global inventory_ws_connection, inventory_ws_reconnect_task
    
    if inventory_ws_connection is None:
        logger.error("WebSocket connection is None, cannot handle messages")
        return
    
    try:
        async for message in inventory_ws_connection:
            try:
                data = json.loads(message)
                logger.info(f"Received message from inventory: {data}")
                
                # If this is a stock update, process it
                if data.get("type") == "stock_update":
                    product_data = data.get("data", {})
                    product_id = product_data.get("product_id")
                    
                    if product_id:
                        # Trigger a sync for this specific product
                        from main import sync_specific_inventory_product
                        asyncio.create_task(sync_specific_inventory_product(product_id))
                        logger.info(f"Triggered sync for product {product_id}")
            except json.JSONDecodeError:
                logger.error(f"Received invalid JSON from inventory: {message}")
            except Exception as process_error:
                logger.error(f"Error processing inventory message: {process_error}")
    
    except ConnectionClosed:
        logger.warning("Inventory WebSocket connection closed")
        inventory_ws_connection = None
        # Schedule reconnection
        inventory_ws_reconnect_task = asyncio.create_task(schedule_reconnect())
    except Exception as e:
        logger.error(f"Error in inventory WebSocket handler: {e}")
        inventory_ws_connection = None
        # Schedule reconnection
        inventory_ws_reconnect_task = asyncio.create_task(schedule_reconnect())

async def notify_cafe_beata_of_stock_change(product_id: int) -> bool:
    """
    Notifies the cafe-beata system that the stock for a product has changed in the inventory system
    This is called from the inventory system when stock changes occur
    """
    try:
        webhook_url = "http://localhost:8000/api/inventory-webhook/stock-update"
        data = {
            "product_id": product_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Make request to cafe-beata webhook
        response = requests.post(webhook_url, json=data, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"Successfully notified cafe-beata of stock change for product {product_id}")
            return True
        else:
            logger.error(f"Failed to notify cafe-beata of stock change: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error notifying cafe-beata of stock change: {e}")
        return False

async def get_inventory_product(product_id: int) -> Optional[Dict[str, Any]]:
    """
    Gets product information from the inventory system
    """
    try:
        # Use the inventoryproduct endpoint instead
        url = f"{INVENTORY_BASE_URL}/inventory/inventoryproduct/{product_id}"
        logger.info(f"Fetching product {product_id} from inventory at: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return {"success": True, "product": response.json()}
        else:
            logger.error(f"Failed to get product from inventory: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting product from inventory: {e}")
        return None

async def get_ready_made_products() -> Optional[Dict[str, Any]]:
    """
    Gets all Ready-Made products from the inventory system
    """
    try:
        # Use the inventoryproducts/filter endpoint instead
        url = f"{INVENTORY_BASE_URL}/inventory/inventoryproducts/filter?process_type=Ready-Made"
        logger.info(f"Fetching Ready-Made products from inventory at: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"Successfully fetched {len(response.json())} Ready-Made products from inventory")
            return {"success": True, "products": response.json()}
        else:
            logger.error(f"Failed to get Ready-Made products from inventory: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting Ready-Made products from inventory: {e}")
        return None 