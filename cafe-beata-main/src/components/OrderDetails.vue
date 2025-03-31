<template>
  <div class="order-container">
    <div class="order-card">
      <h1>Order Details</h1>
      
      <div class="order-info">
        <div class="order-header">
          <div class="order-header-item">
            <span class="label">Order ID:</span>
            <span class="value">{{ orderId }}</span>
          </div>
          <div class="order-header-item">
            <span class="label">Customer:</span>
            <span class="value">{{ customerName }}</span>
          </div>
        </div>
        
        <div class="order-items-list">
          <h2>Items</h2>
          <table class="items-table">
            <thead>
              <tr>
                <th>Image</th>
                <th>Item</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in items" :key="index">
                <td class="item-image-cell">
                  <img :src="getImagePath(item)" :alt="item.name" class="item-image"/>
                </td>
                <td>{{ item.name }}</td>
                <td>{{ item.quantity }}</td>
                <td>₱{{ item.price.toFixed(2) }}</td>
                <td>₱{{ (item.price * item.quantity).toFixed(2) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="4" class="total-label">Total</td>
                <td class="total-value">₱{{ calculateTotal() }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <div class="button-container">
        <button @click="goBackToHistory" class="back-button">Back to Order History</button>
        <button @click="orderAgain" class="order-again-button">Order Again</button>
      </div>
      
      <!-- Success Message -->
      <div v-if="showSuccessMessage" class="success-message">
        <p>Items added to cart successfully!</p>
      </div>
    </div>

    <!-- Unavailable Items Modal -->
    <div v-if="showUnavailableModal" class="modal-overlay">
      <div class="unavailable-modal">
        <h2>Some Items Are Unavailable</h2>
        <p>The following items from your order are currently unavailable:</p>
        
        <div class="unavailable-items-list">
          <div v-for="(item, index) in unavailableItems" :key="index" class="unavailable-item">
            <img :src="getImagePath(getItemByName(item))" :alt="item" class="small-item-image"/>
            <span class="item-name">{{ item }}</span>
            <span class="unavailable-badge">UNAVAILABLE</span>
            <button @click="removeFromOrder(item)" class="remove-item-btn">Remove</button>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="closeUnavailableModal" class="cancel-btn">Cancel</button>
          <button @click="proceedWithAvailable" class="proceed-btn">Proceed with Available Items</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrderDetails',
  data() {
    return {
      items: this.parseItems(this.$route.query.items),
      orderId: this.$route.query.orderId,
      customerName: this.$route.query.customerName,
      showSuccessMessage: false,
      unavailableItems: [], // Track unavailable items
      showUnavailableModal: false, // Control modal visibility
      itemsToOrder: [], // Items to add to cart after filtering
      itemMap: {}, // Store item details keyed by name
      stockMap: {}, // Store stock details keyed by item ID
      menuItems: [] // Store the complete menu items for lookup
    };
  },
  methods: {
    parseItems(items) {
      try {
        return JSON.parse(items) || [];
      } catch (error) {
        console.error("Error parsing order items:", error);
        return [];
      }
    },
    
    goBackToHistory() {
      this.$router.push({ name: "OrderHistory" });
    },

    calculateTotal() {
      if (!Array.isArray(this.items)) return "0";
      return this.items.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);
    },

    getImagePath(item) {
      try {
        // If no item or no image path, return default image
        if (!item || !item.image) {
          return require('@/assets/default.png');
        }

        // If it's already a full URL (including inventory system on localhost:8001)
        if (item.image.startsWith('http://') || item.image.startsWith('https://')) {
          // Check if this is an inventory image that needs to be fixed
          if (item.image.includes('localhost:8001')) {
            // Check if the path needs to be fixed - it should point to /uploads/products/
            if (item.image.includes('/uploads/') && !item.image.includes('/uploads/products/')) {
              // Extract the filename
              const parts = item.image.split('/');
              const filename = parts[parts.length - 1];
              const fixedPath = `http://localhost:8001/uploads/products/${filename}`;
              console.log('Fixed inventory image path:', fixedPath);
              return fixedPath;
            }
          }
          return item.image;
        }
        
        // Handle inventory system images
        if (item.image.includes('localhost:8001')) {
          // Same fix as above if needed
          if (item.image.includes('/uploads/') && !item.image.includes('/uploads/products/')) {
            const parts = item.image.split('/');
            const filename = parts[parts.length - 1];
            return `http://localhost:8001/uploads/products/${filename}`;
          }
          return item.image;
        }

        // If it's a backend upload path
        if (item.image.startsWith('/uploads/')) {
          return `http://localhost:8000${item.image}`;
        }

        // If it's just a filename, try to load from assets
        try {
          return require(`@/assets/${item.image}`);
        } catch (error) {
          console.log('Failed to load image from assets, trying uploads folder');
          // If not found in assets, try backend uploads
          return `http://localhost:8000/uploads/avatars/${item.image}`;
        }
      } catch (error) {
        console.error('Error in getImagePath:', error);
        return require('@/assets/default.png');
      }
    },

    // Get item object by name from the original items array
    getItemByName(name) {
      return this.items.find(item => item.name === name) || {};
    },

    // Remove an item from the unavailable items list and proceed
    removeFromOrder(itemName) {
      // Remove the item from the unavailable items array
      this.unavailableItems = this.unavailableItems.filter(name => name !== itemName);
      
      // Find the corresponding original item to add to the order
      const itemToAdd = this.items.find(item => item.name === itemName);
      
      if (itemToAdd) {
        // Find the menu item to get its ID
        const menuItem = this.findItemInMenu(itemToAdd.name);
        
        if (menuItem) {
          // Get stock information
          const stock = this.stockMap[menuItem.id];
          
          // Only add if there's actually some stock available
          // (user might be removing from the modal but the item is still unavailable)
          if (stock && stock.quantity > 0) {
            // Use the available quantity if it's less than what was ordered
            const quantityToAdd = Math.min(itemToAdd.quantity, stock.quantity);
            
            // Add it to the items to order
            this.itemsToOrder.push({
              id: menuItem.id,
              name: itemToAdd.name,
              price: itemToAdd.price,
              image: itemToAdd.image,
              quantity: quantityToAdd
            });
            
            // If we couldn't add the full quantity, let the user know
            if (quantityToAdd < itemToAdd.quantity) {
              alert(`Only ${quantityToAdd} units of ${itemToAdd.name} are available.`);
            }
          } else {
            // If still no stock, inform the user
            alert(`${itemToAdd.name} is still unavailable.`);
          }
        }
      }
      
      // If all unavailable items have been removed, close the modal and proceed
      if (this.unavailableItems.length === 0) {
        this.showUnavailableModal = false;
        this.addItemsToCart();
      }
    },

    // Close the unavailable items modal without proceeding
    closeUnavailableModal() {
      this.showUnavailableModal = false;
    },

    // Proceed with only available items
    proceedWithAvailable() {
      this.showUnavailableModal = false;
      this.addItemsToCart();
    },

    // Add filtered items to cart and navigate to confirm order
    addItemsToCart() {
      const userName = localStorage.getItem('userName') || 'Guest';
      const userCartKey = `cart_${userName}`;
      
      // Get existing cart from localStorage or initialize empty array
      let cart = JSON.parse(localStorage.getItem(userCartKey) || '[]');
      
      // Add only available items to cart
      let addedItems = 0;
      
      // Process each item to order
      this.itemsToOrder.forEach(item => {
        // Skip if the item is in the unavailable list (it shouldn't be, but double-check)
        if (this.unavailableItems.includes(item.name)) {
          console.log(`Skipping unavailable item: ${item.name}`);
          return;
        }
        
        // Check if item already exists in cart
        const existingItemIndex = cart.findIndex(cartItem => 
          cartItem.name === item.name && 
          cartItem.price === item.price
        );
        
        if (existingItemIndex !== -1) {
          // If item exists, increase quantity
          cart[existingItemIndex].quantity += item.quantity;
          console.log(`Updated quantity for item: ${item.name}`);
        } else {
          // If item doesn't exist, add it to cart
          cart.push(item);
          console.log(`Added new item to cart: ${item.name}`);
        }
        
        addedItems++;
      });
      
      if (addedItems === 0) {
        alert('No items could be added to cart.');
        return;
      }
      
      // Save updated cart to localStorage with user-specific key
      localStorage.setItem(userCartKey, JSON.stringify(cart));
      console.log(`Saved ${addedItems} items to cart`);
      
      // Show success message
      this.showSuccessMessage = true;
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        this.showSuccessMessage = false;
        // Navigate to the ConfirmOrder page
        this.$router.push({ name: 'ConfirmOrder' });
      }, 1500);
    },

    async orderAgain() {
      // First check if the items are available in stock
      try {
        // Fetch stock information from the backend
        const response = await fetch('http://localhost:8000/api/stocks');
        const stocksData = await response.json();
        
        if (!stocksData.success) {
          console.error('Failed to fetch stock information');
          alert('Unable to verify item availability. Please try again later.');
          return;
        }
        
        // Also need to fetch items to get their IDs
        const itemsResponse = await fetch('http://localhost:8000/api/items');
        const itemsData = await itemsResponse.json();
        
        if (!itemsData.items) {
          console.error('Failed to fetch items');
          alert('Unable to verify item availability. Please try again later.');
          return;
        }
        
        // Store the complete menu items for lookup
        this.menuItems = itemsData.items;
        
        // Create lookup maps for easier access
        this.stockMap = stocksData.items.reduce((map, stock) => {
          map[stock.item_id] = stock;
          return map;
        }, {});
        
        // Clear previous data
        this.unavailableItems = [];
        this.itemsToOrder = [];
        
        console.log("Checking availability for items:", this.items);
        console.log("Available menu items:", this.menuItems.map(i => i.name));
        console.log("Stock data:", stocksData.items);
        
        // Check each item's availability and prepare data
        for (const orderItem of this.items) {
          // Case-insensitive lookup
          const menuItem = this.findItemInMenu(orderItem.name);
          
          console.log(`Checking item: ${orderItem.name}, found in menu:`, menuItem);
          
          // If item doesn't exist in the menu anymore
          if (!menuItem) {
            console.log(`Item not found in menu: ${orderItem.name}`);
            this.unavailableItems.push(orderItem.name);
            continue;
          }
          
          // Check if item is disabled in the database (if available property exists)
          if (Object.prototype.hasOwnProperty.call(menuItem, 'available') && menuItem.available === false) {
            console.log(`Item is disabled in menu: ${orderItem.name}`);
            this.unavailableItems.push(orderItem.name);
            continue;
          }
          
          const stock = this.stockMap[menuItem.id];
          console.log(`Stock for ${orderItem.name}:`, stock);
          
          // If item has no stock record or quantity is 0
          if (!stock || stock.quantity === 0) {
            console.log(`Item out of stock: ${orderItem.name}`);
            this.unavailableItems.push(orderItem.name);
            continue;
          }
          
          // Check if stock is sufficient
          if (stock.quantity < orderItem.quantity) {
            console.log(`Not enough stock for ${orderItem.name}: required ${orderItem.quantity}, available ${stock.quantity}`);
            this.unavailableItems.push(orderItem.name);
            continue;
          }
          
          // Item is available, add to items to order
          console.log(`Item available: ${orderItem.name}`);
          this.itemsToOrder.push({
            id: menuItem.id,
            name: orderItem.name,
            price: orderItem.price,
            image: orderItem.image,
            quantity: orderItem.quantity
          });
        }
        
        // Double-check against any matching names that might be unavailable 
        // in case our item lookup missed something
        for (const item of this.items) {
          // Check if this item already marked as unavailable
          if (this.unavailableItems.includes(item.name)) {
            continue;
          }
          
          // Find exact match for Matcha Frappe and other items that might be problematic
          const exactNameMatches = this.menuItems.filter(menuItem => 
            menuItem.name.toLowerCase().trim() === item.name.toLowerCase().trim()
          );
          
          // If matches exist, check if they're all unavailable
          if (exactNameMatches.length > 0) {
            const allUnavailable = exactNameMatches.every(menuItem => {
              const stock = this.stockMap[menuItem.id];
              return !stock || stock.quantity === 0 || 
                    (Object.prototype.hasOwnProperty.call(menuItem, 'available') && menuItem.available === false);
            });
            
            if (allUnavailable) {
              console.log(`Found item exact match as unavailable: ${item.name}`);
              this.unavailableItems.push(item.name);
              // Remove from itemsToOrder if it was added
              this.itemsToOrder = this.itemsToOrder.filter(i => i.name !== item.name);
            }
          }
        }
        
        console.log("Unavailable items:", this.unavailableItems);
        console.log("Items to order:", this.itemsToOrder);
        
        // If there are unavailable items, show the modal
        if (this.unavailableItems.length > 0) {
          // If all items are unavailable
          if (this.unavailableItems.length === this.items.length) {
            alert('All items in this order are currently unavailable.');
            return;
          }
          
          // Show modal with unavailable items
          this.showUnavailableModal = true;
        } else {
          // If all items are available, add them to cart immediately
          this.addItemsToCart();
        }
      } catch (error) {
        console.error('Error checking item availability:', error);
        alert('An error occurred while checking item availability. Please try again later.');
      }
    },
    
    // Helper function to find an item in the menu
    findItemInMenu(itemName, items = null) {
      const menuItems = items || this.menuItems;
      if (!menuItems) return null;
      
      // Normalize the name for comparison (trim whitespace, lowercase)
      const normalizedName = itemName.toLowerCase().trim();
      
      // Case insensitive search
      return menuItems.find(item => 
        item.name.toLowerCase().trim() === normalizedName
      );
    }
  },
};
</script>

