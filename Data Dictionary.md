# Table 2.0 Data Dictionary

## Inventory Management System (IMS)

### PROCESSES

| Process Name | Description | Process # | Input Flows | Output Flows |
|--------------|-------------|-----------|------------|--------------|
| Add/Edit Product | Allows the admin to add or modify product details in the inventory system. | 1.0 | Product Details (Name, Description, Category, Price, Stock Level) | Updated Product Data (to Inventory Database) |
| Update Stocks | Adjusts stock levels based on confirmed actions. | 2.0 | Stock Changes (Quantity, Product ID) | Updated Stock Data (to Stock Database) |
| Add/Edit Stock | Allows the admin to add or modify stock entries. | 3.0 | Stock Details (Product ID, Quantity, Location, Supplier ID, Cost Price) | Confirmed Stock Changes (to Stock Database) |
| Update Categories | Modifies category information for better organization. | 4.0 | Category Changes (Category Name, Description, Image) | Updated Categories Data (to Category Database) |
| Update Suppliers | Updates supplier information, including contact details and product supply. | 5.0 | Supplier Changes (Supplier Name, Contact Info, Products Supplied) | Updated Suppliers Data (to Supplier Database) |
| Add/Edit Categories | Allows the admin to create or modify categories. | 6.0 | Category Details (Name, Image) | Confirmed Category Changes (to Category Database) |
| Show Categories | Displays a list of product categories for review or selection. | 7.0 | Categories Data (from Category Database) | Displayed Category List (to Admin Terminal) |
| Add/Edit Suppliers | Enables the admin to add or edit supplier details. | 8.0 | Supplier Details (Name, Contact Info, Supplied Products) | Confirmed Supplier Changes (to Supplier Database) |
| Show Suppliers | Displays a list of suppliers for review or selection. | 9.0 | Suppliers Data (from Supplier Database) | Displayed Supplier List (to Admin Terminal) |
| Generate Reports | Generates low stock and summary reports for the admin. | 10.0 | Inventory Data, Sales Data | Generated CSV Reports (Low Stock Report, Summary Report) |
| Dashboard Display | Shows inventory metrics and key performance indicators. | 11.0 | Aggregated Database Information | Visual Dashboard (to Admin Terminal) |

### FILES/DATA STORES

| Data Store | Description | Physical Implementation | Primary Attributes |
|------------|-------------|-------------------------|-------------------|
| Inventory Database | Stores product details, including name, category, and stock level. | MySQL table: inventoryproduct | Product ID, Name, Quantity, UnitPrice, CategoryID, ProcessType, Threshold, Image, Status |
| Stock Database | Tracks stock levels and changes for each product. | MySQL table: stock_details | ID, ProductID, batch_number, quantity, expiration_date, cost_price, SupplierID, created_at |
| Category Database | Contains information about product categories. | MySQL table: categories | Category ID, CategoryName, ImagePath | 
| Supplier Database | Maintains supplier information and supplied products. | MySQL table: suppliers | Supplier ID, suppliername, contactinfo, email |
| Reports Data Store | Stores generated reports for administrative review. | File system: CSV files | Report Type (Low Stock, Summary), Generated Date, Content |
| Activity Logs | Records all system activities for auditing. | MySQL table: activity_logs | ID, icon, title, time, status |
| Inventory Transactions | Tracks all inventory movements. | MySQL table: inventory_transactions | ID, ProductID, product_name, transaction_type, quantity, created_at |

### SOURCE/SINK/ENTITIES

| Entity | Description | Physical Implementation | Input Flows | Output Flows |
|--------|-------------|-------------------------|------------|--------------|
| Admin | The system user responsible for managing inventory, categories, suppliers, and generating reports. | Web browser on Admin Terminal | Displayed data (inventory lists, reports, dashboards) | Form submissions and API requests (Add/Edit Products, Stocks, Categories, Suppliers; Generate Reports) |
| Supplier | Provides products for the inventory system. | External entity | N/A | Supplier Details (via Admin) |
| System | The computerized inventory management platform. | FastAPI backend with MySQL database | API requests, Database queries | API responses, Database updates, Generated reports |

## Sales Management System (SMS)

### PROCESSES

