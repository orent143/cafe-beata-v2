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
        <button class="add-quantity-btn" @click="openAddQuantityModal">
           Add Quantity
        </button>
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
            <tr v-for="sale in salesData" :key="sale.product_id">
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
    
    <!-- Add Quantity Modal -->
    <!-- Add Quantity Modal -->
<div v-if="showAddQuantityModal" class="modal-overlay">
  <div class="modal-content">
    <h3>Add Beginning Quantity</h3>

    <div class="modal-form-group">
      <label for="productInput">Product</label>
      <!-- Input field for product name -->
      <input 
        type="text" 
        id="productInput" 
        v-model="selectedProductName"
        class="modal-input" 
        placeholder="Enter product name"
        @input="filterProductByName"
      />
      <div class="filtered-products-list">
  <li 
    v-for="product in filteredProducts" 
    :key="product.product_id"
    @click="selectProduct(product)"
  >
    {{ product.name }}
  </li>
</div>

    </div>

    <div class="modal-form-group">
      <label for="quantityInput">Quantity</label>
      <input
        type="number"
        id="quantityInput"
        v-model.number="modalQuantity"
        min="0"
        class="modal-input"
        placeholder="Enter quantity"
      />
    </div>

    <div class="modal-form-group">
      <label for="dateInput">Date</label>
      <input
        type="date"
        id="dateInput"
        v-model="modalDate"
        class="modal-input"
      />
    </div>

    <div class="modal-actions">
      <button class="cancel-btn" @click="closeAddQuantityModal">Cancel</button>
      <button class="confirm-btn" @click="confirmAddQuantity">Confirm</button>
    </div>
  </div>
