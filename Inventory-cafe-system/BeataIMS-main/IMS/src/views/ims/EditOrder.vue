<template>
    <div class="edit-order-container">
      <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />
      <SideBar :isCollapsed="isSidebarCollapsed" />
      
      <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
        <div class="order-edit-form">
          <div class="page-header">
            <h1><i class="fas fa-edit"></i> Edit Order #{{ $route.params.id }}</h1>
            <nav class="breadcrumb">
              <span @click="$router.push('/ordershistory')">Orders</span> 
              <i class="fas fa-chevron-right"></i> 
              <span @click="$router.push(`/vieworderdetails/${orderData.history_id}`)">Order #{{ $route.params.id }}</span>
              <i class="fas fa-chevron-right"></i> 
              <span class="current">Edit</span>
            </nav>
          </div>
          
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>Loading order details...</p>
          </div>
          
          <div v-else-if="error" class="error-container">
            <i class="fas fa-exclamation-circle"></i>
            <p>{{ error }}</p>
            <button class="retry-btn" @click="fetchOrderDetails">Try Again</button>
          </div>
          
          <form v-else @submit.prevent="submitForm" class="edit-form">
            <div class="form-layout">
              <!-- Left column -->
              <div class="form-layout-main">
                <!-- Customer Information Section -->
                <div class="form-section customer-section">
                  <div class="section-header">
                    <h2><i class="fas fa-user"></i> Customer Information</h2>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-group">
                      <label for="customer_name">Customer Name</label>
                      <div class="input-wrapper">
                        <input 
                          id="customer_name" 
                          v-model="orderData.customer_name" 
                          type="text" 
                          placeholder="Enter customer name"
                          required
                        />
                      </div>
                    </div>
                    
                    <div class="form-group">
                      <label for="payment_method">Payment Method</label>
                      <div class="select-wrapper">
                        <select id="payment_method" v-model="orderData.payment_method" required>
  <option value="" disabled>Select payment method</option>
  <option value="Cash">Cash</option>
  <option value="Tally">Tally</option>
</select>
                        <i class="fas fa-chevron-down select-arrow"></i>
                      </div>
                    </div>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-group">
                      <label for="created_at">Order Date</label>
                      <div class="input-wrapper">
                        <input 
                          id="created_at" 
                          v-model="orderData.created_at" 
                          type="datetime-local"
                          required
                        />
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Order Items Section -->
                <div class="form-section items-section">
                  <div class="section-header">
                    <h2><i class="fas fa-shopping-cart"></i> Order Items</h2>
                  </div>
                  
                  <div class="items-container">
                    <div class="item-header">
                      <div class="item-col product-col">Product</div>
                      <div class="item-col quantity-col">Quantity</div>
                      <div class="item-col price-col">Price</div>
                      <div class="item-col subtotal-col">Subtotal</div>
                      <div class="item-col action-col"></div>
                    </div>
                    
                    <div v-for="(item, index) in orderData.items" :key="index" class="item-row">
                      <div class="item-col product-col">
                        <div class="select-wrapper">
                          <select 
                            v-model="item.product_id" 
                            @change="updateProductDetails(index)"
                            required
                          >
                          <option v-for="product in availableProducts" 
        :key="product.id" 
        :value="product.id">
  {{ product.name }}
