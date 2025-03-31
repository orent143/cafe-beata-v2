<template>
  <div :class="['order-id-page', { 'dark-mode': isDarkMode }]">
    
    <!-- Order Queue Notification -->
    <h4>
      Your order is in queue.. Please check your dashboard notifications regularly for updates.
    </h4>

    <h4>
      PLEASE SCREENSHOT OR SAVE THE ORDER ID NUMBER ALWAYS!
    </h4>

    <!-- Order Confirmation Box -->
    <div class="order-confirmation-box">
      <div class="checkmark">
        <span>✔️</span> <!-- Checkmark icon -->
      </div>
      <h2>Order Confirmed :)</h2>
      <p>{{ currentDate }}</p>

      <!-- Add horizontal line -->
      <hr class="order-line"/>

      <!-- Order Details -->
      <div class="order-details">
        <p><strong>Order No:</strong> {{ parseInt(orderID) }}</p>
        <p><strong>Customer:</strong> {{ customerName }}</p>
        <ul>
          <li v-for="(item, index) in orderItems" :key="index">
            {{ item.name }} - ₱{{ item.price * item.quantity }} x{{ item.quantity }}
          </li>
        </ul>
        <p><strong>Total Payment:</strong> ₱{{ total }}</p>
      </div>

      <!-- Back to Dashboard Button -->
      <button @click="goBackToDashboard" class="back-button">Back to Dashboard</button>
    </div>
  </div>
</template>



<script>
export default {
  data() {
    return {
      orderID: this.$route.query.orderID || "Unknown",
      orderItems: [],
      customerName: this.$route.query.customerName || localStorage.getItem('userName') || "Guest", // Ensure it's from localStorage
      orderCompletedMessage: "", // Store the order completion message
      isDarkMode: localStorage.getItem("darkMode") === "true",
      orderCompleted: false, // Add a flag to track if the order is completed
      currentDate: new Date().toLocaleDateString(),  // Current date for order confirmation
      total: 0 // Total amount for the order
    };
  },
  created() {
    this.loadOrderItems();
    
    // Only add the notification if it doesn't already exist in localStorage
    const userName = localStorage.getItem("userName");
    const userNotificationsKey = `user_notifications_${userName}`;
    const existingNotifications = JSON.parse(localStorage.getItem(userNotificationsKey)) || [];
    
    // Check if any notification for this order already exists
    const hasExistingNotification = existingNotifications.some(n => n.orderId === this.orderID);
    
    // Only send the notification if none exists for this order
    if (!hasExistingNotification) {
      this.sendEstimatedTimeNotification();
    }
  },
  methods: {
    loadOrderItems() {
      try {
        this.orderItems = JSON.parse(this.$route.query.items || "[]");
        this.total = this.orderItems.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);
      } catch (error) {
        console.error("Error parsing order items:", error);
        this.orderItems = [];
      }
    },

    // New method to send estimated preparation time notification
    sendEstimatedTimeNotification() {
      // Calculate if the order has drinks only, food, or both
      const hasDrinks = this.orderItems.some(item => 
        item.category && 
        (item.category.toLowerCase().includes('drink') || 
         item.category === 'Juice Drinks' || 
         item.category === 'Chocolate Drinks' ||
         item.category === 'Coffee')
      );
      
      const hasFood = this.orderItems.some(item => 
        item.category && 
        !item.category.toLowerCase().includes('drink') && 
        item.category !== 'Juice Drinks' && 
        item.category !== 'Chocolate Drinks' &&
        item.category !== 'Coffee'
      );
      
      // Determine estimated time based on order content
      let estimatedTime;
      if (hasDrinks && !hasFood) {
        estimatedTime = "10-12 minutes";
      } else if (hasFood || (hasDrinks && hasFood)) {
        estimatedTime = "12-15 minutes";
      } else {
        estimatedTime = "10-15 minutes";
      }
      
      // Create the notification message
      const orderDetails = this.orderItems.map(item => `${item.name} x${item.quantity}`).join(", ");
      
      const message = `Your order #${this.orderID} has been received! Estimated preparation time: ${estimatedTime}. <span class="highlighted-order-details">Order details: ${orderDetails}. Total: ₱${this.total}</span>`;
      
      // Create the notification object
      const notification = {
        orderId: this.orderID,
        customerName: this.customerName,
        message: message,
        timestamp: new Date().toISOString(),
      };
      
      // Add the notification to localStorage
      this.addNotificationToUserNotifications(notification);
    },

    // This method sends the notification to a specific user
    markOrderAsDone() {
      if (!this.orderCompleted) {
        this.orderCompleted = true;  // Set order to completed
        this.orderCompletedMessage = "Your Order Has Completed Ready To Pickup!";
        
        const orderDetails = this.orderItems.map(item => `${item.name} x${item.quantity}`).join(", ");
        const total = this.orderItems.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);
        
        // Constructing the notification message with highlighted details
        const message = `Your order is ready! Proceed to the cashier for payment and pickup. <span class="highlighted-order-details">Order details: ${orderDetails}. Total: ₱${total}</span>`;
        
        const notification = {
          orderId: this.orderID,
          customerName: this.customerName, // Attach the customer name
          message: message, // Highlighted message
          timestamp: new Date().toISOString(),
        };

        // Add the notification to localStorage under the specific user's notifications
        this.addNotificationToUserNotifications(notification);
      }
    },

    // Add the notification to localStorage, ensuring it's saved per user
    addNotificationToUserNotifications(notification) {
      const userNotificationsKey = `user_notifications_${this.customerName}`; // Use the customerName
      let notifications = JSON.parse(localStorage.getItem(userNotificationsKey)) || [];
      
      // Check if a notification for this order ID with the same message already exists
      const existingNotificationIndex = notifications.findIndex(
        n => n.orderId === notification.orderId && n.message === notification.message
      );
      
      // Only add the notification if it doesn't already exist
      if (existingNotificationIndex === -1) {
        notifications.push(notification);
        localStorage.setItem(userNotificationsKey, JSON.stringify(notifications));
      }
    },

    goBackToDashboard() {
      this.$router.push({ name: "Dashboard" });
    },

    clearNotification() {
      this.orderCompletedMessage = ""; // Clear the message
    }
  }
};
</script>