</div>

    
    <!-- Confirmation Modal -->
    <div v-if="showConfirmationModal" class="modal-overlay">
      <div class="modal-content confirmation-modal">
        <h3>Confirm Update</h3>
        <p>Are you sure you want to update the beginning quantity?</p>
        
        <div class="confirmation-details">
          <p><strong>Product:</strong> {{ selectedProductName }}</p>
          <p><strong>Quantity:</strong> {{ modalQuantity }}</p>
          <p><strong>Date:</strong> {{ modalDate }}</p>
        </div>
        
        <div class="modal-actions">
          <button class="confirm-btn" @click="submitQuantityUpdate">Yes, Update</button>
          <button class="cancel-btn" @click="closeConfirmationModal">Cancel</button>
        </div>
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
      filteredProducts: [],  
      showFilterDropdown: false,
      selectedDate: new Date().toISOString().slice(0, 10), // Default to today
      toast: useToast(),
      searchTerm: '',
      
      // Add Quantity Modal
      showAddQuantityModal: false,
      selectedProductName: '',
      modalQuantity: '',
      modalDate: new Date().toISOString().slice(0, 10), // Default to today
      
      // Confirmation Modal
      showConfirmationModal: false
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
        const params = this.selectedDate ? { filter_date: this.selectedDate } : {};
        const response = await axios.get(`${SALES_API}/sales`, { params });
        this.salesData = response.data;

        console.log("Sales data:", this.salesData);
        console.log("Fetched Sales Data:", this.salesData);
      } catch (error) {
        console.error("Error fetching sales data:", error);
        this.toast.error("Failed to fetch sales data. Please try again.");
      }
    },
    
    toggleFilterDropdown() {
      this.showFilterDropdown = !this.showFilterDropdown;
    },
    
    filterSalesData() {
      if (!this.searchTerm) {
        return;
      }
      
      const searchLower = this.searchTerm.toLowerCase();
      this.$nextTick(() => {
        const tableElement = document.querySelector('.sales-table tbody');
        if (tableElement) {
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

    openAddQuantityModal() {
  this.fetchSalesData(); // ensure updated list
  this.selectedProductName = '';
  this.selectedProductId = '';
  this.modalQuantity = '';
  this.modalDate = this.selectedDate || new Date().toISOString().slice(0, 10);
  
  // If no sales data is available, show a message
  if (this.salesData.length === 0) {
    this.toast.error("No sales data available. Please try again later.");
  }
  
  this.showAddQuantityModal = true;
},
    
    closeAddQuantityModal() {
      this.showAddQuantityModal = false;
    },
    
    // Filter Product by Name as user types
    filterProductByName() {
  // Filter sales data based on product name
  this.filteredProducts = this.salesData.filter(product => 
    product.name.toLowerCase().includes(this.selectedProductName.toLowerCase())
  );
},

    selectProduct(product) {
  this.selectedProductName = product.name;
  if (!this.selectedProductName) {
  this.toast.error("Please select a product");
  return;
}
  console.log("Selected Product ID: ", this.selectedProductId);  // Debugging line
  console.log("Selected Product Name: ", this.selectedProductName);  // Debugging line
  this.filteredProducts = [];  // Clear filtered list after selection
},

confirmAddQuantity() {
  console.log({
    selectedProductName: this.selectedProductName,
    modalQuantity: this.modalQuantity,
    modalDate: this.modalDate
  });

  if (!this.selectedProductName) {
    this.toast.error("Please select a product");
    return;
  }

  if (!this.modalQuantity || this.modalQuantity < 0) {
    this.toast.error("Please enter a valid quantity");
    return;
  }

  if (!this.modalDate) {
    this.toast.error("Please select a date");
    return;
  }

  // Proceed with the update or submission of the quantity
  this.showConfirmationModal = true;
},
    
    // Confirmation Modal Methods
    closeConfirmationModal() {
      this.showConfirmationModal = false;
    },
    
    async submitQuantityUpdate() {
  try {
    // Make sure all the required fields are populated
    if (!this.selectedProductName) {
  this.toast.error("Please select a product");
  return;
}

    if (!this.modalQuantity || this.modalQuantity < 0) {
      this.toast.error("Please enter a valid quantity");
      return;
    }

    if (!this.modalDate) {
      this.toast.error("Please select a date");
      return;
    }

    // Send a PUT request to the backend
    const response = await axios.put(`${SALES_API}/inventory/beginning-quantity`, {
  product_name: this.selectedProductName,
  quantity: this.modalQuantity,
  date: this.modalDate
});

    // Handle the response
    this.toast.success("Beginning quantity updated successfully");
    this.closeConfirmationModal();
    this.closeAddQuantityModal();
    this.fetchSalesData(); // Refresh the sales data after update
  } catch (error) {
    console.error("Error updating beginning quantity:", error.response?.data?.detail || error);
    this.toast.error("Failed to update beginning quantity");
    this.closeConfirmationModal();
  }
}

  },
  mounted() {
    this.fetchSalesData(); // Initial fetch on page load
  }
};
</script>


<style scoped>
/* Base styles from original component */
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
  width: 70%; /* Reduced to make room for buttons */
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
  color: #343a40;
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

/* Add Quantity Button */
.add-quantity-btn {
  padding: 10px;
  background-color: #E54F70;
      border: 1px solid #ccc;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    color: white;
    transition: color 0.3s;
    display: flex
;
    align-items: center;
    gap: 8px;
}

.add-quantity-btn:hover {
  background-color: #752939;
}

.add-quantity-btn i {
  font-size: 14px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 10px;
  width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  font-size: 25px;
    font-family: 'Arial', sans-serif;
    font-weight: 1000;
    color: #000000;
}

.modal-form-group {
  margin-bottom: 15px;
}

.modal-form-group label {
  font-weight: 600;
    font-size: 14px;
    margin-bottom: 5px;
    display: block;
    color: #272727;
}

.modal-input {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.modal-actions button {
  padding: 10px 20px;
  background-color: #E54F70;
  color: #dbdbdb;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}


.confirm-btn:hover {
  background-color: #a33950;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
}

.cancel-btn:hover {
  background-color: #d32f2f;
}

/* Confirmation Modal */
.confirmation-modal {
  text-align: center;
}

.confirmation-details {
  margin: 20px 0;
  text-align: left;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 5px;
}

.confirmation-details p {
  margin: 10px 0;
}

.confirmation-details strong {
  display: inline-block;
  width: 80px;
}
.filtered-products-list {
  max-height: 120px; /* Adjust as needed */
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-top: 5px;
  padding: 5px;
  background-color: #fff;
}

.filtered-products-list li {
  padding: 6px;
  cursor: pointer;
  list-style-type: none;
}

.filtered-products-list li:hover {
  background-color: #f0f0f0;
}

</style>