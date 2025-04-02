<template>
  <div class="dashboard">
    <!-- Sidebar Toggle Button (For Mobile) -->
    <button class="menu-button" @click="toggleSidebar">
      <div class="menu-icon-container">
        ≡
      </div>
    </button>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    
    <div v-if="isSidebarOpen" class="overlay" @click="closeSidebar"></div>
    
    <!-- Sidebar -->
    <div :class="['sidebar', { 
      'open': isSidebarOpen, 
      'light-mode': !isDarkMode,
      'dark-mode': isDarkMode 
    }]" @click.stop>
      <button class="close-sidebar" @click="toggleSidebar">✕</button>
      
      <!-- User Profile Section -->
      <div class="user-profile-section">
        <div class="profile-image">
          <!-- Use the same method for getting avatar as in UserProfileCafe -->
          <img :src="getAvatarUrl(userAvatar)" alt="Profile Picture">
        </div>
        <div class="profile-info">
          <span class="user-name">{{ userName }}</span>
        </div>
      </div>

      <!-- Dark Mode Toggle beside profile -->
      <button class="theme-toggle" @click="toggleDarkMode">
        <i :class="['fas', isDarkMode ? 'fa-sun' : 'fa-moon', { 'light-icon': !isDarkMode, 'dark-icon': isDarkMode }]"></i>
      </button>

      <!-- Profile Section -->
      <button class="profile-section" @click="handleProfile">
        <i class="fas fa-user"></i>
        <span>Profile</span>
      </button>

      <hr class="utility-divider">

      <!-- Utility Buttons Section -->
      <div class="utility-section">
        <button class="utility-button" @click="handleOrderHistory">
          <i class="fas fa-history"></i>
          <span>Order History</span>
        </button>
        
        <!-- Other utility buttons can be added here if needed -->
      </div>

      <!-- Categories -->
      <div class="menu-section">
        <h3>Drinks</h3>
        <div class="menu-items">
          <button 
            class="menu-item" 
            @click="filterCategory('All Drinks')"
          >
            <i class="fas fa-coffee"></i>
            <span>All Drinks</span>
          </button>
          <button 
            v-for="category in drinkCategories" 
            :key="category"
            class="menu-item" 
            @click="filterCategory(category)"
          >
            <i :class="getCategoryIcon(category)"></i>
            <span>{{ category }}</span>
          </button>
        </div>

        <h3>Food</h3>
        <div class="menu-items">
          <button 
            class="menu-item" 
            @click="filterCategory('All Food')"
          >
            <i class="fas fa-utensils"></i>
            <span>All Food</span>
          </button>
          <button 
            v-for="category in foodCategories" 
            :key="category"
            class="menu-item" 
            @click="filterCategory(category)"
          >
            <i :class="getCategoryIcon(category)"></i>
            <span>{{ category }}</span>
          </button>
        </div>
        
        <div class="menu-category">
          <!-- Ready Made Products Section -->
          <h3>
            Ready Made Items
            <button 
              v-if="isAdmin" 
              class="sync-button prominent" 
              @click="syncInventoryProducts" 
              :disabled="isSyncing"
              title="Pull latest Ready Made products from Inventory System"
            >
              <i :class="isSyncing ? 'fas fa-sync fa-spin' : 'fas fa-sync'"></i>
              <span>{{ isSyncing ? 'Syncing...' : 'Sync Inventory' }}</span>
            </button>
          </h3>
          <div class="menu-items">
            <button 
              class="menu-item" 
              @click="filterCategory('All Ready Made')"
            >
              <i class="fas fa-shopping-basket"></i>
              <span>Ready Made</span>
            </button>
            <!-- Remove the v-for for readyMadeCategories since we just need a single entry -->
          </div>
        </div>
      </div>

      <!-- Logout Button -->
      <div class="logout-container">
        <button class="utility-button logout" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Logout</span>
        </button>
      </div>
    </div>

    <!-- Main content area -->
    <div :class="['content', { 'close': isSidebarOpen }]" @click="closeSidebar">
      <!-- Top Bar -->
      <div class="top-bar">
        <div class="centered-content">
          <div class="logo-container">
            <img src="@/assets/cafe-logo1.png" alt="University Logo" class="logo logo-light" />
            <div class="cafe-title">Cafe Beata</div>
          </div>
          
          <div class="search-container">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search our Drinks and Food"
              @input="filterItems"
            />
          </div>
          
          <div class="top-controls">
            <div class="live-time">{{ currentTime }}</div>
            <!-- Add UserNotifications component inside top bar -->
            <UserNotifications />
          </div>
        </div>
      </div>
      
      <!-- Floating Cart Button - keep this outside the top bar -->
      <div class="floating-cart" @click="goToCart">
        <i class="fas fa-shopping-cart"></i>
        <span v-if="cartItemCount > 0" class="floating-cart-badge">{{ cartItemCount }}</span>
      </div>

      <!-- Dashboard Title -->
      <h1 class="dashboard-title"></h1>
      

      <!-- Display category title dynamically -->
      <div class="category-header">
        <h2>{{ 
          currentCategory === 'All Drinks' ? 'Menu' : 
          currentCategory === 'All Ready Made' ? 'Ready Made Items' : 
          currentCategory 
        }}</h2>
      </div>

      <!-- Loading indicator -->
      <div v-if="isLoading" class="loading-indicator">
        <p>Loading menu items...</p>
      </div>

      <!-- Display filtered items based on the current category -->
      <div v-else-if="filteredItems.length" class="items">
        <div
          v-for="item in filteredItems"
          :key="item.id || item.name"
          class="item"
          @click="checkAndNavigate(item)"
          :class="{
            'out-of-stock': !itemStocks[item.id]?.quantity,
            'inventory-item': isInventoryItemStyled(item)
          }"
        >
          <div class="item-image-container">
            <img 
              :src="getImagePath(item.image)" 
              :alt="item.name" 
              @error="handleImageError" 
            />
            <div v-if="isInventoryItem(item) && isInventoryItemStyled(item)" class="inventory-badge" title="From Inventory System">
              <i class="fas fa-box-open"></i>
              <span>Inventory</span>
            </div>
          </div>
          <StockIndicator 
            v-if="itemStocks[item.id]"
            :itemId="item.id" 
            :quantity="itemStocks[item.id]?.quantity || 0" 
            :minStockLevel="10"
          />
          <div class="item-details">
            <span>{{ item.name }}</span>
            <span class="item-price">₱{{ Number(item.price).toFixed(2) }}</span>
          </div>
        </div>
      </div>
      <div v-else class="no-items">
        <p>No items found in this category.</p>
      </div>

      <!-- Item Click Modal -->
      <div v-if="showItemModal" class="item-modal">
        <div class="modal-content">
          <span class="close" @click="closeItemModal">&times;</span>
          <div class="modal-item-details">
            <div class="modal-image-container">
              <img 
                :src="selectedItem ? getImagePath(selectedItem.image) : require('@/assets/default.png')" 
                :alt="selectedItem ? selectedItem.name : ''" 
                @error="handleImageError"
              />
              <div v-if="selectedItem && isInventoryItem(selectedItem) && isInventoryItemStyled(selectedItem)" class="inventory-badge-modal" title="From Inventory System">
                <i class="fas fa-box-open"></i>
                <span>Inventory Item</span>
              </div>
            </div>
            <h3>{{ selectedItem ? selectedItem.name : '' }}</h3>
            <p class="price">₱{{ selectedItem ? Number(selectedItem.price).toFixed(2) : '0.00' }}</p>
            
            <!-- Add quantity controls -->
            <div class="modal-quantity-controls">
              <button @click="decreaseModalQuantity" class="quantity-btn">-</button>
              <span class="quantity-display">{{ modalQuantity }}</span>
              <button @click="increaseModalQuantity" class="quantity-btn">+</button>
            </div>
            <p class="total-price">Total: ₱{{ selectedItem ? (Number(selectedItem.price) * modalQuantity).toFixed(2) : '0.00' }}</p>
          </div>
          <div class="modal-buttons">
            <button @click="addToCart" class="add-cart-btn">Add to Cart</button>
            <button @click="orderNow" class="order-now-btn">Order Now</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>



