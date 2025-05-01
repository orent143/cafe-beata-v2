<template>
  <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />
  <SideBar :isCollapsed="isSidebarCollapsed" />

  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="order-details">
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="order-container">


          
          <!-- Order Summary Section -->
          <div class="summary-section">
      <div class="summary-header">
        <h2><i class="fas fa-file-invoice"></i> Order Summary</h2>
        <div class="action-buttons">
          <router-link
            v-if="order.history_id || $route.params.id"
            :to="{ name: 'EditOrder', params: { id: order.history_id || $route.params.id } }"
            class="action-btn edit-btn"
            title="Edit Order"
          >
            <i class="pi pi-pencil"></i>
          </router-link>
          <button
            v-if="order"
            @click="showDeleteModal = true"
            class="action-btn delete-btn"
            title="Delete Order"
          >
            <i class="pi pi-trash"></i>
          </button>
        </div>
      </div>

            <div class="summary-details">
              <div class="detail-row">
                <span>Order ID:</span>
                <span>#{{ order.history_id }}</span>
              </div>
              <div class="detail-row">
                <span>Customer Name:</span>
                <span>{{ order.customer_name }}</span>
              </div>
              <div class="detail-row">
                <span>Date:</span>
                <span>{{ formatDate(order.created_at) }}</span> 
              </div>
              <div class="detail-row">
                <span>Payment Method:</span>
                <span>{{ order.payment_method }}</span>
              </div>
              <div class="detail-row">
                <span>Total Items:</span>
                <span>{{ order.total_items }}</span>
              </div>
              <div class="detail-row">
                <span>Total Amount:</span>
                <span>₱{{ formatPrice(order.total_amount) }}</span>
              </div>
            </div>
          </div>
  
          <!-- Order Items Section -->
          <div class="items-section">
            <h2>Order Items</h2>
            <table>
              <thead>
                <tr>
                  <th>Product ID</th>
                  <th>Name</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in order.items" :key="item.product_id">
                  <td>{{ item.product_id }}</td>
                  <td>{{ item.product_name }}</td>
                  <td>{{ item.quantity }}</td>
                  <td>₱{{ formatPrice(item.price) }}</td>
                  <td>₱{{ formatPrice(item.quantity * item.price) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

    <div class="modal-overlay" v-if="showDeleteModal">
      <div class="verification-modal">
        <div class="modal-content">
          <h3>Confirm Delete Order</h3>
          <p>Are you sure you want to delete this order? This action cannot be undone.</p>
          <form @submit.prevent="verifyAndDelete">
            <div class="form-group">
              <label for="delete-admin-username">Admin Username:</label>
              <input 
                v-model="adminCredentials.username" 
                id="delete-admin-username" 
                type="text" 
                required
              />
            </div>
            <div class="form-group">
              <label for="delete-admin-password">Admin Password:</label>
              <input 
                v-model="adminCredentials.password" 
                id="delete-admin-password" 
                type="password" 
                required
              />
            </div>
            <div class="modal-actions">
              <button type="button" @click="showDeleteModal = false" class="cancel-btn">
                Cancel
              </button>
              <button type="submit" class="confirm-btn delete">
                Verify & Delete
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import Header from '@/components/Header.vue'    
  import SideBar from '@/components/ims/SideBar.vue'
  import { ORDER_SUMMARY_API } from '@/api/config.js'
  import { useToast } from 'vue-toastification'
  
  export default {
    components: {
      SideBar,
      Header,
    },
    setup() {
      const toast = useToast();
      return { toast };
    },
    name: 'OrderDetails',
    data() {
      return {
      showDeleteModal: false,
      adminCredentials: {
        username: '',
        password: ''
      },
        isSidebarCollapsed: false,
        order: null,
        loading: true,
        error: null
      }
    },
    async verifyAndEdit() {
      try {
        await axios.put(`${ORDER_SUMMARY_API}/orders/history/${this.order.history_id}/details`, {
          ...this.order,
          admin_username: this.adminCredentials.username,
          admin_password: this.adminCredentials.password
        });
        
        this.toast.success('Order updated successfully');
        this.showEditModal = false;
        this.fetchOrderDetails(); // Refresh order details
      } catch (error) {
        this.toast.error(error.response?.data?.detail || 'Failed to update order');
      }
    },
    async verifyAndDelete() {
      try {
        await axios.delete(
          `${ORDER_SUMMARY_API}/orders/history/${this.order.history_id}/details`, {
            params: {
              admin_username: this.adminCredentials.username,
              admin_password: this.adminCredentials.password
            }
          }
        );
        
        this.toast.success('Order deleted successfully');
        this.showDeleteModal = false;
        this.$router.push('/orderhistory'); // Redirect to order history
      } catch (error) {
        this.toast.error(error.response?.data?.detail || 'Failed to delete order');
      }
    },

    async created() {
    try {
        const historyId = this.$route.params.id; // Get the ID from the route
        console.log('Route ID:', historyId); // Debugging log

        if (!historyId) {
            throw new Error('Order ID is missing in the route.');
        }

        const response = await axios.get(`${ORDER_SUMMARY_API}/orders/history/${historyId}`);
        console.log('Order Data:', response.data); // Debugging log

        this.order = response.data; // Assign the fetched order data
        this.loading = false;
    } catch (err) {
        this.error = 'Error loading order details';
        this.loading = false;
        console.error('Error:', err);
        this.toast.error(err.response?.data?.detail || 'Failed to load order details. Please try again.');
    }
},
    methods: {
      handleSidebarToggle(collapsed) {
        this.isSidebarCollapsed = collapsed;
      },
      formatDate(date) {
        if (!date) return "N/A";
        const options = { year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit" };
        return new Date(date).toLocaleDateString("en-US", options);
      },
      formatPrice(value) {
        return value ? Number(value).toFixed(2) : "0.00";
      },
      async verifyAndDelete() {
      try {
        await axios.delete(`${ORDER_SUMMARY_API}/orders/history/${this.order.history_id}/details`, {
          params: {
            admin_username: this.adminCredentials.username,
            admin_password: this.adminCredentials.password,
          },
        });

        this.toast.success('Order deleted successfully');
        this.showDeleteModal = false;
        this.$router.push('/ordershistory'); // Redirect to order history
      } catch (error) {
        this.toast.error(error.response?.data?.detail || 'Failed to delete order');
      }
    },

    }
  }
  </script>
  

<style scoped>

.order-details {
    padding: 20px;
    max-width: 1000px;
    margin: 0 auto;
}

.loading, .error {
    text-align: center;
    padding: 20px;
}

.error {
    color: red;
}

.order-container {
    display: grid;
    gap: 20px;
}
.items-section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    max-height: 400px; /* Adjust height as needed */
    overflow-y: auto; /* Enables vertical scrolling */
    overflow-x: hidden; /* Prevents horizontal overflow */
}
.summary-section, .items-section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.summary-details {
    display: grid;
    gap: 10px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid #eee;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}

th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background-color: #f8f9fa;
    font-weight: 600;
}

h2 {
    margin-bottom: 20px;
    color: #333;
}
.action-buttons {
  display: flex;
  margin-bottom: 20px;
}

.edit-btn, .delete-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 600;
  background-color: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 16px;
  transition: all 0.3s ease;
}

.action-btn.edit-btn{
  
  color: #1976d2;
  display: inline-block; /* Ensure buttons are displayed */
}

.action-btn.delete-btn {
  color: #ff4444;
  border: none;
}
.edit-btn:hover {
  color: #0c3864;
}
.delete-btn:hover {
  color: #5c0000;
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

.verification-modal {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease-out;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn, .confirm-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  color: #333;
}

.confirm-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
}

.confirm-btn.delete {
  background-color: #ff4444;
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
</style>