<style scoped>
.order-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2f, #3a3a52);
  color: white;
  padding: 20px;
}

.order-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  text-align: center;
  width: 90%;
  max-width: 800px;
  backdrop-filter: blur(10px);
  position: relative;
}

h1 {
  font-size: 28px;
  margin-bottom: 20px;
  color: rgb(216, 144, 178);
}

h2 {
  font-size: 22px;
  margin-bottom: 15px;
  color: rgb(216, 144, 178);
  text-align: left;
}

.order-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.order-header-item {
  margin: 5px 10px;
  text-align: left;
}

.label {
  font-weight: bold;
  color: #aaa;
  margin-right: 5px;
}

.value {
  color: rgb(236, 155, 225);
  font-weight: bold;
}

.order-items-list {
  margin-top: 20px;
  text-align: left;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  margin-bottom: 20px;
}

.items-table th,
.items-table td {
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: left;
  vertical-align: middle;
}

.items-table th {
  background: rgba(216, 144, 178, 0.2);
  color: rgb(236, 155, 225);
}

.item-image-cell {
  width: 80px;
  text-align: center;
}

.item-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.total-label {
  text-align: right;
  font-weight: bold;
  color: #fff;
}

.total-value {
  font-weight: bold;
  color: #ff9800;
}

.button-container {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.back-button, .order-again-button {
  padding: 12px 25px;
  font-size: 14px;
  font-weight: bold;
  background: transparent;
  color: #fff;
  border: 2px solid rgb(235, 172, 216);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  transition: 0.3s;
  width: 48%;
}

.back-button::before, .order-again-button::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #ffeb3b, #ff9800, #ffeb3b);
  transition: 0.3s;
  z-index: -1;
}