| Process Name | Description | Process # | Input Flows | Output Flows |
|--------------|-------------|-----------|------------|--------------|
| Create Order | Captures order details from the customer and processes them. | 1.0 | Order Request (Customer Details, Items, Quantities) | Order Entry (to Order Database) |
| Receive Orders | Records orders in the system and updates status. | 2.0 | Order Creation Data | Order Records (to Order Database) |
| Process Order Status | Updates order status (pending, completed, canceled). | 3.0 | Order Status Change Request | Updated Order Status (to Order Database) |
| Update Sales Inventory | Updates the sales and inventory records based on completed orders. | 4.0 | Order Records (Transaction Details) | Updated Product Data (to Sales Database and Inventory Database) |
| Generate Sales Reports | Produces reports for sales analysis. | 5.0 | Sales Data | Sales Reports in CSV format |
| View Inventory | Displays the current inventory status for the cashier or admin. | 6.0 | Inventory Data (from Inventory Database) | Displayed Inventory List (to Cafe Staff Terminal) |
| Add Menu Item | Enables staff to add new menu items. | 7.0 | Menu Item Details (Name, Category, Price) | New Menu Item (to Menu Database) |
| Filter Orders | Allows filtering orders by status or date. | 8.0 | Filter Criteria | Filtered Orders List (to Cafe Staff Terminal) |
| View Order History | Displays completed orders for analysis. | 9.0 | Historical Order Data | Order History Display (to Cafe Staff Terminal) |

### FILES/DATA STORES

| Data Store | Description | Physical Implementation | Primary Attributes |
|------------|-------------|-------------------------|-------------------|
| Order Database | Logs all orders including status and details. | MySQL tables: order_history, order_history_detail | history_id, customer_name, total_items, total_amount, payment_method, created_at, order_details |
| Sales Database | Stores sales data for reporting and analytics. | MySQL table: sales | id, product_id, product_name, quantity_sold, unit_price, remitted, created_at |
| Menu Database | Maintains details of menu items. | MySQL table (part of inventoryproduct) | ID, Name, Category, Price, Image |
| User Database | Manages user accounts and permissions. | MySQL table: users | id, username, email, password, role, profile_pic, created_at |

### SOURCE/SINK/ENTITIES

| Entity | Description | Physical Implementation | Input Flows | Output Flows |
|--------|-------------|-------------------------|------------|--------------|
| Customer | The individual placing orders through the cashier. | External entity | N/A | Order Request (via Cafe Staff) |
| Cafe Staff | The system user who manages order entries and inventory checks. | Web browser on POS Terminal | Displayed data (inventory, orders, sales) | Form submissions and API requests (Create Orders, Update Status, Generate Reports) |
| Barista | Prepares orders based on confirmed details. | Web browser / Mobile device | Order notifications | Order status updates |
| System | The computerized sales and order management platform. | FastAPI backend with MySQL database | API requests, Database queries | API responses, Database updates, Generated reports |

## DATA FLOWS

| Flow ID | Description | Source | Destination | Data Elements | Physical Implementation |
|---------|-------------|--------|-------------|---------------|------------------------|
| DF1 | Product Management Flow | Admin | Inventory Database | Product ID, Name, Quantity, UnitPrice, CategoryID, ProcessType, Threshold, Image | HTTP POST/PUT/DELETE via FastAPI endpoints |
| DF2 | Stock Management Flow | Admin | Stock Database | Product ID, batch number, quantity, expiration date, cost price, supplier ID | HTTP POST/PUT/DELETE via FastAPI endpoints |
| DF3 | Supplier Management Flow | Admin | Supplier Database | Supplier ID, name, contact info, email | HTTP POST/PUT/DELETE via FastAPI endpoints |
| DF4 | Category Management Flow | Admin | Category Database | Category ID, name, image path | HTTP POST/PUT/DELETE via FastAPI endpoints |
| DF5 | Report Generation Flow | Admin | Reports Data Store | Report type, parameters, generated CSV data | File system write operations |
| DF6 | Dashboard Display Flow | Inventory & Sales Databases | Admin Terminal | Aggregated metrics, KPIs, statistics | SQL aggregation queries, JSON responses |
| DF7 | Order Creation Flow | Cafe Staff | Order Database | Customer name, items, quantities, payment method | HTTP POST via FastAPI endpoints |
| DF8 | Order Processing Flow | Order Database | Inventory Database | Product IDs, quantities | SQL transactions, triggers |
| DF9 | Sales Recording Flow | Order Database | Sales Database | Product sales data, transaction details | SQL transactions, triggers |
| DF10 | Menu Management Flow | Cafe Staff | Menu Database | Menu item details | HTTP POST/PUT/DELETE via FastAPI endpoints |
| DF11 | Sales Analytics Flow | Sales Database | Admin/Cafe Staff Terminal | Sales statistics, forecasts, trends | SQL aggregation queries, JSON responses |
| DF12 | Integration Flow | Barista System | IMS/SMS Databases | Real-time updates | WebSockets, API endpoints |
| DF13 | Authentication Flow | Users Database | All System Processes | User credentials, tokens, permissions | JWT tokens in authorization headers | 