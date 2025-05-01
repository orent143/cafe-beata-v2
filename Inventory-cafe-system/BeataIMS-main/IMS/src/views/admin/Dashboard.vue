<template>
  <!-- Import Header component -->
  <Header />
  <sidebar />
  <div class="app-container">
    <div class="dashboard-container">
      <div class="header-section">
          <h2 class="section-title">Dashboard</h2>         
        </div>
      <div class="main-container">
  
        <div class="dashboard-grid">
    <div class="card stats">
      <h3>Total Sales</h3>
      <div class="stat-value">${{ formatCurrency(dashboardStats.totalRevenue) }}</div>
      <div class="stat-change positive">Current Revenue</div>
    </div>

    <div class="card stats">
      <h3>Low Stock Items</h3>
      <div class="stat-value">{{ dashboardStats.totalLowStock }}</div>
      <div class="stat-change" :class="lowStockStatus.class">{{ lowStockStatus.text }}</div>
    </div>

    <div class="card stats">
      <h3>Out of Stock</h3>
      <div class="stat-value">{{ dashboardStats.totalOutOfStock }}</div>
      <div class="stat-change negative">{{ outOfStockStatus }}</div>
    </div>
  
          <div class="card stats">
            <h3>Active Staff</h3>
            <div class="stat-value">{{ activeUsers.length }}</div>
            <div class="stat-change" :class="activeUsersStatus.class">{{ activeUsersStatus.text }}</div>
          </div>
  
          <div class="card chart">
            <h3>Sales Overview</h3>
            <div class="chart-container">
              <canvas ref="salesChart"></canvas>
            </div>
          </div>
  
          
          <div class="card active-users">
            <h3>Active Users</h3>
            <div v-if="isLoadingUsers" class="loading-indicator">
              <i class="pi pi-spin pi-spinner"></i> Loading users...
            </div>
            <div v-else-if="userErrorMessage" class="error-message">
              {{ userErrorMessage }}
            </div>
            <table v-else>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>{{user.username}}</td>
                  <td>{{user.email}}</td>
                  <td>{{user.role}}</td>
                  <td><span :class="'status ' + (user.status ? user.status.toLowerCase() : 'active')">{{user.status || 'Active'}}</span></td>
                  <td>
                    <button class="action-btn" @click="viewUserDetails(user.id)">
                      <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn" @click="toggleUserStatus(user)">
                      <i :class="user.status === 'Inactive' ? 'fas fa-toggle-off' : 'fas fa-toggle-on'"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Database Maintenance section -->
    <div class="maintenance-section">
      <div class="card maintenance-card">
        <h3>Database Maintenance</h3>
        <p>Use these tools to fix and maintain the database.</p>
        
        <div class="maintenance-actions">
          <button class="maintenance-btn" @click="fixSalesRecords" :disabled="isFixingRecords">
            <i class="pi pi-refresh" :class="{'pi-spin': isFixingRecords}"></i>
            Fix Sales Records ({{ isFixingRecords ? 'Processing...' : 'Add Missing Product Names' }})
          </button>
          <button class="maintenance-btn" @click="syncUserData" :disabled="isSyncingUsers">
            <i class="pi pi-sync" :class="{'pi-spin': isSyncingUsers}"></i>
            Sync User Data ({{ isSyncingUsers ? 'Processing...' : 'Update User Info' }})
          </button>
          <div v-if="fixResult" class="fix-result" :class="{ 'success': fixResult.success }">
            {{ fixResult.message }}
          </div>
        </div>
      </div>
    </div>



    <!-- User Details Modal -->
    <div v-if="showUserModal" class="modal">
      <div class="modal-content">
        <span class="close-btn" @click="closeUserModal">&times;</span>
        <h2>User Details: {{selectedUser.username}}</h2>
        <div class="user-details">
          <div class="user-profile">
            <img :src="selectedUser.profile_pic || '/api/placeholder/150/150'" alt="Profile" class="profile-image">
          </div>
          <div class="user-info">
            <div class="detail-row">
              <span class="label">Email:</span>
              <span class="value">{{selectedUser.email}}</span>
            </div>
            <div class="detail-row">
              <span class="label">Role:</span>
              <span class="value">{{selectedUser.role}}</span>
            </div>
            <div class="detail-row">
              <span class="label">Status:</span>
              <span class="value status" :class="(selectedUser.status || 'active').toLowerCase()">
                {{selectedUser.status || 'Active'}}
              </span>
            </div>
            <div class="detail-row">
              <span class="label">Created:</span>
              <span class="value">{{formatDate(selectedUser.created_at)}}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script>
