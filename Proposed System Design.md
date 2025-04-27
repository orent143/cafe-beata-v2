# Part III. Proposed System Design 

## Information System(s) Identified

Based on the problems identified, the company requires a combination of systems, including a Transaction Processing System (TPS) for real-time transaction management, a Management Information System (MIS) for generating reports, an Inventory Management System (IMS) for inventory control and supplier management, and a Sales Management System (SMS) for managing orders and tracking sales, all working together seamlessly.

## Inventory Management System (IMS)

### Inventory Management

#### Add Inventory Product 
This section in the cafe inventory system is a tool designed to help the Admin manage and add products to the cafe's stock. It allows the Admin to input essential details about each item to ensure proper inventory control and easy access to information.

The following data are necessary:
- Product Name
- Product Quantity
- Unit Price
- Category ID

#### Create Inventory Product
This section in the cafe inventory system is a tool designed to help the Admin manage and add coffee and other beverages to the cafe's stock. It allows the Admin to input essential details about each drink to ensure proper inventory control and easy access to information.
 
The following data are necessary:
- Product Name
- Product Quantity
- Unit Price
- Category
- Stock ID

#### Edit Inventory Product
It allows the Admin to update any information related to an existing product. This is useful for correcting errors, adjusting quantities, changing supplier details, or updating prices.

The following data are necessary:
- Product Name
- Product Quantity
- Unit Price
- Category ID

#### Delete Inventory Product
Allows you to remove a product from the inventory list entirely. This is useful when a product is no longer needed, discontinued, or incorrectly added.

#### Add Reports
Another feature is the Inventory summary report. This report helps the Admin monitor the total value of the stock, track how much inventory is on hand, and assess inventory performance in different categories. The system generates a detailed summary of all inventory Products with key information for each item, including stock levels, cost prices, and supplier details.

The following data are necessary:
- Product Name
- Product Quantity
- Unit Price
- Category ID
- Item Status

#### Add Inventory Stock 
This section in the cafe inventory system is a tool designed to help the Admin manage and add stocks to the cafe's stock. It allows the Admin to input essential details about each item to ensure proper inventory control and easy access to information.

The following data are necessary:
- Stock Name
- Stock Quantity
- Cost Price
- Category ID
- Supplier ID

#### Edit Inventory Stock
It allows the Admin to update any information related to an existing stock. This is useful for correcting errors, adjusting quantities, changing supplier details, or updating prices.

The following data are necessary:
- Stock Name
- Stock Quantity
- Cost Price
- Category ID
- Supplier ID

#### Delete Inventory Stock
Allows you to remove a stock from the inventory list entirely. This is useful when a stock is no longer needed, discontinued, or incorrectly added.

#### Add Reports
One of the features is Low stock reports; it helps track inventory products that are near or below the predefined reorder level. The Admin will select products with quantities that are below their reorder level by clicking the box and compiling a list of these items into the Low Stock Report.

The following data are necessary:
- Stock Name
- Stock Quantity
- Cost Price
- Category ID
- Supplier ID
- Item Status

### Suppliers Management

#### Add Suppliers
The Admin can input the details of new suppliers into the system. This allows the business to track multiple suppliers for each item, manage contact information, and record terms and conditions related to deliveries or pricing.

The following data are necessary:
- Supplier Name
- Supplier Contact Information (phone, email, address)
- Items Supplied (linked to inventory items)

#### Edit Suppliers
The Admin can update the details of an existing supplier, whether it's updating contact information, adding new items supplied, or modifying terms of supply. This ensures that the most accurate and up-to-date information is always available for decision-making.

The following data are necessary:
- Supplier Name
- Supplier Contact Information (phone, email, address)
- Items Supplied (linked to inventory items)

#### Delete Supplier
If a supplier is no longer providing services or if there is a change in suppliers, the Admin can remove them from the system. This is especially useful for suppliers that have been discontinued or have unreliable delivery schedules.

### Categories Management

#### Add Category
The Admin can create new categories to group inventory items based on type, usage, or other business criteria. This helps in organizing the inventory in a way that allows for easy tracking and reporting. Categories are linked to inventory items, ensuring that each item is placed under the appropriate group.

The following data are necessary:
- Category Name (e.g., "Beverages", "Pastries", "Snacks")
- Category Image  

#### Edit Category
The Admin can modify an existing category, such as changing the name, updating the description, or reclassifying items within the category. This ensures that the categories remain aligned with the evolving needs of the business.

The following data are necessary:
- Category Name (e.g., "Beverages", "Pastries", "Snacks")
- Category Image 
- Linked Inventory Items (to identify any items that will need to be reassigned) 

#### View Category
The system should allow the Admin to view all existing categories, their descriptions, and the inventory items assigned to each category. This view can be used for management, reporting, and analysis, helping the business identify trends, best-sellers, or understocked categories.

The following data are necessary:
- Category Name (e.g., "Beverages", "Pastries", "Snacks")
- Category Image 
- Linked Inventory Items (List of Items under the category) 
- Number of Items in the Category

#### Delete Category
The Admin can modify an existing category, such as changing the name, updating the description, or reclassifying items within the category. This ensures that the categories remain aligned with the evolving needs of the business.

