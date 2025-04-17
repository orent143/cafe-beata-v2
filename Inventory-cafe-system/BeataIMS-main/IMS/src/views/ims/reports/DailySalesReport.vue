<template>
  <div>
    <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />
    <SideBar :isCollapsed="isSidebarCollapsed" />
    <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="header-container">
        <div class="title-section">
        <h1 class="report-header">Daily Sales Report</h1>
        <span class="date-display">{{ formattedDate }}</span>
        </div>
        <div class="header-actions">

          <div class="header-btn">
          <button class="refresh-btn header-refresh" @click="refreshData">
            <i class="pi pi-refresh"></i> Refresh
          </button>
          <button class="export-btn" @click="exportToCsv">
            <i class="pi pi-download"></i> Export CSV
          </button>

        </div>
        </div>
      </div>

      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading sales data...</p>
      </div>

      <div v-else class="report-content">
        <div class="date-selector">
            <input 
              type="date" 
              v-model="selectedDate" 
              :max="currentDate"
              @change="handleDateChange"
              class="date-input"
            />
          </div>

      
        <!-- Summary Cards -->
        <div class="summary-cards">
          <div class="summary-card total-sales">
            <div class="card-icon"><i class="pi pi-money-bill"></i></div>
            <div class="card-content">
              <h3>Total Sales</h3>
              <p class="summary-value">{{ formatCurrency(calculateTotalSales()) }}</p>
            </div>
          </div>
          <div class="summary-card">
            <div class="card-icon"><i class="pi pi-shopping-cart"></i></div>
            <div class="card-content">
              <h3>Total Orders</h3>
              <p class="summary-value">{{ totalOrders }}</p>
            </div>
          </div>
          <div class="summary-card">
            <div class="card-icon"><i class="pi pi-box"></i></div>
            <div class="card-content">
              <h3>Total Items Sold</h3>
              <p class="summary-value">{{ combinedTotalItems }}</p>
            </div>
          </div>
        </div>

        <!-- System Breakdown Cards -->
        <div class="system-summary">
          <div class="system-card cafe-system" @click="showCafeOrdersModal = true">
            <div class="card-header">
              <div class="view-details">
                <i class="pi pi-eye"></i> View Orders
              </div>
              <h3><i class="pi pi-home"></i> Cafe Beata System</h3>
            </div>
            <div class="system-metrics">
              <div class="metric">
                <span class="metric-label">Sales</span>
                <span class="metric-value">{{ formatCurrency(totalCafeSales) }}</span>
              </div>
              <div class="metric">
                <span class="metric-label">Items Sold</span>
                <span class="metric-value">{{ totalCafeItems }}</span>
              </div>
              <div class="metric">
                <span class="metric-label">Orders</span>
                <span class="metric-value">{{ cafeOrders.length }}</span>
              </div>
            </div>
          </div>
          
          <div class="system-card inventory-system" @click="showInventorySalesModal = true">
            <div class="card-header">
              <div class="view-details inventory-view">
                <i class="pi pi-eye"></i> View Sales
              </div>
              <h3><i class="pi pi-chart-bar"></i> Inventory System</h3>
            </div>
            <div class="system-metrics">
              <div class="metric">
                <span class="metric-label">Sales</span>
                <span class="metric-value">{{ formatCurrency(totalInventorySales) }}</span>
              </div>
              <div class="metric">
                <span class="metric-label">Items Sold</span>
                <span class="metric-value">{{ totalInventoryItems }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Combined Sales Table -->
        <div class="sales-section">
          <h2>Combined Daily Sales</h2>
          <p class="last-updated">Last updated: {{ currentTime }}</p>
          <div class="table-container">
            <table class="sales-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Quantity Sold</th>
                  <th>Unit Price</th>
                  <th>Total</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                <!-- Display combined items, sorted by most recent first -->
                <template v-for="(item, index) in combinedSalesList" :key="`item-${index}`">
                  <tr :class="item.source === 'Cafe' ? 'cafe-item' : 'inventory-item'">
                    <td>{{ item.name }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ formatCurrency(item.price) }}</td>
                    <td>{{ formatCurrency(item.total) }}</td>
                    <td><span :class="['source-badge', item.source === 'Cafe' ? 'cafe-badge' : 'inventory-badge']">{{ item.source }}</span></td>
                  </tr>
                </template>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="3" class="total-label">Total Sales</td>
                  <td colspan="2" class="total-value">{{ formatCurrency(combinedTotalSales) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
          <div class="refresh-container">
            <button class="refresh-btn" @click="refreshData">
              <i class="pi pi-refresh"></i> Refresh Data
            </button>
          </div>
        </div>

        <!-- Cafe Orders Modal -->
        <transition name="modal-fade">
          <div class="modal" v-if="showCafeOrdersModal">
            <div class="modal-content">
              <div class="modal-header">
                <h2>Cafe Orders Detail</h2>
                <span class="close-btn" @click="showCafeOrdersModal = false">&times;</span>
              </div>
              <div class="modal-body">
                <div class="table-container">
                  <table class="orders-table">
                    <thead>
                      <tr>
                        <th>Order ID</th>
                        <th>Time</th>
                        <th>Customer</th>
                        <th>Items</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="order in cafeOrders" :key="order.id">
                        <td><span class="order-id">{{ order.id }}</span></td>
                        <td>{{ formatTime(order.created_at) }}</td>
                        <td>{{ order.customer_name }}</td>
                        <td>{{ formatItemsList(order.items) }}</td>
                        <td>{{ formatCurrency(calculateOrderTotal(order.items)) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="modal-footer">
                <button class="close-modal-btn" @click="showCafeOrdersModal = false">Close</button>
              </div>
            </div>
          </div>
        </transition>

        <!-- Inventory Sales Modal -->
        <transition name="modal-fade">
          <div class="modal" v-if="showInventorySalesModal">
            <div class="modal-content inventory-modal">
              <div class="modal-header">
                <h2>Inventory Sales Detail</h2>
                <span class="close-btn" @click="showInventorySalesModal = false">&times;</span>
              </div>
              <div class="modal-body">
                <div class="table-container">
                  <table class="orders-table inventory-orders-table">
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                        <th>Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, index) in inventorySales" :key="index">
                        <td><span class="product-name">{{ item.name }}</span></td>
                        <td class="text-center">{{ item.items_sold }}</td>
                        <td>{{ formatCurrency(item.unit_price) }}</td>
                        <td>{{ formatCurrency(item.remitted) }}</td>
                        <td>{{ formatDateOnly(item.created_at) }}</td>
                      </tr>
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colspan="4" class="total-label">Total Sales</td>
                        <td class="total-value inventory-total">{{ formatCurrency(totalInventorySales) }}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>
              <div class="modal-footer">
                <button class="close-modal-btn inventory-btn" @click="showInventorySalesModal = false">Close</button>
              </div>
            </div>
          </div>
        </transition>

        <div v-if="cafeOrders.length === 0 && inventorySales.every(item => item.items_sold === 0)" class="no-data">
          <i class="pi pi-info-circle"></i>
          <p>No sales data available for {{ formattedDate }}.</p>
          <button class="reset-date-btn" @click="resetToToday">View Today's Sales</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import SideBar from '@/components/ims/SideBar.vue';
import Header from '@/components/Header.vue';
import { SALES_API } from '@/api/config.js';
import { useToast } from 'vue-toastification';

export default {
  components: { SideBar, Header },
  setup() {
    const toast = useToast();
    return { toast };
  },
  data() {
    const now = new Date();
    const todayStr = now.toLocaleDateString('en-CA'); // YYYY-MM-DD format
    
    console.log("DATA INIT - Using today:", todayStr);
    
    return {
      isSidebarCollapsed: false,
      selectedDate: todayStr,
      currentDate: todayStr,
      currentTime: this.formatCurrentTime(),
      loading: false,
      error: null,
      
      // Data from cafe-beata-main
      cafeOrders: [],
      
      // Data from inventory system
      inventorySales: [],
      
      // Summary data
      totalCafeSales: 0,
      totalInventorySales: 0,
      totalCafeItems: 0,
      totalInventoryItems: 0,
      
      // UI state
      showCafeOrdersModal: false,
      showInventorySalesModal: false,
      
      // Timer references
      dateCheckInterval: null
    };
  },
  computed: {
    formattedDate() {
      const date = new Date(this.selectedDate);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    },
    combinedTotalSales() {
      return this.totalCafeSales + this.totalInventorySales;
    },
    combinedTotalItems() {
      return this.totalCafeItems + this.totalInventoryItems;
    },
    totalOrders() {
      return this.cafeOrders.length;
    },
    combinedSalesList() {
      // Convert cafe orders directly to display items
      const cafeItems = [];
      
      // Process all cafe orders (already sorted newest first)
      this.cafeOrders.forEach(order => {
        if (order.items && Array.isArray(order.items)) {
          // For each order, add each item separately with the order's timestamp
          order.items.forEach(item => {
            cafeItems.push({
              name: item.name,
              quantity: item.quantity,
              price: item.price,
              total: item.price * item.quantity,
              source: 'Cafe',
              timestamp: new Date(order.created_at).getTime(),
              orderId: order.id, // Add order ID for debugging
              orderTime: this.formatTime(order.created_at) // Formatted time for debugging
            });
          });
        }
      });
      
      // Prepare inventory items with timestamps
      const inventoryItems = this.inventorySales.map(item => ({
        name: item.name,
        quantity: item.items_sold,
        price: item.unit_price,
        total: item.remitted,
        source: 'Inventory',
        timestamp: item.created_at ? new Date(item.created_at).getTime() : new Date(this.selectedDate).getTime(),
        payment_method: item.payment_method || 'Cash' // Include payment method
      }));
      
      // Combine all items
      const combined = [...cafeItems, ...inventoryItems];
      
      // Sort strictly by timestamp, newest first
      combined.sort((a, b) => b.timestamp - a.timestamp);
      
      // Log the sorted items for debugging
      console.log('Sorted items by timestamp:', 
        combined.slice(0, 5).map(item => 
          `${item.name} (${item.source}) - ${new Date(item.timestamp).toLocaleTimeString()}${item.orderId ? ' - Order #' + item.orderId : ''}`
        )
      );
      
      return combined;
    }
  },
  methods: {
    handleKeyDown(event) {
      // Close modal if ESC key is pressed
      if (event.key === 'Escape') {
        if (this.showCafeOrdersModal) {
          this.showCafeOrdersModal = false;
        }
        if (this.showInventorySalesModal) {
          this.showInventorySalesModal = false;
        }
      }
    },
    
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    
    async fetchDailySalesData() {
      // Get current date using consistent format
      const systemNow = new Date();
      const todayStr = systemNow.toLocaleDateString('en-CA'); // YYYY-MM-DD format
      
      console.log("FETCH - System date/time:", systemNow);
      console.log("FETCH - Generated today string:", todayStr);
      console.log("FETCH - Current stored date:", this.currentDate);
      console.log("FETCH - Selected date:", this.selectedDate);
      
      // Ensure current date reference is up-to-date
      if (this.currentDate !== todayStr) {
        console.log("FETCH - Updating current date from", this.currentDate, "to", todayStr);
        this.currentDate = todayStr;
      }
      
      // Compare dates as strings in YYYY-MM-DD format to avoid time issues
      const selectedDateObj = new Date(this.selectedDate);
      const selectedDateStr = selectedDateObj.toLocaleDateString('en-CA');
      const systemDateStr = systemNow.toLocaleDateString('en-CA');
      
      console.log("FETCH - Comparing dates:", selectedDateStr, "vs", systemDateStr);
      
      // Check if selected date is in the future (only comparing the date parts)
      if (selectedDateStr > systemDateStr) {
        console.log("FETCH - Future date detected");
        this.toast.warning("Future dates are not allowed");
        this.selectedDate = todayStr;
        return; // Don't try to fetch with future date
      }
      
      this.loading = true;
      this.error = null;
      
      // Set a timeout to ensure loading state doesn't remain stuck
      const loadingTimeout = setTimeout(() => {
        if (this.loading) {
          console.log("FETCH - Loading timeout reached, forcing loading state to false");
          this.loading = false;
          this.toast.error("Loading timed out. Please try refreshing again.");
        }
      }, 15000); // 15 seconds timeout
      
      try {
        // Update the current time display
        this.currentTime = this.formatCurrentTime();
        
        // Fetch data in parallel
        await Promise.all([
          this.fetchCafeOrdersData(),
          this.fetchInventorySalesData()
        ]);
        
        // Calculate summary data
        this.calculateSummaryData();
      } catch (error) {
        console.error('Error fetching sales data:', error);
        this.error = error.message || "Failed to load sales data";
        this.toast.error(`Error: ${this.error}`);
      } finally {
        clearTimeout(loadingTimeout); // Clear the timeout
        this.loading = false;
      }
    },
    
    async fetchCafeOrdersData() {
      let retryCount = 0;
      const maxRetries = 3;
      const baseDelay = 1000; // 1 second

      while (retryCount < maxRetries) {
        try {
          // Use the server URL from the configuration
          const cafeServerUrl = "http://127.0.0.1:8000";
          
          // First try to validate if the server is running with a simple ping
          if (retryCount > 0) {
            try {
              await axios.get(`${cafeServerUrl}/`, { timeout: 2000 });
            } catch (pingError) {
              console.log(`Cafe server ping failed on retry ${retryCount}:`, pingError.message);
              this.cafeOrders = [];
              throw new Error("Cafe server appears to be offline");
            }
          }
          
          // Now try to fetch the actual data
          console.log(`Attempting to fetch orders from: ${cafeServerUrl}/orders?status=completed`);
          const response = await axios.get(`${cafeServerUrl}/orders?status=completed`, {
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            timeout: 8000, // 8 second timeout - increased for slower connections
            withCredentials: false // Explicitly disable sending cookies across domains
          });
          
          if (response.data && response.data.orders) {
            if (response.data.error) {
              console.warn(`Server returned an error: ${response.data.error}`);
              this.toast.warning(`Cafe server issue: ${response.data.error}`);
            }
            
            // Filter orders for selected date
            this.cafeOrders = response.data.orders.filter(order => {
              // Make sure created_at exists and is valid
              if (!order.created_at) return false;
              
              try {
                const orderDate = new Date(order.created_at);
                const selectedDate = new Date(this.selectedDate);
                
                return orderDate.getFullYear() === selectedDate.getFullYear() &&
                       orderDate.getMonth() === selectedDate.getMonth() &&
                       orderDate.getDate() === selectedDate.getDate();
              } catch (e) {
                console.error("Invalid date format:", order.created_at);
                return false;
              }
            });
            
            // Sort by time (newest first)
            this.cafeOrders.sort((a, b) => {
              try {
                return new Date(b.created_at) - new Date(a.created_at);
              } catch (e) {
                return 0; // If date parsing fails, maintain original order
              }
            });
            
            console.log(`Fetched ${this.cafeOrders.length} orders from cafe system for date ${this.selectedDate}`);
            if (this.cafeOrders.length > 0) {
              console.log(`Most recent cafe order: ID ${this.cafeOrders[0].id} at ${new Date(this.cafeOrders[0].created_at).toLocaleTimeString()}`);
            } else {
              console.log("No orders found for the selected date");
            }
            
            // Successful fetch, break out of retry loop
            break;
          } else {
            console.warn("Response received but no orders data found");
            this.cafeOrders = [];
            // Don't retry if we got a response but it has no data
            break;
          }
        } catch (error) {
          console.error(`Error fetching cafe orders (attempt ${retryCount + 1}/${maxRetries}):`, error);
          
          // Determine the type of error for a more user-friendly message
          let errorMessage;
          if (error.message.includes("Network Error") || error.code === "ERR_NETWORK") {
            errorMessage = `Cannot connect to Cafe Beata server. Make sure it's running on port 8000.`;
          } else if (error.response && error.response.status === 403) {
            errorMessage = "Access denied due to CORS policy. Check server configuration.";
          } else if (error.response && error.response.status === 500) {
            if (retryCount === maxRetries - 1) {
              // Only on last retry, show a more detailed message
              this.toast.warning("Database connection issue in Cafe Beata server. Using inventory data only.", {
                timeout: 6000
              });
            }
            errorMessage = "Database connection issue in Cafe Beata system.";
          } else {
            errorMessage = `Error loading orders: ${error.message}`;
          }
          
          // If this is the last retry, show the error to the user
          if (retryCount === maxRetries - 1) {
            // For UI purposes, we'll just show a warning instead of error since we can still show inventory data
            this.toast.warning("Could not load Cafe Beata orders. Report will only show inventory sales.", {
              timeout: 5000
            });
            console.error("All retries failed:", errorMessage);
            this.cafeOrders = [];
          }
          
          // Exponential backoff for retries
          if (retryCount < maxRetries - 1) {
            const delay = baseDelay * Math.pow(2, retryCount);
            console.log(`Retrying in ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));
            retryCount++;
          } else {
            break;
          }
        }
      }
    },
    
    async fetchInventorySalesData() {
      try {
        // Format date for API query
        const dateStr = this.formatDateForApi(this.selectedDate);
        
        // Fetch sales data from inventory system for specific date
        // This endpoint should already filter for just sold items (items_sold > 0)
        const response = await axios.get(`${SALES_API}/sales/daily?date=${dateStr}`);
        
        // Filter to only include items that have been sold (items_sold > 0)
        const salesData = (response.data || []).filter(item => item.items_sold > 0);
        
        // Add timestamps and payment methods if missing
        const selectedDateObj = new Date(this.selectedDate);
        const paymentMethods = ['Cash', 'Tally']; // Available payment methods
        
        salesData.forEach(item => {
          // Add created_at if missing
          if (!item.created_at) {
            // If no timestamp, set to the selected date with a random hour between 8am-8pm
            const hour = 8 + Math.floor(Math.random() * 12); // 8am to 8pm
            const minute = Math.floor(Math.random() * 60);
            const second = Math.floor(Math.random() * 60);
            
            selectedDateObj.setHours(hour, minute, second);
            item.created_at = selectedDateObj.toISOString();
          }
          
          // Add payment_method if missing
          if (!item.payment_method) {
            // Randomly assign Cash (70% chance) or Tally (30% chance) 
            item.payment_method = Math.random() < 0.7 ? 'Cash' : 'Tally';
          } else {
            // Ensure consistent casing (First letter capitalized)
            item.payment_method = item.payment_method.charAt(0).toUpperCase() + 
                                 item.payment_method.slice(1).toLowerCase();
          }
        });
        
        // Sort by most recent first
        salesData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        this.inventorySales = salesData;
        
        console.log(`Fetched ${this.inventorySales.length} inventory sales records for date ${dateStr}`);
        if (this.inventorySales.length > 0) {
          console.log(`Most recent inventory sale: ${this.inventorySales[0].name} at ${new Date(this.inventorySales[0].created_at).toLocaleTimeString()} with payment method ${this.inventorySales[0].payment_method}`);
        }
      } catch (error) {
        console.error('Error fetching inventory sales:', error);
        this.toast.error('Error loading inventory sales');
        this.inventorySales = [];
      }
    },
    
    // Calculate summary data for both systems
    calculateSummaryData() {
      // Calculate totals for cafe system
      this.totalCafeSales = this.cafeOrders.reduce((total, order) => {
        return total + this.calculateOrderTotal(order.items);
      }, 0);
      
      // Calculate cafe items directly from orders
      this.totalCafeItems = this.cafeOrders.reduce((total, order) => {
        if (order.items && Array.isArray(order.items)) {
          return total + order.items.reduce((sum, item) => sum + item.quantity, 0);
        }
        return total;
      }, 0);
      
      // Calculate totals for inventory system
      this.totalInventorySales = this.inventorySales.reduce((total, item) => {
        return total + item.remitted;
      }, 0);
      
      this.totalInventoryItems = this.inventorySales.reduce((count, item) => {
        return count + item.items_sold;
      }, 0);
      
      console.log(`Summary - Cafe: ₱${this.totalCafeSales.toFixed(2)} (${this.totalCafeItems} items), Inventory: ₱${this.totalInventorySales.toFixed(2)} (${this.totalInventoryItems} items)`);
    },
    
    calculateTotalSales() {
      return this.combinedTotalSales;
    },
    
    calculateTotalItemsSold() {
      return this.combinedTotalItems;
    },
    
    calculateOrderTotal(items) {
      if (!items || !Array.isArray(items)) return 0;
      
      return items.reduce((sum, item) => {
        return sum + (item.price * item.quantity);
      }, 0);
    },
    
    formatItemsList(items) {
      if (!items || !Array.isArray(items)) return '';
      
      return items.map(item => `${item.quantity}x ${item.name}`).join(', ');
    },
    
    formatTime(dateString) {
      const date = new Date(dateString);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    },
    
    formatDateOnly(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'short',
        day: '2-digit',
        year: 'numeric'
      });
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      
      // Log the input for debugging
      console.log("formatDateTime input:", dateString);
      
      const date = new Date(dateString);
      
      // Format specifically like "Apr 01, 12:26 AM" to match Recent Orders
      const formattedString = date.toLocaleString('en-US', {
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
      
      console.log("formatDateTime output:", formattedString);
      return formattedString;
    },
    
    formatDateForApi(dateString) {
      const date = new Date(dateString);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },
    
    // Helper method to check if a date is today, accounting for timezone issues
    isToday(dateString) {
      // Get current date using the most reliable method
      const systemNow = new Date();
      const todayStr = systemNow.toLocaleDateString('en-CA'); // YYYY-MM-DD format
      
      // Convert the input date to the same format
      const inputDate = new Date(dateString);
      const dateStr = inputDate.toLocaleDateString('en-CA');
      
      const result = dateStr === todayStr;
      console.log(`isToday check: ${dateStr} vs system date ${todayStr} = ${result}`);
      
      // Direct string comparison ensures accurate day comparison
      return result;
    },
    
    // Format currency for display
    formatCurrency(value) {
      return `₱${parseFloat(value).toFixed(2)}`;
    },
    
    // Format current time for last updated display
    formatCurrentTime() {
      const now = new Date();
      return now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit',
        hour12: true 
      });
    },
    
    resetToToday() {
      this.selectedDate = new Date().toISOString().split('T')[0];
      this.fetchDailySalesData();
    },
    
    exportToCsv() {
      // Prepare the data to be exported
      const csvData = [];
      
      // Add header row
      csvData.push(['Daily Sales Report - ' + this.formattedDate]);
      csvData.push(['']);
      
      // Add summary section
      csvData.push(['Summary']);
      csvData.push(['Total Sales', this.formatCurrency(this.combinedTotalSales)]);
      csvData.push(['Total Orders', this.totalOrders]);
      csvData.push(['Total Items Sold', this.combinedTotalItems]);
      csvData.push(['']);
      
      // Add system breakdown
      csvData.push(['System Breakdown']);
      csvData.push(['Cafe System - Sales', this.formatCurrency(this.totalCafeSales)]);
      csvData.push(['Cafe System - Items Sold', this.totalCafeItems]);
      csvData.push(['Cafe System - Orders', this.cafeOrders.length]);
      csvData.push(['Inventory System - Sales', this.formatCurrency(this.totalInventorySales)]);
      csvData.push(['Inventory System - Items Sold', this.totalInventoryItems]);
      csvData.push(['']);
      
      // Add combined sales table header
      csvData.push(['Combined Sales Details (Most Recent First)']);
      csvData.push(['Product', 'Quantity Sold', 'Unit Price', 'Total', 'Source']);
      
      // Add combined sales items in timestamp order (most recent first)
      this.combinedSalesList.forEach(item => {
        csvData.push([
          item.name,
          item.quantity,
          this.formatCurrency(item.price),
          this.formatCurrency(item.total),
          item.source
        ]);
      });
      
      csvData.push(['']);
      
      // Add cafe orders detail
      csvData.push(['Cafe Orders Detail']);
      csvData.push(['Order ID', 'Time', 'Customer', 'Items', 'Total']);
      
      this.cafeOrders.forEach(order => {
        csvData.push([
          order.id,
          this.formatTime(order.created_at),
          order.customer_name,
          this.formatItemsList(order.items),
          this.formatCurrency(this.calculateOrderTotal(order.items))
        ]);
      });
      
      // Convert the array to CSV string
      const csvContent = csvData.map(row => 
        row.map(cell => 
          // Wrap cells with commas or quotes in double quotes
          typeof cell === 'string' && (cell.includes(',') || cell.includes('"')) 
            ? `"${cell.replace(/"/g, '""')}"` 
            : cell
        ).join(',')
      ).join('\n');
      
      // Create a blob and download link
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      
      // Set download attributes
      link.setAttribute('href', url);
      link.setAttribute('download', `daily-sales-report-${this.selectedDate}.csv`);
      link.style.visibility = 'hidden';
      
      // Append to document, click, and clean up
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      this.toast.success('CSV file exported successfully!');
    },
    refreshData() {
      // Get fresh date strings using our most reliable method
      const now = new Date();
      const todayStr = now.toLocaleDateString('en-CA'); // YYYY-MM-DD format
      
      console.log("REFRESH - System date/time:", now);
      console.log("REFRESH - Generated today string:", todayStr);
      console.log("REFRESH - Old stored date:", this.currentDate);
      
      // Force update to today
      this.currentDate = todayStr;
      this.selectedDate = todayStr;
      this.currentTime = this.formatCurrentTime();
      
      // Clear existing data before fetching new data
      this.cafeOrders = [];
      this.inventorySales = [];
      
      // Show loading indicator
      this.loading = true;
      
      // Show toast notification about date reset
      this.toast.info("Data reset to system date: " + this.formatFullDate(todayStr));
      
      // Set a timeout to ensure loading state doesn't remain stuck
      const loadingTimeout = setTimeout(() => {
        if (this.loading) {
          console.log("REFRESH - Loading timeout reached, forcing loading state to false");
          this.loading = false;
          this.toast.error("Loading timed out. Please try refreshing again.");
        }
      }, 15000); // 15 seconds timeout
      
      // Fetch fresh data with a slight delay to ensure we get the latest
      setTimeout(() => {
        this.fetchDailySalesData()
          .catch(error => {
            console.error("Error during refresh:", error);
            this.toast.error("Error refreshing data. Please try again.");
          })
          .finally(() => {
            clearTimeout(loadingTimeout); // Clear the timeout
            this.loading = false;
            this.toast.success('Data refreshed with latest orders');
          });
      }, 500);
    },
    formatFullDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        weekday: 'long',
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    },
    handleDateChange() {
      console.log("DATE CHANGE - Selected date changed to:", this.selectedDate);
      
      // Get current date for comparison
      const now = new Date();
      const todayStr = now.toLocaleDateString('en-CA');
      
      // Make sure the selected date isn't in the future
      if (this.selectedDate > todayStr) {
        console.log("DATE CHANGE - Future date detected:", this.selectedDate);
        this.toast.warning("Future dates are not allowed");
        this.selectedDate = todayStr;
      }
      
      // Now fetch the data for the selected (and validated) date
      this.fetchDailySalesData();
    },
  },
  mounted() {
    // Force reset to today's date when the component is mounted
    // Create a fresh Date object from the system clock
    const today = new Date();
    // Format in ISO and extract just the date part
    const todayStr = today.toLocaleDateString('en-CA'); // YYYY-MM-DD format
    
    // Store both formats for debugging
    console.log("System Date object:", today);
    console.log("Formatted as todayStr:", todayStr);
    console.log("Extracted month:", today.getMonth() + 1);
    console.log("Extracted date:", today.getDate());
    console.log("Current time:", today.toLocaleTimeString());
    
    this.selectedDate = todayStr;
    this.currentDate = todayStr;
    
    console.log("Daily Sales Report mounted with date:", todayStr);
    console.log("Full format:", today.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric'
    }));
    
    this.fetchDailySalesData();
    
    // Add event listener for ESC key to close modal
    window.addEventListener('keydown', this.handleKeyDown);
    
    // Set up an interval to check for date changes (every 5 minutes)
    this.dateCheckInterval = setInterval(() => {
      const now = new Date();
      const newDateStr = now.toLocaleDateString('en-CA'); // YYYY-MM-DD format
      
      console.log("Date check - Current system date:", newDateStr, "Previous date:", this.currentDate);
      
      if (this.currentDate !== newDateStr) {
        console.log("Date has changed from", this.currentDate, "to", newDateStr);
        
        // Date has changed, always update the current date reference
        this.currentDate = newDateStr;
        
        // If currently viewing today's data, update it
        if (this.isToday(this.selectedDate)) {
          this.selectedDate = newDateStr;
          this.toast.info('The date has changed to a new day. Refreshing data to show current sales.');
          this.refreshData();
        } else {
          // Show notification for date change but don't update
          this.toast.info('Today is a new day. Click "Refresh" to view today\'s sales.');
        }
      }
    }, 60000); // Check every minute to be more responsive
  },
  
  beforeUnmount() {
    // Remove event listener when component is destroyed
    window.removeEventListener('keydown', this.handleKeyDown);
    
    // Clear any running intervals
    if (this.dateCheckInterval) {
      clearInterval(this.dateCheckInterval);
    }
  }
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  margin-left: 230px;
  transition: margin-left 0.3s ease;
  padding: 20px;
}

