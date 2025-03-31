<template>
  <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />
  <SideBar :isCollapsed="isSidebarCollapsed" />
  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="details-container">
      <div class="header-section">
        <button class="back-btn" @click="$router.go(-1)">
          <i class="pi pi-arrow-left"></i> Back
        </button>
        <h1>Product Details</h1>
        <button class="debug-btn" @click="toggleDebugMode">
          {{ showDebug ? 'Hide Debug' : 'Debug Mode' }}
        </button>
      </div>

      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="product" class="content-layout">
        <div class="main-content">
          <div class="product-details-container">
            <!-- Product Details -->
            <div class="product-details">
              <img :src="product.Image || 'https://via.placeholder.com/150'" 
                   alt="Product Image" 
                   class="product-image" />
              <div class="product-title">
                <h2>{{ product.ProductName }}</h2>
                <span class="product-id">ID: {{ product.ProductID }}</span>
              </div>
            </div>

            <div class="details-grid">
              <div class="detail-item">
                <label>Process Type</label>
                <span>{{ product.ProcessType || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <label>Quantity</label>
                <span>{{ product.Quantity }}</span>
              </div>
              <div class="detail-item">
                <label>Current Supplier</label>
                <span class="supplier-name">{{ product.CurrentSupplier || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <label>Status</label>
                <span :class="'status status-' + product.Status?.toLowerCase().replace(/ /g, '-')">
                  {{ product.Status }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="stock-details-sidebar">
          <div class="stock-details-header-container">
            <div class="stock-right">
              <h3 class="stock-details-header">Stock & Deducted Transactions</h3>
              <div class="transaction-filters">
                <button 
                  :class="['filter-btn', { active: transactionFilter === 'added' }]"
                  @click="transactionFilter = 'added'">
                  Added Stock
                </button>
                <button 
                  :class="['filter-btn', { active: transactionFilter === 'deducted' }]"
                  @click="transactionFilter = 'deducted'">
                  Deducted Stock
                </button>
              </div>
            </div>
            <div class="stock-left">
              <div class="date-filter">
                <div class="date-inputs">
                  <div class="date-input">
                    <label>From:</label>
                    <input 
                      type="date" 
                      v-model="dateFilter.from"
                      :max="dateFilter.to || today" />
                  </div>
                  <div class="date-input">
                    <label>To:</label>
                    <input 
                      type="date" 
                      v-model="dateFilter.to"
                      :min="dateFilter.from"
                      :max="today" />
                  </div>
                </div>
                <button class="clear-filter" @click="clearDateFilter">
                  <i class="pi pi-times"></i> Clear
                </button>
              </div>
            </div>
          </div>

          <div class="combined-container" v-if="transactionFilter === 'added'">
            <div class="combined-transactions">
              <table v-if="filteredTransactions.length > 0">
                <thead>
                  <tr>
                    <th>Batch Number</th>
                    <th>Quantity</th>
                    <th>Expiration Date</th>
                    <th>Supplier Name</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in filteredTransactions" :key="item.id">
                    <td>{{ item.batch_number }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ formatDate(item.expiration_date) }}</td>
                    <td>{{ item.SupplierName }}</td>
                    <td>
                      <button class="action-btn delete" @click="deleteAddedTransaction(item.id)">
                        <i class="pi pi-trash"></i> 
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="no-data">
                No added stock available.
              </div>
            </div>
          </div>

          <div class="combined-container" v-if="transactionFilter === 'deducted'">
            <div class="combined-transactions">
              <table v-if="filteredTransactions.length > 0">
                <thead>
                  <tr>
                    <th>Transaction Date</th>
                    <th>Quantity Deducted</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in filteredTransactions" :key="item.TransactionID">
                    <td>{{ formatDate(item.TransactionDate) }}</td>
                    <td>{{ item.QuantityDeducted }}</td>
                    <td>
                      <button class="action-btn delete" @click="deleteDeductedTransaction(item.TransactionID)">
                        <i class="pi pi-trash"></i> 
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="no-data">
                No deducted stock available.
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="error">
        No product found. Please check the product ID.
      </div>

      <!-- Debug Information Panel -->
      <div v-if="showDebug" class="debug-panel">
        <h3>Debug Information</h3>
        <div class="debug-section">
          <h4>Request Information</h4>
          <p><strong>Product ID:</strong> {{ $route.params.id }}</p>
          <p><strong>API Base URL:</strong> {{ INVENTORY_API }}</p>
          <div class="debug-log" v-if="debugLogs.length > 0">
            <h4>API Request Log</h4>
            <div v-for="(log, index) in debugLogs" :key="index" class="log-entry">
              <p><strong>{{ log.timestamp }}</strong></p>
              <p>{{ log.message }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useToast } from 'vue-toastification';
import axios from 'axios';
import Header from '@/components/Header.vue';
import SideBar from '@/components/ims/SideBar.vue';
import { INVENTORY_API } from '@/api/config.js';

export default {
  components: {
    Header,
    SideBar
  },
  data() {
    return {
      isSidebarCollapsed: false,
      product: null,
      loading: true,
      error: null,
      dateFilter: {
        from: '',
        to: ''
      },
      addedTransactions: [],
      deductedTransactions: [],
      transactionFilter: 'added', // Set initial filter to 'added'
      showDebug: false,
      debugLogs: [],
      INVENTORY_API: INVENTORY_API
    };
  },
  computed: {
    today() {
      return new Date().toISOString().split('T')[0];
    },
    filteredTransactions() {
      let transactions = this.transactionFilter === 'added' ? this.addedTransactions : this.deductedTransactions;

      if (this.dateFilter.from || this.dateFilter.to) {
        const fromDate = new Date(this.dateFilter.from);
        const toDate = new Date(this.dateFilter.to);
        toDate.setHours(23, 59, 59); // To include the end of the 'to' date

        transactions = transactions.filter(item => {
          const itemDate = new Date(item.created_at || item.TransactionDate); // Filter by correct date
          return itemDate >= fromDate && itemDate <= toDate;
        });
      }

      return transactions;
    }
  },
  async created() {
    try {
      // Get the product ID from route params
      let productId = this.$route.params.id;
      
      this.addDebugLog(`Original product ID from route: ${productId}`);
      
      // Remove any leading zeros and convert to number if it's a numeric string
      if (/^\d+$/.test(productId.replace(/^0+/, ''))) {
        const numericId = parseInt(productId.replace(/^0+/, ''), 10);
        this.addDebugLog(`Converted ID to numeric: ${numericId}`);
        productId = numericId;
      }
      
      // Try to fetch the product data
      const success = await this.fetchProductData(productId);
      
      if (!success) {
        this.addDebugLog("Failed to fetch product data");
        this.error = `Product with ID ${productId} not found. Please check the ID and try again.`;
        useToast().error(this.error);
      }
    } catch (error) {
      console.error("API Error:", error);
      this.error = error.response?.data?.detail || 'Failed to load product details';
      this.addDebugLog(`Error: ${this.error}`);
      useToast().error(this.error);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    
    // New methods for debug logging
    addDebugLog(message) {
      const timestamp = new Date().toLocaleTimeString();
      this.debugLogs.unshift({ timestamp, message });
      // Keep logs limited to prevent UI clutter
      if (this.debugLogs.length > 50) {
        this.debugLogs.pop();
      }
      console.log(`[DEBUG] ${timestamp}: ${message}`);
    },
    
    // New method to attempt fetching product data with different ID formats
    async fetchProductData(productId) {
      try {
        // Reset error state before attempt
        this.error = null;
        
        this.addDebugLog(`Fetching product with ID: ${productId}`);
        
        // Try all possible API endpoints for product data
        const endpoints = [
          // Main inventory endpoints
          `${INVENTORY_API}/inventoryproducts/${productId}`,
          // Stock-related endpoints
          `${INVENTORY_API}/stockin/${productId}`,
          // Try with and without trailing slash
          `${INVENTORY_API}/inventoryproducts/${productId}/`,
          `${INVENTORY_API}/stockin/${productId}/`,
          // Try product singular endpoint
          `${INVENTORY_API}/product/${productId}`,
          `${INVENTORY_API}/product/${productId}/`
        ];
        
        for (const endpoint of endpoints) {
          try {
            this.addDebugLog(`Trying endpoint: ${endpoint}`);
            const response = await axios.get(endpoint);
            
            if (response.data) {
              this.addDebugLog(`Success! Product found at endpoint: ${endpoint}`);
              this.product = { 
                ...response.data,
                ProductID: productId,
                Status: this.getProductStatus(
                  response.data.Quantity || 0, 
                  response.data.Threshold || 0
                )
              };
              
              // Now fetch stock transactions for this product
              await this.fetchStockTransactions(productId);
              return true;
            }
          } catch (endpointError) {
            this.addDebugLog(`Failed: ${endpoint} - ${endpointError.message}`);
            // Continue to next endpoint
          }
        }
        
        // If we get here, none of the endpoints worked
        this.addDebugLog("Error: No endpoints returned product data");
        throw new Error("No endpoints returned product data");
      } catch (error) {
        this.error = "Product not found with the given ID";
        return false;
      }
    },
    
    // Separate method for fetching stock transactions
    async fetchStockTransactions(productId) {
      try {
        this.addDebugLog(`Fetching stock transactions for product ${productId}`);
        
        // Try to get stock details
        const response = await axios.get(`${INVENTORY_API}/stockdetails/${productId}`);
        
        if (response.data) {
          // Handle added transactions
          this.addedTransactions = (response.data.StockDetails || []).map(transaction => ({
            id: transaction.id || transaction.TransactionID,
            batch_number: transaction.batch_number || transaction.BatchNumber || 'N/A',
            quantity: transaction.quantity || transaction.Quantity || 0,
            expiration_date: transaction.expiration_date || transaction.ExpirationDate,
            SupplierName: transaction.SupplierName || transaction.supplier_name || 'N/A',
            created_at: transaction.created_at || transaction.CreatedAt || new Date().toISOString()
          }));
          
          // Handle deducted transactions
          this.deductedTransactions = (response.data.DeductedTransactions || []).map(transaction => ({
            TransactionID: transaction.TransactionID || transaction.id,
            QuantityDeducted: transaction.QuantityDeducted || transaction.quantity_deducted || 0,
            TransactionDate: transaction.TransactionDate || transaction.transaction_date || new Date().toISOString()
          }));
          
          this.addDebugLog(`Successfully loaded ${this.addedTransactions.length} added and ${this.deductedTransactions.length} deducted transactions`);
        } else {
          this.addDebugLog('No transaction data found in response');
          this.addedTransactions = [];
          this.deductedTransactions = [];
        }
      } catch (error) {
        this.addDebugLog(`Error loading transactions: ${error.message}`);
        // Don't fail the whole page if just transactions fail to load
        this.addedTransactions = [];
        this.deductedTransactions = [];
      }
    },
    
    deleteAddedTransaction(id) {
      this.addedTransactions = this.addedTransactions.filter(item => item.id !== id);
      useToast().success('Added transaction deleted');
    },
    deleteDeductedTransaction(TransactionID) {
      this.deductedTransactions = this.deductedTransactions.filter(item => item.TransactionID !== TransactionID);
      useToast().success('Deducted transaction deleted');
    },
    clearDateFilter() {
      this.dateFilter = { from: '', to: '' };
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString();
      } catch (e) {
        return 'Invalid Date';
      }
    },
    getProductStatus(quantity, threshold) {
      if (quantity <= 0) {
        return 'Out of Stock';
      } else if (quantity <= threshold) {
        return 'Low Stock';
      } else {
        return 'In Stock';
      }
    },
    toggleDebugMode() {
      this.showDebug = !this.showDebug;
    }
  }
};
</script>

<style scoped>
.app-container {
  margin-left: 230px;
  background: #f8f9fa;
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

.app-container.sidebar-collapsed {
  margin-left: 70px; 
}

.details-container {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  max-width: 100%;
  margin: 0 auto;
}

/* Header Styles */
.header-section {
  display: flex;
  align-items: center;
  gap: 25px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 15px;
}

.header-section h1 {
  margin: 0;
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}

.back-btn {
  padding: 10px 20px;
  background: white;
  border: 2px solid #E54F70;
  border-radius: 8px;
  color: #E54F70;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #E54F70;
  color: white;
  transform: translateX(-5px);
}

.content-layout {
  display: grid;
  grid-template-columns: 1fr; /* Single column layout to center everything */
  gap: 30px;
  min-height: calc(100vh - 180px);
}

.details-container {
  display: flex;
  flex-direction: column;
}
.main-content {
  background: white;
  border-radius: 15px;
  padding: 30px;
  display: flex;
  gap: 20px;
  width: auto;
}
.product-details-container {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  width: 100%;
}
.product-details {
  flex: 1;
  max-width: 350px;
}
.details-grid {
  flex: 1;
  max-width: 100%;
}
/* Product Header Styles */
.product-header {
  display: flex;
  align-items: flex-start;
  gap: 30px;
  margin-bottom: 40px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.product-image {
  width: 180px;
  height: 180px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.product-image:hover {
  transform: scale(1.05);
}

.product-title {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 10px;
}

.product-title h2 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
  font-weight: 700;
}

.product-id {
  color: #666;
  font-size: 1rem;
  padding: 4px 12px;
  background: #e9ecef;
  border-radius: 6px;
  display: inline-block;
}

/* Details Grid Styles */
.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
  margin: 30px 0;
  padding: 25px;
  background: white;
  border-radius: 12px;
  border: 1px solid #eee;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.detail-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.detail-item label {
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-item span {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

/* Status Styles */
.status {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 4px;
  font-weight: bold;
  color: #fff;
  text-align: center;
}

.status-in-stock {
  background: #d4edda;
  color: #155724;
}

.status-low-stock {
  background: #fff3cd;
  color: #856404;
}

.status-out-of-stock {
  background: #f8d7da;
  color: #721c24;
}

/* Loading and Error States */
.loading, .error {
  text-align: center;
  padding: 60px;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 500;
}

.loading {
  background: #f8f9fa;
  color: #6c757d;
}

.error {
  background: #fff5f5;
  color: #dc3545;
}
.supplier-name {
  color: #E54F70;
  font-weight: 600;
}
.supplier-tag {
  background: #E54F70;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-block;
}

/* Stock Details Styles */
.stock-details {
  margin-top: 40px;
  padding: 30px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}
.stock-details-sidebar {
  padding: 20px;
  position: sticky;
  top: 20px;
  height: calc(100vh - 140px);
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.stock-cards-container {
  flex: 1;
  overflow-y: auto;
  margin-top: 10px;
  padding-right: 10px;
}

.stock-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stock-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eee;
}

.transaction-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #eee;
  transition: all 0.3s ease;
  position: relative;
  margin-bottom: 15px;
}
.transaction-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(to right, #E54F70, #ff8fa3);
  border-radius: 12px 12px 0 0;
}

.stock-card-header, .transaction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eee;
}

.stock-card-item, .transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 10px;
}
.transaction-card:last-child {
  margin-bottom: 0;
}
.stock-card-item:last-child, .transaction-item:last-child {
  margin-bottom: 0;
}

.value {
  font-weight: 600;
  font-size: 1rem;
  padding: 4px 12px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.value.quantity {
  color: #2e7d32;
  background: #e8f5e9;
}

.value.quantity-deducted {
  color: #E54F70;
  background: #fff5f5;
}

.value.price {
  color: #1976d2;
  background: #e3f2fd;
  font-family: monospace;
  font-size: 1.1rem;
}

.value.expiring {
  color: #f57c00;
  background: #fff3e0;
  animation: pulse 2s infinite;
}

table {
  width: 100%;
  border-collapse: collapse;
}

table th,
table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

table th {
  background-color: #f8f9fa;
  color: #333;
  font-weight: bold;
}

table td {
  background-color: white;
}

table tbody tr:hover {
  background-color: #f1f1f1;
}
.timestamp, .transaction-date {
  font-size: 0.85rem;
  color: #666;
  background: #f8f9fa;
  padding: 4px 10px;
  border-radius: 12px;
}
.stock-details-header {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 20px;
}
.stock-details-header-container{
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stock-right{
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 20px;
}
.stock-left{
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 20px;
}
.date-filter {
  background: #f8f9fa;
  padding: 30px;
  display:flex;
  border-radius: 12px;
}
.transaction-filters {
  display: flex;
  gap: 10px;
  margin: 15px 0;
}

.filter-btn {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid #E54F70;
  background: white;
  color: #E54F70;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: #fff5f5;
}

.filter-btn.active {
  background: #E54F70;
  color: white;
}
.date-inputs {
  display: flex; /* Ensure date inputs are stacked vertically */
  gap: 50px; 
}

.date-input {
  display: block; /* Each date input takes full width */
  margin-bottom: 15px;
}

.date-input label {
  display: block; 
  margin-bottom: 5px;
}

.date-input input {
  width: 100%; 
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.date-input input:hover {
  border-color: #E54F70;
}
.date-input input:focus {
  outline: none;
  border-color: #E54F70;
  box-shadow: 0 0 0 2px rgba(229, 79, 112, 0.1);
}

.clear-filter {
  background: white;
  border: 1px solid #E54F70;
  color: #E54F70;
  padding:  12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  margin-left: 50px;
}

.clear-filter:hover {
  background: #E54F70;
  color: white;
}
.combined-container {
  position: relative;
  flex-grow: 1;
  max-height: 500px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  border-radius: 15px;
  overflow-y: auto;
  margin-left: 5px;
  padding: 0;
}
.action-btn.delete {
  background-color: transparent;
  color: #dc3545;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-btn.delete:hover {
  background-color: rgba(220, 53, 69, 0.1);
}

.no-data {
  padding: 30px;
  text-align: center;
  color: #666;
  font-style: italic;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* Debug panel styles */
.debug-btn {
  padding: 8px 15px;
  background: #f3f3f3;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-left: auto;
  color: #555;
}

.debug-btn:hover {
  background: #e5e5e5;
}

.debug-panel {
  margin-top: 30px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  font-family: monospace;
}

.debug-section {
  margin-bottom: 15px;
}

.debug-section h4 {
  font-size: 14px;
  color: #333;
  margin: 0 0 10px 0;
  border-bottom: 1px solid #ddd;
  padding-bottom: 5px;
}

.debug-log {
  max-height: 400px;
  overflow-y: auto;
  background: #2d2d2d;
  color: #f8f8f8;
  padding: 10px;
  border-radius: 4px;
}

.log-entry {
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #444;
}

.log-entry p {
  margin: 0;
  padding: 2px 0;
}

.log-entry strong {
  color: #9cdcfe;
}

/* Mobile responsiveness for debug panel */
@media (max-width: 768px) {
  .debug-btn {
    font-size: 10px;
    padding: 5px 10px;
  }
  
  .debug-panel {
    font-size: 11px;
  }
}

/* Responsive Styles */
@media (max-width: 768px) {
  .app-container {
    padding: 15px;
    margin-left: 0;
  }
  
  .details-container {
    padding: 20px;
  }
  
  .product-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .product-image {
    width: 150px;
    height: 150px;
  }
  
  .stock-cards {
    grid-template-columns: 1fr;
  }
  .supplier-tag {
    font-size: 0.8rem;
    padding: 3px 10px;
  }
  
  .stock-card-header {
    margin-bottom: 10px;
    padding-bottom: 10px;
  }
  .header-section h1 {
    font-size: 1.5rem;
  }
  date-inputs {
    flex-direction: column;
    gap: 10px;
  }
}
@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .stock-details-sidebar {
    position: relative;
    top: 0;
    height: 500px;
    margin-top: 20px;
  }
}
</style>