.back-button:hover::before, .order-again-button:hover::before {
  left: 0;
}

.back-button:hover, .order-again-button:hover {
  background: rgba(255, 235, 59, 0.3);
  border-color: #ff9800;
}

.order-again-button {
  background-color: rgba(216, 144, 178, 0.2);
  border-color: rgb(216, 144, 178);
}

.order-again-button::before {
  background: linear-gradient(90deg, #ff9800, #ff5722, #ff9800);
}

.success-message {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  background-color: rgba(76, 175, 80, 0.8);
  color: white;
  padding: 10px;
  border-radius: 5px;
  margin: 0 auto;
  width: 80%;
  animation: fadeIn 0.5s;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

.unavailable-modal {
  background-color: #2a2a42;
  border-radius: 15px;
  padding: 25px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  text-align: center;
}

.unavailable-modal h2 {
  color: #ff5252;
  text-align: center;
  margin-bottom: 15px;
}

.unavailable-modal p {
  color: #ddd;
  margin-bottom: 20px;
}

.unavailable-items-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.unavailable-item {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.05);
  margin-bottom: 10px;
  border-radius: 8px;
  position: relative;
}

.small-item-image {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  margin-right: 12px;
  object-fit: cover;
}

.item-name {
  flex-grow: 1;
  text-align: left;
  margin-right: 10px;
}

.unavailable-badge {
  background-color: #ff5252;
  color: white;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  margin-right: 10px;
}

.remove-item-btn {
  background-color: transparent;
  border: 1px solid #ff9800;
  color: #ff9800;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.remove-item-btn:hover {
  background-color: #ff9800;
  color: #000;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.cancel-btn, .proceed-btn {
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  width: 48%;
}

.cancel-btn {
  background-color: transparent;
  border: 2px solid #aaa;
  color: #ddd;
}

.cancel-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.proceed-btn {
  background-color: #8e24aa;
  border: none;
  color: white;
}

.proceed-btn:hover {
  background-color: #6a1b9a;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .order-card {
    padding: 20px;
    width: 95%;
  }
  
  .items-table th,
  .items-table td {
    padding: 8px;
    font-size: 14px;
  }
  
  .item-image {
    width: 40px;
    height: 40px;
  }
  
  h1 {
    font-size: 24px;
  }
  
  h2 {
    font-size: 20px;
  }
  
  .button-container {
    flex-direction: column;
  }
  
  .back-button, .order-again-button {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .unavailable-modal {
    width: 95%;
    padding: 15px;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .cancel-btn, .proceed-btn {
    width: 100%;
    margin-bottom: 10px;
  }
}

@media (max-width: 480px) {
  .items-table {
    font-size: 12px;
  }
  
  .items-table th,
  .items-table td {
    padding: 6px;
  }
  
  .item-image {
    width: 30px;
    height: 30px;
  }
}
</style>
