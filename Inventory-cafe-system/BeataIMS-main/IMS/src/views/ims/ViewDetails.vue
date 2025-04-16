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
      </div>

      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="content-layout">

        <div class="product-info-section">
          <div class="product-details-container">
            <!-- Product Details -->
            <div class="product-details">
              <img :src="getProductImageUrl(product?.Image)" 
                   alt="Product Image" 
                   class="product-image"
                   @error="handleImageError" />
              <div class="product-title" v-if="product">
                <h2>{{ product.ProductName }}</h2>
                <span class="product-id">ID: {{ product.ProductID }}</span>
              </div>
              <div class="product-title" v-else>
                <h2>Product Not Found</h2>
                <span class="product-id">ID: {{ $route.params.id }}</span>
              </div>
            </div>

            <div class="details-grid">
              <div class="detail-item">
                <label>Process Type</label>
                <span>{{ product.ProcessType || product.process_type || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <label>Quantity</label>
                <span>{{ product.Quantity || product.quantity || 0 }}</span>
              </div>
              <div class="detail-item">
                <label>Current Supplier</label>
                <span class="supplier-name">{{ product.CurrentSupplier || product.supplier_name || product.supplier || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <label>Status</label>
                <span :class="'status status-' + getStockStatusClass(product.Quantity).replace('status-', '')">
                  {{ getStockStatus(product.Quantity) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="transactions-section">
          <div class="transactions-header">
            <h3>Stock & Deducted Transactions</h3>
            <div class="transactions-filter-controls">
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
                  <button class="clear-filter" @click="clearDateFilter">
                    <i class="pi pi-times"></i> Clear
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="transactions-content">
            <div class="transactions-table" v-if="transactionFilter === 'added'">
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

            <div class="transactions-table" v-if="transactionFilter === 'deducted'">
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
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Header from '@/components/Header.vue';
import SideBar from '@/components/ims/SideBar.vue';
import { useToast } from 'vue-toastification';
import { API_BASE_URL } from '@/api/config.js';

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
      imageError: false
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
  created() {
    this.fetchProductDetails();
  },
  mounted() {
    // No special handling for product 100 needed anymore
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
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
    handleImageError(e) {
      this.imageError = true;
      // Use a data URL instead of external service or local file
      e.target.src = 'data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22180%22%20height%3D%22180%22%3E%3Crect%20fill%3D%22%23eee%22%20width%3D%22180%22%20height%3D%22180%22%2F%3E%3Ctext%20fill%3D%22%23999%22%20font-family%3D%22Arial%2CSans-serif%22%20font-size%3D%2220%22%20text-anchor%3D%22middle%22%20x%3D%2290%22%20y%3D%2290%22%3ENo%20Image%3C%2Ftext%3E%3C%2Fsvg%3E';
    },
    getProductImageUrl(imagePath) {
      if (!imagePath) {
        // Use a data URL instead of external service or local file
        return 'data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22180%22%20height%3D%22180%22%3E%3Crect%20fill%3D%22%23eee%22%20width%3D%22180%22%20height%3D%22180%22%2F%3E%3Ctext%20fill%3D%22%23999%22%20font-family%3D%22Arial%2CSans-serif%22%20font-size%3D%2220%22%20text-anchor%3D%22middle%22%20x%3D%2290%22%20y%3D%2290%22%3ENo%20Image%3C%2Ftext%3E%3C%2Fsvg%3E';
      }
      
      console.log('Processing image path:', imagePath);
      
      // If it's already a full URL, return it
      if (imagePath.startsWith('http')) {
        return imagePath;
      }
      
      // For local development - check if we have a direct product image
      // This might be in the format like: /uploads/products/water.jpg or just water.jpg
      const baseUrl = API_BASE_URL;
      
      // If path is just a filename (no slashes)
      if (!imagePath.includes('/')) {
        return `${baseUrl}/uploads/products/${imagePath}`;
      }
      
      // If path starts with /uploads
      if (imagePath.startsWith('/uploads') || imagePath.includes('/uploads/')) {
        // Ensure no double slash
        const cleanPath = imagePath.startsWith('/') ? imagePath.substring(1) : imagePath;
        return `${baseUrl}/${cleanPath}`;
      }
      
      // Default case - just join the base URL and path
      return `${baseUrl}/${imagePath.startsWith('/') ? imagePath.substring(1) : imagePath}`;
    },
    async fetchProductDetails() {
      try {
        // Get the product ID from the route params
        let productId = this.$route.params.id;
        
        if (!productId) {
          throw new Error("Invalid product ID in the URL");
        }
        
        // Make sure we're using a numeric ID
        productId = parseInt(productId, 10).toString();
        console.log(`Fetching details for product ID: ${productId}`);
        
        // Try all possible endpoints until we find the product
        let baseUrl = API_BASE_URL;
        let productResponse = null;
        let lastError = null;
        
        // Try each possible endpoint
        const endpoints = [
          `/api/inventory/products/${productId}`,
          `/api/products/${productId}`,
          `/api/inventoryproducts/${productId}`,
          `/api/inventory/${productId}`,
          `/api/stock/stockin/${productId}`,
          // Add additional endpoints if needed
        ];
        
        for (const endpoint of endpoints) {
          try {
            console.log(`Trying: ${baseUrl}${endpoint}`);
            const response = await axios.get(`${baseUrl}${endpoint}`, { timeout: 5000 });
            if (response.data) {
              productResponse = response;
              console.log('Found product at:', baseUrl + endpoint);
              break;
            }
          } catch (error) {
            console.log(`Failed endpoint ${endpoint}:`, error.message);
            lastError = error;
            // Continue to next endpoint rather than failing immediately
          }
        }
        
        // If we still couldn't find it, create a fallback product instead of throwing an error
        if (!productResponse) {
          console.log(`Product ID ${productId} not found in any endpoint`);
          this.createFallbackProduct(productId);
          return; // Exit the method early
        }
        
        // Extract product data
        let productData = null;
        if (productResponse.data && productResponse.data.product) {
          productData = productResponse.data.product;
        } else if (productResponse.data) {
          productData = productResponse.data;
        }
        
        // Assign product data and normalize properties
        this.product = { ...productData };
        this.normalizeProductData(productId);
        
        // Now try to get stock details
        await this.fetchStockDetails(productId, baseUrl);
        
      } catch (error) {
        console.error("API Error:", error);
        this.error = error.message;
        this.createFallbackProduct(this.$route.params.id);
      } finally {
        this.loading = false;
      }
    },
    
    normalizeProductData(productId) {
      // Make sure we have at least basic properties with proper casing
      this.product.ProductID = this.product.ProductID || this.product.id || productId;
      this.product.ProductName = this.product.ProductName || this.product.name || this.product.product_name || "Product " + productId;
      this.product.Quantity = this.product.Quantity !== undefined ? this.product.Quantity : 
                              (this.product.quantity !== undefined ? this.product.quantity : 0);
      this.product.ProcessType = this.product.ProcessType || this.product.process_type || 'N/A';
      this.product.CurrentSupplier = this.product.CurrentSupplier || this.product.supplier_name || this.product.supplier || 'N/A';
      
      // Set status based on quantity
      const quantity = Number(this.product.Quantity || this.product.quantity || 0);
      
      if (quantity <= 0) {
        this.product.Status = 'Out of Stock';
      } else if (quantity <= 10) {
        this.product.Status = 'Low Stock';
      } else {
        this.product.Status = 'In Stock';
      }
    },
    
    async fetchStockDetails(productId, baseUrl) {
      // Try to get stock details for this product
      const stockEndpoints = [
        `/api/stock/stockdetails/${productId}`,
        `/api/inventory/stockdetails/${productId}`,
        `/api/inventory/stock/${productId}`,
        `/api/stock/stockin/${productId}/details`
      ];
      
      let stockResponse = null;
      
      for (const endpoint of stockEndpoints) {
        try {
          console.log(`Trying stock details: ${baseUrl}${endpoint}`);
          const response = await axios.get(`${baseUrl}${endpoint}`, { timeout: 5000 });
          if (response.data) {
            stockResponse = response;
            console.log('Found stock details at:', baseUrl + endpoint);
            break;
          }
        } catch (error) {
          console.log(`Failed stock endpoint ${endpoint}:`, error.message);
        }
      }
      
      // If we have the stock data from the stockin endpoint but it's not in the expected format,
      // try to adapt it to the expected format
      if (stockResponse && !stockResponse.data.StockDetails && !stockResponse.data.DeductedTransactions) {
        console.log('Converting stockin response to expected format');
        
        // Create compatible structures based on the data we have
        const stockData = stockResponse.data;
        if (stockData) {
          // We might not have transaction details in this endpoint, but we can at least show current data
          this.addedTransactions = [{
            id: stockData.ProductID,
            batch_number: 'Current Stock',
            quantity: stockData.Quantity,
            expiration_date: null,
            created_at: new Date().toISOString(),
            SupplierName: stockData.CurrentSupplier || 'N/A'
          }];
          
          this.deductedTransactions = [];
          return;
        }
      }
      
      // If we still couldn't find it, create a fallback product instead of throwing an error
      if (!stockResponse) {
        console.log(`Product ID ${productId} not found in any stock endpoint`);
        this.addedTransactions = [];
        this.deductedTransactions = [];
        return;
      }
      
      // Extract stock data
      let stockData = null;
      if (stockResponse.data && stockResponse.data.StockDetails) {
        stockData = stockResponse.data.StockDetails;
      } else if (stockResponse.data) {
        stockData = stockResponse.data;
      }
      
      // Assign stock data
      this.addedTransactions = stockData || [];
      this.deductedTransactions = stockResponse.data.DeductedTransactions || [];
      
      // Get supplier name from transactions
      this.updateSupplierFromTransactions();
    },
    
    updateSupplierFromTransactions() {
      if (this.addedTransactions.length > 0) {
        // Sort transactions by date to get the most recent one
        const sortedTransactions = [...this.addedTransactions].sort((a, b) => {
          const dateA = new Date(a.created_at || a.date || a.TransactionDate || 0);
          const dateB = new Date(b.created_at || b.date || b.TransactionDate || 0);
          return dateB - dateA; // Most recent first
        });
        
        // Update the current supplier from the most recent transaction
        const mostRecentTransaction = sortedTransactions[0];
        
        // Check different possible field names for supplier name
        const supplierName = mostRecentTransaction.SupplierName || 
                            mostRecentTransaction.supplier_name || 
                            mostRecentTransaction.supplier;
                            
        if (supplierName) {
          console.log(`Setting supplier name to: ${supplierName}`);
          this.product.CurrentSupplier = supplierName;
        }
        
        // Normalize supplier names in all transactions
        this.addedTransactions = this.addedTransactions.map(transaction => {
          if (!transaction.SupplierName) {
            transaction.SupplierName = transaction.supplier_name || 
                                      transaction.supplier ||
                                      'Unknown';
          }
          return transaction;
        });
      }
    },
    
    createFallbackProduct(productId) {
      this.product = {
        ProductID: productId || this.$route.params.id,
        ProductName: "Product Not Found",
        ProcessType: "N/A",
        Quantity: 0,
        CurrentSupplier: "Unknown",
        Status: "Unknown",
        Image: null
      };
      
      // Set a user-friendly error message
      this.error = `The product with ID ${productId || this.$route.params.id} could not be found. It may have been deleted or does not exist.`;
      
      // Clear transaction data
      this.addedTransactions = [];
      this.deductedTransactions = [];
    },
    getStockStatusClass(quantity) {
      if (quantity <= 0) {
        return 'out-of-stock';
      } else if (quantity <= 10) {
        return 'low-stock';
      } else {
        return 'in-stock';
      }
    },
    getStockStatus(quantity) {
      if (quantity <= 0) {
        return 'Out of Stock';
      } else if (quantity <= 10) {
        return 'Low Stock';
      } else {
        return 'In Stock';
      }
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
  padding: 20px;
}

.app-container.sidebar-collapsed {
  margin-left: 70px; 
}

.details-container {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  max-width: 1200px;
  margin: 0 auto;
}

/* Header Styles */
.header-section {
  display: flex;
  align-items: center;
  gap: 25px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 15px;
  margin-bottom: 25px;
}

.header-section h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
  font-weight: 700;
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
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* Product Details Section */
.product-info-section {
  background: white;
  border-radius: 12px;
  padding: 0;
  border: 1px solid #eee;
}

.product-details-container {
  display: flex;
  flex-wrap: wrap;
  gap: 25px;
  padding: 20px;
}

.product-details {
  flex: 1;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 12px;
}

.product-image {
  width: 180px;
  height: 180px;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  background: white;
  padding: 10px;
}

.product-image:hover {
  transform: scale(1.05);
}

.product-title {
  text-align: center;
  width: 100%;
}

.product-title h2 {
  font-size: 1.6rem;
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.product-id {
  color: #666;
  font-size: 0.9rem;
  padding: 4px 12px;
  background: #e9ecef;
  border-radius: 6px;
  display: inline-block;
}

.details-grid {
  flex: 2;
  min-width: 300px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  background: #f8f9f9;
  border-radius: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
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

/* Transactions Section */
.transactions-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #eee;
}

.transactions-header {
  margin-bottom: 20px;
}

.transactions-header h3 {
  font-size: 1.3rem;
  margin: 0 0 15px 0;
  color: #333;
  font-weight: 600;
}

.transactions-filter-controls {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.transaction-filters {
  display: flex;
  gap: 10px;
}

.filter-btn {
  padding: 8px 15px;
  background: #f1f1f1;
  border: none;
  border-radius: 6px;
  color: #555;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: #e0e0e0;
}

.filter-btn.active {
  background: #E54F70;
  color: white;
}

.date-filter {
  display: flex;
  align-items: center;
  gap: 15px;
}

.date-inputs {
  display: flex;
  gap: 15px;
  align-items: center;
}

.date-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input label {
  font-weight: 500;
  color: #555;
}

.date-input input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #333;
}

.clear-filter {
  padding: 8px 15px;
  background: #f1f1f1;
  border: none;
  border-radius: 6px;
  color: #555;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.clear-filter:hover {
  background: #e0e0e0;
}

/* Transactions Table Styles */
.transactions-table {
  width: 100%;
  overflow-x: auto;
  margin-top: 15px;
}

.transactions-table table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.transactions-table th {
  background: #f8f9fa;
  color: #333;
  font-weight: 600;
  padding: 12px 15px;
  border-bottom: 2px solid #e9ecef;
}

.transactions-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #e9ecef;
  color: #555;
}

.transactions-table tr:hover {
  background: #f8f9fa;
}

.action-btn {
  padding: 6px 10px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6c757d;
}

.action-btn.delete {
  color: #dc3545;
}

.action-btn.delete:hover {
  background: #f8d7da;
}

.no-data {
  text-align: center;
  padding: 30px;
  color: #6c757d;
  background: #f8f9fa;
  border-radius: 8px;
}

/* Responsive Styles */
@media (max-width: 992px) {
  .product-details-container {
    flex-direction: column;
  }
  
  .details-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .transactions-filter-controls {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .app-container {
    margin-left: 0;
    padding: 15px;
  }
  
  .details-container {
    padding: 15px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .date-inputs {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 576px) {
  .product-details {
    padding: 15px;
  }
  
  .product-image {
    width: 150px;
    height: 150px;
  }
  
  .transactions-table {
    font-size: 0.9rem;
  }
  
  .transactions-table th,
  .transactions-table td {
    padding: 8px 10px;
  }
}
</style>