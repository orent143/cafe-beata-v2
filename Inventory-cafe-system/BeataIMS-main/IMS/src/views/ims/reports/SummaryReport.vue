<template>
  <Header />
  <SideBar />
  <div class="app-container">
    <div class="header-container">
      <h1 class="products-header">Summary Reports</h1>
      <div class="header-actions">
        <input 
          type="date" 
          v-model="selectedDate" 
          class="date-picker" 
          @change="fetchInventoryReport"
        />
        <button class="export-btn" @click="exportSummary">Export CSV</button>
      </div>
    </div>

    <div class="inventory-container">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading report data...</p>
      </div>
      
      <div v-else-if="filteredInventory.length === 0" class="no-data-container">
        <p>No inventory items found for the selected date.</p>
      </div>
      
      <div v-else>
        <div class="table-container">
          <table class="stock-table">
            <thead>
              <tr>
                <th>Product ID</th>
                <th>Product Name</th>
                <th>Category</th>
                <th>Unit Price</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredInventory" :key="product.ProductID">
                <td>{{ product.ProductID }}</td>
                <td>{{ product.ProductName }}</td>
                <td>{{ product.CategoryName }}</td>
                <td>₱{{ parseFloat(product.UnitPrice).toFixed(2) }}</td>
                <td>
                  <span :class="'status status-' + product.Status.toLowerCase().replace(' ', '-')">
                    {{ product.Status }}
                  </span>
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
            <span>Total Items: </span>
            <span>{{ reportData.total_items }}</span>
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
import { REPORTS_API, CATEGORIES_API, getImageUrl } from "@/api/config.js";
import { useToast } from "vue-toastification";

export default {
  components: {
    SideBar,
    Header,
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  name: "SummaryReport",
  data() {
    return {
      reportData: {
        date: "",
        total_items: 0,
        total_value: 0,
      },
      inventoryProducts: [],
      selectedDate: new Date().toISOString().split("T")[0], 
      currentDate: new Date().toISOString().split("T")[0],
      loading: false,
      fallbackImage: "https://via.placeholder.com/100",
      error: null,
      categories: []
    };
  },
  computed: {
    filteredInventory() {
      return this.inventoryProducts;
    },
  },
  methods: {
    async fetchInventoryReport() {
      try {
        this.loading = true;
        this.error = null;
        
        console.log(`Fetching inventory report from: ${REPORTS_API}/inventory_report?date=${this.selectedDate}`);
        const response = await axios.get(`${REPORTS_API}/inventory_report?date=${this.selectedDate}`);
        console.log("Inventory API Response:", response.data);
        
        this.reportData = {
          date: response.data.date || new Date().toISOString(),
          total_items: response.data.total_items || 0,
          total_value: parseFloat(response.data.total_value || 0),
        };

        this.inventoryProducts = (response.data.items || []).map(item => ({
          ProductID: item.ProductID || 0,
          ProductName: item.ProductName || "Unknown Product",
          CategoryID: item.CategoryID || 0,
          CategoryName: this.getCategoryName(item.CategoryID),
          UnitPrice: parseFloat(item.UnitPrice || 0).toFixed(2),
          Status: item.Status || "Unknown"
        }));
        
        if (this.inventoryProducts.length === 0) {
          this.toast.info("No inventory data found for the selected date");
        }
      } catch (error) {
        console.error("Error fetching inventory report:", error);
        this.error = error.message || "Failed to load report";
        this.toast.error(`Error fetching inventory report: ${this.error}`);
        this.inventoryProducts = [];
        this.reportData = {
          date: new Date().toISOString(),
          total_items: 0,
          total_value: 0,
        };
      } finally {
        this.loading = false;
      }
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
    handleImageError(event) {
      event.target.src = this.fallbackImage;
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(cat => cat.id === categoryId);
      return category ? category.CategoryName : 'Unknown Category';
    },
    exportSummary() {
      if (!this.inventoryProducts.length) {
        this.toast.warning("No data to export");
        return;
      }

      try {
        const headers = ["Product ID", "Product Name", "Category", "Unit Price", "Status"];
        const data = this.inventoryProducts.map((product) => [
          product.ProductID,
          product.ProductName,
          product.CategoryName,
          parseFloat(product.UnitPrice).toFixed(2),
          product.Status,
        ]);

        const csvContent = [headers.join(","), ...data.map((row) => row.join(","))].join("\n");

        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `inventory-summary-${this.selectedDate || "all"}.csv`;
        a.click();
        
        this.toast.success("Report exported successfully");
      } catch (error) {
        console.error("Error exporting report:", error);
        this.toast.error("Failed to export report");
      }
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
    async fetchCategories() {
      try {
        const response = await axios.get(`${CATEGORIES_API}`);
        this.categories = response.data;
      } catch (error) {
        console.error('Error fetching categories:', error);
        this.toast.error('Failed to load categories');
      }
    },
  },
  created() {
    this.fetchCategories();
    this.fetchInventoryReport();
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.product-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.product-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.product-image {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.date-picker {
  padding: 8px 12px;
  border: 2px solid #E54F70;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}
.date-picker:focus {
  outline: none;
  border-color: #E54F70;
  box-shadow: 0 0 5px rgba(229, 79, 112, 0.5);
}
.filter-container {
  position: relative;
}

.filter-btn {
  background: none;
  border: none;
  font-size: 19px;
  cursor: pointer;
}

.dropdown {
  position: absolute;
  top: 35px;
  right: 0;
  background-color: white;
  border: 1px solid #ccc;
  padding: 10px;
  width: 200px;
}

.filter-select {
  width: 100%;
  padding: 8px;
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
.stock-table td {
  font-size: 14px;
  color: #333;
  font-weight: 500;
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
  padding: 0;
}

.table-container {
  flex-grow: 1;
  overflow-y: auto;
  border-radius: 15px;
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
.export-btn {
  background-color: #E54F70;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-container {
  position: relative;
}

.search-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #333;
  pointer-events: none;
}

.search-bar {
  padding: 8px 30px 8px 8px;
  border: 1px solid #94949400;
  border-radius: 10px;
  width: 130px;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  background-color: #D9D9D9;
}

.summary-spacer {
  height: 5px;
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
.stock-table td {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}
</style>