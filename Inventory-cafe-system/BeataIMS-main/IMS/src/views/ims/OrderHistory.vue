<template>
  <Header 
    :isSidebarCollapsed="isSidebarCollapsed" 
    @toggle-sidebar="handleSidebarToggle"
    v-model:searchQuery="searchQuery"
    @update:searchQuery="filterOrders"
  />
  <SideBar :isCollapsed="isSidebarCollapsed" />

  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <div class="header-title">
        <h1 class="sales-header">Order History</h1>
        <p class="sub-description">
          Review past orders including customer info, payment method, and order totals. Use filters to narrow down results.
        </p>
      </div>
      <div class="header-actions">
        <div class="filters-wrapper">
          <!-- Filter Dropdown -->
          <div class="filter-container">
            <div class="filter-label">Filter by</div>
            <button class="filter-btn" @click="toggleFilterDropdown">
              <span>{{ selectedStatus || 'Payment Method' }}</span>
              <i class="fas fa-angle-down"></i>
            </button>
            <div v-if="showFilterDropdown" class="filter-dropdown">
              <select v-model="selectedStatus" class="filter-select">
                <option value="">All Orders</option>
                <option value="Cash">Cash</option>
                <option value="Tally">Tally</option>
              </select>
              <div class="date-range">
                <div class="date-input">
                  <label for="start-date">FROM</label>
                  <input 
                    type="date"
                    v-model="startDate"
                    class="date-select"
                  />
                </div>
                <div class="date-input">
                  <label for="end-date">TO</label>
                  <input 
                    type="date"
                    v-model="endDate"
                    class="date-select"
                  />
                </div>
                <button class="apply-filter" @click="filterByDateRange">Apply Filter</button>
              </div>
            </div>
          </div>

          <!-- Order Logs Button Card -->
          <button class="btn-view-logs" @click="handleViewLogs">View Logs</button>
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

    <OrderLogsModal 
  v-if="showOrderLogs"
  :isVisible="showOrderLogs"
  :logs="logs"
  @close="showOrderLogs = false"
/>
  </div>
</template>


<script>
import axios from 'axios';
import SideBar from '@/components/ims/SideBar.vue';
import Header from '@/components/Header.vue';
import { ORDER_SUMMARY_API } from '@/api/config.js';
import OrderLogsModal from '@/components/ims/OrderLogsModal.vue';
import { useToast } from 'vue-toastification';

export default {
  components: {
    SideBar,
    Header,
    OrderLogsModal
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  data() {
    return {
      isSidebarCollapsed: false,
      showOrderLogs: false,
      logs: [],
      orders: [],
      selectedStatus: '',
      showFilterDropdown: false,
      searchQuery: '',
      loading: false,
      selectedDate: '',
      startDate: '',
      endDate: '',
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
    handleViewLogs() {
    this.fetchLogs();
    this.showOrderLogs = true;
  },
    filterOrders() {
      // When search query changes, the computed filteredOrders will be recalculated automatically
    },
    async fetchLogs() {
  try {
    const response = await axios.get(`${ORDER_SUMMARY_API}/orders/history-logs`);
    this.logs = response.data;
  } catch (error) {
    this.toast.error('Failed to load logs.');
  }
},
    async fetchOrders(date = '') {
    this.loading = true;
    try {
      const url = date
        ? `${ORDER_SUMMARY_API}/orders/history/date?order_date=${date}`
        : `${ORDER_SUMMARY_API}/orders/history`;

      const response = await axios.get(url);
      this.orders = response.data.map(order => ({
        history_id: order.history_id,
        customer_name: order.customer_name,
        total_items: order.total_items,
        total_amount: order.total_amount,
        payment_method: order.payment_method,
        created_at: order.created_at || 'N/A'
      }));

      if (this.orders.length === 0) {
        this.toast.info("No orders found for the selected date");
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
      this.toast.error('Failed to load order history. Please try again.');
    } finally {
      this.loading = false;
    }
  },

  async filterByDateRange() {
    if (!this.startDate && !this.endDate) {
      await this.fetchOrders();
      return;
    }

    this.loading = true;
    try {
      let url = `${ORDER_SUMMARY_API}/orders/history/date?`;
      const params = [];
      
      if (this.startDate) {
        params.push(`start_date=${this.startDate}`);
      }
      if (this.endDate) {
        params.push(`end_date=${this.endDate}`);
      }
      
      url += params.join('&');
      const response = await axios.get(url);
      
      this.orders = response.data.map(order => ({
        history_id: order.history_id,
        customer_name: order.customer_name,
        total_items: order.total_items,
        total_amount: order.total_amount,
        payment_method: order.payment_method,
        created_at: order.created_at || 'N/A'
      }));

      if (this.orders.length === 0) {
        this.toast.info("No orders found for the selected date range");
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
.header-title {
  display: flex;
  flex-direction: column;
}
.sales-header {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}
.sub-description {
  font-size: 14px;
  color: #666;
  margin-top: -10px;
  margin-bottom: 15px;
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
  color: #343a40;
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

.filter-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.filter-btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  min-width: 150px;
  justify-content: space-between;
}

.filter-btn:hover {
  border-color: #E54F70;
  color: #E54F70;
}

.filter-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 10px;
  z-index: 1000;
  margin-top: 5px;
  min-width: 200px;
}

.filter-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  outline: none;
  transition: all 0.3s;
}

.date-select {
  margin-top: 8px;
  cursor: pointer;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  outline: none;
  transition: all 0.3s;
}

.filter-select:hover,
.date-select:hover {
  border-color: #E54F70;
}

.filter-select:focus,
.date-select:focus {
  border-color: #E54F70;
  box-shadow: 0 0 0 2px rgba(229, 79, 112, 0.1);
}

.dropdown {
  display: none; /* Remove old dropdown styles */
}

.totals-container {
  display: flex;
  justify-content: space-between;
  padding: 18px 25px;
  background-color: #f8f9fa;
  margin-top: auto; 
  border-bottom-right-radius: 15px;
  border-bottom-left-radius: 15px;
  position: sticky;
  bottom: 0;
  box-shadow: 0 -3px 10px rgba(0, 0, 0, 0.05);
  border-top: 1px solid #e9ecef;
}

.totals-item {
  width: 30%;
  font-weight: 600;
  color: #343a40;
  font-size: 15px;
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
.date-range {
  display: flex;
  flex-direction: column;
  margin-top: 8px;
}
.date-input {
  display: flex;
  flex-direction: column;
}

.date-input label {
  font-size: 0.8rem;
}
.apply-filter {
  background-color: #E54F70;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.apply-filter:hover {
  background-color: #d33d5e;
}
.filters-wrapper {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  align-items: center;
}



.btn-view-logs {
  padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    color: #333;
    transition: all 0.3s;
    display: flex
;
    align-items: center;

    gap: 8px;
    background: white;
    justify-content: space-between;
}

.btn-view-logs:hover {
  border-color: #E54F70;
  color: #E54F70;
}
</style>