The following data are necessary:
- Category Name (e.g., "Beverages", "Pastries", "Snacks")
- Category Image 
- Linked Inventory Items (to identify any items that will need to be reassigned)

### Reports Management

#### Generate Low Stock
The Low Stock Report helps track inventory items that are near or below their predefined reorder level. Based on the Low Stock Report, the Admin can initiate restocking orders, contact suppliers, or review sales trends to adjust reorder levels for future cycles.

By clicking Generate Reports the system would give you the summary reports of low stocks in the inventory and generate it into a CSV file for forecasting.

The following data are necessary:
- Stock Name
- Stock Quantity
- Cost Price
- Category ID
- Supplier ID
- Stock Status

#### Generate Inventory Summary Report
The Inventory Summary Report helps the Admin understand overall inventory value, allowing for better financial planning and stock management. The system automatically compiles a summary of all inventory stocks, their stock levels, cost prices, and other key information. 

By clicking Generate Reports the system would give you the summary reports of overall stocks inside the inventory and generate it into a CSV file for forecasting.

The following data are necessary:
- Product Name
- Quantity
- Unit Price
- Category ID
- Stock Status

### Dashboard Management

#### Total Inventory Value
Displays the total value of the current inventory based on the quantity of stock and their cost price.

The following data are necessary:
- Stock Name
- Stock Quantity (Current stock of each item)
- Cost Price (Cost price per unit)
- Total Inventory Value 

#### Total Sales
Displays the total value of the current sales from the integrated Barista system.

The following data are necessary:
- Product Name
- Product Quantity
- Unit Price
- Sold Items
- Sales
- Items Left

#### Low Stocks
Displays a list of inventory items that are near or below their predefined reorder level.

The following data are necessary:
- Stock Name
- Stock Quantity
- Cost Price
- Category ID
- Supplier ID
- Stock Status

#### Total Quantity
The system displays the current total Quantity value of the stocks within the inventory.

The following data are necessary:
- Stock Name
- Stock Quantity

## Sales Management System (SMS)

### Create Order Management

#### Create Orders
The Create Order allows the user to create new orders within the system. This allows the Cashier to select the menu items for the particular order and provide customer details.

The following data are necessary:
- Customer Name
- Table Number
- Item ID
- Total Quantity
- Total Amount

### Orders Management

#### Receiving of Orders
The system should be able to record the orders from the Create Orders. It should be able to show all orders in the system that is created and show the order status and also update the status once order is created.

The following data are necessary:
- Order ID
- Order Details
- Date of Order
- Total Amount

#### Filter Orders by Status
The Filter Orders by Status and Date functionality allows users to easily filter and view orders based on their status (e.g., pending, completed, canceled). This feature simplifies the management of orders and helps businesses track and report sales performance more efficiently.

The following data are necessary:
- Order Status (e.g., Pending, Completed, Canceled)

#### Order History
The Order History feature allows users to view completed orders from the past. It provides a detailed log of all finalized orders and can be used to track customer preferences, review order trends, and analyze sales performance over time.

The following data are necessary:
- Order ID
- Customer Name
- Table Number
- Item Name
- Total Quantity
- Total Amount
- Date of Order
- Order Status (Completed)

#### Add Orders History Report
The Add Orders History functionality allows users to seamlessly integrate newly recorded orders into the system's reports. This ensures that every completed order is captured in real-time, providing a comprehensive overview of sales activity, customer behavior, and inventory status. By adding the most up-to-date order data to reports, businesses can track performance, monitor trends, and respond to changing market demands swiftly.

The following data are necessary:
- Order ID
- Customer Name
- Table Number
- Item Name
- Total Quantity
- Total Amount
- Date of Order
- Order Status (Completed)

### Inventory Management

#### View Inventory
This section in the cafe sales system is a tool designed to help the Cashier view available stocks for the cafe. This tool allows the Cashier to easily access essential information about each item in the inventory.

The following data are necessary:
- Product Name
- Product Quantity
- Unit Price
- Category
- Item Status

#### Add Menu Item
This section in the cafe sales system is a tool designed to help the Cashier add a menu item for the cafe. This tool allows the Cashier to easily access essential information about each item in the inventory.

The following data are necessary:
- Item Name
- Unit Price
- Category

### Sales Management

#### Receiving of Sold Products
The system should be able to record the total sold products based on completed orders. It should update the sold product quantities, remitted cash, and remaining inventory for each product based on the orders that have been marked as completed. This ensures accurate tracking of sales and inventory levels.

The following data are necessary:
- Product Name
- Product Quantity
- Unit Price
- Sold Items
- Sales
- Items Left

#### Add Sales Report
The Add Sales Report feature compiles and presents the detailed data on sold products, providing an overview of sales performance and inventory management. It aggregates information from completed orders, updating the quantities of sold items, remitted cash, and remaining inventory in real-time. This report enables businesses to monitor sales trends, identify popular products, and ensure accurate stock levels.

The following data should be necessary:
- Product Name
- Product Quantity
- Unit Price
- Sold Items
- Sales
- Items Left

