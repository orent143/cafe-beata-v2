<template>
  <!-- Import Header component -->
  <Header />
      <sidebar />
    <div class="app-container">
    <div class="dashboard-container">
      <main class="main-content">
        <nav class="top-nav">
          <div class="search-bar">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="Search...">
          </div>
          <div class="nav-items">
            <i class="fas fa-bell"></i>
            <i class="fas fa-user-circle"></i>
          </div>
        </nav>
  
        <div class="dashboard-grid">
          <div class="card stats">
            <h3>Today's Sales</h3>
            <div class="stat-value">$2,459</div>
            <div class="stat-change positive">+15.3%</div>
          </div>
  
          <div class="card stats">
            <h3>Total Orders</h3>
            <div class="stat-value">147</div>
            <div class="stat-change positive">+8.2%</div>
          </div>
  
          <div class="card stats">
            <h3>Low Stock Items</h3>
            <div class="stat-value">12</div>
            <div class="stat-change negative">-2.4%</div>
          </div>
  
          <div class="card stats">
            <h3>Active Staff</h3>
            <div class="stat-value">8</div>
            <div class="stat-change neutral">0%</div>
          </div>
  
          <div class="card chart">
            <h3>Sales Overview</h3>
            <!-- Add chart component here -->
          </div>
  
          <div class="card recent-orders">
            <h3>Recent Orders</h3>
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer</th>
                  <th>Items</th>
                  <th>Total</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in recentOrders" :key="order.id">
                  <td>#{{order.id}}</td>
                  <td>{{order.customer}}</td>
                  <td>{{order.items}}</td>
                  <td>${{order.total}}</td>
                  <td><span :class="'status ' + order.status.toLowerCase()">{{order.status}}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
</div>
  </template>
  
  <script>
  import sidebar from '@/components/admin/sidebar.vue';
  import Header from '@/components/Header.vue';
  export default {
    name: 'Dashboard',
    components: {
      sidebar,
      Header
    },
    data() {
      return {
        recentOrders: [
          { id: '1234', customer: 'John Doe', items: '3', total: '45.00', status: 'Completed' },
          { id: '1235', customer: 'Jane Smith', items: '2', total: '32.50', status: 'Pending' },
          { id: '1236', customer: 'Bob Wilson', items: '1', total: '18.00', status: 'Processing' },
          { id: '1237', customer: 'Alice Brown', items: '4', total: '67.25', status: 'Completed' },
        ]
      }
    }
  }
  </script>
  
  <style scoped>
  .app-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1; /* Allow the container to take remaining space */
  margin-left: 230px; /* Make space for sidebar, adjust as needed */
  height: 100vh; /* Full height of the page */
}
  .dashboard-container {
    display: flex;
    background-color: #f5f5f5;
  }
  
  .main-content {
    flex: 1;
    padding: 20px;
  }
  
  .top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background: white;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .search-bar {
    display: flex;
    align-items: center;
    background: #f5f5f5;
    padding: 8px 15px;
    border-radius: 20px;
  }
  
  .search-bar input {
    border: none;
    background: none;
    margin-left: 10px;
    outline: none;
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
  
  .recent-orders {
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
  
  @media (max-width: 1024px) {
    .dashboard-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  @media (max-width: 768px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
    
    .chart, .recent-orders {
      grid-column: span 1;
    }
  }
  </style>