<script>
import StockIndicator from './StockIndicator.vue';
// Import UserNotifications component
import UserNotifications from '@/components/UserNotifications.vue';
import { eventBus } from "@/utils/eventBus";

export default {
  components: {
    StockIndicator,
    UserNotifications
  },
  data() {
    return {
      userName: '',
      userProfileImage: '',
      userEmail: localStorage.getItem('userEmail'),
      itemsRefreshInterval: null,
      searchQuery: '',
      isDarkMode: localStorage.getItem("darkMode") === "true",
      currentCategory: 'All Drinks',
      currentTime: new Date().toLocaleTimeString(),
      isSidebarOpen: false,
      isLoading: false,
      apiItems: [],
      filteredItems: [],
      categories: [],
      showItemModal: false,
      selectedItem: null,
      cartItemCount: 0,
      cart: [], // Array to store cart items
      modalQuantity: 1,
      itemStocks: {}, // Add back the itemStocks property
      ws: null,
      wsConnected: false,
      isAdmin: localStorage.getItem('role') === 'admin',
      isSyncing: false,
      userAvatar: '', // Add this property to store the user's avatar URL
      unreadNotificationsCount: 0,
    };
  },

  

  created() {
    // Just listen for notification updates to sync with UserNotifications
    window.addEventListener("notificationUpdated", this.handleNotificationUpdate);
    window.addEventListener("items-updated", this.handleItemsUpdated);
    this.initWebSocket();
  },
  
  beforeUnmount() {
    // Remove listeners
    window.removeEventListener("notificationUpdated", this.handleNotificationUpdate);
    window.removeEventListener("items-updated", this.handleItemsUpdated);
    window.removeEventListener('categories-updated', this.handleCategoriesUpdated);
    this.stopPollingForItems();
    window.removeEventListener('storage', this.updateCartCount);
    if (this.ws) {
      this.ws.close();
    }
  },
  
  async mounted() {
    // Watch for notification updates through eventBus for UI updates
    this.$watch(() => eventBus.notificationsCount, (newCount) => {
      console.log('Notification count updated:', newCount);
      // No need to store locally as UserNotifications manages this
    });
    
    // Check for last viewed category first
    const lastViewedCategory = localStorage.getItem('lastViewedCategory');
    if (lastViewedCategory) {
      this.currentCategory = lastViewedCategory;
    } else if (this.$route.query.category) {
      // Only use route query if no last viewed category exists
      this.currentCategory = this.$route.query.category;
    }
    
    this.updateTime();
    this.applyDarkMode(this.isDarkMode);
    await this.loadUserProfile();
    
    // Initialize WebSocket first for real-time updates
    this.initWebSocket();
    
    // Load initial data
    await this.fetchItems();
    this.startPollingForItems();
    await this.loadCategories();
    
    // Trigger a sync of inventory products when the component mounts
    // This ensures the latest Ready Made products are available
    try {
      if (!this.isSyncing) {
        console.log('Triggering inventory sync on component mount');
        await this.syncInventoryProducts();
      }
    } catch (error) {
      console.error('Error syncing inventory on mount:', error);
    }
    
    // Filter items after loading everything
    this.filterItems();
    
    window.addEventListener('categories-updated', this.handleCategoriesUpdated);
    this.updateCartCount();
    window.addEventListener('storage', this.updateCartCount);
  },
    
 
  methods: {
    // Handle notification updates
    handleNotificationUpdate() {
      // This event is fired when notifications are updated
      // The UserNotifications component already manages the badge state
      console.log('Notification update detected');
    },
    
    // Handle item updates from ItemEditor
    handleItemsUpdated(event) {
      console.log('Items updated event received:', event.detail);
      
      // Silently refresh items without showing loading indicators
      try {
        fetch('http://localhost:8000/api/items')
          .then(response => response.json())
          .then(data => {
            if (data.items) {
              this.apiItems = data.items;
              this.filterItems();
            }
          });
      } catch (error) {
        console.error('Error refreshing items after update:', error);
      }
      
      // Only switch to the category if the user is not on the "All Drinks" view
      // This way, new items will appear in the All Drinks view without changing the user's context
      if (this.currentCategory !== 'All Drinks' && event.detail.action !== 'deleted' && 
          event.detail.category && event.detail.category !== this.currentCategory) {
        this.currentCategory = event.detail.category;
      }
    },
    
    // New method to manually refresh items
    async refreshItems() {
      this.isLoading = true;
      await this.fetchItems();
      this.filterItems();
      this.isLoading = false;
    },
    
    // New method to start polling for items
    startPollingForItems() {
      this.itemsRefreshInterval = setInterval(async () => {
        // Fetch items silently in the background without showing loading indicators
        try {
          const response = await fetch('http://localhost:8000/api/items');
          const data = await response.json();
          if (data.items) {
            this.apiItems = data.items;
            // Update filtered items without changing the loading state
            this.filterItems();
          }
        } catch (error) {
          console.error('Error fetching items during background refresh:', error);
        }
      }, 10000); // Check for new items every 10 seconds
    },
    
    // New method to stop polling for items
    stopPollingForItems() {
      if (this.itemsRefreshInterval) {
        clearInterval(this.itemsRefreshInterval);
      }
    },
    
    // New method to fetch items from API
    async fetchItems() {
      const wasLoading = this.isLoading;
      
      try {
        const [itemsResponse, stocksResponse] = await Promise.all([
          fetch('http://localhost:8000/api/items'),
          fetch('http://localhost:8000/api/stocks')
        ]);
        
        const itemsData = await itemsResponse.json();
        const stocksData = await stocksResponse.json();
        
        if (itemsData.items) {
          this.apiItems = itemsData.items;
          
          // Debug log for inventory items
          const inventoryItems = this.apiItems.filter(item => item.external_source === 'inventory');
          console.log(`Found ${inventoryItems.length} items from inventory system:`, 
                      inventoryItems.map(item => ({ id: item.id, name: item.name, category: item.category })));
        }
        
        if (stocksData.success) {
          // Convert array to object for easier lookup
          this.itemStocks = stocksData.items.reduce((acc, stock) => {
            acc[stock.item_id] = stock;
            return acc;
          }, {});
        }
        
        if (!wasLoading) {
          this.filterItems();
        }
      } catch (error) {
        console.error('Error fetching items or stocks:', error);
      } finally {
        if (wasLoading) {
          this.isLoading = false;
        }
      }
    },

    async loadUserProfile() {
      const userName = localStorage.getItem('userName');
      const userEmail = localStorage.getItem('userEmail');
      if (userName) {
        this.userName = userName;
        
        // Fetch profile data from the server to get avatar
        if (userEmail) {
          try {
            const response = await fetch(`http://127.0.0.1:8000/profile/${encodeURIComponent(userEmail)}`);
            const data = await response.json();
            if (response.ok) {
              // Set the avatar from the profile data
              this.userAvatar = data.avatar || '';
            }
          } catch (error) {
            console.error('Error loading profile:', error);
            // Fall back to the avatar service if profile loading fails
          }
        }
      } else {
        // If no username, redirect to login
        this.$router.push({ name: 'Login' });
      }
    },

    // toggleDarkMode is the next method after removing the notification related methods
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
      localStorage.setItem("darkMode", this.isDarkMode ? "enabled" : "disabled");
      this.applyDarkMode(this.isDarkMode);
    },

    applyDarkMode(isDark) {
      if (isDark) {
        document.body.classList.add('dark-mode');
      } else {
        document.body.classList.remove('dark-mode');
      }
    },

    updateTime() {
      setInterval(() => {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        let seconds = now.getSeconds();
        let ampm = hours >= 12 ? 'PM' : 'AM';

        hours = hours % 12 || 12; // Convert 24-hour time to 12-hour format
        minutes = minutes < 10 ? '0' + minutes : minutes; // Ensure two digits for minutes
        seconds = seconds < 10 ? '0' + seconds : seconds; // Ensure two digits for seconds

        this.currentTime = `${hours}:${minutes}:${seconds} ${ampm}`; // Example: 2:03:11 PM
      }, 1000); // Update every second
    },

    filterCategory(category) {
      this.currentCategory = category;
      // Save the selected category
      localStorage.setItem('lastViewedCategory', category);
      this.filterItems();
      
      // Close sidebar on mobile after selecting a category
      if (window.innerWidth <= 768) {
        this.closeSidebar();
      }
    },

    getImagePath(imagePath) {
      // If there's no image path, use a default image
      if (!imagePath) {
        return require('@/assets/default.png');
      }
      
      // Check if this is an inventory system item (using port 8001)
      if (imagePath.includes('localhost:8001') || (this.selectedItem && this.isInventoryItem(this.selectedItem))) {
        console.log('Inventory image path:', imagePath);
        
        // Check if the path needs to be fixed - it should point to /uploads/products/
        if (imagePath.includes('/uploads/') && !imagePath.includes('/uploads/products/')) {
          // Extract the filename
          const parts = imagePath.split('/');
          const filename = parts[parts.length - 1];
          const fixedPath = `http://localhost:8001/uploads/products/${filename}`;
          console.log('Fixed inventory image path:', fixedPath);
          return fixedPath;
        }
        
        // If it's already a full URL to the inventory system, use it directly
        if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
          return imagePath;
        }
        
        // For simple filenames in inventory system
        if (!imagePath.includes('/')) {
          return `http://localhost:8001/uploads/products/${imagePath}`;
        }
        
        return imagePath;
      }
      
      // For cafe-beata system (regular menu items)
      
      // If it's already a full URL, use it directly
      if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath;
      }
      
      // For cafe-beata system uploads with /uploads/ path
      if (imagePath.startsWith('/uploads/')) {
        return `http://localhost:8000${imagePath}`;
      }
      
      // For simple filenames in cafe-beata system
      if (!imagePath.includes('/')) {
        return `http://localhost:8000/uploads/${imagePath}`;
      }
      
      // Default fallback
      return require('@/assets/default.png');
    },

    filterItems() {
      const query = this.searchQuery.toLowerCase();
      
      // Add debug log for all inventory items
      const inventoryItems = this.apiItems.filter(item => item.external_source === 'inventory');
      console.log(`Total inventory items in database: ${inventoryItems.length}`);
      if (inventoryItems.length > 0) {
        console.log("Inventory items:", inventoryItems.map(item => ({ id: item.id, name: item.name })));
      }
      
      // Filter API items based on category and search query
      if (this.currentCategory === 'All Drinks') {
        // For "All Drinks", exclude all inventory items
        this.filteredItems = this.apiItems.filter(item => 
          !this.foodCategories.includes(item.category) && // Exclude food categories
          !this.readyMadeCategories.includes(item.category) && // Exclude ready-made categories
          item.external_source !== 'inventory' && // Exclude inventory items from drinks
          item.name.toLowerCase().includes(query)
        );
      } else if (this.currentCategory === 'All Food') {
        // For "All Food", exclude all inventory items
        this.filteredItems = this.apiItems.filter(item => 
          this.foodCategories.includes(item.category) &&
          item.external_source !== 'inventory' && // Exclude inventory items from food
          item.name.toLowerCase().includes(query)
        );
      } else if (this.currentCategory === 'All Ready Made') {
        // For "All Ready Made", ONLY show inventory items
        this.filteredItems = this.apiItems.filter(item => 
          item.external_source === 'inventory' &&
          item.name.toLowerCase().includes(query)
        );
        
        console.log(`Showing ${this.filteredItems.length} inventory items in the Ready Made section`);
      } else {
        // For specific categories
        const isReadyMadeCategory = this.readyMadeCategories.includes(this.currentCategory);
        
        if (isReadyMadeCategory) {
          // For Ready Made categories, only show inventory items for that category
          this.filteredItems = this.apiItems.filter(item => 
            item.category === this.currentCategory &&
            item.external_source === 'inventory' &&
            item.name.toLowerCase().includes(query)
          );
        } else {
          // For other categories, exclude all inventory items
          this.filteredItems = this.apiItems.filter(item => 
            item.category === this.currentCategory &&
            item.external_source !== 'inventory' &&
            item.name.toLowerCase().includes(query)
          );
        }
      }
      
      // Log the filtered items for debugging
      console.log(`Filtered ${this.filteredItems.length} items for category: ${this.currentCategory}`);
    },

   checkAndNavigate(item) {
      const stock = this.itemStocks[item.id];
      if (!stock || stock.quantity === 0) {
        alert('Sorry, this item is Temporarily Unavailable.');
        return;
      }
      this.showItemModal = true;
      this.selectedItem = item;
    },
    handleLogout() {
      localStorage.removeItem('loggedIn');
      this.$router.push({ name: 'Login' });
    },
    handleOrderHistory() {
      this.$router.push({ name: 'OrderHistory' });
    },
    handleProfile() {
      this.$router.push({ name: 'UserProfileCafe' }); // Navigate to the Profile page
    },
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen; // Toggle sidebar open/close
      localStorage.setItem('sidebarOpen', this.isSidebarOpen.toString());
    },
    closeSidebar() {
      this.isSidebarOpen = false;
      localStorage.setItem('sidebarOpen', this.isSidebarOpen.toString());
    },
    getCategoryIcon(category) {
      const foundCategory = this.categories.find(cat => cat.name === category);
      return foundCategory ? foundCategory.icon : 'fas fa-utensils';
    },
    async loadCategories() {
      try {
        const response = await fetch('http://localhost:8000/api/categories');
        const data = await response.json();
        if (data.categories) {
          console.log('Original categories from API:', data.categories);
          
          // Normalize category types
          this.categories = data.categories.map(cat => {
            // Normalize ready-made category types
            if (cat.type && 
               (cat.type.toLowerCase() === 'ready made' || 
                cat.type.toLowerCase() === 'ready-made' ||
                cat.type.toLowerCase() === 'readymade' ||
                cat.type.toLowerCase() === 'ready_made')) {  // Added underscore format
              return { ...cat, type: 'ready-made' };
            }
            // Normalize drink category types
            else if (cat.type && 
                    (cat.type.toLowerCase() === 'drink' || 
                     cat.type.toLowerCase() === 'beverage')) {
              return { ...cat, type: 'drinks' };
            }
            // Normalize food category types
            else if (cat.type && cat.type.toLowerCase() === 'food') {
              return { ...cat, type: 'food' };
            }
            return cat;
          });
          
          console.log('Normalized categories:', this.categories);
          console.log('Ready Made categories:', this.readyMadeCategories);
          
          // If current category doesn't exist anymore, reset to a valid one
          const allCategoryNames = [...this.drinkCategories, ...this.foodCategories, ...this.readyMadeCategories];
          if (!allCategoryNames.includes(this.currentCategory) && 
              this.currentCategory !== 'All Drinks' && 
              this.currentCategory !== 'All Food' &&
              this.currentCategory !== 'All Ready Made') {
            this.currentCategory = this.drinkCategories.length > 0 ? 'All Drinks' : 
                                  (this.foodCategories.length > 0 ? 'All Food' : 
                                  (this.readyMadeCategories.length > 0 ? 'All Ready Made' : 'All'));
            localStorage.setItem('lastViewedCategory', this.currentCategory);
          }
        }
      } catch (error) {
        console.error('Error loading categories:', error);
      }
    },
    handleCategoriesUpdated() {
      this.loadCategories();
      this.fetchItems();
    },
    goToCart() {
      // Navigate to confirm order page to view cart
      this.$router.push({ name: "ConfirmOrder" });
    },
    closeItemModal() {
      this.showItemModal = false;
      this.selectedItem = null;
      this.modalQuantity = 1; // Reset quantity when closing modal
    },
    async addToCart() {
      if (!this.selectedItem) return;
      
      const stock = this.itemStocks[this.selectedItem.id];
      if (!stock || stock.quantity < this.modalQuantity) {
        alert('Sorry, not enough stock available.');
        return;
      }
      
      const imagePath = this.getImagePath(this.selectedItem.image);
      const userCartKey = `cart_${this.userName}`;
      let cart = JSON.parse(localStorage.getItem(userCartKey)) || [];
      
      const existingItemIndex = cart.findIndex(item => item.name === this.selectedItem.name);
      
      if (existingItemIndex !== -1) {
        const newQuantity = cart[existingItemIndex].quantity + this.modalQuantity;
        if (newQuantity > stock.quantity) {
          alert('Sorry, not enough stock available for the requested quantity.');
          return;
        }
        cart[existingItemIndex].quantity = newQuantity;
      } else {
        cart.push({
          id: this.selectedItem.id,
          name: this.selectedItem.name,
          price: this.selectedItem.price,
          image: imagePath,
          quantity: this.modalQuantity
        });
      }
      
      localStorage.setItem(userCartKey, JSON.stringify(cart));
      this.updateCartCount();
      
      // Save current category before closing modal
      localStorage.setItem('lastViewedCategory', this.currentCategory);
      
      this.closeItemModal();
    },
    orderNow() {
      if (!this.selectedItem) return;
      
      const imagePath = this.getImagePath(this.selectedItem.image);
      const userCartKey = `cart_${this.userName}`;
      let cart = JSON.parse(localStorage.getItem(userCartKey)) || [];
      
      const existingItemIndex = cart.findIndex(item => item.name === this.selectedItem.name);
      
      if (existingItemIndex !== -1) {
        cart[existingItemIndex].quantity += this.modalQuantity;
      } else {
        cart.push({
          name: this.selectedItem.name,
          price: this.selectedItem.price,
          image: imagePath,
          quantity: this.modalQuantity
        });
      }
      
      // Save current category before navigating
      localStorage.setItem('lastViewedCategory', this.currentCategory);
      
      localStorage.setItem(userCartKey, JSON.stringify(cart));
      this.updateCartCount();
      
      this.$router.push({
        name: "ConfirmOrder"
      });
    },
    updateCartCount() {
      const userCartKey = `cart_${this.userName}`;
      const cart = JSON.parse(localStorage.getItem(userCartKey)) || [];
      // Count unique items instead of total quantities
      this.cartItemCount = cart.length;
    },
    decreaseModalQuantity() {
      if (this.modalQuantity > 1) {
        this.modalQuantity -= 1;
      }
    },
    increaseModalQuantity() {
      const stock = this.itemStocks[this.selectedItem?.id];
      if (stock && this.modalQuantity < stock.quantity) {
        this.modalQuantity += 1;
      } else {
        alert('Maximum available stock reached.');
      }
    },
    initWebSocket() {
      const wsUrl = `ws://${window.location.hostname}:8000/ws/orders`;
      
      // Close existing connection if any
      if (this.ws) {
        this.ws.close();
      }
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.wsConnected = true;
        // Initial fetch of data when connection is established
        this.fetchItems();
        this.loadCategories();
      };
      
      this.ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);
          
          if (data.type === 'stock_update') {
            console.log('Stock update received:', data);
            
            // STEP 1: Immediately update the UI with new stock values
            // Update the itemStocks object with the new stock data
            this.itemStocks[data.item_id] = {
              quantity: data.new_quantity,
              min_stock_level: data.min_stock_level
            };
            
            // If the item is currently selected in the modal, update its stock info immediately
            if (this.selectedItem && this.selectedItem.id === data.item_id) {
              this.selectedItem = {
                ...this.selectedItem,
                stock: data.new_quantity
              };
              
              // If the item is out of stock, close the modal
              if (data.new_quantity === 0) {
                this.closeItemModal();
              }
            }
            
            // Update the filtered items in the display immediately
            this.filteredItems = this.filteredItems.map(item => {
              if (item.id === data.item_id) {
                return {
                  ...item,
                  stock: data.new_quantity
                };
              }
              return item;
            });
            
            // STEP 2: Optional refresh of data in the background
            // This can be done asynchronously and won't block the UI updates
            setTimeout(async () => {
              try {
                await this.fetchItems();
                this.filterItems();
              } catch (error) {
                console.error('Error refreshing items after stock update:', error);
              }
            }, 1000); // Delay refresh for 1 second to ensure UI is responsive first
          } else if (data.type === 'menu_update') {
            console.log('Menu update received, refreshing items and categories');
            // First refresh categories to ensure any new/updated categories are loaded
            await this.loadCategories();
            // Then refresh items
            await this.fetchItems();
            // Finally, apply the current category filter
            this.filterItems();
            
            // Show notification if items were added or updated
            if (data.message && data.message.includes('Menu updated')) {
              console.log('Menu update notification:', data.message);
              // Optional: add a visual notification here
            }
          } else if (data.type === 'category_update') {
            console.log('Category update received:', data);
            // Refresh categories and items when categories change
            await this.loadCategories();
            await this.fetchItems();
            this.filterItems();
            
            // If the current category was renamed, update the selection
            if (data.action === 'update' && data.category.old_name === this.currentCategory) {
              this.currentCategory = data.category.name;
              localStorage.setItem('lastViewedCategory', this.currentCategory);
            }
            
            // If the current category was deleted, reset to default
            if (data.action === 'delete' && data.category_name === this.currentCategory) {
              this.currentCategory = this.categories.length > 0 ? 
                (this.drinkCategories.length > 0 ? 'All Drinks' : 
                 (this.foodCategories.length > 0 ? this.foodCategories[0] : 'All')) : 'All';
              localStorage.setItem('lastViewedCategory', this.currentCategory);
            }
          }
        } catch (error) {
          console.error('Error processing WebSocket message:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.wsConnected = false;
        // Try to reconnect after 5 seconds
        setTimeout(() => {
          this.initWebSocket();
        }, 5000);
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.wsConnected = false;
        // Try to reconnect after error
        setTimeout(() => {
          if (!this.wsConnected) {
            this.initWebSocket();
          }
        }, 5000);
      };
    },
    async syncInventoryProducts() {
      if (this.isSyncing) return;
      
      this.isSyncing = true;
      try {
        const response = await fetch('http://localhost:8000/api/sync-inventory-products');
        const result = await response.json();
        
        if (result.success) {
          console.log(`Successfully synchronized products: ${result.message}`);
          // Commented out the alert to avoid showing the notification
          // alert(`Successfully synchronized products from inventory system: ${result.message}`);
        } else {
          console.log(`Sync info: ${result.message}`);
          // Commented out the alert to avoid showing the notification 
          // alert(`Sync info: ${result.message}`);
        }
        
        // Refresh the items list
        await this.fetchItems();
        this.filterItems();
      } catch (error) {
        console.error('Error syncing inventory products:', error);
        // Only show alert for errors
        alert('Failed to sync products from inventory system');
      } finally {
        this.isSyncing = false;
      }
    },
    isInventoryItem(item) {
      return item.external_source === 'inventory';
    },
    // Add this method to handle image loading errors
    handleImageError(event) {
      // If image fails to load, use the default image
      event.target.src = require('@/assets/default.png');
      console.log('Profile image failed to load, using default image');
    },
    isInventoryItemStyled(item) {
      // Only apply special styling to inventory items when not in the Ready Made sections
      return this.isInventoryItem(item) && 
             this.currentCategory !== 'All Ready Made' && 
             !this.currentCategory.includes('Ready Made');
    },
    getAvatarUrl(avatar) {
      return avatar ? `http://127.0.0.1:8000${avatar}` : `https://ui-avatars.com/api/?name=${encodeURIComponent(this.userName)}&background=E54F70&color=fff&size=128`;
    },
  },
  watch: {
    isDarkMode: {
      handler(newValue) {
        if (newValue) {
          document.body.classList.add('dark-mode');
        } else {
          document.body.classList.remove('dark-mode');
        }
      },
      immediate: true
    }
  },
  computed: {
    drinkCategories() {
      return this.categories
        .filter(cat => cat.type === 'drinks')
        .map(cat => cat.name);
    },
    
    foodCategories() {
      return this.categories
        .filter(cat => cat.type === 'food')
        .map(cat => cat.name);
    },
    readyMadeCategories() {
      return this.categories
        .filter(cat => {
          // Simplify to only include the exact Ready Made category
          // This ensures we don't mistakenly include other categories
          return cat.name === 'Ready Made' || 
                 (cat.type && (
                    cat.type === 'ready_made' || 
                    cat.type === 'ready-made' || 
                    cat.type === 'Ready Made'
                 ));
        })
        .map(cat => cat.name);
    }
  },
};
</script>