### Reports Management

#### Generate Sales Report
The Sales Report aggregates data from completed orders, updating quantities of sold items, sales totals, and inventory levels in real-time. It helps businesses track which products are performing well, adjust stock levels, ensure accurate sales reporting, and generate it into a CSV file for forecasting.

The following data are necessary:
- Product Name
- Product Quantity
- Unit Price
- Sold Items
- Sales
- Items Left

#### Generate Orders History Report
The Orders History Report captures data on completed orders, providing a detailed log of sales activity, customer behavior, and inventory usage. This feature ensures that businesses have a real-time view of how many orders have been placed, the total quantity of items sold, and generate it into a CSV file for forecasting.

The following data are necessary:
- Order ID
- Customer Name
- Table Number
- Item Name
- Total Quantity
- Total Amount
- Date of Order
- Order Status (Completed)

## Use Cases

### Table 1.0: Use Case Glossary (IMS)

| Use-Case Name | Use-Case Description | Participating Actors and Roles |
|---------------|----------------------|--------------------------------|
| **Inventory Management:** | | |
| Add Inventory Product | Admin adds a new product to the inventory system. | Admin |
| Edit Inventory Product | Admin edits details of an existing inventory product. | Admin |
| Delete Inventory Product | Admin removes a product from the inventory list. | Admin |
| Add Inventory Summary Report (for product) | Admin generates a summary report of the entire inventory. | Admin |
| Add Inventory Stock | Admin adds new stock entries to the inventory system. | Admin |
| Edit Inventory Stock | Admin edits an existing stock entry. | Admin |
| Delete Inventory Stock | Admin removes stock from the inventory. | Admin |
| Add Low Stock Report (for Stock) | Admin adds a low stock report for stock items. | Admin |
| **Suppliers Management:** | | |
| Add New Supplier | Admin can add a new supplier into the system, including contact details and items supplied. | Admin |
| Edit Supplier Information | Admin can edit an existing supplier's information, such as contact details or items supplied. | Admin |
| Delete Supplier | Admin can remove a supplier from the system if they are no longer providing services or if there is a change in suppliers. | Admin |
| **Categories Management:** | | |
| View Category | This use case allows the Admin to view an existing category in order to see what is the item inside. | Admin |
| Add Category | This use case allows the Admin to create new categories to group inventory items. | Admin |
| Edit Category | This use case allows the Admin to modify an existing category. Edits may include changing the category name, or updating its image. | Admin |
| Delete Category | This use case allows the Admin to delete an existing category. | Admin |
| **Reports Management:** | | |
| Generate Low Stock Report | Admin generates a report for all inventory products/stocks that are low on stock and generates them into a CSV file. | Admin |
| Generate Inventory Summary Report | Admin generates a report summarizing all stock details and generates them into a CSV file. | Admin |
| **Dashboard Management:** | | |
| Display Total Inventory Value | Admin views the total value of the current inventory. | Admin |
| Display Low Stocks | Admin views a list of stocks below their reorder level. | Admin |

### Table 1.1: Use Case Glossary (SMS)

| Use-Case Name | Use-Case Description | Participating Actors and Roles |
|---------------|----------------------|--------------------------------|
| **Orders Management:** | | |
| Create Orders | The system allows the Cafe Staff to create new orders, select menu items, and input customer details such as name and table number. | Cafe Staff |
| Receiving of Orders | The system records the orders created in the Create Orders feature and tracks order status (pending, completed, etc.). | Cafe Staff |
| Filter Orders by Status | The system enables filtering of orders by their status (e.g., pending, completed, canceled) to help manage and report on orders more effectively. | Cafe Staff |
| Filter Orders by Date | The system allows filtering orders by a specific date or date range for reporting and analysis purposes. | Cafe Staff |
| Order History | The system stores completed orders, providing a detailed log of past transactions for sales analysis, customer behavior, and trend tracking. | Cafe Staff |
| Add Orders to Reports | The system automatically adds newly recorded orders to various reports, ensuring real-time analysis of sales performance and customer behavior. | Cafe Staff |
| **Sales Management:** | | |
| Receiving of Sold Products | The system tracks sold products based on completed orders, updating quantities, remitted cash, and remaining inventory for each product. | Cafe Staff |
| Add Sales Report | The system generates sales reports based on completed orders, aggregating sales data for different time periods (daily, weekly, monthly, yearly) to assess performance. | Admin, Cafe Staff |
| **Inventory Management:** | | |
| View Inventory | The system provides a view of the cafe's current inventory, including item details such as stock name, quantity, cost price, and supplier information. | Cafe Staff |
| Add Menu Item | This section in the cafe sales system is a tool designed to help the Cashier add a menu item for the cafe. | Cafe Staff |
| **Reports Management:** | | |
| Generate Reports | The system allows the Cafe staff to generate all reports into a CSV file. | Cafe Staff |
| Display Total Sales | The system displays the total sales value from the Barista system. | Cafe Staff |
| Display Low Stocks | The system displays a list of items that are below their reorder level. | Barista |
| Display Top Selling Products | The system displays a list of the top-selling products based on quantity sold or revenue generated. | Barista | 