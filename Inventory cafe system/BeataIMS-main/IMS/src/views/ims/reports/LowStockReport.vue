<template>
  <Header />
  <SideBar />
  <div class="app-container">
    <div class="header-container">
      <div class="title-section">
        <h1 class="products-header">Out of Stock Report</h1>
        <div v-if="getStatusCount('Out of Stock') > 0" class="header-alert">
          {{ getStatusCount('Out of Stock') }} Out of Stock
        </div>
      </div>
      <div class="header-actions">
        <button class="export-btn" @click="exportLowStockReport">Export CSV</button>
      </div>
    </div>

    <div class="inventory-container">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading report data...</p>
      </div>
      
      <div v-else-if="outOfStockItems.length === 0" class="no-data-container">
        <p>No out-of-stock items found.</p>
      </div>
      
      <div v-else>
        <div class="summary-banner">
          <div class="summary-header">
            <span class="summary-title">Out of Stock Report</span>
            <span class="summary-date">{{ formatDate(reportData.date) }}</span>
          </div>
          <div class="stock-alert-info">
            <div class="critical-alert" v-if="getStatusCount('Out of Stock') > 0">
              <span class="alert-count">{{ getStatusCount('Out of Stock') }}</span> Out of Stock
            </div>
          </div>
          <div class="summary-counts">
            <span class="summary-count total">
              <span class="count-num">{{ outOfStockItems.length }}</span> Items Need Attention
            </span>
            <span class="summary-count out">
              <span class="count-num">{{ getStatusCount('Out of Stock') }}</span> Out of Stock
            </span>
          </div>
        </div>
        
        <div class="table-container">
          <table class="stock-table">
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Current</th>
                <th>Threshold</th>
                <th>Price</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in outOfStockItems" :key="item.ProductID || item.StockID || item.ReportID">
                <td>
                  <div class="stock-info">
                    <img 
                      :src="getImageUrl(item.Image)" 
                      :alt="item.StockName || item.ProductName"
                      @error="handleImageError"
                      class="stock-image"
                    />
                    <span class="stock-name">{{ item.StockName || item.ProductName }}</span>
                  </div>
                </td>
                <td :class="{ 'zero-quantity': item.Quantity <= 0 }">{{ item.Quantity }}</td>
                <td>{{ item.Threshold || 10 }}</td>
                <td>₱{{ parseFloat(item.CostPrice || item.UnitPrice).toFixed(2) }}</td>
                <td>
                  <span :class="'status status-' + getStatus(item.Quantity, item.Threshold).toLowerCase().replace(' ', '-')">
                    {{ getStatus(item.Quantity, item.Threshold) }}
                  </span>
                </td>
                <td>
                  <button class="action-btn" @click="goToInventory()">
                    <i class="pi pi-eye"></i> View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="totals-container">
          <div class="totals-item">
            <span>Report Date: </span>
            <span>{{ formatDate(reportData.date) }}</span>
          </div>
          <div class="totals-item">
            <span>Total Out of Stock Items: </span>
            <span>{{ outOfStockItems.length }}</span>
          </div>
          <div class="totals-item">
            <span>Total Value: </span>
            <span>₱{{ parseFloat(reportData.total_value).toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from "@/components/ims/SideBar.vue";
import Header from "@/components/Header.vue";
import axios from "axios";
import { REPORTS_API, INVENTORY_API, getImageUrl } from "@/api/config.js";
import { useToast } from "vue-toastification";

export default {
  components: {
    SideBar,
    Header,
  },
  name: "LowStockReport",
  setup() {
    const toast = useToast();
    return { toast };
  },
  data() {
    return {
      reportData: {
        date: new Date().toISOString(),
        total_items: 0,
        total_value: 0,
      },
      lowStockItems: [],
      outOfStockItems: [],
      allProductItems: [], // Store all inventory products
      filteredItems: [], // Store filtered Ready-Made products
      selectedDate: new Date().toISOString().split("T")[0], 
      currentDate: new Date().toISOString().split("T")[0], 
      fallbackImage: "https://via.placeholder.com/100", // Default Image
      loading: false,
      error: null
    };
  },
  methods: {
    async fetchInventoryProducts() {
      try {
        this.loading = true;
        this.error = null;

        console.log(`Fetching inventory products from: ${INVENTORY_API}/inventoryproducts/filter?process_type=Ready-Made`);
        const response = await axios.get(`${INVENTORY_API}/inventoryproducts/filter?process_type=Ready-Made`);
        console.log("Inventory API Response:", response.data);
        
        // Process all inventory products
        this.allProductItems = response.data.map(item => {
          // Explicitly convert quantities to numbers to ensure correct comparisons
          const qty = Number(item.Quantity);
          const threshold = Number(item.Threshold || 10);
          
          let status = '';
          // Determine status based on quantity and threshold
          if (qty <= 0) {
            status = 'Out of Stock';
          } else if (qty <= threshold) {
            status = 'Low Stock';
          } else {
            status = 'In Stock';
          }
          
          return {
            ProductID: item.id ? String(item.id).padStart(4) : 'N/A',
            StockName: item.ProductName || "Unknown Product",
            ProductName: item.ProductName || "Unknown Product",
            Quantity: qty,
            Threshold: threshold,
            UnitPrice: item.UnitPrice || 0,
            CostPrice: item.UnitPrice || 0,
            Details: item.Details || '',
            Status: status,
            ProcessType: item.ProcessType || '',
            Image: item.Image ? this.getImageUrl(item.Image) : this.fallbackImage,
          };
        });
        
        // Filter for Ready-Made products
        this.filteredItems = this.allProductItems.filter(item => 
          item.ProcessType === "Ready-Made"
        );
        
        // Filter to only include out-of-stock items
        this.outOfStockItems = this.filteredItems.filter(item => 
          item.Quantity <= 0 || item.Status === 'Out of Stock'
        );
        
        console.log("Filtered Ready-Made products:", this.filteredItems.length);
        console.log("Out of stock items:", this.outOfStockItems.length);
        
        // Set report data
        this.reportData = {
          date: new Date().toISOString(),
          total_items: this.filteredItems.length,
          total_value: this.calculateTotalValue(this.filteredItems),
        };
        
        if (this.outOfStockItems.length === 0) {
          this.toast.info("No out-of-stock items found.");
        }
      } catch (error) {
        console.error("Error fetching out-of-stock report:", error);
        this.error = error.message || "Failed to load report";
        this.toast.error(`Error fetching out-of-stock report: ${this.error}`);
        this.filteredItems = [];
        this.outOfStockItems = [];
        this.reportData = {
          date: new Date().toISOString(),
          total_items: 0,
          total_value: 0
        };
      } finally {
        this.loading = false;
      }
    },
    
    calculateTotalValue(items) {
      return items.reduce((total, item) => {
        const quantity = Number(item.Quantity) || 0;
        const price = Number(item.UnitPrice || item.CostPrice) || 0;
        return total + (quantity * price);
      }, 0).toFixed(2);
    },
    
    getStatusCount(status) {
      return this.outOfStockItems.filter(item => 
        this.getStatus(item.Quantity, item.Threshold) === status
      ).length;
    },
    
    getImageUrl(imagePath) {
      if (!imagePath) return this.fallbackImage;
      
      // Special case for product image paths
      if (imagePath && imagePath.includes('products/')) {
        const filename = imagePath.split('/').pop();
        return `${REPORTS_API.split('/api/reports')[0]}/products/${filename}`;
      }
      
      return imagePath.startsWith("http") ? imagePath : getImageUrl(imagePath);
    },
    
    handleImageError(event) {
      event.target.src = this.fallbackImage;
    },
    
    getStatus(quantity, threshold = 10) {
      // Ensure quantity is treated as a number
      quantity = Number(quantity);
      threshold = Number(threshold || 10);
      
      if (quantity <= 0) return "Out of Stock";
      if (quantity <= threshold) return "Low Stock";
      return "In Stock";
    },
    
    formatDate(dateString) {
      if (!dateString) return "N/A";
      try {
        return new Date(dateString).toLocaleString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          hour12: true,
        });
      } catch (e) {
        return dateString || "N/A";
      }
    },
    
    exportLowStockReport() {
      if (!this.outOfStockItems.length) {
        this.toast.warning("No data to export");
        return;
      }

      try {
        const headers = ["Product Name", "Current Quantity", "Threshold", "Price", "Status"];
        const data = this.outOfStockItems.map((item) => [
          item.StockName || item.ProductName,
          item.Quantity,
          item.Threshold || 10,
          parseFloat(item.CostPrice || item.UnitPrice).toFixed(2),
          this.getStatus(item.Quantity, item.Threshold),
        ]);

        const csvContent = [headers.join(","), ...data.map((row) => row.join(","))].join("\n");

        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `out-of-stock-report-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        
        this.toast.success("Report exported successfully");
      } catch (error) {
        console.error("Error exporting report:", error);
        this.toast.error("Failed to export report");
      }
    },
    
    goToInventory() {
      this.$router.push('/viewinventory');
    }
  },
  created() {
    this.fetchInventoryProducts();
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  margin-left: 230px;
  height: 100%;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-left: 18px;
  width: 95%;
}

.title-section {
  display: flex;
  align-items: center;
}

.products-header {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}

.header-alert {
  background-color: #ffebee;
  color: #d32f2f;
  padding: 8px 15px;
  border-radius: 8px;
  margin-left: 10px;
  font-weight: bold;
  font-size: 16px;
  display: flex;
  align-items: center;
  border: 1px solid #f44336;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
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

.no-data-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  font-size: 18px;
  color: #666;
}

.summary-banner {
  background-color: #f5f5f5;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-header {
  display: flex;
  flex-direction: column;
}

.summary-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.summary-date {
  font-size: 14px;
  color: #666;
}

.stock-alert-info {
  display: flex;
  align-items: center;
}

.critical-alert {
  background-color: #ffebee;
  color: #d32f2f;
  padding: 8px 15px;
  border-radius: 8px;
  margin-right: 10px;
  font-weight: bold;
  font-size: 16px;
  display: flex;
  align-items: center;
  border: 1px solid #f44336;
}

.alert-count {
  background-color: #f44336;
  color: white;
  font-weight: bold;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
}

.summary-counts {
  display: flex;
  gap: 15px;
}

.summary-count {
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.summary-count.out {
  background-color: #ffebee;
  color: #d32f2f;
}

.summary-count.low {
  background-color: #fff8e1;
  color: #ff8f00;
}

.count-num {
  font-weight: bold;
  margin-right: 5px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
}

.stock-table th,
.stock-table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.stock-table tbody {
  font-size: 15px;
}

.stock-table th {
  background-color: #f4f4f4;
  padding: 13px;
  color: #333;
  font-weight: bold;
}

.stock-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.stock-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stock-image {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.inventory-container {
  position: relative;
  flex-grow: 1;
  height: 37dvw;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  border-radius: 15px;
  overflow-y: auto;
  margin-left: 5px;
  padding: 15px;
}

.table-container {
  flex-grow: 1;
  overflow-y: auto;
  border-radius: 15px;
}

.totals-container {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background-color: #f4f4f4;
  margin-top: auto; 
  border-bottom-right-radius: 15px;
  border-bottom-left-radius: 15px;
  position: sticky;
  bottom: 0;
}

.totals-item {
  width: 30%;
  font-weight: bold;
}

.export-btn {
  background-color: #E54F70;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.status {
  padding: 4px 8px;
  border-radius: 15px;
  font-size: 12px;
  display: inline-block;
}

.status-in-stock {
  background: #E8F5E9; 
  color: #4CAF50; 
}

.status-low-stock {
  background: #FFF3E0; 
  color: #FF9800;
}

.status-out-of-stock {
  background: #F8D7DA; 
  color: #721c24; 
}

.action-btn {
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.action-btn:hover {
  background-color: #0d8bf2;
}

.zero-quantity {
  color: #d32f2f;
  font-weight: bold;
  background-color: rgba(211, 47, 47, 0.1);
}
</style>
