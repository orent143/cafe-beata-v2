<template>
  <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />

  <SideBar :isCollapsed="isSidebarCollapsed" />
  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <h1 class="products-header">Inventory Reports</h1>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading report data...</p>
    </div>
    <div v-else class="report-cards">
      <div class="report-card" @click="goToReport('summary')">
        <div class="report-card-header">
          <i class="pi pi-chart-line report-icon"></i>
          <h3>Product Summary Report</h3>
        </div>
        <div class="report-card-body">
          <p>Complete overview of all inventory products with quantities and values</p>
          <div class="report-stats">
            <span><strong>{{ totalSummaryReports }}</strong> Total Products</span>
            <span>₱{{ totalSummaryAmount }}</span>
          </div>
        </div>
      </div>

      <div class="report-card sales-card" @click="goToReport('dailySales')">
        <div class="report-card-header">
          <i class="pi pi-money-bill report-icon"></i>
          <h3>Daily Sales Report</h3>
        </div>
        <div class="report-card-body">
          <p>Combined daily sales from both cafe and inventory systems</p>
          <div class="report-stats">
            <span><strong>Today's Date:</strong> {{ formatCurrentDate() }}</span>
          </div>
        </div>
      </div>

      <div class="report-card low-stock-card" @click="goToReport('lowStock')">
        <div class="report-card-header">
          <i class="pi pi-exclamation-triangle report-icon warning-icon"></i>
          <h3>Low Stock Report</h3>
          <div v-if="outOfStockCount > 0" class="attention-badge">{{ outOfStockCount }}</div>
        </div>
        <div class="report-card-body">
          <p>Items that need immediate attention - low stock or out of stock</p>
          <div v-if="outOfStockCount > 0" class="alert-banner">
            <strong>{{ outOfStockCount }} items are OUT OF STOCK</strong>
          </div>
          <div class="stock-status-summary">
            <div class="status-item out-of-stock">
              <span class="status-count">{{ outOfStockCount }}</span>
              <span class="status-label">Out of Stock</span>
            </div>
            <div class="status-item low-stock">
              <span class="status-count">{{ lowStockCount }}</span>
              <span class="status-label">Low Stock</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import SideBar from '@/components/ims/SideBar.vue';
import Header from '@/components/Header.vue';
import { REPORTS_API, INVENTORY_API } from '@/api/config.js';
import { useToast } from 'vue-toastification';

