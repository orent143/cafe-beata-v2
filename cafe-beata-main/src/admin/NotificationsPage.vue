<template>
  <div class="notifications-page">
    <!-- Sidebar Toggle Button (For Mobile) -->
    <button class="menu-button" @click="toggleSidebar">
      <div class="menu-icon-container">
        <i class="fa fa-bars"></i>
      </div>
    </button>

    <div v-if="isSidebarOpen" class="overlay"></div>
    
    <!-- Sidebar -->
    <div :class="['sidebar', { 'open': isSidebarOpen }]" @click.stop>
      <button class="close-sidebar" @click="toggleSidebar">
        <i class="fa fa-times"></i>
      </button>
      
      <!-- Admin Profile Section -->
      <div class="user-profile-section">
        <h3><i class="fa fa-user-circle"></i> Admin Dashboard</h3>
      </div>

      <hr class="utility-divider">

      <!-- Utility Buttons -->
      <div class="utility-section">
        <button @click="goToOrderRecord" class="utility-button">
          <i class="fa fa-history"></i>
          <span>View Order Record</span>
        </button>

        <button @click="toggleMenuEditor" class="utility-button">
          <i class="fa fa-utensils"></i>
          <span>Menu Editor</span>
        </button>

        <button @click="toggleStockManager" class="utility-button">
          <i class="fa fa-boxes"></i>
          <span>Stock Management</span>
        </button>

        <button @click="logout" class="utility-button logout">
          <i class="fa fa-sign-out"></i>
          <span>Logout</span>
        </button>
      </div>

      <!-- Cafe Status Section -->
      <div class="cafe-status-section">
        <button @click="toggleCafeStatus" :class="{'open-btn': isCafeOpen, 'closed-btn': !isCafeOpen}" class="cafe-toggle-btn">
          <i :class="isCafeOpen ? 'fa fa-check-circle' : 'fa fa-times-circle'"></i>
          {{ isCafeOpen ? 'Set Cafe Closed' : 'Set Cafe Open' }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div :class="['content', { 'shifted': isSidebarOpen }]">
      <!-- Add the top bar with pink gradient at the very top -->
      <div class="top-bar">
        <div class="centered-content">
          <div class="logo-container">
            <div class="cafe-title">Cafe Preorder Admin Dashboard</div>
          </div>
        </div>
      </div>

      <div class="content-below-top-bar">
        <div v-if="notificationVisible" :class="['notification-popup', notificationClass]">
          <p>{{ notificationMessage }}</p>
        </div>

        <!-- Search Bar -->
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search orders by ID, customer name..." 
            class="search-input"
          />
        </div>

        <div v-if="isLoading" class="loading">Loading...</div>

        <div v-if="filteredOrders.length && !isLoading" class="orders-container">
          <h2>Pending Orders</h2>
          <div class="orders-list">
            <div class="order-item" v-for="order in filteredOrders" :key="order.id">
              <div class="order-details">
                <h3>Order ID: {{ order.id }}</h3>
                <p><strong>Customer:</strong> {{ order.customer_name }}</p>
                <p><strong>Status:</strong> {{ order.status }}</p>
                <p><strong>Time Order: </strong> {{ timeAgo(order.created_at) }}</p> <!-- Time Ago Display -->

                <div class="items-section">
                  <strong>Items:</strong>
                  <ul>
                    <li v-for="item in order.items" :key="item.name">
                      {{ item.name }} - ₱{{ item.price }} x {{ item.quantity }}
                    </li>
                  </ul>
                </div>

                <!-- Total Amount below items -->
                <div class="order-total">
                  <p><strong>Total Amount: ₱{{ calculateOrderTotal(order.items) }}</strong></p>
                </div>
              </div>

              <div class="order-actions">
                <!-- Mark as Completed Buttons -->
                <button 
                  @click="showCompletionConfirmation(order.id)" 
                  class="mark-completed-btn small-btn"
                  :disabled="!orderReadyStatus[order.id]"
                  :class="{ 'disabled': !orderReadyStatus[order.id] }"
                >
                  Mark as Completed
                </button>

                <!-- Order Ready button -->
                <button 
                  @click="sendOrderReadyNotification(order.id, order.customer_name, order.items)" 
                  class="order-ready-btn small-btn"
                >
                  Order Ready  🔔
                </button>

                <!-- Decline button -->
                <button @click="openDeclineDialog(order)" class="decline-btn">
                  Decline
                </button>
              </div>

              <!-- Custom message input for decline -->
              <div v-if="order.id === activeDeclineOrderId" class="decline-container">
                <textarea v-model="customDeclineMessage" placeholder="Customize your message here..." rows="3" ref="declineText"></textarea>
                
                <!-- Button Container -->
                <div class="decline-buttons">
                  <button @click="declineOrder(order.id, order.customer_name, order.items)" class="decline-submit-btn">
                    Submit
                  </button>
                  <button @click="activeDeclineOrderId = null" class="decline-cancel-btn">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Completion Confirmation Popup -->
          <div v-if="confirmCompleteOrderId" class="completion-confirmation-popup">
            <div class="completion-confirmation-content">
              <h3>Confirm Completion</h3>
              <p>Are you sure Order ID: {{ confirmCompleteOrderId }} is completed?</p>
              <div class="confirmation-buttons">
                <button @click="confirmCompletion" class="confirm-yes-btn">Yes</button>
                <button @click="cancelCompletion" class="confirm-no-btn">No</button>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!isLoading" class="no-orders">
          <p>No pending orders at the moment.</p>
        </div>

        <!-- Popup Notification Sent -->
        <div v-if="notificationSent" class="notification-sent-popup">
          <p>Notification Sent!</p>
          <button @click="notificationSent = false" class="close-popup-btn">Close</button>
        </div>

        <!-- Menu Editor Popup Modal -->
        <div v-if="showMenuEditor" class="menu-editor-modal">
          <div class="menu-editor-content">
            <div class="menu-editor-header">
              <h2>Menu Editor</h2>
              <button @click="toggleMenuEditor" class="close-modal-btn">
                <i class="fa-solid fa-times"></i>
              </button>
            </div>
            <div class="menu-editor-body">
              <ItemEditor />
            </div>
          </div>
        </div>

        <!-- Stock Management Modal -->
        <div v-if="showStockManager" class="stock-manager-modal">
          <div class="stock-manager-content">
            <div class="stock-manager-header">
              <h2>Stock Management</h2>
              <button @click="toggleStockManager" class="close-modal-btn">
                <i class="fa-solid fa-times"></i>
              </button>
            </div>
            <div class="stock-manager-body">
              <!-- Search Bar -->
              <div class="stock-search-bar">
                <div class="stock-filters">
                  <input 
                    type="text" 
                    v-model="stockSearchQuery" 
                    placeholder="Search items..." 
                    class="search-input"
                  />
                  <select v-model="selectedCategory" class="category-filter">
                    <option value="">All Categories</option>
                    <option v-for="category in uniqueCategories" :key="category" :value="category">
                      {{ category }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Stock Items Table -->
              <div class="stock-table-container">
                <table class="stock-table">
                  <thead>
                    <tr>
                      <th>Item Name</th>
                      <th>Category</th>
                      <th>Current Stock</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in filteredStockItems" :key="item.id">
                      <td>{{ item.name }}</td>
                      <td>{{ item.category }}</td>
                      <td>{{ item.quantity >= 999999 ? 'Unlimited' : item.quantity }}</td>
                      <td :class="getStockStatusClass(item)">{{ getStockStatus(item) }}</td>
                      <td>
                        <button @click="openStockUpdateModal(item)" class="update-stock-btn">
                          Update Stock
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Stock Update Modal -->
        <div v-if="showStockUpdateModal" class="stock-update-modal">
          <div class="stock-update-content">
            <h3>Update Stock: {{ selectedItem?.name }}</h3>
            <div class="stock-update-form">
              <div class="form-group">
                <label>Current Stock: {{ selectedItem?.quantity >= 999999 ? 'Unlimited' : selectedItem?.quantity }}</label>
              </div>
              <div class="form-group">
                <label>Action:</label>
                <select v-model="stockUpdateAction">
                  <option value="add">Add Stock</option>
                  <option value="subtract">Remove Stock</option>
                  <option value="set">Set Stock</option>
                  <option value="disabled">Disabled (Out of Stock)</option>
                  <option value="enabled">Enabled (Unlimited Orders)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Quantity:</label>
                <input 
                  v-if="stockUpdateAction !== 'disabled' && stockUpdateAction !== 'enabled'"
                  type="number" 
                  v-model.number="stockUpdateQuantity" 
                  min="0"
                  :max="stockUpdateAction === 'subtract' ? selectedItem?.quantity : 999999"
                />
                <span v-else-if="stockUpdateAction === 'disabled'">
                  Item will be marked as out of stock and cannot be ordered.
                </span>
                <span v-else-if="stockUpdateAction === 'enabled'">
                  Item will be available for unlimited orders regardless of quantity.
                </span>
              </div>
              <div class="form-group">
                <label>Reason:</label>
                <input type="text" v-model="stockUpdateReason" placeholder="Enter reason for update"/>
              </div>
              <div class="update-buttons">
                <button @click="submitStockUpdate" class="confirm-btn">Update Stock</button>
                <button @click="closeStockUpdateModal" class="cancel-btn">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ItemEditor from './ItemEditor.vue'

export default {
  components: {
    ItemEditor
  },
  data() {
    return {
      orders: [], // Store pending orders
      isLoading: false, // For loading state
      ws: null, // WebSocket connection
      wsConnected: false,
      activeDeclineOrderId: null, // Track the order for which decline message is being customized
      customDeclineMessage: "", // Store the custom decline message
      notificationSent: false, // To track if the notification has been sent
      searchQuery: "", // To hold the search query input
      isCafeOpen: true,
      notificationMessage: "",
      notificationClass: "", 
      notificationVisible: false,
      showMenuEditor: false, // Control visibility of menu editor popup
      isSidebarOpen: true, // Always open by default
      orderReadyStatus: {}, // Track which orders are ready
      confirmCompleteOrderId: null, // Track which order is being confirmed for completion
      showStockManager: false,
      showStockUpdateModal: false,
      stockItems: [],
      stockSearchQuery: '',
      selectedItem: null,
      stockUpdateAction: 'add',
      stockUpdateQuantity: 0,
      stockUpdateReason: '',
      selectedCategory: '',
      uniqueCategories: [],
    };
  },
  computed: {
    // Filter orders based on search query
    filteredOrders() {
      if (!this.searchQuery) {
        return this.orders;
      }
      return this.orders.filter(order => {
        const lowerCaseSearchQuery = this.searchQuery.toLowerCase();
        return (
          order.id.toString().includes(lowerCaseSearchQuery) || // Search by Order ID
          order.customer_name.toLowerCase().includes(lowerCaseSearchQuery) // Search by Customer Name
        );
      });
    },
    filteredStockItems() {
      return this.stockItems.filter(item => {
        if (!item || !item.name) return false;
        const matchesSearch = item.name.toLowerCase().includes((this.stockSearchQuery || '').toLowerCase());
        const matchesCategory = !this.selectedCategory || item.category === this.selectedCategory;
        return matchesSearch && matchesCategory;
      });
    }
  },

  methods: {
    toggleCafeStatus() {
    this.isCafeOpen = !this.isCafeOpen; // Toggle the cafe status
    localStorage.setItem('isCafeOpen', this.isCafeOpen); // Store cafe status

    // Set the notification message and class based on the cafe status
    if (this.isCafeOpen) {
      this.notificationMessage = "Cafe Beàta is now Open!";
      this.notificationClass = "open-notification"; // Set class for green when open
    } else {
      this.notificationMessage = "Cafe Beàta is now Closed!";
      this.notificationClass = "closed-notification"; // Set class for red when closed
    }

    this.showNotification();  // Show the notification
  },
  
   showNotification() {
    // Show the notification and reset visibility after a timeout
    this.notificationVisible = true;

    setTimeout(() => {
      this.notificationVisible = false;
    }, 3000);  // Hide after 3 seconds
  },


    timeAgo(timestamp) {
    // If timestamp is a string, ensure it's in ISO format by replacing space with "T"
    if (typeof timestamp === "string") {
      timestamp = timestamp.replace(" ", "T"); // Convert to ISO format: "YYYY-MM-DD HH:MM:SS" -> "YYYY-MM-DDTHH:MM:SS"
    }

    const now = new Date();
    const orderTime = new Date(timestamp); // Parse the timestamp

    // Check if the timestamp is valid
    if (isNaN(orderTime)) {
      return "Invalid time"; // Return fallback message if timestamp is invalid
    }

    const differenceInSeconds = Math.floor((now - orderTime) / 1000);

    if (differenceInSeconds < 60) {
      return 'Just now';
    } else if (differenceInSeconds < 3600) {
      const minutes = Math.floor(differenceInSeconds / 60);
      return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (differenceInSeconds < 86400) {
      const hours = Math.floor(differenceInSeconds / 3600);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (differenceInSeconds < 2592000) {
      const days = Math.floor(differenceInSeconds / 86400);
      return `${days} day${days > 1 ? 's' : ''} ago`;
    } else if (differenceInSeconds < 31536000) {
      const months = Math.floor(differenceInSeconds / 2592000);
      return `${months} month${months > 1 ? 's' : ''} ago`;
    } else {
      const years = Math.floor(differenceInSeconds / 31536000);
      return `${years} year${years > 1 ? 's' : ''} ago`;
    }
  },



    // Method to format the order date in the required format
    formatDate(dateString) {
      const date = new Date(dateString);
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const year = date.getFullYear();
      const hours = date.getHours();
      const minutes = date.getMinutes().toString().padStart(2, '0');
      const period = hours >= 12 ? 'PM' : 'AM';
      const hour12 = (hours % 12 || 12).toString().padStart(2, '0');
      
      // Format: MM-DD-YYYY with highlighted time
      const formattedDate = `${month}-${day}-${year} <span class="highlighted-time">${hour12}:${minutes} ${period}</span>`;
      return formattedDate;
    },

    cancelDecline() {
      this.activeDeclineOrderId = null; // Hide decline input
      this.customDeclineMessage = ""; // Clear text
    },

    // Navigate to the Order Record page
    goToOrderRecord() {
      this.$router.push({ name: "OrderRecord" });  // Ensure this matches the name of the route
    },

    logout() {
      this.$router.push({ name: "Login" });  // Redirect the user to the Login page (adjust the route as needed)
    },

    // Fetch orders only once at initial load
    async fetchOrders() {
      if (this.isLoading) return;
      this.isLoading = true;
      
      try {
        const response = await fetch("http://127.0.0.1:8000/orders");
        const data = await response.json();
        if (data.orders && Array.isArray(data.orders)) {
          // Filter pending orders and sort them by ID in ascending order
          this.orders = data.orders
            .filter(order => order.status === "pending")
            .sort((a, b) => {
              // Convert order IDs to numbers for proper numerical sorting
              const idA = parseInt(a.id);
              const idB = parseInt(b.id);
              return idA - idB; // Sort in ascending order (lower IDs first)
            });
          
          // Check if any of the fetched orders have ready notifications
          // This ensures the "Mark as Completed" button is enabled for orders that are ready
          this.orders.forEach(order => {
            // If the order is already marked as ready in localStorage, keep that status
            if (this.orderReadyStatus[order.id]) {
              return;
            }
            
            // Check if there's a notification for this order
            const userNotificationsKey = `user_notifications_${order.customer_name}`;
            const notifications = JSON.parse(localStorage.getItem(userNotificationsKey)) || [];
            const hasReadyNotification = notifications.some(n => n.orderId === order.id);
            
            if (hasReadyNotification) {
              this.orderReadyStatus[order.id] = true;
            }
          });
          
          // Update localStorage with any changes
          localStorage.setItem('orderReadyStatus', JSON.stringify(this.orderReadyStatus));
        } else {
          console.error("Invalid data format", data);
          this.orders = [];
        }
      } catch (error) {
        console.error("Error fetching orders:", error);
      } finally {
        this.isLoading = false;
      }
    },

    // Format ordered items for notification message
    formatItems(items) {
      if (!Array.isArray(items)) {
        console.error("Invalid item format:", items);
        return "Invalid item data";
      }
      return items.map(item => `${item.name} x${item.quantity}`).join(", ");
    },

    // Calculate the total price for a single order
    calculateOrderTotal(items) {
      if (!Array.isArray(items)) return "₱0";
      return items.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);
    },

    // Mark an order as completed and send notification
    markAsCompleted(orderId, customerName, items) {
      // Log for debugging
      console.log(`Marking order ${orderId} as completed...`);
      
      // Ensure items is properly formatted
      let processedItems = items;
      if (typeof items === 'string') {
        try {
          processedItems = JSON.parse(items);
        } catch (e) {
          console.error("Failed to parse items:", e);
          alert("Error processing order items. Please try again.");
          return;
        }
      }
      
      fetch(`http://127.0.0.1:8000/orders/${orderId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "completed" })
      })
        .then(response => {
          // First check if the response is actually received
          if (!response) {
            throw new Error('No response received from server');
          }
          
          // Then check if it's OK
          if (!response.ok) {
            return response.text().then(text => {
              try {
                // Try to parse as JSON
                const data = JSON.parse(text);
                throw new Error(data.detail || `Server error: ${response.status}`);
              } catch (e) {
                // If parsing fails, use the raw text
                throw new Error(`Server error: ${response.status} - ${text || 'Unknown error'}`);
              }
            });
          }
          return response.json();
        })
        .then((data) => {
          console.log("Order completed successfully:", data);
          
          // Immediately remove from pending orders
          this.orders = this.orders.filter(order => order.id !== orderId);

          // Remove from orderReadyStatus
          delete this.orderReadyStatus[orderId];
          // Update localStorage
          localStorage.setItem('orderReadyStatus', JSON.stringify(this.orderReadyStatus));

          // Calculate the total price
          const total = processedItems.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);

          // Prepare the notification with highlighted order details
          const notification = {
            orderId,
            customerName,
            message: `Your order is completed! ✔️ Thank you for choosing Café Beata. Enjoy your food and drinks! 🥰. <span class="highlighted-order-details">Order details: ${this.formatItems(processedItems)}. Total: ₱${total}</span>`,
            timestamp: new Date().toISOString(),
            items: processedItems,
            total,
          };

          // Save the notification in localStorage for the specific user
          const userNotificationsKey = `user_notifications_${customerName}`;
          let notifications = JSON.parse(localStorage.getItem(userNotificationsKey)) || [];
          notifications.push(notification);
          localStorage.setItem(userNotificationsKey, JSON.stringify(notifications));

          // Send real-time notification via WebSocket if connected
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
              type: 'user_notification',
              action: 'order_completed',
              notification: notification,
              target_user: customerName
            }));
          }

          // Emit an event to notify other components
          window.dispatchEvent(new Event("notificationUpdated"));

          alert("Order marked as completed!");
        })
        .catch(error => {
          console.error("Error marking order as completed:", error);
          alert(error.message || "Error completing order. Please try again.");
          // Refresh orders to ensure UI is in sync
          this.fetchOrders();
        });
    },

    // Open the custom decline message input for a specific order
    openDeclineDialog(order) {
      this.activeDeclineOrderId = order.id;
      this.customDeclineMessage = localStorage.getItem(`customDeclineMessage_${order.id}`) || ""; // Get saved message from localStorage
    },

    // Decline an order and send notification with custom message
    declineOrder(orderId, customerName, items) {
      const message = this.customDeclineMessage || "Unfortunately, this item is temporarily out of stock. We apologize for the inconvenience and appreciate your patience. 🙏";

      fetch(`http://127.0.0.1:8000/orders/${orderId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "declined" }) // Properly formatted JSON
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then(() => {
          // Immediately remove from pending orders
          this.orders = this.orders.filter(order => order.id !== orderId);

          // Remove from orderReadyStatus if it exists
          if (this.orderReadyStatus[orderId]) {
            delete this.orderReadyStatus[orderId];
            // Update localStorage
            localStorage.setItem('orderReadyStatus', JSON.stringify(this.orderReadyStatus));
          }

          // Calculate the total price
          const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);

          // Prepare the notification with the custom message and order details
          const notification = {
            orderId,
            customerName,
            message: `${message} Order details: ${this.formatItems(items)}. Total: ₱${total}`,
            timestamp: new Date().toISOString(),
            items,  // Include items in the notification
            total,  // Include total in the notification
          };

          // Save the notification in localStorage for the specific user
          const userNotificationsKey = `user_notifications_${customerName}`;
          let notifications = JSON.parse(localStorage.getItem(userNotificationsKey)) || [];
          notifications.push(notification);
          localStorage.setItem(userNotificationsKey, JSON.stringify(notifications));

          // Emit an event to notify other components (optional)
          window.dispatchEvent(new Event("orderDeclined"));

          alert("Order has been declined!");
        })
        .catch(error => console.error("Error declining order:", error));

      // Reset after submission
      this.activeDeclineOrderId = null;
      this.customDeclineMessage = "";
      localStorage.removeItem(`customDeclineMessage_${orderId}`); // Clear message from localStorage after submission
    },

    // Save the decline message to localStorage whenever it's updated
    updateDeclineMessage() {
      if (this.activeDeclineOrderId !== null) {
        localStorage.setItem(`customDeclineMessage_${this.activeDeclineOrderId}`, this.customDeclineMessage);
      }
    },

    // New method to handle the "Order Ready" button click and show pop-up notification
    sendOrderReadyNotification(orderId, customerName, items) {
      const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);

      const notification = {
        orderId,
        customerName,
        message: `Your order is now ready! Proceed to the cashier for payment and pickup. ☺️ Order details: ${this.formatItems(items)}. Total: ₱${total}`,
        timestamp: new Date().toISOString(),
        items,
        total,
      };

      // Save the notification in localStorage for the specific user
      const userNotificationsKey = `user_notifications_${customerName}`;
      let notifications = JSON.parse(localStorage.getItem(userNotificationsKey)) || [];
      
      // Add the notification without replacing existing ones
      notifications.push(notification);
      
      // Sort notifications by timestamp (newest first)
      notifications.sort((a, b) => {
        const dateA = new Date(a.timestamp);
        const dateB = new Date(b.timestamp);
        return dateB - dateA;
      });
      
      localStorage.setItem(userNotificationsKey, JSON.stringify(notifications));

      // Set order as ready using direct assignment
      this.orderReadyStatus[orderId] = true;
      // Force reactivity update
      this.orderReadyStatus = { ...this.orderReadyStatus };
      
      // Save orderReadyStatus to localStorage
      localStorage.setItem('orderReadyStatus', JSON.stringify(this.orderReadyStatus));

      // Send real-time notification via WebSocket if connected
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'user_notification',
          action: 'order_ready',
          notification: notification,
          target_user: customerName
        }));
      }

      // Show success notification to admin
      this.notificationSent = true;
      setTimeout(() => {
        this.notificationSent = false;
      }, 3000);
    },

    // Toggle menu editor popup visibility
    toggleMenuEditor() {
      this.showMenuEditor = !this.showMenuEditor;
      
      // When opening the modal, prevent scrolling on the body
      if (this.showMenuEditor) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    },

    // Toggle sidebar visibility
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
      // When opening the sidebar, prevent scrolling on the body
      if (this.isSidebarOpen) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    },

    // Close sidebar - only called when X button is clicked
    closeSidebar() {
      this.isSidebarOpen = false;
      document.body.style.overflow = '';
    },

    // Handle clicks outside sidebar - removed to prevent auto-closing when clicking outside
    handleOutsideClick() {
      // Do nothing - sidebar should stay open
    },

    // Add new methods for completion confirmation
    showCompletionConfirmation(orderId) {
      this.confirmCompleteOrderId = orderId;
    },

    confirmCompletion() {
      const order = this.orders.find(o => o.id === this.confirmCompleteOrderId);
      if (order) {
        this.markAsCompleted(order.id, order.customer_name, order.items);
      }
      this.confirmCompleteOrderId = null;
    },

    cancelCompletion() {
      this.confirmCompleteOrderId = null;
    },

    toggleStockManager() {
      this.showStockManager = !this.showStockManager;
      if (this.showStockManager) {
        this.fetchStockItems();
      }
    },

    async fetchStockItems() {
      try {
        const response = await fetch('http://localhost:8000/api/stocks');
        const data = await response.json();
        console.log('Fetched stock data:', data); // Debug log
        
        if (data.success && Array.isArray(data.items)) {
          // Map the items to include name and category from item_name
          this.stockItems = data.items.map(item => ({
            id: item.item_id, // Use item_id from the API response
            name: item.item_name,
            category: item.category,
            quantity: item.quantity,
            min_stock_level: item.min_stock_level
          }));
          
          // Update unique categories
          this.uniqueCategories = [...new Set(this.stockItems.map(item => item.category))];
          console.log('Processed stock items:', this.stockItems); // Debug log
        } else {
          console.error('Invalid data format received:', data);
        }
      } catch (error) {
        console.error('Error fetching stock items:', error);
      }
    },

    getStockStatus(item) {
      if (item.quantity === 0) return 'Disabled (Out of Stock)';
      if (item.quantity >= 999999) return 'Enabled (Unlimited)';
      if (item.quantity <= item.min_stock_level) return 'Low Stock';
      return 'In Stock';
    },

    getStockStatusClass(item) {
      if (item.quantity === 0) return 'status-disabled';
      if (item.quantity >= 999999) return 'status-enabled';
      if (item.quantity <= item.min_stock_level) return 'status-low';
      return 'status-ok';
    },

    openStockUpdateModal(item) {
      console.log('Opening modal for item:', item); // Debug log
      this.selectedItem = item;
      this.showStockUpdateModal = true;
      this.stockUpdateQuantity = 0;
      this.stockUpdateAction = 'add';
      this.stockUpdateReason = '';
    },

    closeStockUpdateModal() {
      this.showStockUpdateModal = false;
      this.selectedItem = null;
      this.stockUpdateQuantity = 0;
      this.stockUpdateReason = '';
    },

    async submitStockUpdate() {
      // Validate required fields
      if (!this.selectedItem || !this.selectedItem.id) {
        alert('No item selected');
        return;
      }

      if (!this.stockUpdateAction) {
        alert('Please select an action');
        return;
      }

      try {
        let requestBody = {};
        
        // Handle different action types
        if (this.stockUpdateAction === 'disabled') {
          // For disabled, set quantity to 0 and use 'set' action
          requestBody = {
            action: 'set',
            quantity: 0,
            reason: this.stockUpdateReason || 'Disabled - Out of Stock'
          };
        } else if (this.stockUpdateAction === 'enabled') {
          // For enabled, set a special value to indicate unlimited
          requestBody = {
            action: 'set',
            quantity: 999999, // Very large number to represent unlimited
            reason: this.stockUpdateReason || 'Enabled - Unlimited Orders'
          };
        } else {
          // For regular actions (add, subtract, set)
          if (!this.stockUpdateQuantity || this.stockUpdateQuantity <= 0) {
            alert('Please enter a valid quantity (greater than 0)');
            return;
          }

          // Additional validation for subtract action
          if (this.stockUpdateAction === 'subtract' && this.stockUpdateQuantity > this.selectedItem.quantity) {
            alert('Cannot remove more than current stock');
            return;
          }
          
          requestBody = {
            action: this.stockUpdateAction,
            quantity: parseInt(this.stockUpdateQuantity),
            reason: this.stockUpdateReason || 'Stock update'
          };
        }

        console.log('Sending request:', requestBody);

        const response = await fetch(`http://localhost:8000/api/stocks/${this.selectedItem.id}/update`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });

        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'Failed to update stock');
        }

        if (data.success) {
          alert('Stock updated successfully!');
          this.closeStockUpdateModal();
          await this.fetchStockItems(); // Refresh the stock list
        } else {
          throw new Error(data.message || 'Failed to update stock');
        }
      } catch (error) {
        console.error('Error updating stock:', error);
        alert(error.message || 'Failed to update stock. Please try again.');
      }
    },

    initWebSocket() {
      // Use the same host as the API
      const wsUrl = `ws://${window.location.hostname}:8000/ws/orders`;
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.wsConnected = true;
      };
      
      this.ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);

          if (data.type === 'new_order') {
            // Handle new order
            if (data.order.status === 'pending') {
              // Add the new order to the orders array
              this.orders.push(data.order);
              
              // Re-sort the orders array by ID in ascending order
              this.orders.sort((a, b) => {
                const idA = parseInt(a.id);
                const idB = parseInt(b.id);
                return idA - idB; // Sort in ascending order (lower IDs first)
              });
            }
          } else if (data.type === 'order_status_update') {
            // Handle order status update
            if (data.status !== 'pending') {
              this.orders = this.orders.filter(order => order.id !== data.order_id);
              
              // Remove from orderReadyStatus if it exists
              if (this.orderReadyStatus[data.order_id]) {
                delete this.orderReadyStatus[data.order_id];
                // Update localStorage
                localStorage.setItem('orderReadyStatus', JSON.stringify(this.orderReadyStatus));
              }
            }
          } else if (data.type === 'stock_update') {
            // Handle stock update
            const stockItem = this.stockItems.find(item => item.id === data.item_id);
            if (stockItem) {
              stockItem.quantity = data.new_quantity;
              stockItem.min_stock_level = data.min_stock_level;
              
              // Update unique categories if needed
              if (!this.uniqueCategories.includes(data.category)) {
                this.uniqueCategories.push(data.category);
              }
            }
            // Refresh stock items to ensure all data is up to date
            await this.fetchStockItems();
          } else if (data.type === 'menu_update') {
            // Handle menu updates (new items, edited items, or deleted items)
            await this.fetchStockItems(); // Refresh stock items when menu changes
          } else if (data.type === 'category_update') {
            // Handle category updates
            await this.fetchStockItems(); // Refresh stock items when categories change
            
            // Update unique categories list
            if (data.action === 'add' && data.category && data.category.name) {
              if (!this.uniqueCategories.includes(data.category.name)) {
                this.uniqueCategories.push(data.category.name);
              }
            } else if (data.action === 'update' && data.category) {
              // Replace old category name with new one
              const index = this.uniqueCategories.indexOf(data.category.old_name);
              if (index !== -1) {
                this.uniqueCategories[index] = data.category.name;
              } else if (!this.uniqueCategories.includes(data.category.name)) {
                this.uniqueCategories.push(data.category.name);
              }
              
              // Update selected category if it was renamed
              if (this.selectedCategory === data.category.old_name) {
                this.selectedCategory = data.category.name;
              }
            } else if (data.action === 'delete' && data.category_name) {
              // Remove deleted category
              this.uniqueCategories = this.uniqueCategories.filter(cat => cat !== data.category_name);
              
              // Reset selected category if it was deleted
              if (this.selectedCategory === data.category_name) {
                this.selectedCategory = '';
              }
            }
          }
        } catch (error) {
          console.error('Error processing WebSocket message:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.wsConnected = false;
        // Try to reconnect after 5 seconds
        setTimeout(() => {
          this.initWebSocket();
        }, 5000);
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.wsConnected = false;
      };
    },
  },

  mounted() {
    const savedCafeStatus = localStorage.getItem('isCafeOpen');
    if (savedCafeStatus !== null) {
      this.isCafeOpen = JSON.parse(savedCafeStatus);
    }
    
    // Load orderReadyStatus from localStorage
    const savedOrderReadyStatus = localStorage.getItem('orderReadyStatus');
    if (savedOrderReadyStatus !== null) {
      this.orderReadyStatus = JSON.parse(savedOrderReadyStatus);
    }
    
    // Initialize WebSocket first
    this.initWebSocket();
    
    // Then fetch initial orders
    this.fetchOrders();
  },

  beforeUnmount() {
    // Close WebSocket connection
    if (this.ws) {
      this.ws.close();
    }
  }
};
</script>