<style scoped>

/* Styling for the horizontal line between date and order ID */
/* Styling for the horizontal broken line between date and order ID */
.order-line {
  width: 100%;
  border: none;
  border-top: 2px dashed #000000; /* Dashed green line */
  margin: 20px 0;
}
/* 🌙 Dark Mode - Order Confirmation Box */
.dark-mode .order-confirmation-box {
  background-color: #f0f0f0 !important; /* Light background for dark mode */
  color: black !important; /* Ensure text is dark */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important; /* Add shadow for better visibility */
}

/* Order Confirmation Box (Default Light Mode) */
.order-confirmation-box {
  background-color: #fce6e6; /* Light background for light mode */
  color: black; /* Ensure text is dark */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Light shadow */
}



/* Order Completion Notification */
.order-notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #4CAF50;
  color: white;
  padding: 15px 20px;
  border-radius: 5px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
  font-weight: bold;
  z-index: 1000;
}

.order-notification button {
  margin-left: 10px;
  background-color: white;
  color: #4CAF50;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 3px;
}

.order-notification button:hover {
  background-color: #f8f8f8;
}

/* 🌙 Dark Mode - Dark Outer Background */
.dark-mode .order-id-page {
  background-color: #222 !important;
  color: white !important;
}

/* 🌙 Dark Mode - Keep Order ID Box Light */
.dark-mode .order-id {
  background-color:rgb(197, 197, 197) !important;
  color: black !important;
  border: 1px solid #ccc !important;
}

/* 🌙 Dark Mode - Keep Order Details Box Light */
.dark-mode .order-details li {
 background-color:rgb(197, 197, 197) !important;
  color: black !important;
  border: 1px solid #ccc !important;
}

.dark-mode h1,
.dark-mode h3,
.dark-mode h4,
.dark-mode .order-details h3,
.dark-mode .order-id-page h1,
.dark-mode .order-id-page h3,
.dark-mode .order-id-page h4 {
  color: white !important;
}

