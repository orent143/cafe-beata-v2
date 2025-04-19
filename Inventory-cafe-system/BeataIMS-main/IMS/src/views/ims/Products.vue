<template>
  <Header 
    :isSidebarCollapsed="isSidebarCollapsed" 
    @toggle-sidebar="handleSidebarToggle"
    v-model:searchQuery="searchTerm"
    @update:searchQuery="handleSearchUpdate"
  />
  <SideBar :isCollapsed="isSidebarCollapsed"/>
  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <div class="header-title">
      <h1 class="products-header">Product List</h1>
      <p class="products-description">Browse and manage the current inventory of products, including details on pricing, category, and status.</p>
    </div>

      <div class="header-actions">
        <div class="filter-container">
          <div class="filter-label">Filter by</div>
  <button class="filter-btn" @click="toggleFilterDropdown">
    {{ selectedProcessType || 'Process Type' }}
    <i class="pi pi-angle-down"></i>
  </button>
  <div v-if="showFilterDropdown" class="dropdown">
    <select v-model="selectedProcessType" class="filter-select" @change="filterItems">
      <option value="">All Process Types</option>
      <option value="Ready-Made">Ready Made</option>
      <option value="To Be Made">To Be Made</option>
    </select>
          </div>
        </div>
        <button @click="toggleProductTransaction" class="transaction-log-btn">
      <i class="pi pi-history"></i>
      Transaction Log
    </button>
        
      </div>
    </div>

    <div class="inventory-container">
      <table class="stock-table">
        <thead>
      <tr>
        <th>Product ID</th>
        <th>Product Name</th>
        <th>Unit Price</th>
        <th>Category</th>
        <th>Process Type</th>
        <th>Status</th>
        <th>Actions</th>
      </tr>
        </thead>
        <tbody>
          <tr v-for="product in filteredItems" :key="product.id">
            <td>{{ product.ProductID }}</td>
            <td>
              <div class="product-info">
                <img :src="product.Image || 'https://via.placeholder.com/50'" alt="Product Image" class="product-image" />
                <span class="product-name">{{ product.ProductName }}</span>
              </div>
            </td>
            <td>₱{{ product.UnitPrice }}</td>
            <td>{{ getCategoryName(product.CategoryID) }}</td>
            <td>{{ product.ProcessType }}</td> <!-- Display Process Type -->

            <td>
              <span :class="'status status-' + (product.Status ? product.Status.toLowerCase().replace(/ /g, '-') : 'unknown')">
  {{ product.Status || 'Unknown' }}
</span>
            </td>
            <td>
              <button class="action-btn edit" @click="editItem(product)">
                <i class="pi pi-pencil"></i>
              </button>
              <button class="action-btn delete" @click="confirmDelete(product.ProductID)">
  <i class="pi pi-trash"></i>
</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="floating-btn-container">
        <button class="floating-btn" @click="togglePopoutOptions">+</button>
        <div v-if="showPopoutOptions" class="popout-options">
          <button class="popout-option" @click="postInventorySummary">Add Summary</button>
        </div>
      </div>
    </div>

    <div class="modal-overlay" v-if="showConfirmModal">
      <div class="confirmation-modal">
        <div class="modal-content">
          <h3>Confirm Deletion</h3>
          <p>Are you sure you want to delete this product?</p>
          <div class="modal-actions">
            <button @click="confirmSubmit" class="confirm-btn">Yes</button>
            <button @click="cancelSubmit" class="cancel-btn">No</button>
          </div>
        </div>
      </div>
    </div>


    <edit-product
      v-if="showEditForm"
      :isVisible="showEditForm"
      :itemToEdit="selectedItem"
      @close="toggleEditForm"
      @update="handleUpdateProduct"
    />
    <ProductTransaction
    :isVisible="showProductTransaction"
    @close="toggleProductTransaction"
  />
  </div>
</template>

<script>
import axios from 'axios';
import SideBar from '@/components/ims/SideBar.vue';
import EditProduct from '@/components/ims/EditProduct.vue';
import Header from '@/components/Header.vue';
import ProductTransaction from '@/components/ims/ProductTransaction.vue';
import { useToast } from 'vue-toastification';
import { INVENTORY_API, CATEGORIES_API } from '@/api/config.js';

