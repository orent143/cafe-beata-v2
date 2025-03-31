<template>
  <div class="order-history">
    <div class="header">
      <button @click="goToOrderHistory" class="back-button">← Back To Menu</button>
    </div>
    <div :class="{ 'dark-mode': isDarkMode }">
      <h1>Order History</h1>

      <!-- Search Bar -->
      <input 
        type="text" 
        v-model="searchQuery" 
        @input="filterOrders" 
        placeholder="Search by Order ID, Order Date, or Bill Name" 
        class="search-bar"
      />
    </div>

    <!-- Display Orders only when orders array is available -->
    <table class="order-table" v-if="filteredOrders.length">
      <thead>
        <tr>
          <th>Order No. (ID)</th>
          <th>Order Date</th>
          <th>Bill Name</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in filteredOrders" :key="order.id">
          <td>{{ order.id }}</td>
          <td v-html="formatDate(order.created_at)"></td>
          <td>{{ order.customer_name }}</td>
          
          <td>
            <button @click="viewOrderDetails(order)" class="view-details-button">View Details</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- No Orders Message -->
    <div v-else>
      <p>No orders found. Add some orders from the dashboard.</p>
    </div>
  </div>
</template>


<script>
export default {
  data() {
    return {
      isDarkMode: localStorage.getItem('darkMode') === 'true', // Detects dark mode
      orders: [], // Store the fetched orders
      searchQuery: '', // Store search query input
      filteredOrders: [], // Store filtered orders based on search
    };
  },
  methods: {
    goToOrderHistory() {
      this.$router.push({ name: 'Dashboard' });
    },

    fetchOrders() {
      const userName = localStorage.getItem('userName'); 

      if (!userName) {
        console.error("User name not found in localStorage.");
        return;
      }

      fetch(`http://127.0.0.1:8000/orders?customer_name=${userName}&status=completed`) // Fetch completed orders
        .then(response => response.json())
        .then(data => {
          if (data.orders) {
            // Sort orders by created_at date in descending order (newest first)
            this.orders = data.orders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            this.filteredOrders = this.orders; // Initially set filteredOrders to all orders
          } else {
            this.orders = [];
            this.filteredOrders = [];
            console.error("No completed orders found for this user.");
          }
        })
        .catch(error => console.error("Error fetching orders:", error));
    },

    filterOrders() {
      if (this.searchQuery === '') {
        this.filteredOrders = this.orders;
      } else {
        const query = this.searchQuery.toLowerCase();
        this.filteredOrders = this.orders.filter(order => {
          return (
            order.id.toString().includes(query) || 
            order.customer_name.toLowerCase().includes(query) ||
            order.created_at.toLowerCase().includes(query)
          );
        }).sort((a, b) => {
          // Prioritize orders that start with the search query
          const aStartsWith = a.id.toString().startsWith(query) ? 1 : 0;
          const bStartsWith = b.id.toString().startsWith(query) ? 1 : 0;
          const aIncludes = a.id.toString().includes(query) ? 1 : 0;
          const bIncludes = b.id.toString().includes(query) ? 1 : 0;
          return (bStartsWith - aStartsWith) || (bIncludes - aIncludes) || (a.id - b.id);
        });
      }
    },

    // Method to format the order date
    formatDate(dateString) {
      const date = new Date(dateString);
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const year = date.getFullYear();
      const hours = date.getHours();
      const minutes = date.getMinutes().toString().padStart(2, '0');
      const period = hours >= 12 ? 'PM' : 'AM';
      const hour12 = (hours % 12 || 12).toString().padStart(2, '0');
      
      // Format date and time separately
      const datePart = `${month}-${day}-${year}`;
      const timePart = `${hour12}:${minutes} ${period}`;
      
      return `${datePart} <span class="highlighted-time">${timePart}</span>`;
    },

    viewOrderDetails(order) {
      // Ensure each item has its image path preserved
      const itemsWithImages = order.items.map(item => {
        let imagePath = item.image;
        
        // If the item has an image from the backend
        if (imagePath) {
          // If it's already a full URL
          if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
            // Keep the URL as is
          }
          // If it's a backend upload path (starting with /uploads)
          else if (imagePath.startsWith('/uploads/')) {
            imagePath = `http://localhost:8000${imagePath}`;
          }
          // If it's just a filename, assume it's in uploads/avatars
          else if (!imagePath.includes('/')) {
            imagePath = `http://localhost:8000/uploads/avatars/${imagePath}`;
          }
        }

        return {
          ...item,
          image: imagePath // Keep the image path as is, don't set to null
        };
      });

      this.$router.push({
        name: "OrderDetails",
        query: {
          orderId: order.id,
          customerName: order.customer_name,
          items: JSON.stringify(itemsWithImages)
        },
      });
    },
  },
  mounted() {
    this.fetchOrders(); // Fetch orders when the component is mounted
  },
  watch: {
    isDarkMode(newValue) {
      document.body.classList.toggle('dark-mode', newValue);
    },
  },
};
</script>



