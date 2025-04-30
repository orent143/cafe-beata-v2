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
          @change="fetchCategoryReport"
        />
        <button class="export-btn" @click="exportSummaryReport">
          <i class="pi pi-download"></i> Export CSV
        </button>
      </div>
    </div>

    <div class="inventory-container">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading report data...</p>
      </div>
      
      <div v-else-if="categories.length === 0" class="no-data-container">
        <p>No category data found for the selected date.</p>
      </div>
      
      <div v-else>
        <div class="table-container">
          <table class="stock-table">
            <thead>
              <tr>
                <th>Category Name</th>
                <th>Total Items</th>
                <th>Total Amount</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="category in categories" :key="category.category_name">
                <td>{{ category.category_name }}</td>
                <td>{{ category.total_items }}</td>
                <td>₱{{ parseFloat(category.total_amount).toFixed(2) }}</td>
                <td>
                  <button class="btn-details" @click="viewCategoryDetails(category)">
                    View Details
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="totals-container">
        <div class="totals-item">
          <span>Total Items Sold:</span>
          <span>{{ overallItems }}</span>
        </div>
        <div class="totals-item">
          <span>Total Sales:</span>
          <span>₱{{ parseFloat(overallTotal).toFixed(2) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SideBar from "@/components/ims/SideBar.vue";
import Header from "@/components/Header.vue";
import { SALES_API } from "@/api/config.js";
import { useToast } from "vue-toastification";

export default {
  components: {
    SideBar,
    Header,
  },
  data() {
    return {
      selectedDate: localStorage.getItem("selectedDate") || new Date().toISOString().split("T")[0],
      categories: [],
      overallItems: 0,
      overallTotal: 0,
      loading: false,
      toast: useToast(),
    };
  },
  methods: {
    async fetchCategoryReport() {
      try {
        this.loading = true;
        localStorage.setItem("selectedDate", this.selectedDate);
        const response = await axios.get(`${SALES_API}/sales/category-report`, {
          params: { date: this.selectedDate },
        });
        this.categories = response.data.categories || [];
        this.overallItems = response.data.overall_items || 0;
        this.overallTotal = response.data.overall_total || 0;
      } catch (error) {
        console.error("Error fetching category report:", error);
        this.toast.error("Failed to load category report.");
      } finally {
        this.loading = false;
      }
    },
    viewCategoryDetails(category) {
      this.$router.push({
        name: "CategoryDetails",
        params: { categoryName: category.category_name, date: this.selectedDate },
      });
    },
    exportSummaryReport() {
      if (!this.categories.length) {
        this.toast.warning("No data to export");
        return;
      }

      try {
        const headers = ["Category Name", "Total Items", "Total Amount"];
        const data = this.categories.map((category) => [
          category.category_name,
          category.total_items,
          parseFloat(category.total_amount).toFixed(2),
        ]);

        const csvContent = [headers.join(","), ...data.map((row) => row.join(","))].join("\n");

        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `summary-report-${this.selectedDate}.csv`;
        a.click();

        this.toast.success("Report exported successfully");
      } catch (error) {
        console.error("Error exporting report:", error);
        this.toast.error("Failed to export report");
      }
    },
  },
  created() {
    this.fetchCategoryReport();
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
  padding: 15px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.stock-table tbody {
  font-size: 15px;
}

.stock-table th {
  background-color: #f4f4f4;
  padding: 13px;
  color: #343a40;
  font-weight: bold;
}
.stock-table td {
  font-size: 14px;
    color: #333;
    font-weight: 500;
}
.inventory-container {
  position: relative;
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


.totals-item span {
  font-weight: bold;
  margin-right: 5px;
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

.btn-details {
  background-color: transparent;
  color: #4CAF50;
  border: 1.5px solid #4CAF50;
  border-radius: 4px;
  padding: 6px 15px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  width: 120px;
}

.btn-details:hover {
  background-color: #4CAF50;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.stock-table td {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}
</style>