</option>
                          </select>
                          <i class="fas fa-chevron-down select-arrow"></i>
                        </div>
                      </div>
                      
                      <div class="item-col quantity-col">
                        <div class="quantity-control">
                          <button 
                            type="button" 
                            class="quantity-btn"
                            @click="decrementQuantity(index)"
                            :disabled="item.quantity <= 1"
                          >
                            <i class="fas fa-minus"></i>
                          </button>
                          <input 
                            type="number" 
                            v-model.number="item.quantity" 
                            min="1"
                            @change="recalculateTotals"
                            required
                          />
                          <button 
                            type="button" 
                            class="quantity-btn"
                            @click="incrementQuantity(index)"
                          >
                            <i class="fas fa-plus"></i>
                          </button>
                        </div>
                      </div>
                      
                      <div class="item-col price-col">
                        <div class="input-wrapper price-input">
                          <span class="currency-symbol">₱</span>
                          <input 
                            type="number" 
                            v-model.number="item.price" 
                            step="0.01" 
                            min="0"
                            @change="recalculateTotals"
                            required
                          />
                        </div>
                      </div>
                      
                      <div class="item-col subtotal-col">
                        <div class="subtotal">₱{{ formatPrice(item.quantity * item.price) }}</div>
                      </div>
                      
                      <div class="item-col action-col">
                        <button 
                          type="button" 
                          class="remove-item-btn" 
                          @click="removeItem(index)"
                          v-if="orderData.items.length > 1"
                          title="Remove item"
                        >
                          <i class="pi pi-trash"></i>
                        </button>
                      </div>
                    </div>
                    
                    <button type="button" class="add-item-btn" @click="addNewItem">
                      <i class="fas fa-plus"></i> Add Item
                    </button>
                  </div>
                </div>
                
                <!-- Admin Verification Section -->
                <div class="form-section admin-section">
                  <div class="section-header">
                    <h2><i class="fas fa-shield-alt"></i> Admin Verification</h2>
                    <p class="admin-note">Administrator credentials are required to submit changes</p>
                  </div>
                  
                  <div class="form-row">
                    <div class="form-group">
                      <label for="admin_username">Admin Username</label>
                      <div class="input-wrapper">
                        <i class="fas fa-user-shield input-icon"></i>
                        <input 
                          id="admin_username" 
                          v-model="adminCredentials.username" 
                          type="text" 
                          placeholder="Enter admin username"
                          required
                        />
                      </div>
                    </div>
                    
                    <div class="form-group">
                      <label for="admin_password">Admin Password</label>
                      <div class="input-wrapper password-wrapper">
                        <i class="fas fa-lock input-icon"></i>
                        <input 
                          id="admin_password" 
                          v-model="adminCredentials.password" 
                          :type="showPassword ? 'text' : 'password'" 
                          placeholder="Enter admin password"
                          required
                        />
                        <button 
                          type="button" 
                          class="password-toggle" 
                          @click="togglePasswordVisibility"
                        >
                          <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Right column - Summary -->
              <div class="form-layout-sidebar">
                <div class="form-section summary-section">
                  <div class="section-header">
                    <h2><i class="fas fa-file-invoice-dollar"></i> Order Summary</h2>
                  </div>
                  
                  <div class="summary-content">
                    <div class="summary-row">
                      <span class="summary-label">Total Items:</span>
                      <span class="summary-value">{{ orderData.total_items }}</span>
                    </div>
                    
                    <div class="summary-row subtotal-row">
                      <span class="summary-label">Subtotal:</span>
                      <span class="summary-value">₱{{ formatPrice(orderData.total_amount) }}</span>
                    </div>

                    

                  </div>
                  
                  <div class="form-actions">
                    <button type="button" class="cancel-btn" @click="cancelEdit">
                      <i class="fas fa-times"></i> Cancel
                    </button>
                    <button type="submit" class="save-btn" :disabled="submitting">
                      <i class="fas fa-save"></i> {{ submitting ? 'Saving...' : 'Save Changes' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { ORDER_SUMMARY_API, ORDERS_API } from '@/api/config.js'
  import { useToast } from 'vue-toastification'
  import Header from '@/components/Header.vue'
  import SideBar from '@/components/ims/SideBar.vue'

  export default {
    name: 'EditOrder',
    components: {
      Header,
      SideBar
    },
    
    setup() {
      const toast = useToast()
      return { toast }
    },
    
    data() {
    return {
      orderData: {
        history_id: 0,
        customer_name: '',
        total_items: 0,
        total_amount: 0,
        payment_method: '',
        created_at: '',
        items: [],
      },
      adminCredentials: {
        username: '',
        password: '',
      },
      availableProducts: [],
      loading: true,
      error: null,
      submitting: false,
    };
  },
    
  async created() {
  const historyId = this.$route.params.id; // Get the ID from the route
  if (!historyId) {
    this.$toast.error('Order ID is missing.');
    this.$router.push('/ordershistory');
    return;
  }

  await this.fetchOrderDetails(historyId);
  await this.fetchAvailableProducts(); // Fetch menu items here

},
    methods: {
      handleSidebarToggle(collapsed) {
        this.isSidebarCollapsed = collapsed
      },
      
      formatPrice(value) {
        return value ? Number(value).toFixed(2) : "0.00"
      },
      
      formatDateForInput(dateString) {
      const date = new Date(dateString);
      return date.toISOString().slice(0, 16); // Format: YYYY-MM-DDThh:mm
    },
    
    async fetchOrderDetails(historyId) {
    try {
      this.loading = true;
      const response = await axios.get(`${ORDER_SUMMARY_API}/orders/history/${historyId}`);
      console.log('Fetched Order Data:', response.data); // Debugging log
      this.orderData = response.data;
      this.orderData.created_at = this.formatDateForInput(this.orderData.created_at);
    } catch (error) {
      this.error = error.response?.data?.detail || 'Failed to load order details.';
      this.$toast.error(this.error);
    } finally {
      this.loading = false;
    }
  },
      
  async fetchAvailableProducts() {
  try {
    // Use ORDERS_API to match the endpoint in OrderItemSelector
    const response = await axios.get(`${ORDERS_API}/menu_items/all`);
    this.availableProducts = response.data.map(item => ({
      id: item.id,
      name: item.name,
      price: item.price,
      stock: item.process_type === 'To Be Made' ? '∞' : item.stock,
      process_type: item.process_type,
      image: item.image,
      category: item.category,
      status: item.process_type === 'To Be Made' ? 'Available' : (item.stock > 0 ? 'In Stock' : 'Out of Stock')
    }));
  } catch (error) {
    this.$toast.error('Failed to load available products.');
  }
},
      
updateProductDetails(index) {
  const productId = parseInt(this.orderData.items[index].product_id)
  const product = this.availableProducts.find(p => p.id === productId)

  if (product) {
    this.orderData.items[index].product_name = product.name
    this.orderData.items[index].price = product.price
    this.recalculateTotals()
  }
},
      
      recalculateTotals() {
        // Calculate total items
        this.orderData.total_items = this.orderData.items.reduce(
          (sum, item) => sum + (parseInt(item.quantity) || 0), 0
        )
        
        // Calculate total amount
        this.orderData.total_amount = this.orderData.items.reduce(
          (sum, item) => sum + ((parseInt(item.quantity) || 0) * (parseFloat(item.price) || 0)), 0
        )
      },
      
      addNewItem() {
  const defaultProduct = this.availableProducts.length > 0 ? this.availableProducts[0] : null

  const newItem = {
    product_id: defaultProduct ? defaultProduct.id : '',
    product_name: defaultProduct ? defaultProduct.name : '',
    quantity: 1,
    price: defaultProduct ? defaultProduct.price : 0
  }

  this.orderData.items.push(newItem)
  this.recalculateTotals()
  this.toast.info('New item added to order')
},
      
      removeItem(index) {
        if (this.orderData.items.length > 1) {
          const removedItem = this.orderData.items[index]
          this.orderData.items.splice(index, 1)
          this.recalculateTotals()
          this.toast.info(`Item removed from order`)
        }
      },
      
      incrementQuantity(index) {
        this.orderData.items[index].quantity++
        this.recalculateTotals()
      },
      
      decrementQuantity(index) {
        if (this.orderData.items[index].quantity > 1) {
          this.orderData.items[index].quantity--
          this.recalculateTotals()
        }
      },
      
      togglePasswordVisibility() {
        this.showPassword = !this.showPassword
      },
      
      cancelEdit() {
        // Ask for confirmation if form has been modified
        if (this.formModified) {
          if (confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
            this.$router.push(`/orderdetails/${this.orderData.history_id}`)
          }
        } else {
          this.$router.push(`/orderdetails/${this.orderData.history_id}`)
        }
      },
      
      async submitForm() {
      try {
        this.submitting = true;
        const payload = {
          history_id: this.orderData.history_id,
          customer_name: this.orderData.customer_name,
          total_items: this.orderData.total_items,
          total_amount: this.orderData.total_amount,
          payment_method: this.orderData.payment_method,
          created_at: new Date(this.orderData.created_at).toISOString(),
          items: this.orderData.items.map((item) => ({
            product_id: item.product_id,
            quantity: item.quantity,
          })),
        };
        await axios.put(
          `${ORDER_SUMMARY_API}/orders/history/${this.orderData.history_id}/details`,
          payload,
          {
            params: {
              admin_username: this.adminCredentials.username,
              admin_password: this.adminCredentials.password,
            },
          }
        );
        this.toast.success('Order updated successfully.');
        this.$router.push(`/vieworderdetails/${this.orderData.history_id}`);
      } catch (error) {
        this.toast.error(error.response?.data?.detail || 'Failed to update order.');
      } finally {
        this.submitting = false;
      }
    },
    },
    
    computed: {
      formModified() {
        // Logic to determine if form has been modified
        // This is a simplified check - you may need to implement a more comprehensive comparison
        return true
      }
    }
  }
  </script>
  
<style scoped>
  :root {
    --primary-color: #4f46e5;
    --primary-hover: #4338ca;
    --primary-light: #eef2ff;
    --success-color: #10b981;
    --success-hover: #059669;
    --danger-color: #ef4444;
    --danger-hover: #dc2626;
    --warning-color: #f59e0b;
    --info-color: #3b82f6;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    --border-radius-sm: 0.375rem;
    --border-radius: 0.5rem;
    --border-radius-lg: 0.75rem;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --animation-duration: 0.2s;
    --font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  }
  
  /* Base Styles */
  .edit-order-container {
    position: relative;
    background-color: var(--gray-50);
    min-height: 100vh;
    font-family: var(--font-family);
    color: var(--gray-800);
  }
  
  .app-container {
    margin-left: 250px;
    transition: margin var(--animation-duration) ease-in-out;
    padding-top: 1rem;
  }
  
  .app-container.sidebar-collapsed {
    margin-left: 70px;
  }
  
  .order-edit-form {
    padding: 1.5rem;
    max-width: 1320px;
    margin: 0 auto;
  }
  
  /* Page Header */
  .page-header {
    display: flex;
    flex-direction: column;
    margin-bottom: 1.75rem;
  }
  
  .page-header h1 {
    margin-bottom: 0.625rem;
    color: var(--gray-900);
    font-size: 1.875rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    letter-spacing: -0.025em;
  }
  
  .page-header h1 i {
    color: var(--primary-color);
  }
  
  .breadcrumb {
    display: flex;
    align-items: center;
    color: var(--gray-500);
    font-size: 0.875rem;
    background-color: white;
    padding: 0.5rem 0.875rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-sm);
    width: fit-content;
  }
  
  .breadcrumb span {
    cursor: pointer;
    transition: color 0.15s ease;
  }
  
  .breadcrumb span:not(.current):hover {
    color: var(--primary-color);
    text-decoration: underline;
  }
  
  .breadcrumb i {
    margin: 0 0.5rem;
    font-size: 0.625rem;
    color: var(--gray-400);
  }
  
  .breadcrumb .current {
    color: var(--gray-700);
    font-weight: 600;
  }
  
  /* Loading State */
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    background-color: white;
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow);
  }
  
  .loading-spinner {
    border: 3px solid var(--gray-200);
    border-top: 3px solid var(--primary-color);
    border-radius: 50%;
    width: 48px;
    height: 48px;
    animation: spin 1.2s linear infinite;
    margin-bottom: 1.25rem;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .loading-container p {
    color: var(--gray-600);
    font-size: 1.125rem;
    font-weight: 500;
  }
  
  /* Error State */
  .error-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3.5rem 2rem;
    background-color: white;
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow);
    border-left: 5px solid var(--danger-color);
  }
  
  .error-container i {
    color: var(--danger-color);
    font-size: 2.5rem;
    margin-bottom: 1.25rem;
  }
  
  .error-container p {
    color: var(--gray-700);
    font-size: 1.125rem;
    margin-bottom: 1.75rem;
    text-align: center;
    max-width: 500px;
  }
  
  .retry-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 0.625rem 1.75rem;
    border-radius: var(--border-radius);
    font-weight: 600;
    font-size: 0.9375rem;
    cursor: pointer;
    transition: all var(--animation-duration) ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .retry-btn:hover {
    background-color: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow);
  }
  
  .retry-btn:active {
    transform: translateY(0);
  }
  
  /* Form Layout */
  .form-layout {
    display: grid;
    grid-template-columns: 1fr 350px;
    gap: 1.75rem;
  }
  
  @media (max-width: 1200px) {
    .form-layout {
      grid-template-columns: 1fr;
    }
    
    .form-layout-sidebar {
      order: -1;
    }
  }
  
  .form-layout-main {
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
  }
  
  .form-layout-sidebar {
    align-self: start;
  }
  
  /* Form Sections */
  .form-section {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  }
  
  .form-section:hover {
    box-shadow: var(--shadow-md);
  }
  
  .section-header {
    padding: 20px;
    border-bottom: 1px solid var(--gray-200);
    background-color: var(--gray-50);
    
    border-bottom: 1px solid #eee;
  }
  
  .section-header h2 {
    color: var(--gray-800);
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .section-header h2 i {
    color: var(--primary-color);
  }
  
  .section-header p {
    margin-top: 0.5rem;
    color: var(--gray-500);
    font-size: 0.875rem;
  }
  
  .admin-note {
    color: var(--gray-600);
    font-style: italic;
    font-size: 0.875rem;
    display: flex;
    align-items: center;
    gap: 0.4375rem;
    margin-top: 0.625rem;
  }
  
  .admin-note::before {
    content: "ℹ️";
    font-style: normal;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    padding: 20px;
  }
  
  /* Form Controls */
  
  .form-group:last-child {
    margin-bottom: 0;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--gray-700);
    font-size: 0.875rem;
  }
  
  .input-wrapper {
    position: relative;
  }
  
  .input-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--gray-500);
    font-size: 0.875rem;
  }
  
  .input-wrapper input,
  .select-wrapper select {
    padding: 15px;
    border:#6b728046 1px solid;
    width: 90%;
    border-radius: 5px;
    font-size: 0.9375rem;
    transition: all var(--animation-duration) ease;
    color: var(--gray-800);
    
  }
  
  .input-wrapper input:hover,
  .select-wrapper select:hover {
    border-color: var(--gray-400);
  }
  
  .input-wrapper input:focus,
  .select-wrapper select:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
    outline: none;
  }
  
  .input-wrapper input::placeholder {
    color: var(--gray-400);
  }
  
  /* Price Input */
  .price-input {
    display: flex;
    align-items: center;
  }
  
  .currency-symbol {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--gray-600);
    font-weight: 500;
  }
  
  .price-input input {
    padding-left: 2rem;
  }
  
  /* Select Dropdown */
  .select-wrapper {
    position: relative;
  }
  

  
  .select-arrow {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--gray-500);
    pointer-events: none;
    font-size: 0.75rem;
  }
  
  /* Password Field */
  .password-wrapper {
    display: flex;
  }
  
  .password-toggle {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--gray-500);
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color var(--animation-duration) ease;
  }
  
  .password-toggle:hover {
    color: var(--gray-700);
  }
  