<style scoped>

.search-bar {
  margin: 20px 0;
  padding: 10px;
  font-size: 16px;
  border-radius: 10px;
  border: 1px solid #ddd;
  width: 90%;
  max-width: 400px;
  display: block;
}



/* Light mode styles */
.order-history {
  padding: 20px;
  font-family: Arial, sans-serif;
  background-color: #fce6e6; /* Light pink background */
  color: #222; /* Dark text for light background */
  height: 110vh; /* Auto height to fit the content */
  max-height: 95vh; /* Maximum height to avoid overflowing */
  overflow-y: auto; /* Enable scrolling if content exceeds the height */
  transition: height 0.3s ease;  /* Smooth transition when height changes */
  
}

.order-table th {
  background-color: #ffffff; /* White background for table headers */
  color: #333; /* Dark text for better visibility */
  border-color: #ddd; /* Light border */
}

.order-table td {
  background-color: #ffffff; /* White background for table data */
  color: #333; /* Dark text */
  border-color: #ddd; /* Light border */
}

.order-table td button {
  background-color: rgb(31, 28, 29); /* Button color */
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.order-table td button:hover {
  background-color: #b82d67; /* Hover color */
}

/* Dark mode styles (still included for the future or switch) */
.dark-mode .order-table td {
  color: #fff; /* White text for better visibility */
  background-color: #333; /* Dark background for table data */
  border-color: #444; /* Darker borders */
}

.dark-mode .order-table th {
  background-color: #222; /* Dark background for header */
  color: #fff; /* White text for visibility */
  border-color: #444; /* Darker borders */
}

.dark-mode .order-history {
  color: #ccc; /* Lighter text color for better contrast */
  background-color: #1d1d1d; /* Dark background */
}

.dark-mode h1,
.dark-mode .order-table th,
.dark-mode .order-table td {
  color: #fff; /* White text for dark mode */
}

/* Glowing effect for the "Back To Menu" button */
.back-button {
  padding: 10px 20px;
  font-size: 14px;
  background-color: transparent;
  color: #FFF;
  cursor: pointer;
  border-radius: 5px;
  text-transform: uppercase;
  position: relative;
  z-index: 0;
  border: none;
}

.back-button::after {
  content: "";
  z-index: -1;
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #444; /* Darker background */
  left: 0;
  top: 0;
  border-radius: 10px;
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
  border-radius: 10px;
  opacity: 0;
}

/* Hover effect for glowing */
.back-button:hover::before {
  opacity: 1;
}

/* Active button state */
.back-button:active:after {
  background: transparent;
}

.back-button:active {
  color: #000;
  font-weight: bold;
  background-color: #d12f7a;
}

/* Glowing effect for the "View Details" button */
.view-details-button {
  padding: 10px 20px;
  font-size: 14px;
  background-color: transparent;
  color: #FFF;
  cursor: pointer;
  position: relative;
  z-index: 0;
  border-radius: 10px;
  text-transform: uppercase;
  border: none;
}

.view-details-button::after {
  content: "";
  z-index: -1;
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: #444; /* Darker background */
  left: 0;
  top: 0;
  border-radius: 10px;
}

.view-details-button::before {
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
  border-radius: 10px;
  opacity: 0;
}

/* Hover effect for glowing */
.view-details-button:hover::before {
  opacity: 1;
}

/* Active button state */
.view-details-button:active:after {
  background: transparent;
}

.view-details-button:active {
  color: #000;
  font-weight: bold;
  background-color: #d12f7a;
}

/* Glow Animation */
@keyframes glowing {
  0% {background-position: 0 0;}
  50% {background-position: 400% 0;}
  100% {background-position: 0 0;}
}

h1 {
  font-size: 28px;
  color: #333; /* Dark text for light mode */
}

.order-table {
  width: 100%;
  margin-top: 20px;
  border-collapse: collapse;
}

.order-table th, .order-table td {
  padding: 10px;
  border: 1px solid #ddd; /* Lighter border for light mode */
  text-align: center;
}

.order-table th {
  background-color: #f4f4f4; /* Light header background */
}

.order-table td button {
  background-color: rgb(31, 28, 29);
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.order-table td button:hover {
  background-color: #b82d67;
}

/* 📱 Mobile Responsive Adjustments */
@media (max-width: 768px) {
  .order-table th, .order-table td {
    padding: 8px;
    font-size: 14px;
  }

  .order-table td button {
    font-size: 12px;
  }
}

/* Add this at the end of your style section */
.highlighted-time {
  color: #d12f7a;
  font-weight: bold;
  background-color: #f8d2e4;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 4px;
}

.dark-mode .highlighted-time {
  color: #f8d2e4;
  background-color: #d12f7a;
}
</style>
