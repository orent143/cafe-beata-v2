<template>
  <Header 
    :isSidebarCollapsed="isSidebarCollapsed" 
    @toggle-sidebar="handleSidebarToggle"
    v-model:searchQuery="searchTerm"
    @update:searchQuery="filterSalesData"
  />
  <SideBar :isCollapsed="isSidebarCollapsed"/>
  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <div class="header-title">
      <h1 class="sales-header">Sales Product</h1>
      <p class="sub-description">Track daily product sales, review quantities sold, and monitor remittances for better performance insights.</p>
    </div>
      <div class="header-actions">
        <div class="filter-container">
          <button class="filter-btn" @click="toggleFilterDropdown">
            <i class="pi pi-calendar-times"></i> Filter by Date
          </button>
          <div v-if="showFilterDropdown" class="dropdown">
            <!-- Date Picker for filtering sales data -->
            <input 
              type="date" 
              v-model="selectedDate" 
              class="filter-select" 
              @change="fetchSalesData"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="sales-container">
      <div class="sales-table-container" v-if="salesData.length">
        <table class="sales-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Items Sold</th>
              <th>Remitted</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sale in salesData" :key="sale.name">
              <td>{{ sale.name }}</td>
              <td>{{ sale.quantity }}</td>
              <td>₱{{ sale.unit_price.toFixed(2) }}</td>
              <td>{{ sale.items_sold }}</td>
              <td>₱{{ sale.remitted.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="totals-container" v-if="salesData.length">
        <div class="totals-item">
          <span>Total Items Sold:</span>
          <span>{{ totalItemsSold }}</span>
        </div>
        <div class="totals-item">
          <span>Total Sales:</span>
          <span>₱{{ totalSales.toFixed(2) }}</span>
        </div>
      </div>

      <div v-else class="loading">
        <p>Loading sales data...</p>
      </div>
    </div>
  </div>
</template>

<script>
import SideBar from '@/components/ims/SideBar.vue';
import Header from '@/components/Header.vue';
import axios from 'axios';
import { SALES_API } from '@/api/config.js';
import { useToast } from 'vue-toastification';

export default {
  components: { SideBar, Header },
  data() {
    return {
      isSidebarCollapsed: false,
      salesData: [],
      showFilterDropdown: false,
      selectedDate: '', // Date filter
      toast: useToast(),
      searchTerm: '',
    };
  },
  computed: {
    totalItemsSold() {
      return this.salesData.reduce((sum, sale) => sum + sale.items_sold, 0);
    },
    totalSales() {
      return this.salesData.reduce((sum, sale) => sum + (sale.items_sold * sale.unit_price), 0);
    },
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    async fetchSalesData() {
      try {
        const params = this.selectedDate ? { filter_date: this.selectedDate } : {}; // Include date filter if selected
        const response = await axios.get(`${SALES_API}/sales`, { params });
        this.salesData = response.data;
      } catch (error) {
        console.error("Error fetching sales data:", error);
        this.toast.error("Failed to fetch sales data. Please try again.");
      }
    },
    async updateSales(productId, quantitySold, remitted) {
      try {
        const response = await axios.post(`${SALES_API}/update`, {
          product_id: productId,
          quantity_sold: quantitySold,
          remitted: remitted
        });

        console.log(response.data.message);
        this.toast.success("Sales data updated successfully!");
      } catch (error) {
        console.error("Error updating sales:", error.response?.data?.detail || "Unknown error");
        this.toast.error(error.response?.data?.detail || "Failed to update sales");
      }
    },
    toggleFilterDropdown() {
      this.showFilterDropdown = !this.showFilterDropdown;
    },
    filterSalesData() {
      // If no search term, just return the original data
      if (!this.searchTerm) {
        return;
      }
      
      // Create a filtered copy of the sales data
      const searchLower = this.searchTerm.toLowerCase();
      const filteredData = this.salesData.filter(sale => 
        sale.name.toLowerCase().includes(searchLower)
      );
      
      // Update the table display with filtered data
      // We're not actually changing this.salesData to preserve the original data
      this.$nextTick(() => {
        const tableElement = document.querySelector('.sales-table tbody');
        if (tableElement) {
          // Hide rows that don't match the search
          const rows = tableElement.querySelectorAll('tr');
          rows.forEach(row => {
            const nameCell = row.querySelector('td:first-child');
            if (nameCell) {
              const name = nameCell.textContent.toLowerCase();
              row.style.display = name.includes(searchLower) ? '' : 'none';
            }
          });
        }
      });
    },
  },
  mounted() {
    this.fetchSalesData(); // Initial fetch on page load
  }
};
</script>

<style scoped>
/* Add any relevant styles for your table and layout here */
.loading {
  text-align: center;
  margin-top: 20px;
}

.app-container {
  display: flex;
  flex-direction: column;
  margin-left: 230px;
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
  margin-left: 18px;
  width: 95%;
}
.header-title {
  display: flex;
  flex-direction: column;
  width: 95%;
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
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  border-radius: 25px;
  overflow-y: auto;
  margin-left: 5px;
  padding: 0;
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
}

.sales-table th,
.sales-table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #ddd;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.sales-table th {
  background-color: #f4f4f4;
}

.search-container {
  position: relative;
  margin-right: 3px;
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

.filter-btn {
  padding: 10px;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  color: #333;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-btn i {
  font-size: 18px;
}
.filter-btn:hover {
  border-color: #E54F70;
  color: #E54F70;
}
.filter-container {
  position: relative;
}

.dropdown {
  position: absolute;
  top: 45px;
  left: 0;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  padding: 10px;
  z-index: 10;
}

.filter-select {
  padding: 8px;
  font-size: 14px;
  border-radius: 5px;
  margin-bottom: 10px;
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

.add-to-reports-btn {
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
  align-items: center; /* Center vertically */
  justify-content: center; /* Center horizontally */
  position: fixed; /* Fixed position */
  bottom: 20px; /* Distance from the bottom */
  right: 20px; /* Distance from the right */
  z-index: 10;
}

.add-to-reports-btn:hover {
  background-color: #218838; /* Darker green on hover */
}

.selected {
  background-color: #e3f2fd;
}

tr {
  cursor: pointer;
}

input[type="checkbox"] {
  cursor: pointer;
  width: 100%;
  height: 16px;
}
</style>