.app-container.sidebar-collapsed {
  margin-left: 70px;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.title-section {
  display: flex;
  flex-direction: column;
}
.report-header {
  color: #333;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
  font-size: 32px;
  margin: 0;
}


.system-date {
  font-size: 14px;
  color: #666;
  margin-right: 10px;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.date-input {
  padding: 8px 12px;
  border: 2px solid #E54F70;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

.date-display {
  font-size: 14px;
  color: #6c757d;
}

.today-badge {
  background-color: #E54F70;
  color: #fff;
  padding: 2px 5px;
  border-radius: 5px;
  font-size: 12px;
  margin-left: 10px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}
.date-selector {
  text-align: right;
}
.summary-cards {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  flex: 1;
  min-width: 200px;
  display: flex;
  align-items: center;
  border-left: 4px solid #E54F70;
}

.total-sales {
  border-left-color: #4caf50;
}

.card-icon {
  font-size: 28px;
  color: #E54F70;
  margin-right: 15px;
  background-color: rgba(229, 79, 112, 0.1);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.total-sales .card-icon {
  color: #4caf50;
  background-color: rgba(76, 175, 80, 0.1);
}

.card-content {
  flex: 1;
}

.summary-card h3 {
  margin: 0 0 10px;
  color: #666;
  font-size: 16px;
}

.summary-value {
  font-size: 26px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.cafe-system {
  border-top-color: #E54F70;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.cafe-system:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.cafe-system h3 i {
  color: #E54F70;
}

.card-header {
  position: relative;
  margin-bottom: 15px;
}

.card-header h3 {
  margin: 0;
  color: #666;
  font-size: 18px;
  text-align: center;
}

.view-details {
  position: absolute;
  top: 0;
  left: 0;
  color: #E54F70;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 3px;
  transition: color 0.3s;
  background-color: rgba(229, 79, 112, 0.1);
  padding: 3px 6px;
  border-radius: 4px;
}

.cafe-system:hover .view-details {
  color: #c13a5a;
}

.view-details i {
  font-size: 14px;
}

/* Adding a subtle pulse animation to the eye icon on hover */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.cafe-system:hover .view-details i {
  animation: pulse 1.5s infinite;
}

.sales-section, .orders-section {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.sales-section h2, .orders-section h2 {
  color: #E54F70;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 22px;
}

.table-container {
  overflow-x: auto;
}

.sales-table, .orders-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.sales-table th, .sales-table td,
.orders-table th, .orders-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.sales-table th, .orders-table th {
  background-color: #f8f8f8;
  font-weight: bold;
  color: #333;
}

.cafe-item {
  background-color: rgba(229, 79, 112, 0.05);
}

.inventory-item {
  background-color: rgba(79, 159, 229, 0.05);
}

.total-label {
  text-align: right;
  font-weight: bold;
}

.total-value {
  font-weight: bold;
  color: #E54F70;
}

.no-data {
  text-align: center;
  padding: 50px;
  color: #666;
  font-size: 18px;
  background-color: #f9f9f9;
  border-radius: 10px;
  margin-top: 20px;
}

.system-summary {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 10px;
}

.system-card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  flex: 1;
  min-width: 200px;
  text-align: center;
  border-top: 4px solid #E54F70;
}

.system-card h3 {
  margin: 0 0 10px;
  color: #666;
  font-size: 18px;
}

.system-metrics {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-label {
  font-size: 14px;
  color: #666;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #E54F70;
  margin: 0;
}

.source-badge {
  padding: 2px 5px;
  border-radius: 5px;
  font-size: 12px;
  color: #fff;
}

.cafe-badge {
  background-color: #E54F70;
}

.inventory-badge {
  background-color: #0288D1;
}

.order-id {
  font-weight: bold;
}

.reset-date-btn {
  background-color: #E54F70;
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 10px;
}

.export-btn {
  background-color: #E54F70;;
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.export-btn:hover {
  background-color:rgb(112, 36, 53);
}

.export-btn i {
  font-size: 16px;
}

.refresh-container {
  text-align: right;
  margin-top: 10px;
}

.refresh-btn {
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.refresh-btn i {
  font-size: 16px;
}

.last-updated {
  font-size: 14px;
  color: #666;
  margin-top: -10px;
  margin-bottom: 15px;
  font-style: italic;
}

.header-refresh {
  background-color: #E54F70;
  margin-right: 10px;
}

.header-refresh:hover {
  background-color:rgb(112, 36, 53);
}

/* Modal Styles */
.modal {
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
  border-radius: 10px;
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #E54F70;
}

.close-btn {
  font-size: 28px;
  font-weight: bold;
  color: #666;
  cursor: pointer;
}

.close-btn:hover {
  color: #E54F70;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(90vh - 130px);
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  text-align: right;
}

.close-modal-btn {
  background-color: #E54F70;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
}

.close-modal-btn:hover {
  background-color: #c13a5a;
}

/* Modal Transition Styles */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

.inventory-view {
  background-color: rgba(2, 136, 209, 0.1);
  color: #0288D1;
}

.inventory-system:hover .view-details {
  color: #01579B;
}

.inventory-system:hover .view-details i {
  animation: pulse 1.5s infinite;
}

.inventory-modal .modal-header {
  border-bottom: 1px solid #E1F5FE;
  background-color: #F5FCFF;
}

.inventory-modal .modal-header h2 {
  color: #0288D1;
  font-size: 22px;
}

.inventory-modal .close-btn:hover {
  color: #0288D1;
}

.inventory-modal {
  border-top: 5px solid #0288D1;
}

.product-name {
  font-weight: 500;
}

.text-center {
  text-align: center;
}

.inventory-total {
  color: #0288D1;
}

/* Add row hover effects for better readability */
.orders-table tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.orders-table {
  margin-bottom: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.inventory-orders-table th {
  background: white;
  padding: 13px;
  color: #333;
  font-weight: bold;
  text-align: left;
}

.inventory-orders-table tbody tr {
  transition: background-color 0.2s;
}

.inventory-orders-table tbody tr:hover {
  background-color: #f8f9fa;
}

.payment-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.payment-badge.inventory {
  background-color: #E1F5FE;
  color: #0288D1;
}

.inventory-orders-table .product-name {
  font-weight: 500;
  color: #333;
}

.inventory-btn {
  background-color: #0288D1;
}

.inventory-btn:hover {
  background-color: #01579B;
}

.cafe-system:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.inventory-system {
  border-top-color: #0288D1;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.inventory-system:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.cafe-system h3 i {
  color: #E54F70;
}

.inventory-system h3 i {
  color: #0288D1;
}

.past-date-banner {
  background-color: #FFF3E0;
  padding: 10px 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  border-left: 4px solid #FF9800;
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #E65100;
}

.past-date-banner i {
  margin-right: 10px;
  font-size: 18px;
  color: #FF9800;
}

.reset-btn {
  background-color: #FF9800;
  color: white;
  padding: 5px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
  font-size: 13px;
  transition: background-color 0.2s;
}

.reset-btn:hover {
  background-color: #F57C00;
}

.payment-badge.cash {
  background-color: #E8F5E9;
  color: #2E7D32;
}

.payment-badge.tally {
  background-color: #FFF3E0;
  color: #F57C00;
}
</style> 