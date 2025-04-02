<template>
  <div>
    <!-- Confirm Modal -->
    <div v-if="showModal" class="custom-modal">
      <div class="modal-content">
        <span class="close" @click="closeModal">&times;</span>
        <h2>📢 Hey, Wait!!</h2>
        <p>Are you sure, that this is all you want to order?</p>
        <div class="modal-buttons">
          <button @click="confirmOrder" class="yes-btn">Yes, I'm sure</button>
          <button @click="stayOnPage" class="no-btn">No, I want to order more</button>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="confirm-order">
      <!-- Processing Order Section (centered) -->
      <div v-show="isProcessingOrder" class="loading-spinner-container">
        <button class="close-processing" @click="cancelProcessing">&times;</button>
        <h1 class="wedding-text">Café Beàta</h1>
        <h1 class="loading-text">Processing your order...</h1>
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: progressBarWidth + '%' }"></div>
        </div>
      </div>

      <!-- Order Closed Message -->
      <div v-if="!isCafeOpen" class="closed-message">
        <p>We apologize for the inconvenience. Café Beàta is currently closed. Our operating hours are Monday to Saturday, from 6:00 AM to 9:30 PM. </p>
      </div>

      <!-- Confirm Order Content -->
      <h1 class="cart-title">Your Cart ({{ cart.length }} items)</h1>

      <div class="cart-container" v-if="cart.length">
        <div class="cart-header">
          <div class="header-item">Item</div>
          <div class="header-price">Price</div>
          <div class="header-quantity">Quantity</div>
          <div class="header-total">Total</div>
          <div class="header-actions"></div>
        </div>
        
        <div class="cart-items">
          <div v-for="(order, index) in cart" :key="index" class="cart-item">
            <div class="item-details">
              <img :src="getImagePath(order)" :alt="order.name" class="item-image"/>
              <div class="item-info">
                <h3 class="item-name">{{ order.name }}</h3>
                <p v-if="order.name === 'Pi Pizza Oven'" class="estimated-ship">
                  (Estimated Ship Date: June 6th)
                </p>
                <p v-if="order.name === 'Pi Pizza Oven'" class="item-source">
                  Final Source: Wood Only
                </p>
                <p v-if="order.name === 'Grill Ultimate Bundle'" class="item-promotion">
                  Add-in special promotion for $49.99
                </p>
                <a v-if="order.name === 'Pi Pizza Oven'" class="change-link" href="#">Change</a>
              </div>
            </div>
            <div class="item-price">₱{{ order.price.toFixed(2) }}</div>
            <div class="item-quantity">
              <div class="quantity-controls">
                <button @click="decreaseQuantity(index)" class="quantity-btn">-</button>
                <span class="quantity-value">{{ order.quantity }}</span>
                <button @click="increaseQuantity(index)" class="quantity-btn">+</button>
              </div>
            </div>
            <div class="item-total">₱{{ (order.price * order.quantity).toFixed(2) }}</div>
            <div class="item-actions">
              <button class="remove-btn" @click="removeFromCart(index)">×</button>
            </div>
          </div>
        </div>

        <div class="cart-summary">
          <div class="subtotal">
            <span>Subtotal:</span>
            <span>₱{{ totalPrice.toFixed(2) }}</span>
          </div>
          <div class="grand-total">
            <span>Grand total:</span>
            <span>₱{{ totalPrice.toFixed(2) }}</span>
          </div>
        </div>

        <div class="cart-actions">
          <button @click="addMoreOrder" class="continue-shopping">Continue Order</button>
          <button @click="openModal" class="checkout-btn" :disabled="cart.length === 0 || isProcessingOrder || !isCafeOpen">
            Check out
          </button>
        </div>
      </div>

      <!-- No items in cart -->
      <div class="empty-cart" v-else>
        <p>No items in cart. Add some from the dashboard.</p>
        <button @click="addMoreOrder" class="continue-shopping">Start Order</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      cart: [], // Store multiple selected items
      userName: localStorage.getItem('userName') || "Guest", // Fetch the logged-in user's name
      isProcessingOrder: false,  // Track the order processing state
      showModal: false, // Track the modal visibility
      countdown: 3, // Countdown timer for the processing
      progressBarWidth: 0, // Progress bar width
      showOrderClosedMessage: false,
      progressInterval: null, // Store the interval reference
      isItemAdded: false, // New flag to track if item has been added
      isCafeOpen: true, // Add this line to define isCafeOpen
      // Map of product names to their image paths
      productImages: {
        // Ice Coffees
        'Ice Peppermint Latte': 'peppermint-latte.png',
        'Ice Matcha Cafe Latte': 'matcha-cafe-latte.png',
        'Ice Cafe Latte': 'ice-cafe-latte.png',
        'Ice Caramel Macchiato': 'caramel-macchiato.png',
        'Ice Angel Affogato': 'angel-affogato.png',
        'Ice Spanish Latte': 'spanish-latte.png',
        'Ice Cappuccino': 'ice-cappuccino.png',
        'Ice Cafe Mocha': 'cafe-mocha.png',
        'Ice Salted Caramel Macchiato': 'salted-caramel-macchiato.png',
        'Ice White Choco Mocha': 'white-choco-mocha.png',
        'Ice Vanilla Latte': 'vanilla-latte.png',
        'Ice Hazelnut Latte': 'hazelnut-latte.png',
        'Ice Cafe Frizzy': 'cafe-frizzy.png',
        'Ice Americano Lemon': 'americano-lemon.png',
        'Ice Cafe Americano': 'ice-cafe-americano.png',
        
        // Hot Coffees
        'Hot Cafe Americano': 'cafe-americano.png',
        'Hot Peppermint Latte': 'hot-peppermint-latte.png',
        'Hot Matcha Cafe Latte': 'hot-matcha-cafe-latte.png',
        'Hot Cafe Latte': 'cafe-latte.png',
        'Hot Cafe Latte Macchiato': 'hot-cafelattemacc.png',
        'Hot Caramel Macchiato': 'hot-caramel-macchiato.png',
        'Hot Spanish Latte': 'hot-spanish-latte.png',
        'Hot Cappuccino': 'hot-cappuccino.png',
        'Hot Cafe Mocha': 'hot-cafe-mocha.png',
        'Hot Salted Caramel Macchiato': 'hot-salted-caramel-macchiato.png',
        'Hot Vanilla Latte': 'hot-vanilla-latte.png',
        'Hot Hazelnut Latte': 'hot-hazelnut-latte.png',
        'Hot Tea Pot': 'hotea-pot.png',
        
        // Juice Drinks
        'Apple Juice': 'apple.png',
        'Carrot Juice': 'carrot.png',
        'Mango Juice': 'mango.png',
        'Orange Juice': 'orange.png',
        'Fresh Lemon Juice': 'fresh-lemon.png',
        'Strawberry Lemonade': 'strawberry-lemonade.png',
        'Yakult Lemonade': 'yakult-lemonade.png',
        'Yakult Honey Lemonade': 'yakult-honey-lemonade.png',
        'Yakult Apple Lemonade': 'yakult-apple-lemonade.png',
        'Yakult Orange Lemonade': 'yakult-orange-lemonade.png',
        'Yakult Sprite Lemonade': 'yakult-sprite-lemonade.png',
        'Yakult Mango Lemonade': 'yakult-mango-lemonade.png',
        'Yakult Caramel Lemonade': 'yakult-caramel-lemonade.png',
        'Yakult Strawberry Lemonade': 'yakult-strawberry-lemonade.png',
        'Strawberry Mango Blue Lemonade': 'strawberry-mango-blue-lemonade.png',
        'Strawberry Orange Blue Lemonade': 'strawberry-orange-blue-lemonade.png',
        'Strawberry Apple Lemonade': 'strawberry-apple-lemonade.png',
        'Apple Carrot Juice': 'apple-carrot.png',
        'Mogu-Mogu Yakult': 'mogu-mogu-yakult.png',
        'Mogu-Mogu Yakult w/ Lemon': 'mogu-mogu-yakult-with-lemon.png',
        'Mogu-Mogu Yakult with Honey': 'mogu-mogu-yakult-with-honey.png',
        'Mango Matcha Latte': 'mango-matcha-latte.png',
        'Mango Strawberry Latte': 'mango-strawberry-latte.png',
        
        // Milkteas
        'Avocado Milktea': 'avocado-milktea.png',
        'Wintermelon Milktea': 'wintermelon-milktea.png',
        'Okinawa Milktea': 'okinawa-milktea.png',
        'Mango Milktea': 'mango-milktea.png',
        'Oreo Milktea': 'oreo-milktea.png',
        'Caramel Milktea': 'caramel-milktea.png',
        'Chocolate Milktea': 'chocolate-milktea.png',
        'Mocha Milktea': 'mocha-milktea.png',
        'Matcha Milktea': 'matcha-milktea.png',
        'Taro Milktea': 'taro-milktea.png',
        'Red Velvet Milktea': 'red-velvet-milktea.png',
        'Ube Milktea': 'ube-milktea.png',
        'Pandan Milktea': 'pandan-milktea.png',
        'Strawberry Milktea': 'strawberry-milktea.png',
        'Melon Milktea': 'melon-milktea.png',
        'Ube Taro Milktea': 'ube-taro-milktea.png',
        
        // Chocolate Drinks
        'Hot Chocolate': 'hot-chocolate.png',
        'Cold Chocolate': 'cold-chocolate.png',
        
        // Blended Frappes
        'Cookies & Cream Frappe': 'cookies-and-cream.png',
        'Ube Frappe': 'ube.png',
        'Mocha Frappe': 'mocha.png',
        'Matcha Frappe': 'matcha.png',
        'Mango Frappe': 'mango-frappe.png',
        'Chocolate Frappe': 'chocolate.png',
        'Strawberry Frappe': 'strawberry.png',
        'Pandan Frappe': 'pandan.png',
        'Avocado Frappe': 'avocado.png',
        'Melon Frappe': 'melon.png',
        'Cookies & Coffee Frappe': 'cookies-and-coffee.png',
        
        // Pasta and Dishes
        'Carbonara': 'carbonara.png',
        'Baked Mac': 'bakemac.png',
        'Tuna Pasta': 'tunapasta.png'
      }
    };
  },
  computed: {
    totalPrice() {
      return this.cart.reduce((total, item) => total + item.price * item.quantity, 0);
    },
  },
  mounted() {
    // Initialize isCafeOpen from localStorage
    const savedCafeStatus = localStorage.getItem('isCafeOpen');
    if (savedCafeStatus !== null) {
      this.isCafeOpen = JSON.parse(savedCafeStatus);
    }
    
    // Load existing cart first
    this.loadCart();
    
    // Check URL parameters and add item only if not already done
    const itemFromUrl = this.$route.query.name && this.$route.query.price;
    if (itemFromUrl && !this.isItemAdded) {
      this.handleNewItem();
    }
    
    console.log('Customer Name:', this.userName);
    
    // Dynamically adjust the background color and height of the confirm order container
    this.adjustContainerHeight();

    // Check if the cafe is open, if not show the closed message
    if (!this.isCafeOpen) {
      this.openOrderClosedMessage();
    }
  },
  methods: {
    isCafeOpenMethod() {
      const now = new Date();
      const dayOfWeek = now.getDay(); // 0 is Sunday, 1 is Monday, ..., 6 is Saturday
      const hour = now.getHours();
      const minute = now.getMinutes();

      // The cafe is open Monday to Saturday, from 6:00 AM to 9:30 PM
      if (dayOfWeek === 0 || // Closed on Sunday
          hour < 6 || // Before 6 AM
          (hour === 9 && minute > 30) || // After 9:30 PM
          hour > 21) { // After 9 PM
        return false; // Cafe is closed
      }
      return true; // Cafe is open
    },

    openOrderClosedMessage() {
      this.showOrderClosedMessage = true;
      this.showModal = false; // Close the modal if it's open
    },

    closeOrderClosedMessage() {
      this.showOrderClosedMessage = false;
    },

    loadCart() {
      const userCartKey = `cart_${this.userName}`; // Create user-specific cart key
      const storedCart = localStorage.getItem(userCartKey);
      if (storedCart) {
        this.cart = JSON.parse(storedCart);
        // Check if we have items from URL in the cart
        if (this.$route.query.name) {
          const urlItemExists = this.cart.some(item => item.name === this.$route.query.name);
          this.isItemAdded = urlItemExists;
        }
      }
    },

    handleNewItem() {
      const itemName = this.$route.query.name;
      const newItem = {
        name: itemName,
        price: Number(this.$route.query.price) || 0,
        quantity: 1
      };
      
      // Set image path - use provided image from URL parameters
      if (this.$route.query.image) {
        newItem.image = this.$route.query.image;
        
        // If the image is a backend path without the full URL, ensure it's properly formatted
        if (newItem.image.startsWith('/uploads')) {
          // The image path is already in the correct format for getImagePath to handle
          console.log('Using backend image path:', newItem.image);
        }
      } else if (this.productImages[itemName]) {
        // Fallback to the product mapping for predefined items
        newItem.image = this.productImages[itemName];
      } else {
        // If no image is provided and no mapping exists, set a flag to use default image
        console.log('No image found for item:', itemName);
        newItem.image = 'default.png';
      }

      // Check if item exists in cart
      const existingItemIndex = this.cart.findIndex(item => item.name === newItem.name);
      
      if (existingItemIndex === -1) {
        // Item doesn't exist, add it
        this.cart.push(newItem);
        this.isItemAdded = true;
        this.saveCart();
      }
    },

    saveCart() {
      const userCartKey = `cart_${this.userName}`; // Use the same user-specific cart key
      localStorage.setItem(userCartKey, JSON.stringify(this.cart));
    },

    startProcessingOrder() {
      this.isProcessingOrder = true;  // This will display the loading section
      this.progressBarWidth = 0;  // Reset the progress bar to 0%
      this.updateProgressBar();   // Example method to update progress
    },

    updateProgressBar() {
      let width = 0;
      const interval = setInterval(() => {
        if (width < 100) {
          width += 10;
          this.progressBarWidth = width;
        } else {
          clearInterval(interval);
        }
      }, 1000);  // Update every second
    },

    stopProcessingOrder() {
      this.isProcessingOrder = false;  // Stop the loading process
    },

    increaseQuantity(index) {
      this.cart[index].quantity += 1;
      this.saveCart();
    },

    decreaseQuantity(index) {
      if (this.cart[index].quantity > 1) {
        this.cart[index].quantity -= 1;
        this.saveCart();
      }
    },

    removeFromCart(index) {
      this.cart.splice(index, 1);
      this.saveCart();
    },

    addMoreOrder() {
      // Get the last category from localStorage
      const lastCategory = localStorage.getItem('lastCategory');
      
      // Navigate back to Dashboard with the category as a query parameter if available
      if (lastCategory) {
        this.$router.push({ 
          name: 'Dashboard',
          query: { category: lastCategory }
        });
      } else {
        this.$router.push({ name: 'Dashboard' });
      }
    },

    openModal() {
      this.showModal = true;
    },

    closeModal() {
      this.showModal = false;
    },

    confirmOrder() {
      this.showModal = false; // Close the modal

      // Show loading spinner and start countdown
      this.isProcessingOrder = true;
      this.progressBarWidth = 0;
      this.countdown = 2;

      // Store the interval reference so we can clear it when canceling
      this.progressInterval = setInterval(() => {
        if (this.countdown > 0 && this.isProcessingOrder) { // Check if still processing
          this.countdown--;
          this.progressBarWidth += 33.33; // Update the progress bar width
        } else if (this.isProcessingOrder) { // Only process if not cancelled
          clearInterval(this.progressInterval);
          this.processOrder(); // Call the function to send the order
        } else {
          clearInterval(this.progressInterval);
        }
      }, 1000); // Update every second
    },

    processOrder() {
      const customerName = localStorage.getItem('userName') || "Unknown";  // Fetch the correct username
      console.log('Customer Name:', customerName);  // Debugging

      const orderData = {
        customer_name: customerName,  // Use username here
        items: this.cart.map(item => ({
          name: item.name,
          quantity: item.quantity,
          price: item.price,
          image: item.image // Include the image path
        })),
        status: 'pending'
      };

      // Proceed to send the order data to the backend
      fetch('http://127.0.0.1:8000/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      })
      .then(response => response.json())
      .then((data) => {
        this.isProcessingOrder = false; // Hide the loading spinner
        const orderID = data.order_id; // Use the specific order ID returned from the server

        // Navigate to the Order ID page after the delay
        this.$router.push({
          name: 'OrderIDPage',
          query: {
            orderID: orderID, 
            customerName: customerName,
            items: JSON.stringify(this.cart),
            totalPrice: this.totalPrice
          }
        });

        // Clear cart data after the order is placed - use user-specific key
        const userCartKey = `cart_${this.userName}`;
        localStorage.removeItem(userCartKey);
        this.cart = [];
      })
      .catch(error => {
        this.isProcessingOrder = false; // Hide the loading spinner
        console.error("Error creating order:", error);
      });
    },

    stayOnPage() {
      this.showModal = false; // Close the modal and stay on the page
    },

    adjustContainerHeight() {
      const orderItems = document.querySelectorAll('.order-details li'); // Get all items in the order list
      const confirmOrderContainer = document.querySelector('.confirm-order'); // Get the confirm-order container

      const totalItems = orderItems.length;  // Calculate the number of items

      // Dynamically adjust padding based on the number of items
      if (totalItems <= 3) {
        confirmOrderContainer.style.padding = '20px';  // For fewer items, keep normal padding
      } else if (totalItems <= 6) {
        confirmOrderContainer.style.padding = '25px';  // For moderate items, add more padding
      } else {
        confirmOrderContainer.style.padding = '30px';  // For many items, add more padding
      }
    },

    getImagePath(item) {
      // If the item has a URL path already, use it directly
      if (item.image && (item.image.startsWith('http://') || item.image.startsWith('https://'))) {
        return item.image;
      }
      
      // Handle inventory system images (these would be full URLs from the inventory system)
      if (item.image && item.image.includes('localhost:8001')) {
        // Check if the path needs to be fixed - it should point to /uploads/products/
        if (item.image.includes('/uploads/') && !item.image.includes('/uploads/products/')) {
          // Extract the filename
          const parts = item.image.split('/');
          const filename = parts[parts.length - 1];
          const fixedPath = `http://localhost:8001/uploads/products/${filename}`;
          console.log('Fixed inventory image path:', fixedPath);
          return fixedPath;
        }
        return item.image;
      }
      
      // Handle local paths starting with /uploads/
      if (item.image && item.image.startsWith('/uploads/')) {
        return `http://localhost:8000${item.image}`;
      }
      
      // For items loaded from localStorage that have just the filename
      if (item.image && !item.image.includes('/')) {
        return `http://localhost:8000/uploads/avatars/${item.image}`;
      }
      
      // Fallback to default image
      return require('@/assets/default.png');
    },
    cancelProcessing() {
      this.isProcessingOrder = false;
      this.progressBarWidth = 0;
      this.showModal = false;
      if (this.progressInterval) {
        clearInterval(this.progressInterval);
      }
    },
  },
};
</script>

