<template>
  <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />
  <SideBar :isCollapsed="isSidebarCollapsed" />

  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <h1 class="sales-header">Order History</h1>
      <div class="header-actions">
        <div class="filter-container">
          <button class="filter-btn" @click="toggleFilterDropdown">
            <i class="fas fa-filter"></i>
          </button>
          <div v-if="showFilterDropdown" class="dropdown">
            <select v-model="selectedStatus" class="filter-select">
              <option value="">All Orders</option>
              <option value="Cash">Cash</option>
              <option value="Tally">Tally</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="sales-container">
      <table class="sales-table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Customer</th>
            <th>Total Items</th>
            <th>Total Amount</th>
            <th>Payment Method</th>
            <th>Date</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in filteredOrders" :key="order.history_id">
            <td class="order-id">{{ order.history_id }}</td>
            <td>{{ order.customer_name }}</td>
            <td>{{ order.total_items }}</td>
            <td>₱{{ formatPrice(order.total_amount) }}</td>
            <td>
              <span :class="['payment-badge', order.payment_method.toLowerCase()]">
                {{ order.payment_method }}
              </span>
            </td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td>
              <button class="btn-details" @click="redirectToOrderDetails(order.history_id)">
                VIEW DETAILS
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="totals-container">
        <div class="totals-item">
          <span>Total Orders:</span>
          <span>{{ filteredOrders.length }}</span>
        </div>
        <div class="totals-item">
          <span>Total Sales:</span>
          <span>₱{{ formatPrice(totalSales) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import SideBar from '@/components/ims/SideBar.vue';
import Header from '@/components/Header.vue';
import { ORDER_SUMMARY_API } from '@/api/config.js';
import { useToast } from 'vue-toastification';

export default {
  components: {
    SideBar,
    Header
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  data() {
    return {
      isSidebarCollapsed: false,
      orders: [],
      selectedStatus: '',
      showFilterDropdown: false,
      searchQuery: '',
      loading: false
    };
  },
  computed: {
    filteredOrders() {
      let filtered = [...this.orders];

      if (this.selectedStatus) {
        filtered = filtered.filter(order => 
          order.payment_method === this.selectedStatus
        );
      }

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(order =>
          order.customer_name.toLowerCase().includes(query) ||
          order.history_id.toString().includes(query)
        );
      }

      return filtered;
    },
    totalSales() {
      return this.filteredOrders.reduce((sum, order) => 
        sum + parseFloat(order.total_amount), 0
      );
    }
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },

    async fetchOrders() {
      this.loading = true;
      try {
        const response = await axios.get(`${ORDER_SUMMARY_API}/orders/history`);
        this.orders = response.data.map(order => ({
          history_id: order.history_id,
          customer_name: order.customer_name,
          total_items: order.total_items,
          total_amount: order.total_amount,
          payment_method: order.payment_method,
          created_at: order.created_at || 'N/A'  // Handle null dates gracefully
        }));
        if (this.orders.length === 0) {
          this.toast.info("No orders found in history");
        }
      } catch (error) {
        console.error('Error fetching orders:', error);
        this.toast.error('Failed to load order history. Please try again.');
      } finally {
        this.loading = false;
      }
    },

    formatPrice(value) {
      return Number(value).toFixed(2);
    },

    formatDate(dateString) {
      if (!dateString || dateString === 'N/A') return 'N/A';
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    toggleFilterDropdown() {
      this.showFilterDropdown = !this.showFilterDropdown;
    },

    redirectToOrderDetails(historyId) {
      this.$router.push({
        path: `/vieworderdetails/${historyId}`
      });
    }
  },

  mounted() {
    this.fetchOrders();
  }
};
</script>


<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  margin-left: 230px;
  transition: all 0.3s ease;
  overflow: auto; /* <-- changed from overflow-y to allow both directions */
}

.app-container.sidebar-collapsed {
  margin-left: 70px;
  padding-left: 20px;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-left: 18px;
  width: 95%;
}

.sales-header {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}



.sales-container {
  position: relative;
    flex-grow: 1;
    height: 37dvw;
    background-color: #ffffff;
    border-radius: 15px;
    overflow-y: auto;
    margin-left: 5px;
    padding: 0;
}

.sales-table-container {
  overflow-y: auto;
  flex-grow: 1;
  max-height: calc(100vh - 150px);
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
}

.sales-table th, 
.sales-table td {
  padding: 15px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.sales-table th {
  background-color: #f4f4f4;
}
.payment-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.payment-badge.cash {
  background-color: #E8F5E9;
  color: #2E7D32;
}

.payment-badge.tally {
  background-color: #E3F2FD;
  color: #1565C0;
}

.filter-btn {
  padding: 8px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 19px;
  color: #333;
  transition: color 0.3s;
}

.filter-container {
  position: relative;
}

.dropdown {
  position: absolute;
  top: 35px;
  left: 0;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  padding: 10px;
  z-index: 10;
  width: 8dvw;
}

.filter-select {
  padding: 8px;
  font-size: 14px;
  border-radius: 5px;
  width: 100%;
  margin-bottom: 10px;
}

.totals-container {
  display: flex;
  justify-content: space-between;
  margin-top: auto;
  padding: 15px;
  background-color: #f4f4f4;
  border-bottom: 10px;
  font-size: 16px;
}

.totals-item {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 45%;
  margin-right: 15px;
}

.totals-item span {
  font-weight: bold;
  margin-right: 5px;
}

/* General Status Styles */
.status {
  padding: 4px 8px;
  border-radius: 15px;
  font-size: 12px;
  display: inline-block; /* Ensure it behaves like a block element */
}

/* Specific Status Styles */
.status-completed {
  background: #E8F5E9; /* Light green */
  color: #4CAF50; /* Dark green */
}

.status-pending {
  background: #FFF3E0; /* Light yellow */
  color: #FF9800; /* Dark yellow */
}

.status-cancelled {
  background: #F8D7DA; /* Light red */
  color: #721c24; /* Dark red */
}
ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

li {
  padding: 2px 0;
}
.selected {
  background-color: #e3f2fd;
}

tr {
  cursor: pointer;
}

input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.add-to-reports-btn {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 35px;
  height: 35px;
  background-color: #4CAF50;
  color: #0000009d;
  border: none;
  border-radius: 50%;
  font-size: 19px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.add-to-reports-btn:hover {
  background-color: #218838;
}
.order-id {
  font-family: monospace;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
.btn-details {
  background-color: transparent;
  color: #4CAF50;
  border: 1.5px solid #4CAF50;
  border-radius: 4px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
  margin-left: auto;
}

.btn-details:hover {
  background-color: #4CAF50;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-btn i {
  font-size: 14px;
}
</style>