<style scoped>
/* Add loading indicator styles */
.loading-indicator {
  text-align: center;
  padding: 20px;
  font-size: 18px;
  color: #d12f7a;
}

.no-items {
  text-align: center;
  padding: 20px;
  font-size: 18px;
  color: #666;
}

.utility-divider {
  border: none;
  height: 1px;
 background-color: rgba(0, 0, 0, 0.1);
  margin: 10px 0;
}

.user-profile-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.profile-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.profile-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-size: 1.1rem;
  font-weight: 500;
  color: #222;
}

.theme-toggle {
  position: absolute;
  top: 20px;
  left: 20px;
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.theme-toggle:hover {
 background-color: rgba(0, 0, 0, 0.05);
}

.theme-toggle .light-icon {
  color: #333;
}

.theme-toggle .dark-icon {
  color: #fff;
}

.light-mode 

.theme-toggle {
  color: #333;
}

.light-mode 
.user-name {
  color: #333;
}
.dark-mode .user-name {
  color: #fff;
}
.dark-mode .theme-toggle {
  color: #fff;
}
.dark-mode .utility-divider {
  background-color: rgba(255, 255, 255, 0.1);
}

.dark-mode .item {
  background-color: #555555; /* Light grey background for dark mode */
  color: #ffffff; /* Light text color */
  box-shadow: 0px 4px 6px rgba(255, 255, 255, 0.1); /* Lighter box shadow */
}

.dark-mode .item span {
  color: #ffffff; /* Light text for item span */
}

.dark-mode .item-price {
  background-color: #6e6e6e; /* Lighter background for price */
  color: #ffffff; /* Light text color for price */
}

.dark-mode .item-price:hover {
  background-color: #888888; /* Darker price background on hover */
  cursor: pointer;
}


.dark-mode-button, 
.notification-button {
  position: relative;
  background-color: rgb(48, 41, 44);
  color: white;
  padding: 8px 12px;
  font-size: 14px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: red;
  color: white;
  border-radius: 50%; /* This ensures it's fully circular */
  font-size: 12px;
  width: 20px; /* Set a fixed width */
  height: 20px; /* Set a fixed height to ensure it's circular */
  display: flex;
  justify-content: center; /* Centers the content horizontally */
  align-items: center; /* Centers the content vertically */
}

.dark-mode-button i, 
.notification-button i {
  font-size: 18px; /* Adjust icon size */
}

.top-bar-buttons {
  display: flex;
  gap: 10px; /* Space between buttons */
}

.notification-button {
  background-color: rgb(48, 41, 44); /* Same background as dark mode */
  color: white;
  padding: 8px 12px;
  font-size: 14px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
}

.notification-button:hover {
  background-color: #b82d67; /* Same hover effect as dark mode button */
}

.notification-button i {
  font-size: 18px; /* Adjust the icon size */
}

.dark-mode {
  background-color: #121212;
  color: #ffffff;
}

/* Buttons and Sidebar in Dark Mode */
.dark-mode .sidebar,
.dark-mode .dashboard,
.dark-mode .top-bar,
.dark-mode .content {
  background-color: #1e1e1e;
  color: #ffffff;
}


/* Dark Mode Button Styling */
.dark-mode-button {
  background-color: rgb(48, 41, 44);
  color: white;
  padding: 8px 12px;
  font-size: 14px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
}

.dark-mode .sidebar,
.dark-mode .sidebar-category h3,
.dark-mode .sidebar-category ul li {
  color: #ffffff !important;
}

/* Dark Mode for Live Time */
.dark-mode .live-time {
  color: #ffffff !important;
}


   .item-details {
    display: flex;
    flex-direction: column; /* Stack the name and price vertically */
    align-items: center;
    margin-top: 10px;
  }

  /* Style the price to highlight it */
  .item-price {
    font-size: 18px;
    font-weight: bold;
    color: #d12f7a; 
    background-color: #f8e1e6; 
    padding: 5px 10px;
    border-radius: 5px;
    margin-top: 5px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  /* Glowing effect on hover */
  .item-price:hover {
    background-color: #f8c6d0; 
    cursor: pointer;
  }

  /* Glowing Button Styles */
  .profile-button,
  .order-history-button,
  .logout-button {
    padding: 15px 40px;
    border: none;
    outline: none;
    color: #FFF;
    cursor: pointer;
    position: relative;
    z-index: 0;
    border-radius: 12px;
    background-color: transparent;
    border: 2px solid #d12f7a; /* Adjust border color */
    font-size: 14px;
   
  }

  /* Glowing effect */
  .profile-button::after,
  .order-history-button::after,
  .logout-button::after {
    content: "";
    z-index: -1;
    position: absolute;
    width: 100%;
    height: 100%;
    background-color: #333;
    left: 0;
    top: 0;
    border-radius: 10px;
  }

  /* Animation for glowing */
  .profile-button::before,
  .order-history-button::before,
  .logout-button::before {
    content: "";
    background: linear-gradient(
      45deg,
      #FF0000, #FF7300, #FFFB00, #48FF00,
      #00FFD5, #002BFF, #FF00C8, #FF0000
    );
    position: absolute;
    top: -2px;
    left: -2px;
    background-size: 600%;
    z-index: -1;
    width: calc(100% + 4px);
    height: calc(100% + 4px);
    filter: blur(8px);
    animation: glowing 20s linear infinite;
    transition: opacity .3s ease-in-out;
    border-radius: 10px;
    opacity: 0;
  }

  /* Hover effect for glowing */
  .profile-button:hover::before,
  .order-history-button:hover::before,
  .logout-button:hover::before {
    opacity: 1;
  }

  /* Active button state */
  .profile-button:active:after,
  .order-history-button:active:after,
  .logout-button:active:after {
    background: transparent;
  }

  .profile-button:active,
  .order-history-button:active,
  .logout-button:active {
    color: #000;
    font-weight: bold;
    background-color: #d12f7a; /* Active background color */
    border-color: #d12f7a; /* Border color */
  }

  /* Glow Animation */
  @keyframes glowing {
    0% {background-position: 0 0;}
    50% {background-position: 400% 0;}
    100% {background-position: 0 0;}
  }

/* Existing styles (unchanged) */
.profile-button {
  background-color: rgb(100, 14, 51);
  color: white;
  padding: 10px;
  font-size: 18px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease-in-out;
  width: 40px; /* Adjust width and height for round button */
  height: 40px; /* Adjust width and height for round button */
}

.profile-button i {
  font-size: 24px; /* Adjust icon size */
}

.profile-button:hover {
  background-color: #b82d67;

}

.dashboard {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  background-color: #ffffff;
  width: 100%;
  overflow-x: hidden;
  position: relative;
}

html, body {
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background-color: #ffffff;
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: -280px;
  height: 100vh;
  width: 280px;
  background-color: white;
  transition: all 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  padding: 20px 0 20px 0; /* Add bottom padding */
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar.light-mode {
  background-color: white;
}

.sidebar.dark-mode {
  background-color: #333;
  color: #fff;
}

.sidebar.dark-mode .utility-button,
.sidebar.dark-mode .menu-item,
.sidebar.dark-mode .profile-section,
.sidebar.dark-mode h3 {
  color: #fff;
}

.sidebar.dark-mode .utility-button:hover,
.sidebar.dark-mode .menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar.dark-mode .profile-section,
.sidebar.dark-mode .utility-section,
.sidebar.dark-mode .logout {
  border-color: rgba(255, 255, 255, 0.1);
}

.sidebar.open {
  left: 0;
}

.close-sidebar {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: inherit;
  padding: 5px;
}

.profile-section {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 20px;
  color: inherit;
  font-size: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: none;
  border: none;
  width: 100%;
  cursor: pointer;
  text-align: left;
}

.profile-section:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.utility-section {
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.utility-button {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  font-size: 15px;
  text-decoration: none;
  transition: background-color 0.2s;
}

.utility-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.notification-link {
  position: relative;
  text-decoration: none;
  color: inherit;
}

.notification-icon {
  position: relative;
  display: inline-block;
  width: 20px;
}

.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: red;
  color: white;
  border-radius: 50%; /* This ensures it's fully circular */
  font-size: 11px;
  min-width: 15px;
  height: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-section {
  flex: 1;
  padding: 15px 0 0 0;
  overflow-y: auto;
  margin-bottom: 0;
}

.menu-section h3 {
  padding: 0 20px;
  margin: 10px 0 5px;
  font-size: 16px;
  color: inherit;
  font-weight: 500;
}

.menu-items {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 20px;
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  font-size: 15px;
  text-align: left;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.menu-item i {
  width: 20px;
  text-align: center;
  font-size: 14px;
}

.logout-container {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0;
  background-color: white;
  margin-bottom: 20px; /* Add space after logout button */
}

.dark-mode .logout-container {
  background-color: #333;
  border-top-color: rgba(255, 255, 255, 0.1);
}

.logout {
  color: inherit;
  padding: 10px 20px;
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .content {
    margin-left: 0;
    padding: 15px;
  }
  
  .menu-button {
    display: block;
  }
}

/* Desktop Responsive */
@media (min-width: 769px) {
  .content {
    margin-left: 0; /* Remove default margin to match mobile behavior */
  }
  
  .menu-button {
    display: block; /* Show menu button on desktop */
    background: rgb(255, 255, 255);
    color: black;
    padding: 10px 15px;
    font-size: 18px;
    border-radius: 15px;
    transition: background 0.3s ease-in-out;
  }

  /* When sidebar is open */
  .sidebar.open + .content {
    margin-left: 270px;
  }
}

/* Update menu button base styles */
.menu-button {
  position: fixed;
  top: 15px;
  left: 15px;
  z-index: 300;
  background: white;
  color: #E54F70;
  padding: 10px 15px;
  font-size: 18px;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
  display: block; /* Always show the menu button */
}

.menu-icon-container {
  position: relative;
  display: inline-block;
}

.menu-notification-badge {
  position: absolute;
  top: -8px;
  right: -20px;
  background-color: red;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* Add overlay styles */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 299;
  display: none;
}

.overlay.show {
  display: block;
}

/* Update content transition */
.content {
  transition: margin-left 0.3s ease;
}

/* Style the container for both logo and live time */
.logo-time-container {
  display: none;
}

.search-cart-container {
  display: flex;
  align-items: center;
  width: 80%;
  max-width: 400px;
  position: relative;
}

.search-container { 
  display: flex;
  justify-content: center; 
  padding: 10px;
  border-radius: 15px;
  width: 100%;
  max-width: 300px;
} 

.cart-icon-container {
  position: absolute;
  right: -40px;
  cursor: pointer;
  padding: 10px;
  font-size: 24px;
  color: #d12f7a;
  transition: color 0.3s ease;
}

@media (max-width: 768px) {
  .search-cart-container {
    width: 90%;
    max-width: none;
    position: relative;
  }
  
  .search-container {
    width: 100%;
    max-width: none;
  }
  
  .cart-icon-container {
    right: -35px;
    font-size: 20px;
  }
  
  .search-container input {
    width: 100%;
    max-width: none;
  }
}

.cart-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: red;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 15px;
  text-align: center;
  width: 90%;
  max-width: 400px;
  position: relative;
  border: 2px solid #E54F70;
}

/* Update close button styles */
.modal-content .close {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 32px;
  color: #333;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
  background: none;
  border: none;
  padding: 0;
  line-height: 1;
}

.modal-content .close:hover {
  color: #d12f7a;
  transform: scale(1.1);
}

/* Dark mode styles for close button */
.dark-mode .modal-content .close {
  color: #fff;
}

.dark-mode .modal-content .close:hover {
  color: #f8c6d0;
}

@media (max-width: 768px) {
  .modal-content .close {
    font-size: 28px;
    width: 35px;
    height: 35px;
  }
}

.modal-item-details {
  margin-bottom: 20px;
}

.modal-item-details img {
  width: 150px;
  height: 150px;
  object-fit: contain;
  margin-bottom: 15px;
}

.modal-item-details h3 {
  color: #333;
  margin: 10px 0;
}

.modal-item-details .price {
  color: #d12f7a;
  font-size: 20px;
  font-weight: bold;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.add-cart-btn, .order-now-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.add-cart-btn {
  background-color: #333;
  color: white;
}

.order-now-btn {
  background-color: #d12f7a;
  color: white;
}

.add-cart-btn:hover {
  background-color: #444;
}

.order-now-btn:hover {
  background-color: #b82d67;
}

/* Dark mode styles */
.dark-mode .modal-content {
  background-color: #333;
  color: white;
}

.dark-mode .modal-item-details h3 {
  color: white;
}

.dark-mode .cart-icon-container {
  color: #f8c6d0;
}

.dark-mode .cart-icon-container:hover {
  color: #f8a1b2;
}

@media (max-width: 768px) {
  .search-cart-container {
    max-width: 300px;
  }
  
  .cart-icon-container {
    font-size: 20px;
  }
  
  .modal-content {
    width: 85%;
    padding: 20px;
  }
  
  .modal-item-details img {
    width: 120px;
    height: 120px;
  }
}

/* Add this to your existing styles */
.added-to-cart-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  z-index: 2000;
  animation: slideIn 0.3s ease-out, fadeOut 0.3s ease-out 0.7s;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

/* Dark mode support */
.dark-mode .added-to-cart-notification {
  background-color: #45a049;
}

/* Modal Quantity Controls */
.modal-quantity-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin: 20px 0;
}

.quantity-btn {
  width: 35px;
  height: 35px;
  border: none;
  border-radius: 50%;
  background-color: #d12f7a;
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.quantity-btn:hover {
  background-color: #b82d67;
  transform: scale(1.1);
}

.quantity-display {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  min-width: 40px;
  text-align: center;
}

.total-price {
  font-size: 20px;
  font-weight: bold;
  color: #d12f7a;
  margin-top: 10px;
}

/* Dark mode styles for quantity controls */
.dark-mode .quantity-display {
  color: #fff;
}

.dark-mode .quantity-btn {
  background-color: #444;
}

.dark-mode .quantity-btn:hover {
  background-color: #555;
}

/* Remove all out-of-stock related styles */
.item.out-of-stock {
  opacity: 0.9;
  position: relative;
}

.item.out-of-stock img {
  filter: grayscale(0.7);
}

/* Top Bar */
.top-bar {
  display: flex;
  align-items: center;
  background-image: linear-gradient(to right, #E54F70, #ed9598);
  padding: 0 15px;
  height: 60px;
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.centered-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
  gap: 20px;
}

.top-bar .menu-button {
  position: static;
  background: transparent;
  box-shadow: none;
  font-size: 24px;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 101;
  color: white;
}

.logo-container {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.logo-container img {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.cafe-title {
  color: white;
  font-weight: bold;
  margin-left: 10px;
  font-size: 18px;
  white-space: nowrap;
}

.search-container {
  flex-grow: 0;
  width: 250px;
}

.search-container input {
  width: 100%;
  padding: 8px 15px;
  border-radius: 20px;
  border: 1px solid #ccc;
  font-size: 14px;
  background-color: white;
}

.time-cart-container {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.live-time {
  font-weight: 500;
  font-size: 14px;
  color: white;
  white-space: nowrap;
}

.cart-icon-container {
  cursor: pointer;
  font-size: 22px;
  color: #d12f7a;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: #f8e1e6;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.cart-icon-container:hover {
  transform: scale(1.1);
  background-color: #f8d1d1;
}

.cart-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: red;
  color: white;
  border-radius: 50%;
  font-size: 10px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Dark mode styles for top bar */
.dark-mode .top-bar {
  background-image: linear-gradient(to right, #333, #444);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.dark-mode .cafe-title {
  color: white;
}

.dark-mode .live-time {
  color: white;
}

.dark-mode .search-container input {
  background-color: #444;
  color: white;
  border-color: #555;
}

.dark-mode .top-bar .menu-button {
  color: white;
}

/* Responsive adjustments for top bar */
@media (max-width: 768px) {
  .top-bar {
    padding: 0 10px;
  }
  
  .centered-content {
    gap: 10px;
  }
  
  .search-container {
    width: 180px;
  }
  
  .logo-container img {
    width: 25px;
    height: 25px;
  }
  
  .cafe-title {
    font-size: 16px;
    margin-left: 5px;
  }
}

@media (max-width: 480px) {
  .top-bar {
    padding: 0 5px;
  }
  
  .centered-content {
    gap: 5px;
  }
  
  .search-container {
    width: 120px;
  }
  
  .cafe-title {
    font-size: 14px;
  }
  
  .cart-icon-container {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }
}

/* Dashboard Title */
.dashboard-title {
   font-size: 40px;
  font-weight: bold;
   color: #d12f7a;
  margin-top: 15px;
  margin-bottom: 15px;
  text-align: center;
  font-style: italic; 
  font-family: "Merriweather", serif; 
  letter-spacing: 1px; 
 
}

 .dashboard-title:hover {
    color: #fff; 
    text-shadow: 0 0 10px rgba(209, 47, 122, 1), 0 0 20px rgba(209, 47, 122, 0.7); 

 }
 
 .logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Live Time container */
.live-time-container {
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-weight: bold;
  font-size: 20px;
}

/* Style the search bar */
.search-container input {
  border-radius: 20px;
  border: 1px solid #ccc;
  width: 100%;
  max-width: 300px;
}

.order-history-button,
  .logout-button {
    font-size: 12px;
    padding: 6px 10px;
  }
/* Categories Section */
.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.category {
  width: 48%;
}

.category h2 {
  font-size: 24px;
  font-weight: bold;
  color: #d12f7a;
  text-align: center;
  margin-top: 20px;
  margin-bottom: 10px;
}

/* Items Section */
.items {
  display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
   gap: 20px;
  padding: 20px;
  justify-content: center;
  align-items: center;
}
@media (min-width: 1024px) {
  .items {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Adjust for smaller screens */
@media (max-width: 1023px) {
  .items {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .items {
     display: flex;
    grid-template-columns: repeat(2, 1fr);
       flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .items {
    grid-template-columns: 1fr;
  }
}

/* Item styling */
.item {
  text-align: center;
  background-color: white;
  border-radius: 15px;
  padding: 15px;
  cursor: pointer;
  transition: transform 0.3s ease, opacity 0.3s ease;
  height: auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 200px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #E54F70;
}

.item img {
  width: 100px;
  height: 100px;
  object-fit: contain;
}

.item:hover img {
  transform: scale(1.05);
}

.item span {
  font-weight: bold;
  color: #333;
  font-size: 16px;
  text-align: center;
  display: block;
  line-height: 1.3;
  margin-top: 8px;
}

/* Responsive Text Adjustments */
@media (max-width: 768px) {
  .dashboard-title {
    font-size: 35px;
  }

}
 .item-details {
    display: flex;
    justify-content: space-between;
   flex-direction: column;
  align-items: center;
  margin-top: 10px;
  }

  .item-price {
    font-size: 18px;
    font-weight: bold;
    color: #d12f7a; 
    background-color: #f8e1e6; 
    padding: 5px 10px;
    border-radius: 5px;
    margin-top: 5px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .item-price:hover {
    background-color: #f8c6d0; 
    cursor: pointer;
  }

  .category h2 {
    font-size: 20px;
  }

  .item span {
    font-size: 14px;
  }

 

@media (max-width: 480px) {
  .dashboard-title {
    font-size: 30px;
  }

  .category h2 {
    font-size: 18px;
  }


  .order-history-button,
  .logout-button {
     font-size: 10px;
    padding: 5px 8px;
  }
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.category-header h2 {
  font-size: 24px;
  color:rgb(0, 0, 0);
  text-align: center;
  margin: 0;
  padding: 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Dark mode styles for category header */
.dark-mode .category-header h2 {
  color: #f8c6d0;
}

/* Remove refresh button styles that are no longer needed */
.refresh-button,
.refresh-button:hover,
.refresh-button:disabled,
.fa-spin,
@keyframes fa-spin {
  /* These styles will be removed */
}

.search-cart-container {
  display: flex;
  align-items: center;
  width: 80%;
  max-width: 400px;
  position: relative;
}

.search-container { 
  display: flex;
  justify-content: center; 
  padding: 10px;
  border-radius: 15px;
  width: 100%;
  max-width: 300px;
} 

.cart-icon-container {
  position: absolute;
  right: -40px;
  cursor: pointer;
  padding: 10px;
  font-size: 24px;
  color: #d12f7a;
  transition: color 0.3s ease;
}

@media (max-width: 768px) {
  .search-cart-container {
    width: 90%;
    max-width: none;
    position: relative;
  }
  
  .search-container {
    width: 100%;
    max-width: none;
  }
  
  .cart-icon-container {
    right: -35px;
    font-size: 20px;
  }
  
  .search-container input {
    width: 100%;
    max-width: none;
  }
}

.cart-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: red;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 15px;
  text-align: center;
  width: 90%;
  max-width: 400px;
  position: relative;
  border: 2px solid #E54F70;
}

/* Update close button styles */
.modal-content .close {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 32px;
  color: #333;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
  background: none;
  border: none;
  padding: 0;
  line-height: 1;
}

.modal-content .close:hover {
  color: #d12f7a;
  transform: scale(1.1);
}

/* Dark mode styles for close button */
.dark-mode .modal-content .close {
  color: #fff;
}

.dark-mode .modal-content .close:hover {
  color: #f8c6d0;
}

@media (max-width: 768px) {
  .modal-content .close {
    font-size: 28px;
    width: 35px;
    height: 35px;
  }
}

.modal-item-details {
  margin-bottom: 20px;
}

.modal-item-details img {
  width: 150px;
  height: 150px;
  object-fit: contain;
  margin-bottom: 15px;
}

.modal-item-details h3 {
  color: #333;
  margin: 10px 0;
}

.modal-item-details .price {
  color: #d12f7a;
  font-size: 20px;
  font-weight: bold;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.add-cart-btn, .order-now-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.add-cart-btn {
  background-color: #333;
  color: white;
}

.order-now-btn {
  background-color: #d12f7a;
  color: white;
}

.add-cart-btn:hover {
  background-color: #444;
}

.order-now-btn:hover {
  background-color: #b82d67;
}

/* Dark mode styles */
.dark-mode .modal-content {
  background-color: #333;
  color: white;
}

.dark-mode .modal-item-details h3 {
  color: white;
}

.dark-mode .cart-icon-container {
  color: #f8c6d0;
}

.dark-mode .cart-icon-container:hover {
  color: #f8a1b2;
}

@media (max-width: 768px) {
  .search-cart-container {
    max-width: 300px;
  }
  
  .cart-icon-container {
    font-size: 20px;
  }
  
  .modal-content {
    width: 85%;
    padding: 20px;
  }
  
  .modal-item-details img {
    width: 120px;
    height: 120px;
  }
}

/* Add this to your existing styles */
.added-to-cart-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  z-index: 2000;
  animation: slideIn 0.3s ease-out, fadeOut 0.3s ease-out 0.7s;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

/* Dark mode support */
.dark-mode .added-to-cart-notification {
  background-color: #45a049;
}

/* Modal Quantity Controls */
.modal-quantity-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin: 20px 0;
}

.quantity-btn {
  width: 35px;
  height: 35px;
  border: none;
  border-radius: 50%;
  background-color: #d12f7a;
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.quantity-btn:hover {
  background-color: #b82d67;
  transform: scale(1.1);
}

.quantity-display {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  min-width: 40px;
  text-align: center;
}

.total-price {
  font-size: 20px;
  font-weight: bold;
  color: #d12f7a;
  margin-top: 10px;
}

/* Dark mode styles for quantity controls */
.dark-mode .quantity-display {
  color: #fff;
}

.dark-mode .quantity-btn {
  background-color: #444;
}

.dark-mode .quantity-btn:hover {
  background-color: #555;
}

/* Remove all out-of-stock related styles */
.item.out-of-stock {
  opacity: 0.9;
  position: relative;
}

.item.out-of-stock img {
  filter: grayscale(0.7);
}

/* Add floating cart styles */
.floating-cart {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  background-color: #d12f7a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  transition: all 0.3s ease;
}

.floating-cart:hover {
  transform: scale(1.1);
  background-color: #b82d67;
}

.floating-cart-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: red;
  color: white;
  border-radius: 50%;
  font-size: 14px;
  min-width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.dark-mode .floating-cart {
  background-color: #444;
}

.dark-mode .floating-cart:hover {
  background-color: #333;
}

@media (max-width: 768px) {
  .floating-cart {
    bottom: 20px;
    right: 20px;
    width: 55px;
    height: 55px;
  }
}

@media (max-width: 480px) {
  .floating-cart {
    bottom: 15px;
    right: 15px;
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .floating-cart-badge {
    min-width: 20px;
    height: 20px;
    font-size: 12px;
  }
}

/* Update time-cart-container to just show time */
.time-cart-container {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.sync-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.8rem;
  cursor: pointer;
  margin-left: 10px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.sync-button.prominent {
  background-color: #007bff;
  padding: 6px 12px;
  font-size: 0.9rem;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.sync-button:hover {
  background-color: #45a049;
  transform: scale(1.05);
}

.sync-button.prominent:hover {
  background-color: #0069d9;
  transform: scale(1.05);
}

.sync-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  transform: none;
}

.sync-button i {
  font-size: 12px;
}

/* Add to the style section */
.inventory-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #4CAF50;
  color: white;
  border-radius: 15px;
  padding: 5px 10px;
  display: flex;
  align-items: center;
  gap: 5px;
  z-index: 2;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0,0,0,0.3);
}

.inventory-badge i {
  font-size: 14px;
}

.inventory-badge span {
  color: white !important;
  font-size: 12px !important;
}

.item-image-container {
  position: relative;
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 10px 10px 0 0;
}

.item-image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.inventory-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #4CAF50;
  color: white;
  border-radius: 15px;
  padding: 3px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  z-index: 2;
  font-size: 12px;
}

.inventory-badge i {
  font-size: 18px;
}

.inventory-item {
  border: 2px solid #4CAF50;
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

/* Add CSS for the modal image container and inventory badge */
.modal-image-container {
  position: relative;
  width: 100%;
  max-height: 200px;
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.modal-image-container img {
  max-height: 200px;
  max-width: 100%;
  object-fit: contain;
}

.inventory-badge-modal {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #4CAF50;
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: bold;
}

.dark-mode .item.inventory-item {
  border: 2px solid #4CAF50;
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.top-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* Additional responsive adjustments */
@media (max-width: 768px) {
  .top-controls {
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .top-controls {
    gap: 5px;
  }
  
  .live-time {
    font-size: 14px;
  }
}
</style>