export default {
  components: { EditProduct, SideBar, Header,     ProductTransaction  },
  data() {
    return {
      isSidebarCollapsed: false,
      searchTerm: '',
      selectedStatus: '',
      showFilterDropdown: false,
      selectedProcessType: null,
      showAddForm: false,
      showEditForm: false,
      showPopoutOptions: false,
      selectedItem: null,
      productItems: [],
      filteredItems: [],
      selectedLowStockItems: [],
      isLowStockMode: false,
      currentDate: new Date().toISOString().split('T')[0],
      inventorySummaries: [],
      showConfirmModal: false,
      selectedProductId: null,
      showProductTransaction: false,
      categories: [],
      toast: useToast(),
      refreshInterval: null,
    };
  },

  methods: {
    handleSidebarToggle(collapse) {
      this.isSidebarCollapsed = collapse;
    },
    handleSearchUpdate(query) {
      this.searchTerm = query;
      this.filterItems();
    },
    toggleFilterDropdown() {
      this.showFilterDropdown = !this.showFilterDropdown;
    },
    toggleProductTransaction() {
    this.showProductTransaction = !this.showProductTransaction;
  },

    toggleEditForm() {
      this.showEditForm = !this.showEditForm;
    },
    togglePopoutOptions() {
      this.showPopoutOptions = !this.showPopoutOptions;
    },
    filterItems() {
  let filtered = this.productItems;
  if (this.searchTerm) {
    filtered = filtered.filter(item =>
      item.ProductName.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }
  if (this.selectedProcessType) {
    filtered = filtered.filter(item => item.ProcessType === this.selectedProcessType);
  }
  this.filteredItems = filtered;
  this.showFilterDropdown = false; // Close dropdown after selecting
},
    addItem(newProduct) {
      this.productItems.push(newProduct);
      this.filterItems();
      this.showAddForm = false; 
    },
    async fetchProductItems() {
      try {
        let url = `${INVENTORY_API}/inventoryproducts/all`;

        if (this.selectedProcessType) {
          url = `${INVENTORY_API}/inventoryproducts/filter?process_type=${this.selectedProcessType}`;
        }

        const response = await axios.get(url);

        this.productItems = response.data.map(product => ({
          ...product,
          Status: product.Status || 'Unknown',
          ProductID: product.ProductID || 'N/A'
        }));

        this.filterItems();
      } catch (error) {
        console.error('Error fetching product items:', error);
      }
    },
    confirmDelete(productID) {
    console.log("Confirming delete for ProductID:", productID); // Debug log
    this.selectedProductId = productID;
    this.showConfirmModal = true;
  },
    cancelSubmit() {
      this.showConfirmModal = false;
      this.selectedProductId = null;
    },
    confirmSubmit() {
      this.showConfirmModal = false;
      this.removeItem(this.selectedProductId);
    },
    async removeItem(productId) {
    try {
      if (!productId) {
        this.toast.error("Invalid product ID");
        return;
      }

      console.log("Attempting to delete product with ID:", productId);
      
      const response = await axios.delete(`${INVENTORY_API}/inventoryproduct/${productId}`);
      
      if (response.status === 200) {
        // Use the same ID field for filtering
        this.productItems = this.productItems.filter(item => item.ProductID !== productId);
        this.filterItems();
        this.toast.success("Product deleted successfully!");
      }
    } catch (error) {
      console.error("Error deleting product:", error.response?.data || error);
      const errorMessage = error.response?.data?.detail || "Failed to delete product";
      this.toast.error(errorMessage);
    } finally {
      this.selectedProductId = null;
      this.showConfirmModal = false;
    }
  },
    async fetchCategories() {
      try {
        const response = await axios.get(`${CATEGORIES_API}`);
        this.categories = response.data;
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(cat => cat.id === categoryId);
      return category ? category.CategoryName : 'Unknown';
    },
    async handleUpdateProduct(updatedProduct) {
      try {
        console.log("Updating product in parent:", updatedProduct);

        await this.fetchProductItems();
        
        this.showEditForm = false;
      } catch (error) {
        console.error("Error updating product:", error);
      }
    },
    editItem(product) {
      console.log("Editing product:", product); 
      this.selectedItem = { ...product };
      this.showEditForm = true;
    },
    async postInventorySummary() {
      try {
        const response = await axios.post(`${INVENTORY_API}/inventorysummary`);
        this.inventorySummaries = response.data;
        this.toast.success("Inventory summary generated successfully!");
      } catch (error) {
        console.error('Error posting inventory summary:', error);
        this.toast.error("Failed to generate inventory summary.");
      }
    },
    refreshData() {
      this.toast.info("Refreshing product data...");
      this.fetchProductItems();
    },
  },

  created() {
    this.fetchProductItems();
    this.fetchCategories();
    
    // Set up auto-refresh every 10 seconds
    this.refreshInterval = setInterval(() => {
      console.log("Auto-refreshing products data...");
      this.fetchProductItems();
    }, 10000); // 10 seconds
  },
  
  beforeUnmount() {
    // Clear the refresh interval when component is unmounted
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },

  watch: {
    searchTerm: 'filterItems',
    selectedProcessType: 'filterItems',

    productItems: {
      deep: true,
      handler() {
        localStorage.setItem('productItems', JSON.stringify(this.productItems));
      }
    }
  }
};
</script>

<style scoped>
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
.products-header {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}
.products-description {
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
.stock-table td:first-child {
  font-family: monospace;
  font-size: 14px;
  color: #666;
  font-weight: 500;
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
.filter-btn .pi-angle-down {
  font-size: 17px;
  margin-left: 4px;
}

.filter-btn:hover {
  border-color: #E54F70;
  color: #E54F70;
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
.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 100%;
  z-index: 100;
}

.filter-select {
  width: 100%;
  padding: 8px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  outline: none;
}

.filter-select option {
  padding: 8px;
}
.add-product-btn {
  padding: 8px 12px;
  background-color: #E54F70;
  color: #dbdbdb;
  border: none;
  border-radius: 10px;
  width: 70px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
}

.add-product-btn:hover {
  background-color: #ed9598;
}

.action-btn {
  padding: 8px;
  background-color: transparent;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
  margin-right: 10px;
  width: 35px;
  height: 35px;
  align-items: center;
  justify-content: center;
}

.action-btn.edit {
  color: #1976d2;
}

.action-btn.delete {
  color: #dc3545;
}

.action-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.action-btn:active {
  background-color: rgba(0, 0, 0, 0.2);
}

.floating-btn-container {
  position: fixed; 
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  z-index: 10; 
}

.floating-btn {
  width: 35px;
  height: 35px;
  background-color: #E54F70;
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
}

.floating-btn:hover {
  background-color: #ed9598;
}

.popout-options {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  position: absolute;
  bottom: 0;
  right: 40px;
}

.popout-option {
  background-color: #FFFFFF;
  color: rgb(34, 34, 34);
  padding: 10px;
  margin: 5px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 10px;
  width: 100px;
}

.popout-option:hover {
  background-color: #FF32BA;
}

.popout-option:active {
  background-color: #004080;
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
.status-available {
  background-color: rgba(2, 136, 209, 0.1);
  color: #0288D1;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.confirmation-modal {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-content {
  text-align: center;
}

.modal-content h3 {
  margin-bottom: 15px;
  color: #333;
}

.modal-content p {
  margin-bottom: 20px;
  color: #666;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.cancel-btn, .confirm-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.cancel-btn {
  background-color: #f3f3f3;
  color: #666;
}

.confirm-btn {
  background-color: #E54F70;
  color: white;
}

.cancel-btn:hover {
  background-color: #e7e7e7;
}

.confirm-btn:hover {
  background-color: #d84666;
}
.stock-table td {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}
.transaction-log-btn {
  padding: 8px 16px;
  background-color: #fff;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.transaction-log-btn:hover {
  border-color: #E54F70;
  color: #E54F70;
}

.refresh-btn {
  padding: 8px 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.refresh-btn:hover {
  background-color: #45a049;
}

.refresh-btn i {
  font-size: 14px;
}
</style>