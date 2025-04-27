# Physical Level 0 Data Flow Diagram (Tabular Form)

## System Components and Data Flows

| Source | Process | Destination | Data Flow Description | Physical Implementation |
|--------|---------|-------------|------------------------|--------------------------|
| Admin | 1.0 Inventory Management | Inventory Database | Product Information (add, update, delete) | Admin uses web interface to manage inventory records stored in MySQL database |
| Admin | 1.0 Inventory Management | Stock Database | Stock Details (add, modify, remove) | Admin inputs stock details via forms; data stored in stock_details table |
| Admin | 2.0 Supplier Management | Supplier Database | Supplier Information (add, update, delete) | Admin maintains supplier information through web forms; data stored in suppliers table |
| Admin | 3.0 Category Management | Category Database | Category Information (create, modify, delete) | Web forms for category management; data stored in categories table with image files in uploads directory |
| Admin | 4.0 Report Generation | Report Files | Report Data (inventory, stock levels) | Admin triggers report generation; system processes data and outputs CSV files |
| Inventory Database | 5.0 Dashboard Display | Admin Terminal | Inventory Statistics (counts, values) | PHP/JavaScript processes retrieve aggregated data from database and display on dashboard UI |
| Cafe Staff | 6.0 Order Creation | Order Database | Order Details (customer, items, quantities) | Staff uses order interface to create orders; data stored in order_history table |
| Order Database | 7.0 Order Processing | Inventory Database | Stock Updates | System automatically updates inventory quantities when orders are completed |
| Order Database | 8.0 Sales Reporting | Sales Database | Sales Transactions | Completed orders trigger updates to sales records in sales table |
| Cafe Staff | 9.0 Menu Management | Menu Database | Menu Item Information | Staff manages menu items through web interface; data stored in menu_items table |
| Sales Database | 10.0 Sales Analytics | Admin/Cafe Staff Terminal | Sales Statistics and Forecasts | Analytics engine processes sales data and generates visualizations and forecasts |
| Barista System | 11.0 External Integration | Inventory/Sales Database | Real-time Updates | API endpoints facilitate data exchange between systems; WebSockets for real-time notifications |

## Physical Implementation Components

### Hardware Components

| Component | Description | Specifications |
|-----------|-------------|----------------|
| Server | Hosts the application and database | Windows/Linux server with sufficient RAM and processing power |
| Admin Terminals | Desktop/laptop computers for administrative tasks | Windows PCs with modern web browsers |
| Cafe Staff Terminals | POS terminals or tablets for order processing | Touchscreen-enabled devices with web access |
| Backup Storage | For data backup and recovery | External storage or cloud backup solution |
| Network Equipment | Facilitates communication between components | Routers, switches, and adequate WiFi coverage |

### Software Components

| Component | Description | Technology Used |
|-----------|-------------|----------------|
| Backend Server | Processes application logic | FastAPI (Python) with Uvicorn ASGI server |
| Database Management System | Stores and manages data | MySQL with transaction support |
| Web Interface | User interaction with the system | Vue.js with responsive design |
| API Layer | Facilitates data exchange | RESTful API with JSON data format |
| Real-time Communication | Provides instant updates | WebSocket implementation |
| Report Generation | Creates downloadable reports | CSV generation libraries |
| Authentication System | Secures access to the system | JWT-based authentication with role-based access control |

### Database Tables

| Table | Description | Primary Fields |
|-------|-------------|----------------|
| inventoryproduct | Stores product information | id, ProductName, Quantity, UnitPrice, CategoryID, ProcessType, Threshold, Image |
| stock_details | Tracks stock batches | id, ProductID, batch_number, quantity, expiration_date, cost_price, SupplierID |
| suppliers | Stores supplier details | id, suppliername, contactinfo, email |
| categories | Maintains product categories | id, CategoryName, ImagePath |
| order_history | Records order transactions | history_id, customer_name, total_items, total_amount, payment_method, created_at |
| order_history_detail | Stores line items for orders | id, order_id, product_id, product_name, quantity, product_price |
| sales | Tracks sales by product | id, product_id, product_name, quantity_sold, unit_price, remitted, created_at |
| users | Manages system users | id, username, email, password, role, profile_pic, created_at |
| activity_logs | Records system activities | id, icon, title, time, status |
| inventory_transactions | Tracks inventory movements | id, ProductID, product_name, transaction_type, quantity, created_at |

### Data Flows

| Flow ID | Source | Destination | Data Elements | Implementation Method |
|---------|--------|-------------|---------------|------------------------|
| DF1 | Admin | Inventory Management | Product details, stock information | HTTP POST/PUT/DELETE requests to API endpoints |
| DF2 | Inventory Management | Database | Structured product/stock data | SQL INSERT/UPDATE/DELETE operations |
| DF3 | Database | Dashboard Display | Aggregated statistics | SQL SELECT queries with aggregation functions |
| DF4 | Cafe Staff | Order Creation | Order details (customer, items) | Form submission to API endpoints |
| DF5 | Order Processing | Inventory Database | Stock quantity updates | Automated database transactions |
| DF6 | Order Database | Sales Database | Completed order information | Triggered database updates via SQL |
| DF7 | Report Generation | File System | Formatted report data | File system writes in CSV format |
| DF8 | Barista System | SMS/IMS | Integration data | API calls with authentication headers |
| DF9 | Database | User Interface | Response data | JSON responses to AJAX requests |
| DF10 | Authentication System | All Processes | User credentials, permissions | JWT tokens in authorization headers | 