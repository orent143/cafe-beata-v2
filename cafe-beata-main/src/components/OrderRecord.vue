<template>
  <div class="order-record">
    <div class="header">
      <button @click="goBack" class="back-button">← Back to Notifications</button>
    </div>
    
    <div :class="{ 'dark-mode': isDarkMode }">
      <h1>Order Record</h1>
    </div>

    <!-- Calendar Section -->
    <div class="calendar-section">
      <h2>Sales by Date</h2>
      <div class="calendar-container">
        <div class="date-field">
          <div class="date-input-wrapper">
            <input 
              type="text"
              v-model="manualDateInput"
              @input="handleManualDateInput"
              @focus="handleInputFocus"
              placeholder="MM-DD-YYYY"
              class="date-input"
              ref="dateInput"
            >
            <div class="calendar-icon" @click="openCalendarPicker">
              <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2Ij48cGF0aCBmaWxsPSIjNjY2IiBkPSJNNSAyVjFoMnYxaDJ2MEg1ek0xMyAzdjEwSDNWM2gxMHpNMyAyYTEgMSAwIDAwLTEgMXYxMGExIDEgMCAwMDEgMWgxMGExIDEgMCAwMDEtMVYzYTEgMSAwIDAwLTEtMWgtMVYxYTEgMSAwIDAwLTEtMUg1YTEgMSAwIDAwLTEgMXYxSDNhMSAxIDAgMDAtMSAxeiIvPjwvc3ZnPg==" alt="calendar" />
            </div>
            <input 
              type="date" 
              :value="formatDateForInput(selectedDate)"
              @input="handleDateChange"
              class="calendar-picker"
              ref="calendarPicker"
            >
          </div>
        </div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="search-container">
      <input
        v-model="searchQuery"
        @input="filterOrders"
        type="text"
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
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in filteredOrders" :key="order.id">
          <td>{{ order.id }}</td>
          <td v-html="formatDate(order.created_at)"></td>
          <td>{{ order.customer_name }}</td>
          <td>
            <button @click="viewOrderDetails(order)" class="view-details-btn">View Details</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- No Orders Message -->
    <div v-else>
      <p>No matching orders found.</p>
    </div>

    <!-- Sales Modal -->
    <div class="modal" v-if="showSalesModal">
      <div class="modal-content">
        <span class="close" @click="showSalesModal = false">&times;</span>
        <h2>Sales Summary for {{ formatDateForDisplay(selectedDate) }}</h2>
        <div class="sales-info">
          <div class="sales-card">
            <h3>Total Sales</h3>
            <p class="sales-amount">₱{{ dailySales.total.toFixed(2) }}</p>
          </div>
          <div class="sales-card">
            <h3>Orders Completed</h3>
            <p class="sales-count">{{ dailySales.orderCount }}</p>
          </div>
        </div>
        
        <div class="sales-details" v-if="dailySales.orderCount > 0">
          <h3>Order Details</h3>
          <table class="sales-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Items</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in dailySales.orders" :key="order.id">
                <td>{{ order.id }}</td>
                <td>{{ order.customer_name }}</td>
                <td>{{ formatItems(order.items) }}</td>
                <td>₱{{ calculateTotal(order.items).substring(1) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="no-sales" v-else>
          <p>No sales recorded for this date.</p>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <div class="modal" v-if="showOrderDetailsModal">
      <div class="modal-content order-details-modal">
        <span class="close" @click="showOrderDetailsModal = false">&times;</span>
        <h2>Order Details</h2>
        
        <div class="order-info" v-if="selectedOrder">
          <div class="order-header">
            <div class="order-header-item">
              <span class="label">Order ID:</span>
              <span class="value">{{ selectedOrder.id }}</span>
            </div>
            <div class="order-header-item">
              <span class="label">Customer:</span>
              <span class="value">{{ selectedOrder.customer_name }}</span>
            </div>
            <div class="order-header-item">
              <span class="label">Date:</span>
              <span class="value" v-html="formatDate(selectedOrder.created_at)"></span>
            </div>
          </div>
          
          <div class="order-items-list">
            <h3>Items</h3>
            <table class="items-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in selectedOrder.items" :key="index">
                  <td>{{ item.name }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>₱{{ item.price.toFixed(2) }}</td>
                  <td>₱{{ (item.price * item.quantity).toFixed(2) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="3" class="total-label">Total</td>
                  <td class="total-value">{{ calculateTotal(selectedOrder.items) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  components: {
  },
  data() {
    return {
      isDarkMode: localStorage.getItem('darkMode') === 'true',
      orders: [],
      filteredOrders: [], // This will store filtered results
      searchQuery: "", // Search input field
      selectedDate: new Date(), // Default to today
      manualDateInput: "", // For manual date input
      showSalesModal: false,
      dailySales: {
        total: 0,
        orderCount: 0,
        orders: []
      },
      showOrderDetailsModal: false,
      selectedOrder: null
    };
  },
  methods: {
    goBack() {
      this.$router.push({ name: "Notifications" });
    },

    fetchOrders() {
      fetch("http://127.0.0.1:8000/orders?status=completed") // Fetch only completed orders
        .then(response => response.json())
        .then(data => {
          console.log("Fetched orders:", data); // Debugging
          if (data.orders) {
            // Sort orders by date (newest to oldest) before assigning
            const sortedOrders = data.orders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            this.orders = sortedOrders;
            this.filteredOrders = sortedOrders;
          } else {
            this.orders = [];
            this.filteredOrders = [];
            console.error("No orders found.");
          }
        })
        .catch(error => console.error("Error fetching orders:", error));
    },

    filterOrders() {
      if (this.searchQuery === '') {
        this.filteredOrders = this.orders;
        return;
      }

      const query = this.searchQuery.trim();
      
      // Check if the search query matches the date format MM-DD-YYYY
      const isDateSearch = /^\d{2}-\d{2}-\d{4}$/.test(query);

      this.filteredOrders = this.orders.filter(order => {
        // For date search
        if (isDateSearch) {
          const orderDate = this.formatDateMMDDYYYY(new Date(order.created_at));
          return orderDate === query;
        }

        // For Order ID search (exact match)
        if (!isNaN(query)) {
          return order.id.toString() === query;
        }

        // For customer name search (exact match)
        return order.customer_name === query;
      });

      // If no exact matches found and it's not a date search, try partial matches for names only
      if (this.filteredOrders.length === 0 && !isDateSearch && isNaN(query)) {
        this.filteredOrders = this.orders.filter(order => {
          return order.customer_name.toLowerCase().includes(query.toLowerCase());
        });
      }

      // Sort results
      this.filteredOrders.sort((a, b) => {
        // If searching by ID, prioritize exact matches
        if (!isNaN(query)) {
          const aExact = a.id.toString() === query;
          const bExact = b.id.toString() === query;
          if (aExact && !bExact) return -1;
          if (!aExact && bExact) return 1;
        }
        
        // Default sort by date (newest first)
        return new Date(b.created_at) - new Date(a.created_at);
      });
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

    formatDateForDisplay(date) {
      if (!date) return '';
      
      // Format date as MM-DD-YYYY
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const year = date.getFullYear();
      
      return `${month}-${day}-${year}`;
    },

    formatDateForInput(date) {
      if (!date) return '';
      const d = new Date(date);
      return d.toISOString().split('T')[0];
    },

    formatItems(items) {
      if (!Array.isArray(items)) {
        console.error("Invalid item format:", items);
        return "Invalid item data";
      }
      return items.map((item) => `${item.name} x${item.quantity}`).join(", ");
    },

    calculateTotal(items) {
      if (!Array.isArray(items)) return "₱0";
      return "₱" + items.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2);
    },

    handleInputFocus(event) {
      // If user clicks directly on the text input, don't show the calendar
      event.preventDefault();
      event.stopPropagation();
    },

    openCalendarPicker() {
      this.$refs.calendarPicker.showPicker();
    },
    
    handleDateChange(event) {
      const date = new Date(event.target.value);
      if (!isNaN(date.getTime())) {  // Check if date is valid
        this.selectedDate = date;
        this.manualDateInput = this.formatDateForManualInput(date);
        this.updateSalesData();
      }
    },
    
    fetchSalesForDate() {
      const startOfDay = new Date(this.selectedDate);
      startOfDay.setHours(0, 0, 0, 0);
      
      const endOfDay = new Date(this.selectedDate);
      endOfDay.setHours(23, 59, 59, 999);
      
      // Filter completed orders for the selected date
      const ordersForDate = this.orders.filter(order => {
        const orderDate = new Date(order.created_at);
        return orderDate >= startOfDay && orderDate <= endOfDay;
      });
      
      // Calculate total sales
      let total = 0;
      ordersForDate.forEach(order => {
        const orderTotal = parseFloat(this.calculateTotal(order.items).substring(1));
        total += orderTotal;
      });
      
      // Update dailySales object
      this.dailySales = {
        total: total,
        orderCount: ordersForDate.length,
        orders: ordersForDate
      };
      
      this.showSalesModal = true;
    },
    
    formatDateYYYYMMDD(date) {
      const d = new Date(date);
      return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
    },
    
    formatDateMMDDYYYY(date) {
      const d = new Date(date);
      const month = (d.getMonth() + 1).toString().padStart(2, '0');
      const day = d.getDate().toString().padStart(2, '0');
      const year = d.getFullYear();
      return `${month}-${day}-${year}`;
    },

    // New method to view order details
    viewOrderDetails(order) {
      this.selectedOrder = order;
      this.showOrderDetailsModal = true;
    },

    // Format date for manual input display
    formatDateForManualInput(date) {
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      const year = date.getFullYear();
      return `${month}-${day}-${year}`;
    },

    // Handle manual date input
    handleManualDateInput(event) {
      const input = event.target.value;
      
      // Auto-format as user types
      let formatted = input.replace(/\D/g, ''); // Remove non-digits
      if (formatted.length >= 2) {
        formatted = formatted.slice(0, 2) + (formatted.length > 2 ? '-' : '') + formatted.slice(2);
      }
      if (formatted.length >= 5) {
        formatted = formatted.slice(0, 5) + (formatted.length > 5 ? '-' : '') + formatted.slice(5);
      }
      if (formatted.length > 10) {
        formatted = formatted.slice(0, 10);
      }
      
      this.manualDateInput = formatted;

      // Only process if we have a complete date
      if (formatted.length === 10) {
        const [month, day, year] = formatted.split('-').map(num => parseInt(num, 10));
        const date = new Date(year, month - 1, day);
        
        // Validate date
        if (
          date.getFullYear() === year &&
          date.getMonth() === month - 1 &&
          date.getDate() === day &&
          year >= 1900 && 
          year <= 2100
        ) {
          this.selectedDate = date;
          this.updateSalesData();
        }
      }
    },

    // Initialize manual date input
    initializeManualDateInput() {
      this.manualDateInput = this.formatDateForManualInput(this.selectedDate);
    },

    updateSalesData() {
      this.fetchSalesForDate();
    }
  },
  mounted() {
    this.fetchOrders();
    this.initializeManualDateInput();
  },
  watch: {
    isDarkMode(newValue) {
      document.body.classList.toggle('dark-mode', newValue);
    },
  },
};
</script>




<style scoped>
.order-record {
  padding: 20px;
}

h1 {
  color: #d12f7a;
  font-size: 28px;
  margin-bottom: 20px;
}

h2 {
  color: #d12f7a;
  font-size: 22px;
  margin-bottom: 15px;
}

.search-container {
  margin-bottom: 15px;
  text-align: center;
}

.search-bar {
  width: 50%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #d12f7a;
  border-radius: 5px;
  outline: none;
}

.order-table {
  width: 100%;
  border-collapse: collapse;
}

.order-table th,
.order-table td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: center;
}

.order-table th {
  background-color: #f8d2e4;
  color: #d12f7a;
}

.back-button {
  background-color: #f8d2e4;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
}

.back-button:hover {
  background-color: #d12f7a;
}

.dark-mode {
  background-color: #2d2d2d;
  color: #fff;
}

/* Calendar Section Styles */
.calendar-section {
  margin: 20px auto;
  max-width: 600px;
  padding: 20px;
}

.calendar-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.date-field {
  display: flex;
  gap: 10px;
  align-items: center;
}

.date-input-wrapper {
  position: relative;
  width: 200px;
  display: flex;
  align-items: center;
}

.date-input {
  width: 100%;
  padding: 8px 12px;
  padding-right: 40px;
  border: 2px solid #d12f7a;
  border-radius: 5px;
  font-size: 16px;
  color: #333;
  background: white;
  transition: all 0.3s ease;
}

.date-input:focus {
  outline: none;
  border-color: #b82d67;
  box-shadow: 0 0 5px rgba(209, 47, 122, 0.3);
}

.calendar-icon {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  z-index: 2;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.calendar-icon:hover {
  background-color: rgba(209, 47, 122, 0.1);
}

.calendar-icon img {
  width: 16px;
  height: 16px;
  opacity: 0.6;
  transition: opacity 0.3s ease;
  padding: 2px;
}

.calendar-icon:hover img {
  opacity: 1;
}

.calendar-picker {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  pointer-events: none;
}

.calendar-picker::-webkit-calendar-picker-indicator {
  display: none;
}

/* Dark mode adjustments */
.dark-mode .date-input {
  background: #2c2c2c;
  color: #fff;
  border-color: #d12f7a;
}

.dark-mode .calendar-icon img {
  filter: invert(1);
  opacity: 0.8;
}

.dark-mode .calendar-icon:hover img {
  opacity: 1;
}

/* Media Queries */
@media (max-width: 480px) {
  .date-field {
    flex-direction: column;
    width: 100%;
  }

  .manual-date-input,
  .date-input {
    width: 100%;
  }

  .manual-date-input-wrapper,
  .date-input-wrapper {
    width: 100%;
  }
}

/* Modal Styles */
.modal {
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background-color: #fefefe;
  margin: auto;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}

.close:hover,
.close:focus {
  color: #d12f7a;
  text-decoration: none;
}

/* Sales Info Styles */
.sales-info {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
}

.sales-card {
  background-color: #f8f8f8;
  border-radius: 8px;
  padding: 15px;
  width: 45%;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.sales-amount {
  font-size: 28px;
  font-weight: bold;
  color: #d12f7a;
  margin: 10px 0;
}

.sales-count {
  font-size: 28px;
  font-weight: bold;
  color: #5a67d8;
  margin: 10px 0;
}

.sales-details {
  margin-top: 20px;
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.sales-table th,
.sales-table td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: left;
}

.sales-table th {
  background-color: #f8d2e4;
  color: #d12f7a;
}

.no-sales {
  text-align: center;
  padding: 20px;
  color: #666;
}

/* Dark mode adjustments for new elements */
.dark-mode .calendar-section {
  background-color: #3d3d3d;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.dark-mode .modal-content {
  background-color: #2d2d2d;
  color: #fff;
}

.dark-mode .sales-card {
  background-color: #3d3d3d;
}

.dark-mode .close {
  color: #ddd;
}

.dark-mode .close:hover,
.dark-mode .close:focus {
  color: #f8d2e4;
}

.dark-mode .sales-table th {
  background-color: #444;
}

.dark-mode .sales-table td {
  border-color: #444;
}

.dark-mode .no-sales {
  color: #bbb;
}

.dark-mode .date-input {
  background-color: #2d2d2d;
  border-color: #444;
  color: #fff;
}

.dark-mode .calendar-icon img {
  filter: invert(1);
}

/* View Details Button Styles */
.view-details-btn {
  background-color: #d12f7a;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.view-details-btn:hover {
  background-color: #a82563;
}

/* Order Details Modal Styles */
.order-details-modal {
  max-width: 600px;
}

.order-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 5px;
}

.order-header-item {
  margin: 5px 10px;
}

.label {
  font-weight: bold;
  color: #666;
  margin-right: 5px;
}

.value {
  color: #d12f7a;
}

.order-items-list {
  margin-top: 20px;
}

.items-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.items-table th,
.items-table td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: left;
}

.items-table th {
  background-color: #f8d2e4;
  color: #d12f7a;
}

.total-label {
  text-align: right;
  font-weight: bold;
}

.total-value {
  font-weight: bold;
  color: #d12f7a;
}

/* Dark mode adjustments for order details */
.dark-mode .order-header {
  background-color: #3d3d3d;
}

.dark-mode .label {
  color: #bbb;
}

.dark-mode .value {
  color: #f8d2e4;
}

.dark-mode .items-table th {
  background-color: #444;
}

.dark-mode .items-table td {
  border-color: #444;
}

.dark-mode .total-value {
  color: #f8d2e4;
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
}
</style>
