<template>
  <Header 
    :isSidebarCollapsed="isSidebarCollapsed" 
    @toggle-sidebar="handleSidebarToggle"
    v-model:searchQuery="searchTerm"
    @update:searchQuery="handleSearchUpdate"
  />
  <SideBar :isCollapsed="isSidebarCollapsed" />
  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <div class="header-title">
      <h1 class="products-header">Inventory List</h1>
      <p class="sub-description">
        Monitor current stock levels, pricing, and product details. Use filters to narrow down inventory by process type.
      </p>
    </div>
      <div class="header-actions">
        <div class="filter-container">
          <div class="filter-label">Filtered by</div>
          <button class="filter-btn" @click="toggleFilterDropdown">
            {{ selectedProcessType || 'Process Type' }}
          </button>
        </div>
        <button @click="toggleTransactionLog" class="transaction-log-btn">
          <i class="pi pi-history"></i>
          Transaction Log
        </button>
      </div>
    </div>

    <!-- Stock Summary Banner -->
    <div v-if="stockSummary.total > 0" class="stock-summary-banner" style="display: none;">
      <span class="summary-title">Stock Status:</span>
      <div class="summary-stats">
        <span class="total-stock-count">
          {{ stockSummary.total }} Total Items
        </span>
      </div>
    </div>

    <div class="inventory-container">
      <table class="stock-table">
        <thead>
          <tr>
            <th>Product ID</th>
            <th>Product Name</th>
            <th>Quantity</th>
            <th>Unit Price</th>
            <th class="details-header">Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in filteredItems" :key="product.id">
            <td class="product-id">{{ product.ProductID || 'N/A' }}</td>
            <td>
              <div class="product-info">
                <span class="product-name">{{ product.ProductName || 'Unnamed Product' }}</span>
              </div>
            </td>
            <td>
              <div class="quantity-indicator" :class="getQuantityClass(product.Quantity, product.Threshold)">
                {{ product.Quantity !== undefined ? product.Quantity : 0 }}
              </div>
            </td>
            <td>₱{{ product.UnitPrice || '0.00' }}</td>
            <td>
              <div class="details-container">
                <button class="btn-details" @click="viewDetails(product)">
                  VIEW DETAILS
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <transaction-log 
      :isVisible="showTransactionLog"
      @close="toggleTransactionLog"
    />
  </div>
</template>

<script>
import axios from 'axios';
import SideBar from '@/components/ims/SideBar.vue';
import Header from '@/components/Header.vue';
import TransactionLog from '@/components/ims/TransactionLog.vue';
import { useToast } from 'vue-toastification';
import { INVENTORY_API } from '@/api/config.js';