<style scoped>
/* Reset basic elements */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.cart-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  text-align: left;
  padding: 0 10px;
}

.confirm-order {
  padding: 20px;
  background-color: white; /* Updated to white background */
  max-width: 1200px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  min-height: 100vh;
}

.cart-container {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #E54F70;
}

.cart-header {
  display: grid;
  grid-template-columns: 3fr 1fr 1fr 1fr 0.5fr;
  padding: 15px;
  border-bottom: 1px solid #E54F70;
  font-weight: bold;
  color: #333;
  background-color: rgba(229, 79, 112, 0.05);
}

.cart-items {
  border-bottom: 1px solid #e0e0e0;
}

.cart-item {
  display: grid;
  grid-template-columns: 3fr 1fr 1fr 1fr 0.5fr;
  padding: 20px 15px;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.cart-item:last-child {
  border-bottom: none;
}

.item-details {
  display: flex;
  align-items: center;
}

.item-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  margin-right: 15px;
  border-radius: 4px;
}

.item-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.item-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 4px;
}

.estimated-ship {
  color: #ff6b00;
  font-size: 14px;
  margin-bottom: 4px;
}

.item-source, .item-promotion {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.change-link {
  color: #0066cc;
  text-decoration: none;
  font-size: 14px;
}

.item-price, .item-total {
  font-size: 16px;
  font-weight: bold;
}

.quantity-controls {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  width: fit-content;
}

.quantity-btn {
  background-color: #f5f5f5;
  border: none;
  color: #333;
  font-size: 16px;
  width: 30px;
  height: 30px;
  cursor: pointer;
}

.quantity-value {
  padding: 0 10px;
  font-size: 14px;
}

.remove-btn {
  background: none;
  border: none;
  color: #999;
  font-size: 24px;
  cursor: pointer;
}

.remove-btn:hover {
  color: #333;
}

.cart-summary {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.subtotal, .grand-total {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.grand-total {
  font-size: 18px;
  font-weight: bold;
  margin-top: 15px;
  margin-bottom: 15px;
}

.cart-actions {
  display: flex;
  justify-content: space-between;
  padding: 20px;
}

.continue-shopping {
  background-color: #ffffff;
  border: 1px solid #333;
  color: #333;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.checkout-btn {
  background-color: #E54F70;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.checkout-btn:hover {
  background-color: #d33d5e;
}

.empty-cart {
  padding: 50px 20px;
  text-align: center;
}

.empty-cart p {
  margin-bottom: 20px;
  font-size: 16px;
}

/* Modal Styles - Restored previous styling */
.custom-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal-content {
  background-color: #fce6e6;
  padding: 30px;
  border-radius: 10px;
  text-align: center;
  width: 80%;
  max-width: 600px;
}

.close {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 24px;
  color: #333;
  cursor: pointer;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.modal-buttons button {
  padding: 10px 15px;
  font-size: 14px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.yes-btn {
  background-color: rgb(136, 132, 136);
  color: white;
}

.no-btn {
  background-color: rgb(255, 0, 128);
  color: white;
}

.yes-btn:hover {
  background-color: #ff9a29;
}

.no-btn:hover {
  background-color: #b82d67;
}

/* Processing Order Section */
.loading-spinner-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  text-align: center;
  padding: 20px;
  background-color: #f8d2e4;
  border-radius: 35px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 80%;
  max-width: 400px;
}

.wedding-text {
  font-size: 36px;
  font-weight: bold;
  color: #d12f7a;
  font-family: 'Dancing Script', cursive;
  margin-bottom: 10px;
}

.loading-text {
  font-size: 24px;
  margin-bottom: 20px;
}

.progress-bar-container {
  width: 100%;
  max-width: 400px;
  height: 30px;
  background-color: #d85d7f;
  border-radius: 20px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    red 0%,
    red 10%,
    #d85d7f 10%,
    #d85d7f 20%
  );
  border-radius: 20px;
  animation: progressAnimation 3s linear infinite;
}

@keyframes progressAnimation {
  0% { width: 0%; }
  100% { width: 100%; }
}

.close-processing {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  color: #333;
  padding: 5px 10px;
  border-radius: 50%;
  transition: all 0.3s ease;
  z-index: 1001;
}

/* Closed Message */
.closed-message {
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  font-size: 24px;
  font-family: 'Dancing Script', cursive;
  position: fixed;
  top: 30%;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 600px;
  z-index: 9999;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.closed-message p {
  margin: 0;
  font-size: 22px;
  font-weight: bold;
}

/* Dark Mode Styles */
.dark-mode .confirm-order {
  background-color: #222;
  color: white;
}

.dark-mode .cart-container {
  background-color: #333;
  box-shadow: 0 1px 3px rgba(255, 255, 255, 0.1);
}

.dark-mode .cart-header {
  border-bottom: 1px solid #444;
  color: #fff;
}

.dark-mode .cart-items {
  border-bottom: 1px solid #444;
}

.dark-mode .cart-item {
  border-bottom: 1px solid #444;
}

.dark-mode .item-name {
  color: #fff;
}

.dark-mode .item-source, .dark-mode .item-promotion {
  color: #aaa;
}

.dark-mode .change-link {
  color: #66b0ff;
}

.dark-mode .item-price, .dark-mode .item-total, 
.dark-mode .quantity-value, .dark-mode .subtotal,
.dark-mode .grand-total {
  color: #fff;
}

.dark-mode .quantity-controls {
  border: 1px solid #555;
}

.dark-mode .quantity-btn {
  background-color: #444;
  color: #fff;
}

.dark-mode .remove-btn {
  color: #ccc;
}

.dark-mode .remove-btn:hover {
  color: #fff;
}

.dark-mode .cart-summary {
  border-bottom: 1px solid #444;
}

.dark-mode .continue-shopping {
  background-color: #333;
  border: 1px solid #666;
  color: #fff;
}

.dark-mode .checkout-btn {
  background-color: #d12f7a;
}

.dark-mode .empty-cart p {
  color: #fff;
}

.dark-mode .modal-content {
  background-color: #222;
  color: #fff;
}

.dark-mode .close {
  color: #fff;
}

.dark-mode .loading-spinner-container {
  background-color: #333;
  color: #fff;
}

.dark-mode .wedding-text {
  color: #f8a1b2;
}

.dark-mode .loading-text {
  color: #fff;
}

.dark-mode .close-processing {
  color: #fff;
}

/* Responsive Design */
@media (max-width: 768px) {
  .cart-header {
    display: none;
  }
  
  .cart-item {
    grid-template-columns: 1fr;
    grid-gap: 10px;
    padding: 15px;
  }
  
  .item-details {
    grid-column: 1;
  }
  
  .item-price, .item-quantity, .item-total {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .item-price::before {
    content: "Price:";
    font-weight: bold;
  }
  
  .item-quantity::before {
    content: "Quantity:";
    font-weight: bold;
  }
  
  .item-total::before {
    content: "Total:";
    font-weight: bold;
  }
  
  .item-actions {
    text-align: right;
  }
  
  .cart-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .continue-shopping, .checkout-btn {
    width: 100%;
  }

  .loading-spinner-container {
    width: 80%;
    padding: 12px;
    max-height: 250px;
    overflow: hidden;
  }
  
  .progress-bar-container {
    max-width: 250px;
  }
  
  .close-processing {
    font-size: 28px;
  }
}

@media (max-width: 480px) {
  .item-image {
    width: 50px;
    height: 50px;
  }
  
  .cart-title {
    font-size: 20px;
  }
  
  .item-name {
    font-size: 14px;
  }
  
  .estimated-ship, .item-source, .item-promotion {
    font-size: 12px;
  }
  
  .loading-spinner-container {
    width: 75%;
    padding: 10px;
    max-height: 200px;
    height: auto;
    overflow: hidden;
  }
  
  .progress-bar-container {
    max-width: 220px;
  }
  
  .close-processing {
    font-size: 24px;
  }
}
</style>
