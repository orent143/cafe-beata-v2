<template>
  <Header 
    :isSidebarCollapsed="isSidebarCollapsed" 
    @toggle-sidebar="handleSidebarToggle"
    v-model:searchQuery="searchQuery"
    @update:searchQuery="filterInventoryProducts"
  />
  <SideBar />
  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <div class="title-section">
        <h1 class="products-header">Low Stock Report</h1>
        <span class="summary-date">{{ formatDate(reportData.date) }}</span>
      </div>
      <div class="header-actions">
        <div class="stock-alert-badge">
            {{ getStatusCount('Out of Stock') }} Out of Stock | {{ getStatusCount('Low Stock') }} Low Stock
          </div>
        <button class="export-btn" @click="exportLowStockReport">
          <i class="pi pi-download"></i> Export CSV
        </button>
      </div>
    </div>

    <div class="inventory-container">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading report data...</p>
      </div>
      
      <div v-else-if="lowStockItems.length === 0" class="no-data-container">
        <i class="pi pi-check-circle" style="font-size: 3rem; color: #4caf50; margin-bottom: 15px;"></i>
        <p>No low stock items found.</p>
        <p style="color: #6c757d; font-size: 14px;">All items are adequately stocked.</p>
      </div>
      
      <div v-else>

        
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
              <tr v-for="item in displayedLowStockItems" :key="item.ProductID || item.StockID || item.ReportID">
                <td>
                  <div class="stock-info">
                    <img 
  :src="getImageUrl(item.Image)" 
  :alt="item.StockName || item.ProductName"
  @error="handleImageError"
  class="stock-image"
  loading="lazy"  