export default {
  components: { SideBar, Header, TransactionLog },
  data() {
    return {
      isSidebarCollapsed: false,
      searchTerm: '',
      showFilterDropdown: false,
      selectedProcessType: 'Ready-Made', // Default to Ready-Made
      showPopoutOptions: false,
      selectedItem: null,
      productItems: [],
      filteredItems: [],
      selectedLowStockItems: [],
      isLowStockMode: false,
      currentDate: new Date().toISOString().split('T')[0],
      selectedProductId: null,
      showTransactionLog: false,
      categories: [],
      toast: useToast(),
      stockSummary: {
        total: 0,
        outOfStock: 0,
        lowStock: 0,
      },
      refreshInterval: null, // New property for the refresh interval timer
    };
  },

  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    handleSearchUpdate(query) {
      this.searchTerm = query;
      this.filterItems();
    },
    toggleFilterDropdown() {
      this.showFilterDropdown = !this.showFilterDropdown;
    },
    toggleTransactionLog() {
      this.showTransactionLog = !this.showTransactionLog;
    },
    viewDetails(product) {
      if (!product || !product.id) {
        this.toast.error('Invalid product details');
        return;
      }
      
      // Get the numeric ID without leading zeros
      const numericId = parseInt(String(product.id).replace(/^0+/, ''), 10);
      
      // Format the ID for display (with leading zeros)
      const displayId = String(numericId).padStart(4, '0');
      
      console.log('Navigating to product details:', {
        originalId: product.id,
        numericId: numericId,
        displayId: displayId
      });
      
      // Navigate to the details page with the numeric ID
      this.$router.push({
        name: 'ViewDetailsVue',
        params: { id: numericId }
      });
    },


    filterItems() {
      let filtered = this.productItems;

      if (this.searchTerm) {
        filtered = filtered.filter(item =>
          item.ProductName.toLowerCase().includes(this.searchTerm.toLowerCase())
        );
      }

      // Ensure filtering is applied only to "Ready-Made" products
      filtered = filtered.filter(item => item.ProcessType === "Ready-Made");

      this.filteredItems = filtered;
      this.showFilterDropdown = false;
      
      // Recalculate stock summary when filtered items change
      this.calculateStockSummary();
    },

    getQuantityClass(quantity, threshold) {
      if (quantity <= 0) {
        return 'out-of-stock';
      } else if (quantity <= threshold) {
        return 'low-stock'; // Low stock based on threshold
      } else {
        return 'in-stock'; // In stock
      }
    },

    getStockStatus(quantity, threshold) {
  quantity = Number(quantity);
  threshold = Number(threshold);

  if (quantity <= 0) {
    return 'Out of Stock';
  } else if (quantity <= threshold) {
    return 'Low Stock';
  } else {
    return 'In Stock';
  }
},

    // Get CSS class for stock status
    getStockStatusClass(quantity) {
      quantity = Number(quantity);
      
      if (quantity <= 0) {
        return 'out-of-stock-status';
      } else if (quantity <= 10) {
        return 'low-stock-status';
      } else {
        return 'in-stock-status';
      }
    },

    // Fetch products and map threshold data
    async fetchProductItems() {
      try {
        let url = `${INVENTORY_API}/inventoryproducts/filter?process_type=Ready-Made`;
        const response = await axios.get(url);

        this.productItems = response.data.map(item => {
          // Create a properly formatted product ID for display
          const formattedId = item.id ? String(item.id).padStart(4, '0') : 'N/A';
          
          return {
            ...item,
            ProductID: formattedId,
            // Make sure we preserve the original ID for routing
            id: item.id,
            Status: this.getStockStatus(item.Quantity, item.Threshold)
          };
        });

        console.log('Loaded products:', this.productItems);
        this.filterItems();
        this.calculateStockSummary();
      } catch (error) {
        console.error('Error fetching product items:', error);
        this.toast.error('Error loading inventory items. Please try again.');
      }
    },
    
    // Calculate the stock summary stats
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
      
      // Update the summary object
      this.stockSummary = {
        total: this.filteredItems.length,
        outOfStock: outOfStock,
        lowStock: lowStock
      };
      
      console.log("Stock summary updated:", this.stockSummary);
    },

    // Add new refresh method
    refreshData() {
      this.toast.info("Refreshing inventory data...");
      this.fetchProductItems();
    },
  },

  created() {
    const productId = this.$route.params.id;
    console.log("Product ID:", productId);
    this.fetchProductItems();
    
    // Set up auto-refresh every 10 seconds
    this.refreshInterval = setInterval(() => {
      console.log("Auto-refreshing inventory data...");
      this.fetchProductItems();
    }, 10000); // 10 seconds
  },
  
  beforeUnmount() {
    // Clear the refresh interval when component is unmounted
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },

  mounted() {
    this.fetchProductItems();
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
    padding: 10px;
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }
  
  .stock-table th,
  .stock-table td {
    padding: 15px;
    text-align: center;
    border-bottom: 1px solid #eee;
    vertical-align: middle;
  }
  
  .stock-table tbody {
    font-size: 15px;
  }
  
  .stock-table th {
    background-color: #f4f4f4;
    color: #333;
    font-weight: bold;
  }
  
  .stock-table th:nth-child(1),
  .stock-table td:nth-child(1) {
    width: 15%;
  }
  
  .stock-table th:nth-child(2),
  .stock-table td:nth-child(2) {
    width: 25%;
  }
  
  .stock-table th:nth-child(3),
  .stock-table td:nth-child(3) {
    width: 20%;
  }
  
  .stock-table th:nth-child(4),
  .stock-table td:nth-child(4) {
    width: 15%;
  }
  
  .stock-table th:nth-child(5),
  .stock-table td:nth-child(5) {
    width: 25%;
  }
  
  .product-id {
    font-family: monospace;
    color: #666;
    font-weight: 500;
  }
  

  .product-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
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
  

  
  .quantity-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .quantity-value {
    font-weight: bold;
    min-width: 60px;
    text-align: center;
    color: #000;
  }

  .stock-status {
    padding: 4px 8px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: 500;
    background-color: transparent;
  }

  /* Stock status specific styles */
  .out-of-stock-status {
    color: #F44336;
    background-color: transparent;
  }

  .low-stock-status {
    color: #FF9800;
    background-color: transparent;
  }

  .in-stock-status {
    color: #4CAF50;
    background-color: transparent;
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
  .details-header {
  text-align: center;
}
.details-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.details-text {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
  text-align: center;
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

/* Style for stock summary banner */
.stock-summary-banner {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 12px 20px;
  margin: 0 10px 20px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.summary-title {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.summary-stats {
  display: flex;
  gap: 20px;
}

.out-of-stock-count {
  color: #F44336;
  font-weight: 600;
}

.low-stock-count {
  color: #FF9800;
  font-weight: 600;
}

.total-stock-count {
  color: #555;
  font-weight: 500;
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

.quantity-indicator {
  padding: 4px 8px;
  border-radius: 15px;
  font-size: 14px;
  display: inline-block;
}

.out-of-stock {
  background: #F8D7DA;
  color: #721c24;
}

.low-stock {
  background: #FFF3E0;
  color: #FF9800;
}

.in-stock {
  background: #E8F5E9;
  color: #4CAF50;
}
  </style>