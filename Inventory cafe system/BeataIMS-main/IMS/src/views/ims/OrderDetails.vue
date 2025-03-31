<template>
    <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />
    <SideBar :isCollapsed="isSidebarCollapsed" />
  
    <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="order-details">
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else class="order-container">
          
          <!-- Order Summary Section -->
          <div class="summary-section">
            <h2>Order Summary</h2>
            <div class="summary-details">
              <div class="detail-row">
                <span>Order ID:</span>
                <span>#{{ order.history_id }}</span>
              </div>
              <div class="detail-row">
                <span>Customer Name:</span>
                <span>{{ order.customer_name }}</span>
              </div>
              <div class="detail-row">
                <span>Date:</span>
                <span>{{ formatDate(order.created_at) }}</span> 
              </div>
              <div class="detail-row">
                <span>Payment Method:</span>
                <span>{{ order.payment_method }}</span>
              </div>
              <div class="detail-row">
                <span>Total Items:</span>
                <span>{{ order.total_items }}</span>
              </div>
              <div class="detail-row">
                <span>Total Amount:</span>
                <span>₱{{ formatPrice(order.total_amount) }}</span>
              </div>
            </div>
          </div>
  
          <!-- Order Items Section -->
          <div class="items-section">
            <h2>Order Items</h2>
            <table>
              <thead>
                <tr>
                  <th>Product ID</th>
                  <th>Name</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in order.items" :key="item.product_id">
                  <td>{{ item.product_id }}</td>
                  <td>{{ item.product_name }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>₱{{ formatPrice(item.price) }}</td>
                  <td>₱{{ formatPrice(item.quantity * item.price) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
  
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import Header from '@/components/Header.vue'    
  import SideBar from '@/components/ims/SideBar.vue'
  import { ORDER_SUMMARY_API } from '@/api/config.js'
  import { useToast } from 'vue-toastification'
  
  export default {
    components: {
      SideBar,
      Header,
    },
    setup() {
      const toast = useToast();
      return { toast };
    },
    name: 'OrderDetails',
    data() {
      return {
        isSidebarCollapsed: false,
        order: null,
        loading: true,
        error: null
      }
    },
    async created() {
      try {
        const historyId = this.$route.params.id;
        const response = await axios.get(`${ORDER_SUMMARY_API}/orders/history/${historyId}`);
        this.order = response.data;
        this.loading = false;
      } catch (err) {
        this.error = 'Error loading order details';
        this.loading = false;
        console.error('Error:', err);
        this.toast.error('Failed to load order details. Please try again.');
      }
    },
    methods: {
      handleSidebarToggle(collapsed) {
        this.isSidebarCollapsed = collapsed;
      },
      formatDate(date) {
        if (!date) return "N/A";
        const options = { year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit" };
        return new Date(date).toLocaleDateString("en-US", options);
      },
      formatPrice(value) {
        return value ? Number(value).toFixed(2) : "0.00";
      },
      
    }
  }
  </script>
  

<style scoped>

.order-details {
    padding: 20px;
    max-width: 1000px;
    margin: 0 auto;
}

.loading, .error {
    text-align: center;
    padding: 20px;
}

.error {
    color: red;
}

.order-container {
    display: grid;
    gap: 20px;
}
.items-section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    max-height: 400px; /* Adjust height as needed */
    overflow-y: auto; /* Enables vertical scrolling */
    overflow-x: hidden; /* Prevents horizontal overflow */
}
.summary-section, .items-section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.summary-details {
    display: grid;
    gap: 10px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid #eee;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background-color: #f8f9fa;
    font-weight: 600;
}

h2 {
    margin-bottom: 20px;
    color: #333;
}
</style>