import sidebar from '@/components/admin/sidebar.vue';
import Header from '@/components/Header.vue';
import axios from 'axios';
import { SALES_API, INVENTORY_API } from '@/api/config.js';
import Chart from 'chart.js/auto';
import userService from '@/api/userService';

export default {
  name: 'Dashboard',
  components: {
    sidebar,
    Header
  },
  data() {
    return {
      // Dashboard metrics
      todaySales: '2,459',
      totalOrders: 147,
      lowStockItems: [
        { id: 1, name: 'Coffee Beans - Ethiopian', stock: 5 },
        { id: 2, name: 'Almond Milk', stock: 3 },
        { id: 3, name: 'Chocolate Syrup', stock: 2 }
      ],
      
      // Loading states & errors
      isLoadingOrders: true,
      isLoadingUsers: true,
      errorMessage: null,
      userErrorMessage: null,
      isFixingRecords: false,
      isSyncingUsers: false,
      fixResult: null,
      
      // Orders data
      recentOrders: [],
      
      dashboardStats: {
      totalLowStock: 0,
      totalOutOfStock: 0,
      totalRevenue: 0
    },
      // Users data
      users: [],
      isLoadingUsers: true,
    userErrorMessage: null,
    isFixingRecords: false,
    isSyncingUsers: false,
    fixResult: null,
      
      // Search functionality
      searchQuery: '',
      
      // Modals
      showOrderModal: false,
      selectedOrder: {},
      showUserModal: false,
      selectedUser: {},
      
      // Chart reference
      salesChart: null
    }
  },
  computed: {
    // Calculate active users
    activeUsers() {
      return this.users.filter(user => !user.status || user.status === 'Active');
    },
    outOfStockStatus() {
    const count = this.dashboardStats.totalOutOfStock;
    if (count > 0) {
      return `${count} items need attention`;
    }
    return 'All items in stock';
  },
    
    // Calculate status indicators
    lowStockStatus() {
      const count = this.lowStockItems.length;
      if (count > 10) {
        return { text: '+15.7%', class: 'negative' };
      } else if (count > 5) {
        return { text: '-2.4%', class: 'negative' };
      } else {
        return { text: '-25.3%', class: 'positive' };
      }
    },
    
    activeUsersStatus() {
      const count = this.activeUsers.length;
      const total = this.users.length;
      
      if (count === total) {
        return { text: '100%', class: 'positive' };
      } else if (count >= total * 0.8) {
        return { text: `${Math.round(count/total*100)}%`, class: 'positive' };
      } else {
        return { text: `${Math.round(count/total*100)}%`, class: 'neutral' };
      }
    },
    
    // Filtered data based on search query
    filteredOrders() {
      if (!this.searchQuery) return this.recentOrders;
      
      const query = this.searchQuery.toLowerCase();
      return this.recentOrders.filter(order => 
        order.id.toString().includes(query) ||
        order.customer.toLowerCase().includes(query) ||
        order.status.toLowerCase().includes(query)
      );
    },
    
    filteredUsers() {
      if (!this.searchQuery) return this.users;
      
      const query = this.searchQuery.toLowerCase();
      return this.users.filter(user => 
        user.username.toLowerCase().includes(query) ||
        (user.email && user.email.toLowerCase().includes(query)) ||
        user.role.toLowerCase().includes(query)
      );
    }
  },
  mounted() {
    // Fetch data when component mounts
    this.fetchUsers();
    this.initializeSalesChart();
    this.fetchDashboardStats(); // Add this line

  },
  methods: {
    // Fetch recent orders from API
    async fetchRecentOrders() {
  try {
    this.isLoadingOrders = true;
    
    // Use the correct API endpoint from config
    const response = await axios.get(`${SALES_API}/orders/recent`);
    
    if (response.data && Array.isArray(response.data.orders)) {
      this.recentOrders = response.data.orders.map(order => ({
        id: order.id,
        customer: order.customer_name,
        items: order.total_items,
        total: order.total_amount,
        status: order.status,
        date: new Date(order.created_at).toISOString().split('T')[0]
      }));
    } else {
      // Fallback to sample data if API response is not in expected format
      this.recentOrders = [
        { id: '1234', customer: 'John Doe', items: '3', total: '45.00', status: 'Completed', date: '2025-04-30' },
        { id: '1235', customer: 'Jane Smith', items: '2', total: '32.50', status: 'Pending', date: '2025-04-30' },
        { id: '1236', customer: 'Bob Wilson', items: '1', total: '18.00', status: 'Processing', date: '2025-04-29' }
      ];
    }
    
    this.errorMessage = null;
  } catch (error) {
    console.error('Error fetching recent orders:', error);
    this.errorMessage = 'Failed to load recent orders. Please try again later.';
    
    // Fallback data for development/error cases
    this.recentOrders = [
      { id: '1234', customer: 'John Doe', items: '3', total: '45.00', status: 'Completed', date: '2025-04-30' },
      { id: '1235', customer: 'Jane Smith', items: '2', total: '32.50', status: 'Pending', date: '2025-04-30' }
    ];
  } finally {
    this.isLoadingOrders = false;
  }
},
    
    // In the methods section:
    async fetchDashboardStats() {
  try {
    // Fetch low stock statistics using INVENTORY_API
    const lowStockResponse = await axios.get(`${INVENTORY_API}/low-stock-total`);
    if (lowStockResponse.data) {
      this.dashboardStats.totalLowStock = lowStockResponse.data.total_low_stock || 0;
      this.dashboardStats.totalOutOfStock = lowStockResponse.data.total_out_of_stock || 0;
    }

    // Fetch total sales revenue using SALES_API
    const revenueResponse = await axios.get(`${SALES_API}/total-sales-revenue`);
    if (revenueResponse.data) {
      // Note the correct field name from the API
      this.dashboardStats.totalRevenue = parseFloat(revenueResponse.data.total_sales_revenue || 0);
    }

    console.log('Dashboard stats loaded:', this.dashboardStats);

  } catch (error) {
    console.error('Error fetching dashboard statistics:', error);
    // Set fallback values
    this.dashboardStats.totalRevenue = 0;
    this.dashboardStats.totalLowStock = 0;
    this.dashboardStats.totalOutOfStock = 0;
  }
},

    // Fetch users from API
    async fetchUsers() {
  try {
    this.isLoadingUsers = true;
    this.userErrorMessage = null;

    // Call the userService to fetch users
    const response = await userService.getAllUsers();

    if (response && response.success && response.users) {
      // Transform the response data to match our component's needs
      this.users = response.users.map(user => ({
        id: user.id,
        username: user.username,
        email: user.email || `${user.username}@cafebeata.com`,
        role: user.role,
        status: user.status || 'Active',
        created_at: user.created_at,
        profile_pic: user.profile_pic
      }));

      console.log('Successfully fetched users:', this.users);
    } else {
      throw new Error('Invalid response format from server');
    }
  } catch (error) {
    console.error('Error fetching users:', error);
    this.userErrorMessage = 'Failed to load users. Please try again later.';
    
    if (process.env.NODE_ENV === 'development') {
      // Fallback data for development only
      this.users = [
        {
          id: 1,
          username: 'admin',
          email: 'admin@cafebeata.com',
          role: 'admin',
          status: 'Active',
          created_at: '2025-01-15'
        },
        {
          id: 2,
          username: 'staff',
          email: 'staff@cafebeata.com',
          role: 'cafe_staff',
          status: 'Active',
          created_at: '2025-02-20'
        }
      ];
    }
  } finally {
    this.isLoadingUsers = false;
  }
},
    
    // Initialize sales chart
    initializeSalesChart() {
      const ctx = this.$refs.salesChart.getContext('2d');
      
      const salesData = {
        labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        datasets: [{
          label: 'This Week',
          data: [1250, 1830, 1520, 2100, 2459, 1950, 1670],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true
        }, {
          label: 'Last Week',
          data: [1100, 1650, 1400, 1900, 2200, 1800, 1500],
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          tension: 0.4,
          fill: true
        }]
      };
      
      this.salesChart = new Chart(ctx, {
        type: 'line',
        data: salesData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '$' + value;
                }
              }
            }
          }
        }
      });
    },
    
    // Fix sales records
    async fixSalesRecords() {
      try {
        this.isFixingRecords = true;
        this.fixResult = null;
        
        // Call the API endpoint to update sales records
        const response = await axios.post(`${SALES_API}/update-product-details`);
        
        this.fixResult = {
          success: true,
          message: `Success! Updated ${response.data.updated} sales records with missing product information.`
        };
        
        console.log('Fixed sales records:', response.data);
      } catch (error) {
        console.error('Error fixing sales records:', error);
        this.fixResult = {
          success: false,
          message: `Error: ${error.response?.data?.detail || error.message || 'Unknown error'}`
        };
      } finally {
        this.isFixingRecords = false;
      }
    },
    
    // Sync user data
    async syncUserData() {
      try {
        this.isSyncingUsers = true;
        this.fixResult = null;
        
        // Re-fetch users from the database
        await this.fetchUsers();
        
        this.fixResult = {
          success: true,
          message: `Success! Synchronized user data for ${this.users.length} users.`
        };
      } catch (error) {
        console.error('Error syncing user data:', error);
        this.fixResult = {
          success: false,
          message: `Error syncing user data: ${error.message || 'Unknown error'}`
        };
      } finally {
        this.isSyncingUsers = false;
      }
    },
    
    // Filter data based on search query
    filterData() {
      // The filtering is handled by computed properties
      console.log('Filtering with query:', this.searchQuery);
    },
    
    // View order details
    viewOrderDetails(orderId) {
      const order = this.recentOrders.find(o => o.id === orderId);
      if (order) {
        this.selectedOrder = { ...order };
        this.showOrderModal = true;
      }
    },
    
    // Close order modal
    closeOrderModal() {
      this.showOrderModal = false;
      this.selectedOrder = {};
    },
    
    // View user details
    viewUserDetails(userId) {
      const user = this.users.find(u => u.id === userId);
      if (user) {
        this.selectedUser = { ...user };
        this.showUserModal = true;
      }
    },
    
    // Close user modal
    closeUserModal() {
      this.showUserModal = false;
      this.selectedUser = {};
    },
    
    async toggleUserStatus(user) {
  try {
    const newStatus = user.status === 'Inactive' ? 'Active' : 'Inactive';
    
    // Call the userService to update the user
    const response = await userService.updateUser(user.id, {
      status: newStatus
    });
    
    if (response && response.success) {
      // Update local data
      const index = this.users.findIndex(u => u.id === user.id);
      if (index !== -1) {
        this.users[index].status = newStatus;
      }
      
      this.fixResult = {
        success: true,
        message: `Success! User ${user.username} status changed to ${newStatus}.`
      };
    } else {
      throw new Error('Failed to update user status');
    }
  } catch (error) {
    console.error('Error updating user status:', error);
    this.fixResult = {
      success: false,
      message: `Error updating user status: ${error.message || 'Unknown error'}`
    };
  }
},
    
    // Format date helper
    formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}
  }
}
</script>
  