<style scoped>
/* Base styles for all screen sizes */
.notifications-page {
  height: 100vh;
  display: flex;
  background-color: #ffffff;
}

/* Top Bar Styles to match dashboard */
.top-bar {
  display: flex;
  align-items: center;
  background-image: linear-gradient(to right, #E54F70, #ed9598);
  padding: 0 15px;
  height: 60px;
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.content.shifted .top-bar {
  left: 300px; /* Adjust left position when sidebar is open */
  width: calc(100% - 300px); /* Adjust width when sidebar is open */
}

.content-below-top-bar {
  margin-top: 70px; /* Add margin to account for the fixed top bar */
  padding: 10px 20px;
}

.centered-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
}

.logo-container {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.cafe-title {
  color: white;
  font-weight: bold;
  font-size: 20px;
  white-space: nowrap;
}

/* Menu Button */
.menu-button {
  position: fixed;
  top: 15px;
  left: 15px;
  z-index: 300;
  background: #d12f7a;
  color: white;
  padding: 12px 15px;
  font-size: 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.menu-button:hover {
  background: #b82d67;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}

.menu-icon-container {
  position: relative;
  display: inline-block;
  font-size: 24px;
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: -300px;
  height: 100vh;
  width: 300px;
  background: #f5f5f5;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
  color: #333;
}

.sidebar.open {
  left: 0;
}

.close-sidebar {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(209, 47, 122, 0.1);
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #d12f7a;
  padding: 8px 12px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-sidebar:hover {
  background: rgba(209, 47, 122, 0.2);
  transform: rotate(90deg);
}

/* User Profile Section */
.user-profile-section {
  padding: 30px 20px;
  text-align: center;
  margin-bottom: 20px;
  background: rgba(209, 47, 122, 0.1);
  border-radius: 15px;
  margin: 0 15px 20px;
}

.user-profile-section h3 {
  color: #d12f7a;
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  text-shadow: none;
}

/* Utility Section */
.utility-section {
  padding: 15px;
  margin: 0 15px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.utility-button {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #333;
  font-size: 16px;
  text-decoration: none;
  transition: all 0.3s ease;
  border-radius: 10px;
  margin-bottom: 8px;
  position: relative;
  overflow: hidden;
}

.utility-button:last-child {
  margin-bottom: 0;
}

.utility-button:hover {
  background: rgba(209, 47, 122, 0.1);
  transform: translateX(5px);
}

.utility-button i {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #d12f7a;
  border-radius: 8px;
  font-size: 16px;
  color: white;
  transition: all 0.3s ease;
}

.utility-button:hover i {
  transform: rotate(10deg);
}

.utility-button span {
  font-weight: 500;
}

.utility-button.logout {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
  margin-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.utility-button.logout i {
  background: #f44336;
}

.utility-button.logout:hover {
  background: rgba(244, 67, 54, 0.15);
}

/* Cafe Status Section */
.cafe-status-section {
  padding: 20px;
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.cafe-toggle-btn {
  font-size: 16px;
  padding: 12px 24px;
  border: 2px solid #d12f7a;
  cursor: pointer;
  border-radius: 30px;
  transition: all 0.3s ease;
  font-weight: 600;
  width: 100%;
  background: white;
  color: #d12f7a;
  text-transform: uppercase;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.cafe-toggle-btn::before {
  content: '🏪';
  font-size: 20px;
}

.cafe-toggle-btn:hover {
  background: rgba(209, 47, 122, 0.1);
  transform: translateY(-2px);
}

.cafe-toggle-btn.open-btn {
  border-color: #4CAF50;
  color: #4CAF50;
}

.cafe-toggle-btn.open-btn::before {
  content: '✅';
}

.cafe-toggle-btn.closed-btn {
  border-color: #f44336;
  color: #f44336;
}

.cafe-toggle-btn.closed-btn::before {
  content: '🚫';
}

/* Utility Divider */
.utility-divider {
  border: none;
  height: 1px;
  background: rgba(0, 0, 0, 0.1);
  margin: 15px;
  border-radius: 1px;
}

/* Main Content Area */
.content {
  flex: 1;
  margin-left: 0;
  padding: 20px;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.content.shifted {
  margin-left: 300px;
}

/* Overlay */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 999;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.overlay.visible {
  opacity: 1;
}

/* Search Bar */
.search-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px auto;
  width: 90%;
  max-width: 400px;
  background-color: transparent;
  border-radius: 30px;
  border: 2px solid #d12f7a;
}

.search-input {
  width: 100%;
  padding: 10px 15px;
  font-size: 16px;
  border: none;
  outline: none;
  background-color: transparent;
  color: #333;
  border-radius: 30px;
}

/* Orders Container */
.orders-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.orders-container h2 {
  text-align: center;
  color: #d12f7a;
  margin-bottom: 20px;
}

.orders-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  width: 100%;
}

/* Order Item */
.order-item {
  background-color: #f8d2e4;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: auto;
}

.order-details h3 {
  color: #d12f7a;
  margin-top: 0;
}

.order-details p {
  margin: 5px 0;
}

.items-section {
  margin-top: 15px; 
  flex-grow: 1; /* Allow the items section to expand and adapt */
}

.order-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

ul {
  list-style-type: none;
  padding-left: 20px;
  margin: 0;
}

.order-total {
  margin-top: 10px;
  font-weight: bold;
  color: #d12f7a;
  text-align: center; /* Ensure it aligns nicely with the rest of the content */
}

/* Button styles */
button.mark-completed-btn {
  background-color: #d12f7a;
  color: white;
  border: none;
  padding: 8px 10px;
  border-radius: 5px;
  cursor: pointer;
  width: 100%;
  transition: all 0.3s ease;
}

button.mark-completed-btn:disabled,
button.mark-completed-btn.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}

button.mark-completed-btn:not(:disabled):hover {
  background-color: #b82d67;
}

.order-ready-btn {
  background-color: #4caf50; /* Green background for success */
  color: white; /* White text */
  padding: 8px 10px;
  font-size: 14px;
  border: none;
  border-radius: 5px; /* Rounded corners */
  cursor: pointer;
  width: 100%;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.order-ready-btn:hover {
  background-color: #45a049; /* Slightly darker green when hovered */
  transform: translateY(-2px); /* Slight upward movement on hover */
}

.order-ready-btn:active {
  background-color: #388e3c; /* Even darker green when clicked */
  transform: translateY(0); /* Reset the movement after click */
}

button.decline-btn {
  background-color: #f5a5a5;
  color: white;
  border: none;
  padding: 8px 10px;
  border-radius: 5px;
  cursor: pointer;
  width: 100%;
}

button.decline-btn:hover {
  background-color: #f17b7b;
}

/* Decline container styles */
.decline-container {
  width: 100%;
  padding: 15px;
  box-sizing: border-box; 
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  text-align: center;
  display: flex;
  flex-direction: column;
  margin-top: 10px;
}

.decline-container textarea {
  width: 100%;
  height: 80px;
  border-radius: 5px;
  border: 1px solid #ccc;
  padding: 10px;
  font-size: 14px;
  margin-bottom: 10px;
  resize: none;
}

.decline-buttons {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 10px;
}

.decline-submit-btn,
.decline-cancel-btn {
  padding: 8px 14px;
  border-radius: 5px;
  cursor: pointer;
  border: none;
  flex: 1;
}

.decline-submit-btn {
  background-color: #f17b7b;
  color: white;
}

.decline-submit-btn:hover {
  background-color: #d05e5e;
}

.decline-cancel-btn {
  background-color: #cccccc;
  color: black;
}

.decline-cancel-btn:hover {
  background-color: #999999;
}

/* Notification styles */
.notification-popup,
.notification-sent-popup {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 15px 30px;
  border-radius: 8px;
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
  font-size: 18px;
  min-width: 200px;
  max-width: 90%;
  z-index: 1000;
  transition: opacity 0.3s ease, transform 0.3s ease;
  opacity: 1;
  text-align: center;
}

.notification-sent-popup {
  background-color: rgb(82, 13, 45);
  color: white;
}

.notification-popup.hide {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.notification-popup button,
.notification-sent-popup button {
  background-color: #fff;
  color: #007bff;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 10px;
  font-size: 14px;
}

.notification-popup button:hover,
.notification-sent-popup button:hover {
  background-color: #f1f1f1;
}

.notification-popup.open-notification {
  background-color: #4caf50;
  color: white;
}

.notification-popup.closed-notification {
  background-color: red;
  color: white;
}

.highlighted-order-details {
  display: inline-block;
  background-color: #f8d2e4;
  color: #d12f7a;
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  font-weight: bold;
  border: 2px solid #d12f7a;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  text-align: center;
  box-sizing: border-box;
}

.highlighted-order-details::before {
  content: "——— ";
  font-size: 24px;
  font-weight: bold;
  color: #d12f7a;
}

.loading {
  text-align: center;
  color: #d12f7a;
  font-size: 20px;
  margin-top: 20px;
}

.no-orders {
  text-align: center;
  margin: 30px 0;
}

.highlighted-time {
  color: #d12f7a;
  font-weight: bold;
}

.dark-mode .highlighted-time {
  color: #f8d2e4;
}

.section-divider {
  border-top: 1px solid #ddd;
  margin: 30px 0;
}

/* Media Queries for Responsive Design */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }
  
  .header-buttons {
    order: 3;
    width: 100%;
    justify-content: center;
  }
  
  h1 {
    order: 1;
    width: 100%;
  }
  
  .order-record-button {
    order: 2;
    width: 100%;
    max-width: 200px;
  }
  
  .logout-button {
    order: 4;
    width: 100%;
    max-width: 200px;
  }
  
  .orders-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .notifications-page {
    padding: 10px;
  }
  
  .cafe-toggle-btn {
    width: 180px;
    font-size: 14px;
  }
  
  .notification-popup,
  .notification-sent-popup {
    font-size: 16px;
    padding: 10px 20px;
  }
  
  .order-item {
    padding: 12px;
  }
  
  .decline-container {
    padding: 10px;
  }
  
  .decline-buttons {
    flex-direction: column;
  }
  
  .decline-submit-btn,
  .decline-cancel-btn {
    width: 100%;
  }
}

/* Menu Editor Modal Styles */
.menu-editor-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
  overflow-y: auto;
}

.menu-editor-content {
  background-color: white;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.menu-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f8d2e4;
  border-bottom: 1px solid #e0e0e0;
}

.menu-editor-header h2 {
  color: #d12f7a;
  margin: 0;
}

.close-modal-btn {
  background: none;
  border: none;
  color: #d12f7a;
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
}

.close-modal-btn:hover {
  color: #b82d67;
}

.menu-editor-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(90vh - 70px); /* Subtract header height */
}

/* Media query adjustments for the modal */
@media (max-width: 768px) {
  .menu-editor-content {
    width: 95%;
    max-height: 95vh;
  }
}

@media (max-width: 480px) {
  .menu-editor-header {
    padding: 10px 15px;
  }
  
  .menu-editor-body {
    padding: 15px;
  }
}

/* Completion Confirmation Popup Styles */
.completion-confirmation-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1002;
}

.completion-confirmation-content {
  background-color: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.completion-confirmation-content h3 {
  color: #d12f7a;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.5em;
}

.completion-confirmation-content p {
  margin-bottom: 20px;
  font-size: 1.1em;
  color: #333;
}

.confirmation-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.confirm-yes-btn,
.confirm-no-btn {
  padding: 10px 25px;
  border: none;
  border-radius: 5px;
  font-size: 1.1em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.confirm-yes-btn {
  background-color: #d12f7a;
  color: white;
}

.confirm-yes-btn:hover {
  background-color: #b82d67;
  transform: translateY(-2px);
}

.confirm-no-btn {
  background-color: #f5a5a5;
  color: white;
}

.confirm-no-btn:hover {
  background-color: #f17b7b;
  transform: translateY(-2px);
}

/* Media query adjustments for the confirmation popup */
@media (max-width: 480px) {
  .completion-confirmation-content {
    padding: 20px;
    width: 85%;
  }

  .confirmation-buttons {
    flex-direction: column;
    gap: 10px;
  }

  .confirm-yes-btn,
  .confirm-no-btn {
    width: 100%;
    padding: 12px;
  }
}

/* Stock Management Modal Styles */
.stock-manager-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.stock-manager-content {
  background-color: white;
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.stock-manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #f8d2e4;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.stock-manager-header h2 {
  color: #d12f7a;
  margin: 0;
}

.stock-manager-body {
  padding: 20px;
  overflow-y: auto;
}

.stock-search-bar {
  margin-bottom: 20px;
}

.stock-table-container {
  overflow-x: auto;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.stock-table th,
.stock-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.stock-table th {
  background-color: #f8d2e4;
  color: #d12f7a;
}

.status-out {
  color: #f44336;
  font-weight: bold;
}

.status-low {
  color: #ff9800;
  font-weight: bold;
}

.status-ok {
  color: #4caf50;
  font-weight: bold;
}

.status-disabled {
  color: #9e9e9e;
  font-weight: bold;
}

.status-enabled {
  color: #2196f3;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.update-stock-btn {
  background-color: #d12f7a;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(209, 47, 122, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.update-stock-btn::before {
  content: '📦';
  font-size: 16px;
}

.update-stock-btn:hover {
  background-color: #b82d67;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(209, 47, 122, 0.3);
}

.update-stock-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(209, 47, 122, 0.2);
}

.stock-update-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1002;
}

.stock-update-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
}

.stock-update-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: bold;
}

.form-group input,
.form-group select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.update-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.confirm-btn,
.cancel-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.confirm-btn {
  background-color: #d12f7a;
  color: white;
}

.cancel-btn {
  background-color: #f5a5a5;
  color: white;
}

.low-stock {
  color: #ff9800;
  font-weight: bold;
}

.out-of-stock {
  color: #f44336;
  font-weight: bold;
}

.stock-filters {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  width: 100%;
}

.category-filter {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 150px;
  background-color: white;
  cursor: pointer;
}

.category-filter:hover {
  border-color: #d12f7a;
}

.dark-mode .category-filter {
  background-color: #333;
  color: white;
  border-color: #555;
}

.dark-mode .category-filter:hover {
  border-color: #f8c6d0;
}
</style>