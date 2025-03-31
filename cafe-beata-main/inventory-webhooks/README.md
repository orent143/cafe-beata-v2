# Inventory System Integration with Cafe Beata

This directory contains the code necessary to enable communication between the Cafe Beata ordering system and the Inventory Management System.

## Overview

The integration allows:

1. **Ready-Made Product Synchronization**: Products marked as "Ready-Made" in the Inventory System automatically appear in the Cafe Beata menu.
2. **Stock Level Updates**: Changes in inventory stock levels are reflected in the Cafe Beata system.
3. **Automated Communication**: Both systems communicate through webhooks without manual intervention.

## Files in this Directory

- `cafe_beata_notifier.py` - Core module to integrate into the Inventory System
- `test_webhook.py` - Script to test the webhook integration
- `README.md` - This documentation file

## How the Integration Works

### Architecture

The systems communicate through a webhook architecture:

1. **Inventory System → Cafe Beata**: When stock changes occur in the Inventory System, it sends a notification to the Cafe Beata webhook endpoint.
2. **Cafe Beata Processing**: Cafe Beata receives the webhook, validates it, and updates its database accordingly.

### Data Flow

```
[Inventory System] --- stock change notification ---> [Cafe Beata System]
           ^                                                |
           |                                                |
           +---------------- data sync --------------------+
```

## Installation and Setup

### 1. Inventory System Setup (Already implemented)

The `cafe_beata_notifier.py` module has been integrated into the Inventory System. It uses the following functions:

- `notify_cafe_beata_stock_change(product_id)` - Notifies Cafe Beata of stock changes
- `is_ready_made_product(product_id, connection)` - Checks if a product is classified as "Ready-Made"
- `send_product_update(product_id, connection)` - Sends complete product data to Cafe Beata

### 2. Cafe Beata System Setup (Already implemented)

Cafe Beata has API endpoints to receive and process webhook calls:

- `/api/inventory-webhook/stock-update` - For stock level updates
- `/api/inventory-webhook/product-update` - For complete product information updates

## Testing the Integration

You can use the provided `test_webhook.py` script to test the webhook integration:

```bash
# Test stock update webhook
python test_webhook.py --type stock --product-id 123

# Test product update webhook
python test_webhook.py --type product --product-id 123
```

## Troubleshooting

### Common Issues and Solutions

1. **Webhook Connection Failures**:
   - Ensure both systems are running
   - Check the webhook URL in `cafe_beata_notifier.py` (default is http://localhost:8000/api/inventory-webhook/stock-update)
   - Verify network connectivity between the systems

2. **Products Not Syncing**:
   - Ensure products are marked with ProcessType = "Ready-Made" in the Inventory System
   - Check logs in `cafe_beata_notifier.log` for errors
   - Trigger a manual sync from the Cafe Beata admin dashboard

3. **Error Handling**:
   - Both systems have built-in error handling to prevent crashes
   - Check logs in both systems for detailed error messages

## Customization

### Environment Variables

The webhook integration can be customized using environment variables:

- `CAFE_BEATA_WEBHOOK_URL` - Override the default webhook URL

Example:
```
SET CAFE_BEATA_WEBHOOK_URL=http://custom-domain:8000/api/inventory-webhook/stock-update
```

## Maintenance and Updates

When making changes to either system, consider:

1. Ensuring database compatibility between both systems
2. Testing webhook communication after updates
3. Keeping documentation updated with any changes to the integration architecture 