<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  margin-left: 230px;
  min-height: 100vh;
}

.dashboard-container {
  flex-grow: 1;
    border-radius: 15px;
    overflow: hidden;
    padding: 20px;
}
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e9ecef;
}

.section-title {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}

.search-bar input {
  border: none;
  background: none;
  margin-left: 10px;
  outline: none;
  width: 200px;
}

.nav-items {
  display: flex;
  gap: 20px;
}

.nav-items i {
  font-size: 20px;
  color: #666;
  cursor: pointer;
}

.main-container {
    display: flex
;
    flex-direction: column;
    font-family: var(--font-family);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stats {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0;
}

.stat-change {
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 15px;
  display: inline-block;
}

.positive {
  color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.negative {
  color: #f44336;
  background: rgba(244, 67, 54, 0.1);
}

.neutral {
  color: #2196F3;
  background: rgba(33, 150, 243, 0.1);
}

.chart {
  grid-column: span 2;
  grid-row: span 2;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.recent-orders {
  grid-column: span 2;
}

.active-users {
  grid-column: span 2;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  font-weight: 600;
  color: #666;
}

.status {
  padding: 4px 8px;
  border-radius: 15px;
  font-size: 12px;
}

.completed {
  background: #E8F5E9;
  color: #4CAF50;
}

.pending {
  background: #FFF3E0;
  color: #FF9800;
}

.processing {
  background: #E3F2FD;
  color: #2196F3;
}

.active {
  background: #E8F5E9;
  color: #4CAF50;
}

.inactive {
  background: #FFEBEE;
  color: #F44336;
}

.loading-indicator {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error-message {
  color: #F44336;
  padding: 15px;
  background: #FFEBEE;
  border-radius: 5px;
}

/* Maintenance section */
.maintenance-section {
  padding: 0 20px 20px;
}

.maintenance-card {
  margin-top: 20px;
}

.maintenance-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

.maintenance-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 10px;
  background: #2196F3;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s;
}

.maintenance-btn:hover {
  background: #1976D2;
}

.maintenance-btn:disabled {
  background: #90CAF9;
  cursor: not-allowed;
}

.fix-result {
  padding: 10px;
  border-radius: 5px;
  background: #FFECB3;
  color: #FF8F00;
  margin-top: 10px;
}

.fix-result.success {
  background: #E8F5E9;
  color: #2E7D32;
}

/* Action buttons */
.action-btn {
  background: none;
  border: none;
  color: #2196F3;
  cursor: pointer;
  padding: 5px;
  margin-right: 5px;
  border-radius: 3px;
  transition: background 0.2s;
}

.action-btn:hover {
  background: rgba(33, 150, 243, 0.1);
}

/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 25px;
  border-radius: 10px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.close-btn {
  position: absolute;
  right: 20px;
  top: 15px;
  font-size: 24px;
  cursor: pointer;
}

/* Order details */
.order-details, .user-details {
  margin-top: 20px;
}

.detail-row {
  display: flex;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.detail-row .label {
  font-weight: bold;
  width: 120px;
}

.user-details {
  display: flex;
  gap: 20px;
}

.user-profile {
  flex: 0 0 150px;
}

.profile-image {
  width: 150px;
  height: 150px;
  border-radius: 5px;
  object-fit: cover;
}

.user-info {
  flex: 1;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart, .recent-orders, .active-users {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .chart, .recent-orders, .active-users {
    grid-column: span 1;
  }
  
  .app-container {
    margin-left: 0;
  }
  
  .user-details {
    flex-direction: column;
  }
}
</style>