/* 🌙 Dark Mode - Buttons */
.dark-mode .back-button {
  background-color: #444 !important;
  color: white !important;
  border: 1px solid #666 !important;
}

.dark-mode .back-button:hover {
  background-color: #666 !important;
}

/* 🌙 Dark Mode - Ensure Text Inside Boxes is Dark */
.dark-mode .order-id h2,
.dark-mode .order-details h3,
.dark-mode .order-details span {
  color: black !important;
}

/* Order Confirmation Box */
.order-confirmation-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #fce6e6;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 80%;
  max-width: 500px;
  margin: 0 auto;
  text-align: center;
}

.checkmark {
  font-size: 40px;
  color: #4CAF50;
}

h2 {
  margin: 10px 0;
  font-size: 24px;
}

.order-details {
  font-size: 18px;
  margin: 20px 0;
  text-align: left;
}

.order-details ul {
  list-style-type: none;
  padding: 0;
}

.order-details li {
  margin: 10px 0;
}

.back-button {
  padding: 12px 25px;
  font-size: 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  text-transform: uppercase;
  margin-top: 20px;
}

.back-button:hover {
  background-color: #45a049;
}

/* Order ID Page */
.order-id-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;
  max-height: 100vh;
  overflow-y: auto;
  text-align: center;
  padding: 30px;
  background-color: #fce6e6;
  border-radius: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
  box-sizing: border-box;
}

/* Order ID Display */
.order-id {
  font-size: 28px;
  font-weight: bold;
  margin: 20px 0;
  background: #ffe4ec;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.order-details {
  text-align: center;
  margin-bottom: 30px;
}

.order-details ul {
  list-style-type: none;
  padding: 0;
  font-size: 18px;
}

.order-details li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 12px 0;
  padding: 15px;
  background: #f8d2e4;
  border-radius: 10px;
  font-size: 18px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* New message */
.message {
  font-size: 20px;
  font-weight: bold;
  background: #ffebcd;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Glowing effect for the "Back to Dashboard" button */
.back-button {
  padding: 12px 25px;
  font-size: 16px;
  background-color: transparent;
  color: #FFF;
  border: none;
  cursor: pointer;
  position: relative;
  z-index: 0;
  border-radius: 20px;
  text-transform: uppercase;
}

.back-button::after {
  content: "";
  z-index: -1;
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #333;
  left: 0;
  top: 0;
  border-radius: 20px;
}

.back-button::before {
  content: "";
  background: linear-gradient(
    45deg,
    #FF0000, #FF7300, #FFFB00, #48FF00,
    #00FFD5, #002BFF, #FF00C8, #FF0000
  );
  position: absolute;
  top: -2px;
  left: -2px;
  background-size: 600%;
  z-index: -1;
  width: calc(100% + 4px);
  height: calc(100% + 4px);
  filter: blur(8px);
  animation: glowing 20s linear infinite;
  transition: opacity .3s ease-in-out;
  border-radius: 20px;
  opacity: 0;
}

.back-button:hover::before {
  opacity: 1;
}

.back-button:active:after {
  background: transparent;
}

.back-button:active {
  color: #000;
  font-weight: bold;
  background-color: #d12f7a;
  border-color: #d12f7a;
}

/* Glow Animation */
@keyframes glowing {
  0% {background-position: 0 0;}
  50% {background-position: 400% 0;}
  100% {background-position: 0 0;}
}

/* 📱 Mobile Responsive Adjustments */
@media (max-width: 768px) {
  .order-id {
    font-size: 22px;
    padding: 10px;
  }

  .order-details li {
    flex-direction: column;
    font-size: 16px;
    padding: 14px;
    text-align: center;
  }

  .message {
    font-size: 18px;
    padding: 10px;
  }

  button {
    font-size: 14px;
    padding: 12px;
  }
}

/* Extra Small Screens (iPhone SE, very small phones) */
@media (max-width: 480px) {
  .order-id {
    font-size: 20px;
    padding: 8px;
  }

  .order-details li {
    font-size: 14px;
    padding: 10px;
  }

  .message {
    font-size: 16px;
  }

  button {
    font-size: 13px;
    padding: 10px;
    width: 100%;
  }
}
</style>