/* Items Section */
.items-section {
  position: relative;
  padding: 0; /* Remove padding from section */
}

.items-container {
  overflow-x: auto; /* Enable horizontal scroll if needed */
}

.item-header {
  display: grid;
  grid-template-columns: 3fr 1fr 1fr 1fr 60px; /* Fixed last column width */
  gap: 1rem;
  padding: 1rem 1.5rem;
  background-color: var(--primary-light);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
  font-weight: 600;
  color: var(--gray-700);
  font-size: 0.875rem;
  position: sticky;
  top: 0;
  z-index: 1;
}

.item-row {
  display: grid;
  grid-template-columns: 3fr 1fr 1fr 1fr 60px; /* Match header columns */
  gap: 1rem;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: white;
  border-bottom: 1px solid var(--gray-200);
  transition: all var(--animation-duration) ease;
}

/* Column-specific styles */
.product-col {
  min-width: 200px; /* Minimum width for product column */
}

.quantity-col,
.price-col,
.subtotal-col {
  min-width: 120px; /* Minimum width for number columns */
}

.action-col {
  width: 60px; /* Fixed width for action column */
  justify-content: center;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .item-header,
  .item-row {
    grid-template-columns: 2fr 1fr 1fr 1fr 60px;
    font-size: 0.813rem;
    padding: 1rem;
  }
}

