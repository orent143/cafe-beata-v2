# Cafe Beata Dual System Architecture

This workspace contains two integrated systems:

1. **Cafe Beata Main** - A cafe pre-ordering system (Port 8000)
2. **Inventory Cafe System** - A dedicated inventory management system (Port 8001)

## Quick Start

The easiest way to start both systems is to use the provided batch file:

```bash
start-systems.bat
```

This will:
1. Install any required dependencies
2. Start the Cafe Beata backend on port 8000
3. Start the Inventory System backend on port 8001
4. Run a test webhook to verify the integration is working

## System Architecture

The two systems are designed to work together while remaining modular:

```
┌───────────────────┐                  ┌─────────────────────────┐
│   Cafe Beata      │                  │   Inventory System      │
│   (Port 8000)     │◄────Webhooks────►│   (Port 8001)          │
└───────────────────┘                  └─────────────────────────┘
        │                                        │
        │                                        │
        ▼                                        ▼
┌───────────────────┐                  ┌─────────────────────────┐
│                   │                  │                         │
│  cafe_beata DB    │◄───Shared DB─────│ Same cafe_beata DB     │
│                   │                  │                         │
└───────────────────┘                  └─────────────────────────┘
```

### Integration Features

1. **Ready-Made Products**: Products created in the Inventory System with ProcessType = "Ready-Made" are automatically synced to Cafe Beata's menu
2. **Stock Level Updates**: Changes to stock levels in the Inventory System are reflected in Cafe Beata
3. **Webhook Communication**: Real-time updates through webhook notifications

## Project Structure

### Cafe Beata Main
- `cafe-beata-main/` - Main application directory
  - `backend/` - Backend API (FastAPI, Port 8000)
  - `inventory-webhooks/` - Integration code for the Inventory System
  - `src/` - Frontend code (Vue.js)

### Inventory Cafe System
- `Inventory cafe system/` - Inventory management application
  - `backend-main/` - Backend API (FastAPI, Port 8001)
  - `BeataIMS-main/` - Frontend code (Vue.js)

## Database Setup

Both systems connect to the same MySQL database named `cafe_beata`. The default connection settings are:

```
Host: localhost
User: root
Password: (blank)
Database: cafe_beata
```

The Inventory System will automatically create any required tables when it starts up.

## Testing the Integration

To test if the webhook integration is working:

```bash
python cafe-beata-main/inventory-webhooks/test_webhook.py --type stock --product-id 1
```

For testing a full product update:

```bash
python cafe-beata-main/inventory-webhooks/test_webhook.py --type product --product-id 1
```

## Running the Systems Separately

### Cafe Beata

```bash
cd cafe-beata-main/backend
python -m uvicorn main:app --reload --port 8000
```

### Inventory System

```bash
cd "Inventory cafe system/backend-main"
python -m uvicorn main:app --reload --port 8001
```

## Troubleshooting

If you encounter issues with the integration:

1. **Database Connection**: Ensure MySQL is running and the `cafe_beata` database exists
2. **Port Conflicts**: Make sure ports 8000 and 8001 are available
3. **Webhook Communication**: If webhooks aren't working, check that both systems are running
4. **Missing Dependencies**: Run `pip install requests fastapi uvicorn python-multipart mysql-connector-python`

## Documentation

For more detailed information, see:
- `cafe-beata-main/DUAL_SYSTEM_README.md` - Detailed documentation on the dual system setup
- `cafe-beata-main/inventory-webhooks/README.md` - Documentation on the webhook integration 