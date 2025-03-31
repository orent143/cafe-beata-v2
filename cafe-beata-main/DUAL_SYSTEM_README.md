# Dual System Setup: Cafe Beata and Inventory Management

This workspace contains two separate but related systems:

1. **Cafe Beata** - A cafe pre-ordering system (Port 8000)
2. **Inventory Cafe System** - A dedicated inventory management system (Port 8001)

## Running Both Systems

To avoid port conflicts, the systems have been configured to run on different ports:

- Cafe Beata backend: Port 8000
- Inventory System backend: Port 8001

### Using Batch Files

For convenience, several batch files have been provided:

- `start-cafe-beata.bat` - Runs only the Cafe Beata backend
- `start-inventory-system.bat` - Runs only the Inventory System backend
- `start-both-systems.bat` - Runs both backends in separate command windows
- `update-all-urls.bat` - Updates all API URLs in the Inventory System frontend
- `start-complete-system.bat` - Runs both backends AND the Inventory frontend

For a complete system startup, we recommend using `start-complete-system.bat` as it handles everything in one go.

### Manual Start

If you prefer to start the systems manually:

#### For Cafe Beata:
```
cd backend
python -m uvicorn main:app --reload --port 8000
```

#### For Inventory Cafe System:
```
cd "../Inventory cafe system/backend-main"
python -m uvicorn main:app --reload --port 8001
```

## Frontend Access

After starting the backends, you can access the frontends as follows:

- Cafe Beata: [http://localhost:8080](http://localhost:8080)
- Inventory System: [http://localhost:5173](http://localhost:5173) (requires running the Vue dev server)

To start the Inventory System frontend:
```
cd "../Inventory cafe system/BeataIMS-main/IMS"
npm run dev
```

## API Endpoints

- Cafe Beata API: [http://localhost:8000](http://localhost:8000)
- Inventory System API: [http://localhost:8001](http://localhost:8001)

## Notes on Integration

Both systems are designed to interact with the same database (`cafe_beata`), with each system managing different aspects:

- Cafe Beata handles customer interactions, orders, and customer profiles
- Inventory System manages product stock, suppliers, and inventory reports

When making changes to shared resources (like database structures), consider the impact on both systems.

## Ready-Made Products Integration

A new feature has been added to automatically synchronize "Ready-Made" products from the Inventory System to the Cafe Beata menu. This integration allows you to:

1. Create products in the Inventory System with ProcessType = "Ready-Made"
2. Have these products automatically appear in the Cafe Beata menu under the "Ready Made" category

### Using the Integration

1. **Create a "Ready-Made" product in the Inventory System**:
   - Go to the Inventory System ([http://localhost:5173](http://localhost:5173))
   - Navigate to Inventory → Create Product
   - Fill in the product details and select "Ready-Made" for the Process Type
   - Save the product

2. **Sync the products to Cafe Beata**:
   - **Automatic sync**: The system will automatically sync every 5 minutes
   - **Manual sync**: In the Cafe Beata Dashboard, admins can click the "Sync from Inventory" button in the Ready Made Products section

3. **View the synchronized products**:
   - In Cafe Beata, navigate to the Dashboard
   - Look under the "Ready Made Products" section and click on "All Ready Made"
   - Your inventory products should appear and be available for ordering

### Troubleshooting

If products aren't appearing:
- Ensure both systems are running
- Check that your product is set to "Ready-Made" and has "Available" status
- Try the manual sync option
- Verify that database tables are set up correctly (both systems should share the same database)

## Troubleshooting

### API Connection Issues

If you encounter 404 errors or connection issues when using the Inventory System, it might be because the frontend is still trying to connect to port 8000 instead of 8001. This happens because the Inventory System was originally developed to use port 8000.

To fix this:

1. Run the dedicated URL update script:
   ```
   update-all-urls.bat
   ```

2. Alternatively, when starting the system with one of these batch files:
   ```
   start-inventory-system.bat
   start-both-systems.bat
   start-complete-system.bat
   ```
   
   When prompted "Do you want to update all API URLs to use port 8001?", enter `y` and press Enter.

3. The script will automatically update all the API URLs in the frontend code.

### Specific Common Errors

1. **Profile Image Not Loading**:
   This is a common issue where the profile image URL is hardcoded. Run the update script and ensure the profile.vue file is using `getImageUrl`.

2. **Dashboard Not Loading Data**:
   If the dashboard shows errors fetching data, it's likely using the wrong port. Check HomeIMS.vue and ensure all API URLs use `${API_BASE_URL}`.

### Manual Updates

If you still encounter issues, you might need to manually update some of the API URLs in your code:

1. Import the config in the file:
   ```javascript
   import { API_BASE_URL, getImageUrl } from '@/api/config';
   ```

2. Replace hardcoded URLs:
   ```javascript
   // Before
   const response = await axios.get('http://127.0.0.1:8000/api/users/');
   
   // After
   const response = await axios.get(`${API_BASE_URL}/api/users/`);
   ```

3. For image URLs, use the helper function:
   ```javascript
   // Before
   return `http://127.0.0.1:8000/uploads/profile_pics/${this.user.profile_pic}`;
   
   // After
   return getImageUrl(`/uploads/profile_pics/${this.user.profile_pic}`);
   ```

### Database Conflicts

Since both systems interact with the same database, ensure that your database schema is compatible with both applications. If you made changes to the database for one system, consider the impact on the other system. 