@media (max-width: 768px) {
  .item-header,
  .item-row {
    grid-template-columns: 2fr 1fr 1fr 60px;
    gap: 0.5rem;
  }

  .subtotal-col {
    display: none;
  }
}
  /* Quantity Controls */
  .quantity-control {
    display: flex;
    align-items: center;
    border: 1px solid var(--gray-300);
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
  }
  
  .quantity-btn {
    background-color: var(--gray-100);
    border: none;
    width: 2.25rem;
    height: 2.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: var(--gray-600);
    transition: all 0.15s ease;
  }
  
  .quantity-btn:hover {
    background-color: var(--gray-200);
    color: var(--gray-800);
  }
  
  .quantity-btn:active {
    background-color: var(--gray-300);
  }
  
  .quantity-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .quantity-control input {
    width: 3rem;
    height: 2.25rem;
    border: none;
    border-left: 1px solid var(--gray-300);
    border-right: 1px solid var(--gray-300);
    text-align: center;
    font-size: 0.9375rem;
    color: var(--gray-800);
    font-weight: 500;
  }
  
  /* Buttons */
  .add-item-btn {
    background-color: #E54F70;
    color: white;
    border: 1px dashed var(--primary-color);
    border-top-right-radius: 0px;
    border-top-left-radius: 0px;
    border-bottom-right-radius: 10px;
    border-bottom-left-radius: 10px;
    padding: 0.75rem;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    font-weight: 500;
    transition: all var(--animation-duration) ease;
    margin-top: 1rem;
  }
  
  .add-item-btn:hover {
    background-color: #af3c55;
    transform: translateY(-2px);
  }
  
  .add-item-btn:active {
    transform: translateY(0);
  }
  
  .remove-item-btn {
    background-color: white;
    color: var(--gray-500);
    border: 1px solid var(--gray-300);
    border-radius: var(--border-radius);
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--animation-duration) ease;
  }
  
  .remove-item-btn:hover {
    color: var(--danger-color);
    border-color: var(--danger-color);
    background-color: rgba(239, 68, 68, 0.05);
  }
  
  /* Order Summary */
  .summary-section {
    position: sticky;
    top: 2rem;
  }
  
  .summary-content {
    padding: 1.5rem;
  }
  
  .summary-row {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--gray-200);
  }
  
  .summary-row:last-child {
    border-bottom: none;
  }
  
  .summary-label {
    color: var(--gray-600);
    font-size: 0.9375rem;
  }
  
  .summary-value {
    font-weight: 600;
    color: var(--gray-800);
    font-size: 0.9375rem;
  }
  
  .subtotal-row {
    margin-top: 0.5rem;
    border-bottom: none;
    padding-top: 1rem;
    border-top: 1px solid var(--gray-300);
  }
  
  .subtotal-row .summary-label,
  .subtotal-row .summary-value {
    font-weight: 600;
    font-size: 1.125rem;
  }
  
  .subtotal-row .summary-value {
    color: var(--primary-color);
  }
  
  /* Form Actions */
  .form-actions {
    display: flex;
    gap: 1rem;
    padding: 1.5rem;
    background-color: var(--gray-50);
    border-top: 1px solid var(--gray-200);
  }
  
  .cancel-btn,
  .save-btn {
    flex: 1;
    padding: 0.75rem;
    border-radius: var(--border-radius);
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all var(--animation-duration) ease;
    font-size: 0.9375rem;
  }
  
  .cancel-btn {
    background-color: white;
    color: var(--gray-700);
    border: 1px solid var(--gray-300);
  }
  
  .cancel-btn:hover {
    border-color: var(--gray-400);
    background-color: var(--gray-50);
  }
  
  .save-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
  }
  
  .save-btn:hover {
    background-color: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow);
  }
  
  .save-btn:active {
    transform: translateY(0);
  }
  
  .save-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  
  /* Product Subtotal */
  .subtotal {
    font-weight: 600;
    color: var(--gray-800);
    background-color: var(--gray-100);
    padding: 0.5rem 0.75rem;
    border-radius: var(--border-radius);
    text-align: right;
  }
  
  /* Responsive Adjustments */
  @media (max-width: 768px) {
    .order-edit-form {
      padding: 1rem;
    }
    
    .form-layout {
      gap: 1.25rem;
    }
    
    .item-header,
    .item-row {
      grid-template-columns: 2fr 1fr 1fr auto;
    }
    
    .subtotal-col {
      display: none;
    }
    
    .form-row {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
  }
  
  /* Animations */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .form-section {
    animation: fadeIn 0.3s ease-out forwards;
  }
  
  .form-section:nth-child(2) {
    animation-delay: 0.1s;
  }
  
  .form-section:nth-child(3) {
    animation-delay: 0.2s;
  }

</style>