/>
                    <span class="stock-name">{{ item.StockName || item.ProductName }}</span>
                  </div>
                </td>
                <td class="quantity-cell">
                  <span :class="{ 'zero-quantity': item.Quantity <= 0 }">{{ item.Quantity }}</span>
                </td>
                <td>{{ item.Threshold || 10 }}</td>
                <td>₱{{ parseFloat(item.CostPrice || item.UnitPrice).toFixed(2) }}</td>
                <td>
                  <span :class="'status status-' + getStatus(item.Quantity, item.Threshold).toLowerCase().replace(' ', '-')">
                    <i :class="getStatusIcon(item.Quantity, item.Threshold)" style="margin-right: 5px;"></i>
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
            <i class="pi pi-calendar" style="margin-right: 8px;"></i>
            <span>Report Date: </span>
            <span>{{ formatDate(reportData.date) }}</span>
          </div>
          <div class="totals-item">
            <i class="pi pi-exclamation-circle" style="margin-right: 8px;"></i>
            <span>Total Low Stock Items: </span>
            <span>{{ displayedLowStockItems.length }} {{ searchQuery ? 'filtered' : 'total' }}</span>
          </div>
          <div class="totals-item">
            <i class="pi pi-money-bill" style="margin-right: 8px;"></i>
            <span>Total Value: </span>
            <span>₱{{ parseFloat(calculateTotalValue(displayedLowStockItems)).toFixed(2) }}</span>
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
      isSidebarCollapsed: false,
      reportData: {
        date: new Date().toISOString(),
        total_items: 0,
        total_value: 0,
      },
      lowStockItems: [],
      filteredLowStockItems: [],
      outOfStockItems: [],
      allProductItems: [], //
      filteredItems: [], //
      selectedDate: new Date().toISOString().split("T")[0], 
      currentDate: new Date().toISOString().split("T")[0], 
      fallbackImage: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2VlZWVlZSIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjYWFhYWFhIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBhbGlnbm1lbnQtYmFzZWxpbmU9Im1pZGRsZSI+Tm8gSW1hZ2U8L3RleHQ+PC9zdmc+", // Base64 encoded SVG placeholder
      loading: false,
      error: null,
      searchQuery: '',
    };
  },
  computed: {
    // Display filtered low stock items when search is active
    displayedLowStockItems() {
      return this.filteredLowStockItems.length > 0 ? this.filteredLowStockItems : this.lowStockItems;
    }
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    
    filterInventoryProducts() {
      if (!this.searchQuery) {
        this.filteredLowStockItems = [];
        return;
      }
      
      const searchLower = this.searchQuery.toLowerCase();
      this.filteredLowStockItems = this.lowStockItems.filter(item => {
        const nameMatch = (item.StockName || item.ProductName || '').toLowerCase().includes(searchLower);
        const statusMatch = this.getStatus(item.Quantity, item.Threshold).toLowerCase().includes(searchLower);
        return nameMatch || statusMatch;
      });
    },

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
          // Determine status based on quantity
          if (qty <= 0) {
            status = 'Out of Stock';
          } else if (qty <= 10) {
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
        
        // Filter to include low stock and out of stock items
        this.lowStockItems = this.filteredItems.filter(item => 
          item.Quantity <= 10 || item.Status === 'Out of Stock'
        );
        
        // Sort by quantity (ascending) so out of stock appears first, then low stock
        this.lowStockItems.sort((a, b) => a.Quantity - b.Quantity);
        
        console.log("Filtered Ready-Made products:", this.filteredItems.length);
        console.log("Low and out of stock items:", this.lowStockItems.length);
        
        // Set report data
        this.reportData = {
          date: new Date().toISOString(),
          total_items: this.filteredItems.length,
          total_value: this.calculateTotalValue(this.filteredItems),
        };
        
        if (this.lowStockItems.length === 0) {
          this.toast.info("No low stock items found.");
        }
      } catch (error) {
        console.error("Error fetching low stock report:", error);
        this.error = error.message || "Failed to load report";
        this.toast.error(`Error fetching low stock report: ${this.error}`);
        this.filteredItems = [];
        this.lowStockItems = [];
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
      return this.lowStockItems.filter(item => 
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
      event.target.onerror = null; // Prevent infinite loop if the fallback also fails
    },
    
    getStatus(quantity, threshold = 10) {
      // Ensure quantity is treated as a number
      quantity = Number(quantity);
      
      if (quantity <= 0) return "Out of Stock";
      if (quantity <= 10) return "Low Stock";
      return "In Stock";
    },
    
    getStatusIcon(quantity, threshold = 10) {
      quantity = Number(quantity);
      
      if (quantity <= 0) return "pi pi-times-circle";
      if (quantity <= 10) return "pi pi-exclamation-triangle";
      return "pi pi-check-circle";
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
      if (!this.lowStockItems.length) {
        this.toast.warning("No data to export");
        return;
      }

      try {
        const headers = ["Product Name", "Current Quantity", "Threshold", "Price", "Status"];
        const data = this.lowStockItems.map((item) => [
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
        a.download = `low-stock-report-${new Date().toISOString().split('T')[0]}.csv`;
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
  margin-left: 220px;
  height: 100%;
  background-color: #f8f9fa;
  padding: 20px 30px;
  transition: all 0.3s ease;
}

.app-container.sidebar-collapsed {
  margin-left: 70px;
  padding-left: 20px;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.title-section {
  display: flex;
  flex-direction: column;
}

.products-header {
  color: #333;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
  font-size: 32px;
  margin: 0;
}

.header-alert {
  background-color: #fff3cd;
  color: #856404;
  padding: 10px 18px;
  border-radius: 8px;
  margin-left: 16px;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  align-items: center;
  border: 1px solid #ffeeba;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.export-btn {
  background-color: #E54F70;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 5px rgba(229, 79, 112, 0.3);
}

.export-btn:hover {
  background-color: #d33f5f;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(229, 79, 112, 0.4);
}

.export-btn:active {
  transform: translateY(0);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background-color: white;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.loading-spinner {
  border: 4px solid rgba(229, 79, 112, 0.1);
  border-radius: 50%;
  border-top: 4px solid #E54F70;
  width: 50px;
  height: 50px;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20px;
}

.no-data-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  font-size: 18px;
  color: #6c757d;
  background-color: white;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 30px;
}

.summary-banner {
  background: linear-gradient(to right, #ffffff, #f8f9fa);
  padding: 20px 25px;
  margin-bottom: 20px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #E54F70;
}

.summary-header {
  display: flex;
  flex-direction: column;
}

.summary-title {
  font-size: 18px;
  font-weight: 700;
  color: #343a40;
  margin-bottom: 5px;
}

.summary-date {
  font-size: 14px;
  color: #6c757d;
}

.stock-alert-badge {
  background-color: #E54F70;
  color: white;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  box-shadow: 0 2px 5px rgba(229, 79, 112, 0.3);
}

.inventory-container {
  position: relative;
  flex-grow: 1;
  height: calc(100vh - 180px);
  background-color: #ffffff;
  border-radius: 15px;
  overflow-y: auto;
  padding: 0;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.table-container {
  flex-grow: 1;
  overflow-y: auto;
  border-radius: 15px;
}

.stock-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin-bottom: 10px;
}

.stock-table th,
.stock-table td {
  padding: 15px 10px;
  text-align: center;
  border-bottom: 1px solid #e9ecef;
}

.stock-table tbody tr {
  transition: all 0.2s ease;
}

.stock-table tbody tr:hover {
  background-color: #f1f3f5;
}

.stock-table th {
  background-color: #f4f4f4;
    color: #333;
    font-weight: bold;
}

.stock-name {
  font-size: 15px;
  color: #212529;
  font-weight: 500;
}

.stock-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.stock-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 10px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stock-image:hover {
  transform: scale(1.1);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.15);
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

.status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  display: inline-block;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.status-in-stock {
  background-color: #e8f5e9; 
  color: #2e7d32; 
  border: 1px solid #c8e6c9;
}

.status-low-stock {
  background-color: #fff3e0; 
  color: #ef6c00;
  border: 1px solid #ffe0b2;
}

.status-out-of-stock {
  background-color: #ffebee; 
  color: #c62828; 
  border: 1px solid #ffcdd2;
}

.action-btn {
  background-color: #E54F70;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 5px rgba(229, 79, 112, 0.3);
}

.action-btn:hover {
  background-color: #d33f5f;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(229, 79, 112, 0.4);
}

.action-btn:active {
  transform: translateY(0);
}

.action-btn i {
  font-size: 16px;
}

.zero-quantity {
  color: #E54F70;
  font-weight: bold;
  background-color: white;
  padding: 5px 10px;
  border-radius: 4px;
}

.quantity-cell {
  background-color: white;
  padding: 15px 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