export default {
  components: { SideBar, Header },
  setup() {
    const toast = useToast();
    return { toast };
  },
  data() {
    return {
      isSidebarCollapsed: false,
      totalSummaryReports: 0,
      totalSummaryAmount: 0,
      lowStockCount: 0,
      outOfStockCount: 0,
      totalLowStockAmount: 0,
      loading: false,
      error: null,
      productItems: [],
      filteredItems: [],
    };
  },
  computed: {
    totalLowStockCount() {
      return this.lowStockCount + this.outOfStockCount;
    }
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    
    // Method to determine stock status
    getStockStatus(quantity, threshold) {
      // Ensure quantity is treated as a number
      quantity = Number(quantity);
      threshold = Number(threshold || 10);
      
      if (quantity <= 0) return "Out of Stock";
      if (quantity <= threshold) return "Low Stock";
      return "In Stock";
    },
    
    formatCurrentDate() {
      const now = new Date();
      return now.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    },
    
    async fetchProductItems() {
      try {
        let url = `${INVENTORY_API}/inventoryproducts/filter?process_type=Ready-Made`;
        console.log(`Fetching inventory products from: ${url}`);
        const response = await axios.get(url);

        this.productItems = response.data.map(item => {
          return {
            ...item,
            ProductID: item.id ? String(item.id).padStart(4) : 'N/A',
            Quantity: Number(item.Quantity),
            Threshold: Number(item.Threshold || 10),
          };
        });

        this.filterItems();
      } catch (error) {
        console.error('Error fetching product items:', error);
        this.toast.error('Error loading inventory items. Please try again.');
      }
    },
    
    filterItems() {
      // Filter only Ready-Made products
      this.filteredItems = this.productItems.filter(item => item.ProcessType === "Ready-Made");
      console.log(`Filtered ${this.filteredItems.length} Ready-Made products`);
      
      // Calculate stock counts
      this.calculateStockSummary();
    },
    
    calculateStockSummary() {
      // Reset counters
      let outOfStock = 0;
      let lowStock = 0;
      
      // Count items by stock status
      this.filteredItems.forEach(item => {
        if (item.Quantity <= 0) {
          outOfStock++;
        } else if (item.Quantity <= item.Threshold) {
          lowStock++;
        }
      });
      
      console.log(`Stock summary: ${outOfStock} out of stock, ${lowStock} low stock`);
      
      // Update the counts
      this.outOfStockCount = outOfStock;
      this.lowStockCount = lowStock;
    },
    
    async fetchReportData() {
      try {
        this.loading = true;
        this.error = null;
        
        // Get inventory report for product summary
        console.log(`Fetching inventory report from: ${REPORTS_API}/inventory_report`);
        const response = await axios.get(`${REPORTS_API}/inventory_report`);
        const report = response.data;

        this.totalSummaryReports = report.total_items || 0;
        this.totalSummaryAmount = parseFloat(report.total_value || 0).toFixed(2);

        // Fetch the actual inventory products to get accurate out-of-stock count
        await this.fetchProductItems();
        
      } catch (error) {
        console.error('Error fetching report data:', error);
        this.error = error.message || "Failed to load reports";
        this.toast.error(`Error loading reports: ${this.error}`);
      } finally {
        this.loading = false;
      }
    },
    goToReport(reportType) {
      const reportRoutes = {
        summary: '/reportsims/summary',
        lowStock: '/reportsims/lowStock',
        dailySales: '/reportsims/dailySales'
      };
      if (reportRoutes[reportType]) {
        this.$router.push(reportRoutes[reportType]);
      }
    }
  },
  created() {
    this.fetchReportData(); 
  }
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  margin-left: 230px;
  transition: margin-left 0.3s ease;
}

.app-container.sidebar-collapsed {
  margin-left: 70px;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-left: 18px;
  width: 95%;
}

.products-header {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  margin-top: 40px;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #E54F70;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.report-cards {
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-bottom: 10px;
  margin-top: 40px;
  align-items: center;
  width: 100%;
}

.report-card {
  background-color: #D9D9D9;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 70%;
  padding: 25px;
  cursor: pointer;
  transition: transform 0.2s ease;
  position: relative;
}

.report-card:hover {
  background-color: #f0f0f0;
  transform: translateY(-5px);
}

.low-stock-card {
  border-left: 5px solid #ff9800;
}

.low-stock-card .report-icon.warning-icon {
  color: #ff7043;
}

.sales-card .report-icon {
  color: #4caf50;
}

.alert-banner {
  background-color: rgba(244, 67, 54, 0.15);
  color: #f44336;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 0.95rem;
}

.report-card-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  position: relative;
}

.report-icon {
  font-size: 24px;
  color: #333;
}

.warning-icon {
  color: #ff9800;
}

.attention-badge {
  position: absolute;
  right: 0;
  top: 0;
  background-color: #f44336;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.report-card-header h3 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.report-card-body {
  color: #555;
}

.report-card-body p {
  margin-bottom: 15px;
}

.report-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ccc;
}

.report-stats span {
  font-weight: bold;
  color: #333;
}

.stock-status-summary {
  display: flex;
  justify-content: space-between;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.status-count {
  font-size: 24px;
  font-weight: bold;
}

.status-label {
  font-size: 14px;
}

.out-of-stock .status-count {
  color: #d32f2f;
}

.low-stock .status-count {
  color: #ff9800;
}
</style>