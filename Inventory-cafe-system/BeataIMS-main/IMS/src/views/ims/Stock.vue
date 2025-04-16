<template>
  <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />
  <SideBar :isCollapsed="isSidebarCollapsed" />
  
  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="main-container">
      <div class="header-container">
        <h1 class="header">Add Stock</h1>
      </div>

      <div class="content-wrapper">
        <div class="form-container">
          <form @submit.prevent="submitForm">
            <div class="form-section">
              <h2 class="section-title">Stock Details</h2>
              <div class="form-group">
                <label>Stock ID</label>
                <div class="stock-id-input">
                  <input 
                    list="product-list"
                    v-model.trim="stockData.StockID" 
                    type="text"
                    required
                    class="form-input"
                    placeholder="Enter Stock ID or select from list"
                    @change="handleStockSelection"
                  />
                  <datalist id="product-list">
                    <option 
                      v-for="product in inventoryProducts" 
                      :key="product.ProductID" 
                      :value="product.ProductID"
                      :data-name="product.ProductName"
                    >
                      {{ product.ProductName }} ({{ product.ProcessType }})
                    </option>
                  </datalist>
                </div>
              </div>

              <div class="form-group">
                <label>Supplier</label>
                <select 
                  v-model.number="selectedSupplier" 
                  class="form-input"
                  required
                >
                  <option :value="null" disabled>Select a supplier</option>
                  <option 
                    v-for="supplier in suppliers" 
                    :key="supplier.id" 
                    :value="supplier.id"
                  >
                    {{ supplier.suppliername }}
                  </option>
                </select>
                <span v-if="suppliers.length === 0" class="supplier-warning">
                  No suppliers available
                </span>
              </div>
            </div>

            <div class="form-section">
              <h2 class="section-title">Stock Information</h2>
              <div v-for="(stock, index) in stockData.Stocks" :key="index" class="stock-entry">
                <div class="form-group">
                  <label>Batch Number (Optional)</label>
                  <input 
                    v-model.trim="stock.batch_number" 
                    type="text" 
                    class="form-input" 
                  />
                </div>

                <div class="form-group">
                  <label>Quantity</label>
                  <input 
                    v-model.number="stock.quantity" 
                    type="number" 
                    min="1" 
                    step="1"
                    required 
                    class="form-input"
                    @input="validateQuantity($event, index)"
                  />
                </div>

                <div class="form-group">
                  <label>Expiration Date (Optional)</label>
                  <input 
                    v-model="stock.expiration_date" 
                    type="date" 
                    class="form-input"
                    :min="getCurrentDate()"
                  />
                </div>

                <button 
                  type="button" 
                  @click="removeStock(index)" 
                  class="remove-btn"
                  v-if="stockData.Stocks.length > 1"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>

              <button type="button" @click="addStock" class="add-btn">
                <i class="fas fa-plus"></i> Add Stock Location
              </button>
            </div>

            <div class="form-actions">
              <button type="button" @click="resetForm" class="reset-btn">Reset</button>
              <button type="submit" class="submit-btn" :disabled="isSubmitting">
                {{ isSubmitting ? 'Creating...' : 'Create Stock' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Confirmation Modal -->
        <div class="modal-overlay" v-if="showConfirmModal">
          <div class="confirmation-modal">
            <div class="modal-content">
              <h3>Confirm Submission</h3>
              <p>Are you sure you want to submit this stock entry?</p>
              <div class="modal-actions">
                <button @click="confirmSubmit" class="confirm-btn">Yes</button>
                <button @click="cancelSubmit" class="cancel-btn">No</button>
              </div>
            </div>
          </div>
        </div>

        <div class="summary-section">
          <h2 class="section-title">Stock Summary</h2>
          <div class="summary-details" :class="{ loading: isLoadingStock, 'has-data': stockData.StockID }">
            <p><strong>Stock ID:</strong> {{ stockData.StockID || 'N/A' }}</p>
            <p>
              <strong>Product Name:</strong> 
              <span>{{ stockData.StockName || 'N/A' }}</span>
              <span v-if="stockData.ProductType" class="process-type">
                ({{ stockData.ProductType }})
              </span>
            </p>
            <p><strong>Unit Price:</strong> {{ stockData.UnitPrice || '0.00' }}</p>
            <p>
              <strong>Current Supplier:</strong>
              <span class="supplier-name">{{ stockData.CurrentSupplier || 'N/A' }}</span>
            </p>
            <p><strong>Total Quantity:</strong> {{ getTotalQuantity() }}</p>
            <p><strong>Total Locations:</strong> {{ stockData.Stocks.length }}</p>
            
            <div v-if="stockData.Stocks.length" class="existing-stocks">
              <h3>Existing Stock Details</h3>
              <div class="stock-list">
                <div v-for="(stock, index) in stockData.Stocks" :key="index" class="stock-item">
                  <div class="stock-info">
                    <span>Qty: {{ stock.quantity }}</span>
                    <span>Batch: {{ stock.batch_number || 'N/A' }}</span>
                    <span>Expires: {{ formatDate(stock.expiration_date) || 'N/A' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div> <!-- Closing main-container -->
    </div> <!-- Closing app-container -->
  </div> <!-- Closing app-container -->

</template>


<script>
import axios from 'axios';
import Header from '@/components/Header.vue';
import SideBar from '@/components/ims/SideBar.vue';
import { useToast } from 'vue-toastification';
import { INVENTORY_API, STOCK_API, SUPPLIERS_API } from '@/api/config.js';

export default {
  components: {
    Header,
    SideBar,
  },
  data() {
    return {
      isSidebarCollapsed: false,
      stockData: {
        StockID: '',
        StockName: '',
        ProductType: '',
        UnitPrice: '',
        CurrentSupplier: '',
        Image: '',
        Stocks: [
          {
            batch_number: '',
            quantity: 1,
            expiration_date: '',
          }
        ]
      },
      selectedSupplier: null,
      inventoryProducts: [],
      suppliers: [],
      isSubmitting: false,
      isLoadingStock: false,
      showConfirmModal: false,
      toast: useToast(),
      stockDetails: null,
      loading: false,
    };
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },

    async handleStockSelection() {
      if (this.stockData.StockID) {
        try {
          this.loading = true;
          const response = await axios.get(`${STOCK_API}/stockdetails/${this.stockData.StockID}`);
          this.stockDetails = response.data;
          
          // Update the stockData with information from the response
          this.stockData.ProductName = this.stockDetails.ProductName;
          this.stockData.CurrentQuantity = this.stockDetails.Quantity;
          this.stockData.Status = this.stockDetails.Status;
          this.stockData.CurrentSupplier = this.stockDetails.CurrentSupplier;
          this.stockData.Image = this.stockDetails.Image;
          this.stockData.Stocks = this.stockDetails.StockDetails.map(stock => ({
            batch_number: stock.batch_number,
            quantity: stock.quantity,
            expiration_date: stock.expiration_date
          }));
          this.selectedSupplier = this.suppliers.find(s => s.suppliername === this.stockDetails.CurrentSupplier)?.id || null;
          
          this.loading = false;
        } catch (error) {
          this.toast.error("Failed to fetch stock details");
          console.error("Error fetching stock details:", error);
          this.loading = false;
        }
      } else {
        this.stockDetails = null;
        this.stockData.ProductName = '';
        this.stockData.CurrentQuantity = 0;
        this.stockData.Status = '';
        this.stockData.CurrentSupplier = '';
        this.stockData.Image = '';
        this.stockData.Stocks = [{ batch_number: '', quantity: 1, expiration_date: '' }];
        this.selectedSupplier = null;
      }
    },
    getCurrentDate() {
      const today = new Date();
      return today.toISOString().split("T")[0];
    },

    formatPrice(value) {
      if (!value) return "₱0.00";
      return new Intl.NumberFormat("en-PH", {
        style: "currency",
        currency: "PHP",
        minimumFractionDigits: 2
      }).format(value);
    },

    formatDate(dateString) {
      if (!dateString) return null;
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },

    getSupplierName() {
      if (!this.selectedSupplier) return "Not selected";
      const supplier = this.suppliers.find(s => s.id === this.selectedSupplier);
      return supplier ? supplier.suppliername : "Unknown";
    },

    getTotalQuantity() {
      return this.stockData.Stocks.reduce((total, stock) => {
        return total + (parseInt(stock.quantity) || 0);
      }, 0);
    },

    validateQuantity(event, index) {
      const value = parseInt(event.target.value);
      if (value < 1) {
        this.stockData.Stocks[index].quantity = 1;
        this.toast.warning('Quantity must be at least 1');
      }
    },
    submitForm() {
      // Trigger the confirmation modal before submission
      this.showConfirmationModal();
    },

    showConfirmationModal() {
      this.showConfirmModal = true;
    },

    async confirmSubmit() {
      this.showConfirmModal = false;
      this.isSubmitting = true;

      try {
        const requestBody = {
          ProductID: this.stockData.StockID,
          Stocks: this.stockData.Stocks.map(stock => ({
            batch_number: stock.batch_number || null,
            quantity: stock.quantity,
            expiration_date: stock.expiration_date || null,
            SupplierID: this.selectedSupplier
          }))
        };

        const response = await axios.post(`${STOCK_API}/stockin/`, requestBody);
        this.toast.success(response.data.message || 'Stock added successfully');
        this.resetForm();
      } catch (error) {
        console.error('Error submitting stock:', error);
        this.toast.error('Failed to add stock');
      } finally {
        this.isSubmitting = false;
      }
    },

    cancelSubmit() {
      this.showConfirmModal = false;
    },


    validateForm() {
      if (!this.stockData.StockID || !this.selectedSupplier) {
        this.toast.error('Please fill all required fields');
        return false;
      }
      if (this.stockData.Stocks.some(stock => !stock.batch_number)) {
        this.toast.error('Batch number is required for all entries');
        return false;
      }
      return true;
    },

    prepareRequestBody() {
      return {
        ProductID: this.stockData.StockID,
        Stocks: this.stockData.Stocks.map(stock => ({
          batch_number: stock.batch_number || null,
          quantity: stock.quantity,
          expiration_date: stock.expiration_date || null,
          SupplierID: this.selectedSupplier
        }))
      };
    },

    resetForm() {
      this.stockData = {
        StockID: '',
        StockName: '',
        ProductType: '',
        Stocks: [{ batch_number: '', quantity: 1, expiration_date: '' }]
      };
      this.selectedSupplier = null;
    },

    addStock() {
      this.stockData.Stocks.push({
        batch_number: '',
        quantity: 1,
        expiration_date: ''
      });
    },

    removeStock(index) {
      if (this.stockData.Stocks.length > 1) {
        this.stockData.Stocks.splice(index, 1);
      }
    },

    async fetchProductsAndSuppliers() {
      try {
        this.loading = true;
        
        // Get all ready-made products
        const productsResponse = await axios.get(`${INVENTORY_API}/inventoryproducts/filter?process_type=Ready-Made`);
        this.products = productsResponse.data.map(product => ({
          id: product.id,
          name: product.ProductName,
          quantity: product.Quantity,
          image: product.Image
        }));
        
        // Get all suppliers
        const suppliersResponse = await axios.get(`${SUPPLIERS_API}/`);
        this.suppliers = suppliersResponse.data;
        
        this.loading = false;
      } catch (error) {
        this.toast.error("Failed to load products and suppliers");
        console.error("Error fetching data:", error);
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchProductsAndSuppliers();
  },
  computed: {
    hasStockDetails() {
      return this.stockData.Stocks && this.stockData.Stocks.length > 0;
    },
    isLoading() {
      return this.isLoadingStock || this.isSubmitting;
    },
    hasValidStockData() {
      return this.stockData.StockID && 
             this.stockData.StockName && 
             this.stockData.Stocks.length > 0;
    }
  }
};
</script>


<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  margin-left: 230px; /* Default margin when sidebar is expanded */
  height: 100vh;
  transition: margin-left 0.3s ease; /* Smooth transition for sidebar toggle */
}

.app-container.sidebar-collapsed {
  margin-left: 70px; /* Adjust margin when sidebar is collapsed */
}

.main-container {
  flex-grow: 1;
  padding: 20px;
}

.header{
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}
.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 30px;
}

.form-container {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 1.25rem;
  color: #333;
  margin-bottom: 20px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: #E54F70;
  outline: none;
}
.form-input,
select.form-input {
  width: 100%;
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
  background-color: white;
}

select.form-input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23333' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  padding-right: 2.5rem;
}

select.form-input option {
  padding: 8px;
  font-size: 14px;
}

select.form-input:focus {
  border-color: #E54F70;
  outline: none;
}

.supplier-name {
  font-weight: 500;
  color: #333;
}

.stock-entry {
  position: relative;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 15px;
}
.supplier-warning {
  display: block;
  color: #856404;
  background-color: #fff3cd;
  padding: 8px;
  margin-top: 4px;
  border-radius: 4px;
  font-size: 12px;
}
.remove-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s;
}

.remove-btn:hover {
  background: #c82333;
}

.add-btn {
  width: 100%;
  padding: 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.add-btn:hover {
  background: #45a049;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.submit-btn, .reset-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn {
  background: #E54F70;
  color: white;
}

.reset-btn {
  background: #6c757d;
  color: white;
}

.summary-section {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  height: fit-content;
  position: sticky;
  top: 20px;
}

.process-type {
  font-size: 0.9em;
  color: #666;
  margin-left: 4px;
}

.summary-details p {
  margin: 12px 0;
  line-height: 1.4;
}

.summary-details strong {
  display: inline-block;
  width: 120px;
  color: #555;
}

.summary-details.loading {
  opacity: 0.7;
  position: relative;
}

.summary-details.loading::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(1px);
}
.existing-stocks {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.existing-stocks h3 {
  font-size: 1rem;
  color: #555;
  margin-bottom: 15px;
}

.stock-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stock-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #eee;
}

.stock-location {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stock-info {
  display: flex;
  gap: 12px;
  font-size: 0.9rem;
  color: #666;
}

.stock-info span {
  background: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}
@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .main-container {
    margin-left: 0;
  }
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
</style>