<template>
  <div class="item-editor">
    <div class="header">
      <h2><i class="fa fa-list"></i> Menu Item Editor</h2>
      <div class="header-buttons">
        <button @click="toggleAddItemModal" class="add-item-button">
          <i class="fa fa-plus"></i> Add New Item
        </button>
        <button @click="showCategoryModal" class="add-category-button">
          <i class="fa fa-tags"></i> Manage Categories
        </button>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="notification.show" :class="['notification', notification.type]">
      <i :class="notification.type === 'success' ? 'fa fa-check-circle' : 'fa fa-exclamation-circle'"></i>
      {{ notification.message }}
    </div>

    <!-- Category Filter -->
    <div class="category-filter">
      <label for="category-filter"><i class="fa fa-filter"></i> Filter by Category:</label>
      <select id="category-filter" v-model="selectedCategory" @change="filterItemsByCategory">
        <option value="All">All Categories</option>
        <option v-for="category in categories" :key="category.id" :value="category.name">
          {{ category.name }} ({{ category.type }})
        </option>
      </select>
    </div>

    <!-- Add/Edit Item Modal Popup -->
    <div v-if="showForm" class="item-form-modal">
      <div class="item-form-modal-content">
        <div class="modal-header">
          <h3><i :class="isEditing ? 'fa fa-edit' : 'fa fa-plus-circle'"></i> {{ isEditing ? 'Edit Item' : 'Add New Item' }}</h3>
          <button @click="toggleAddItemModal" class="close-modal-btn">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveItem" class="form-content">
            <div class="form-group">
              <label for="itemName">Item Name:</label>
              <input 
                type="text" 
                id="itemName" 
                v-model="currentItem.name" 
                required 
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="itemPrice">Price (₱):</label>
              <input 
                type="number" 
                id="itemPrice" 
                v-model="currentItem.price" 
                required 
                step="0.01" 
                min="0" 
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="itemCategory">Category:</label>
              <select 
                id="itemCategory" 
                v-model="currentItem.category" 
                class="form-input"
                required
              >
                <option value="">-- Select Category --</option>
                <option v-for="category in categories" :key="category.id" :value="category.name">
                  {{ category.name }} ({{ category.type }})
                </option>
              </select>
              <small class="form-help">Category is required and determines where the item will appear in the menu.</small>
            </div>

            <div class="form-group">
              <label for="itemImage">Image:</label>
              <input 
                type="file" 
                id="itemImage" 
                @change="handleImageUpload" 
                accept="image/*" 
                :required="!isEditing"
                class="form-input"
              />
              <img 
                v-if="imagePreview" 
                :src="imagePreview" 
                class="image-preview" 
                alt="Item preview"
              />
            </div>

            <div class="form-actions">
              <button type="submit" class="save-button" :disabled="isSaving">
                <i :class="isEditing ? 'fa fa-save' : 'fa fa-plus'"></i>
                {{ isEditing ? (isSaving ? 'Updating...' : 'Update Item') : (isSaving ? 'Adding...' : 'Add Item') }}
              </button>
              <button type="button" @click="toggleAddItemModal" class="cancel-button" :disabled="isSaving">
                <i class="fa fa-times"></i> Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Category Management Modal -->
    <div v-if="showCategoryForm" class="category-modal">
      <div class="category-modal-content">
        <div class="modal-header">
          <h3><i class="fa fa-tags"></i> Manage Categories</h3>
          <button @click="closeCategoryModal" class="close-modal-btn">
            <i class="fa fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <!-- Add New Category Form -->
          <form @submit.prevent="addNewCategory" class="add-category-form">
            <h4>{{ editingCategoryId ? 'Edit Category' : 'Add New Category' }}</h4>
            <div class="form-group">
              <label for="newCategory">Category Name:</label>
              <input 
                type="text" 
                id="newCategory" 
                v-model="newCategoryName" 
                required 
                class="form-input"
                placeholder="Enter category name"
              />
            </div>

            <div class="form-group">
              <label for="categoryType">Category Type:</label>
              <select 
                id="categoryType" 
                v-model="newCategoryType" 
                required 
                class="form-input"
              >
                <option value="">Select Type</option>
                <option value="drinks">Drinks</option>
                <option value="food">Food</option>
                <option value="ready_made">Ready Made</option>
              </select>
            </div>

            <div class="form-group">
              <label for="categoryIcon">Category Icon:</label>
              <select 
                id="categoryIcon" 
                v-model="newCategoryIcon" 
                required 
                class="form-input"
              >
                <option value="">Select Icon</option>
                <!-- Drink Icons -->
                <option value="fas fa-coffee">☕ Coffee</option>
                <option value="fas fa-mug-hot">🍵 Hot Drink</option>
                <option value="fas fa-glass-martini">🥤 Cold Drink</option>
                <option value="fas fa-glass-whiskey">🥛 Milk Tea</option>
                <option value="fas fa-wine-glass-alt">🍷 Beverage</option>
                <option value="fas fa-blender">🥤 Smoothie</option>
                <!-- Food Icons -->
                <option value="fas fa-utensils">🍽️ Main Dish</option>
                <option value="fas fa-bread-slice">🍞 Bread & Pastry</option>
                <option value="fas fa-hamburger">🍔 Burger & Sandwich</option>
                <option value="fas fa-pizza-slice">🍕 Pizza & Snacks</option>
                <option value="fas fa-cookie">🍪 Cookies & Sweets</option>
                <option value="fas fa-ice-cream">🍨 Dessert</option>
                <option value="fas fa-egg">🍳 Breakfast</option>
                <option value="fas fa-cheese">🧀 Appetizer</option>
                <option value="fas fa-bacon">🥓 Side Dish</option>
                <option value="fas fa-drumstick-bite">🍗 Rice Meal</option>
                <option value="fas fa-fish">🐟 Seafood</option>
                <option value="fas fa-leaf">🥗 Salad & Veggies</option>
                <option value="fas fa-pepper-hot">🌶️ Spicy Dish</option>
                <option value="fas fa-birthday-cake">🎂 Cake</option>
                <!-- Ready Made Icons -->
                <option value="fas fa-shopping-basket">🧺 Ready Made</option>
                <option value="fas fa-box">📦 Packaged</option>
                <option value="fas fa-store">🏪 Convenience</option>
                <option value="fas fa-boxes">📦 Retail Products</option>
              </select>
              <div class="icon-preview" v-if="newCategoryIcon">
                <i :class="newCategoryIcon"></i>
                <span>Icon Preview</span>
              </div>
            </div>

            <div class="form-actions">
              <button type="submit" class="save-button">
                <i :class="editingCategoryId ? 'fa fa-save' : 'fa fa-plus'"></i>
                {{ editingCategoryId ? 'Update Category' : 'Add Category' }}
              </button>
              <button v-if="editingCategoryId" type="button" @click="resetCategoryForm" class="cancel-button">
                <i class="fa fa-times"></i> Cancel Edit
              </button>
            </div>
          </form>

          <!-- Existing Categories List -->
          <div class="categories-list">
            <h4>Existing Categories</h4>
            <div v-for="category in categories" :key="category.id" class="category-item">
              <div class="category-info">
                <i :class="category.icon"></i>
                <span>{{ category.name }}</span>
                <span class="category-type">{{ formatCategoryType(category.type) }}</span>
              </div>
              <div class="category-actions">
                <button @click="editCategory(category)" class="edit-category-btn">
                  <i class="fa fa-edit"></i>
                </button>
                <button @click="deleteCategory(category.id)" class="delete-category-btn">
                  <i class="fa fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Items List -->
    <div v-if="isLoading" class="loading">
      <i class="fa fa-spinner fa-spin"></i> Loading items...
    </div>
    <div v-else class="items-list">
      <div v-for="item in items" :key="item.id" class="item-card">
        <img :src="getImageUrl(item.image)" :alt="item.name" class="item-image"/>
        <div class="item-info">
          <h4>{{ item.name }}</h4>
          <p class="item-price">₱{{ Number(item.price).toFixed(2) }}</p>
          <p v-if="item.category" class="item-category">
            <i class="fa fa-tag"></i> 
            {{ item.category }}
            <span class="category-type" v-if="getCategoryType(item.category)">
              ({{ formatCategoryType(getCategoryType(item.category)) }})
            </span>
          </p>
        </div>
        <div class="item-actions">
          <button @click="editItem(item)" class="edit-button" :disabled="isSaving">
            <i class="fa fa-edit"></i>
          </button>
          <button @click="deleteItem(item.id)" class="delete-button" :disabled="isSaving">
            <i class="fa fa-trash"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { importMenuItems } from './ImportMenuItems';

export default {
  name: 'ItemEditor',
  emits: ['item-updated'],
  data() {
    return {
      items: [],
      showForm: false,
      showCategoryForm: false,
      newCategoryName: '',
      newCategoryType: '',
      newCategoryIcon: '',
      isEditing: false,
      editingCategoryId: null,
      imagePreview: null,
      isLoading: false,
      isSaving: false,
      notification: {
        show: false,
        message: '',
        type: 'success'
      },
      currentItem: {
        id: null,
        name: '',
        price: '',
        category: '',
        image: null
      },
      categories: [],
      selectedCategory: 'All',
      allItems: [],
      hasImported: false,
      ws: null,
      wsConnected: false,
    }
  },
  methods: {
    showNotification(message, type = 'success') {
      this.notification = {
        show: true,
        message,
        type
      };
      setTimeout(() => {
        this.notification.show = false;
      }, 3000);
    },
    async fetchItems() {
      this.isLoading = true;
      try {
        const response = await fetch('http://localhost:8000/api/items');
        const data = await response.json();
        if (data.items) {
          this.allItems = data.items;
          this.filterItemsByCategory();
          this.$emit('item-updated');
        }
      } catch (error) {
        console.error('Error fetching items:', error);
        this.showNotification('Failed to load items', 'error');
      } finally {
        this.isLoading = false;
      }
    },
    toggleAddItemModal() {
      if (!this.showForm) {
        // Opening the form/modal
        this.currentItem = {
          name: '',
          price: '',
          category: '',
          image: null
        };
        this.isEditing = false;
      } else {
        // Closing the form/modal - reset everything
        this.resetForm();
      }
      this.showForm = !this.showForm;
      if (!this.showForm) {
        this.imagePreview = null;
      }
    },
    editItem(item) {
      // Set up editing mode first before opening the modal
      this.isEditing = true;
      this.currentItem = { 
        id: item.id,
        name: item.name,
        price: item.price,
        category: item.category || '',
        image: null
      };
      this.imagePreview = this.getImageUrl(item.image);
      
      // Then open the modal
      this.showForm = true;
    },
    async saveItem() {
      if (this.isSaving) return;
      
      if (!this.currentItem.category) {
        this.showNotification('Please select a category', 'error');
        return;
      }
      
      this.isSaving = true;

      try {
        const formData = new FormData();
        formData.append('name', this.currentItem.name);
        formData.append('price', this.currentItem.price);
        formData.append('category', this.currentItem.category);
        
        if (this.currentItem.image instanceof File) {
          formData.append('image', this.currentItem.image);
        }

        const url = this.isEditing 
          ? `http://localhost:8000/api/items/${this.currentItem.id}`
          : 'http://localhost:8000/api/items';
        
        const method = this.isEditing ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
          method,
          body: formData
        });

        if (response.ok) {
          const result = await response.json();
          this.showNotification(this.isEditing ? 'Item updated successfully' : 'Item added successfully');
          
          // Update local state immediately
          const newItem = {
            ...this.currentItem,
            id: this.isEditing ? this.currentItem.id : result.id,
            image: result.image_path
          };
          
          if (this.isEditing) {
            const index = this.allItems.findIndex(item => item.id === newItem.id);
            if (index !== -1) {
              this.allItems = [
                ...this.allItems.slice(0, index),
                newItem,
                ...this.allItems.slice(index + 1)
              ];
            }
          } else {
            this.allItems = [...this.allItems, newItem];
          }
          
          // Create initial stock record for new item
          if (!this.isEditing) {
            try {
              await fetch('http://localhost:8000/api/stocks', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  item_id: result.id,
                  quantity: 0,
                  min_stock_level: 0
                })
              });
            } catch (error) {
              console.error('Error creating initial stock record:', error);
            }
          }
          
          this.filterItemsByCategory();
          
          // Emit events for both menu and stock updates
          this.$emit('item-updated');
          window.dispatchEvent(new CustomEvent('stock-updated'));
          
          // Close the modal
          this.showForm = false;
          this.resetForm();
          
          // Refresh items to ensure everything is in sync
          await this.fetchItems();
        } else {
          const error = await response.json();
          throw new Error(error.detail || 'Operation failed');
        }
      } catch (error) {
        console.error('Error saving item:', error);
        this.showNotification(error.message || 'Failed to save item', 'error');
      } finally {
        this.isSaving = false;
      }
    },
    async deleteItem(itemId) {
      if (!confirm('Are you sure you want to delete this item?')) return;
      
      this.isSaving = true;
      try {
        const response = await fetch(`http://localhost:8000/api/items/${itemId}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          this.showNotification('Item deleted successfully');
          
          this.$emit('item-updated', {
            action: 'deleted',
            itemId
          });
          
          const event = new CustomEvent('items-updated', { 
            detail: { 
              action: 'deleted',
              itemId
            } 
          });
          window.dispatchEvent(event);
          
          await this.fetchItems();
        } else {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to delete item');
        }
      } catch (error) {
        console.error('Error deleting item:', error);
        this.showNotification(error.message || 'Failed to delete item', 'error');
      } finally {
        this.isSaving = false;
      }
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.currentItem.image = file;
        this.imagePreview = URL.createObjectURL(file);
      }
    },
    cancelEdit() {
      this.showForm = false;
      this.resetForm();
    },
    resetForm() {
      this.currentItem = {
        id: null,
        name: '',
        price: '',
        category: '',
        image: null
      };
      this.imagePreview = null;
      this.isEditing = false;
    },
    getImageUrl(imagePath) {
      if (!imagePath) {
        return require('@/assets/default.png');
      }
      
      if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath;
      }
      
      if (imagePath.startsWith('/uploads/')) {
        return `http://localhost:8000${imagePath}`;
      }
      
      if (!imagePath.includes('/')) {
        return `http://localhost:8000/uploads/avatars/${imagePath}`;
      }
      
      return require('@/assets/default.png');
    },
    filterItemsByCategory() {
      if (!this.allItems) return;
      
      if (this.selectedCategory === 'All') {
        this.items = [...this.allItems];
      } else {
        this.items = this.allItems.filter(item => item.category === this.selectedCategory);
      }
      
      // Sort items by name for consistency
      this.items.sort((a, b) => a.name.localeCompare(b.name));
    },
    showCategoryModal() {
      this.showCategoryForm = true;
      this.newCategoryName = '';
      this.newCategoryType = '';
      this.newCategoryIcon = '';
    },
    closeCategoryModal() {
      this.showCategoryForm = false;
      this.newCategoryName = '';
      this.newCategoryType = '';
      this.newCategoryIcon = '';
    },
    async loadCategories() {
      try {
        const response = await fetch('http://localhost:8000/api/categories');
        const data = await response.json();
        if (data.categories) {
          this.categories = data.categories.map(cat => ({
            ...cat,
            icon: cat.icon ? cat.icon : 'fas fa-circle'
          }));
        }
      } catch (error) {
        console.error('Error loading categories:', error);
        this.showNotification('Failed to load categories', 'error');
      }
    },
    async addNewCategory() {
      if (!this.newCategoryName.trim() || !this.newCategoryType || !this.newCategoryIcon) {
        this.showNotification('Please fill in all category fields', 'error');
        return;
      }

      try {
        const formData = new FormData();
        formData.append('name', this.newCategoryName.trim());
        formData.append('type', this.newCategoryType);
        formData.append('icon', this.newCategoryIcon);

        const url = this.editingCategoryId 
          ? `http://localhost:8000/api/categories/${this.editingCategoryId}`
          : 'http://localhost:8000/api/categories';

        const method = this.editingCategoryId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
          method,
          body: formData
        });

        if (!response.ok) {
          throw new Error('Failed to process category');
        }

        const result = await response.json();

        // Update local categories immediately
        if (this.editingCategoryId) {
          const index = this.categories.findIndex(c => c.id === this.editingCategoryId);
          if (index !== -1) {
            this.categories = [
              ...this.categories.slice(0, index),
              {
                id: this.editingCategoryId,
                name: this.newCategoryName.trim(),
                type: this.newCategoryType,
                icon: this.newCategoryIcon
              },
              ...this.categories.slice(index + 1)
            ];
          }
        } else {
          this.categories = [...this.categories, {
            id: result.id,
            name: this.newCategoryName.trim(),
            type: this.newCategoryType,
            icon: this.newCategoryIcon
          }];
        }

        // Refresh categories and trigger updates
        await this.loadCategories();
        window.dispatchEvent(new CustomEvent('categories-updated'));
        window.dispatchEvent(new CustomEvent('stock-updated'));
        
        this.showNotification(
          this.editingCategoryId ? 'Category updated successfully' : 'Category added successfully'
        );
        this.resetCategoryForm();
        
        // Force refresh of items to ensure proper category assignment
        await this.fetchItems();
      } catch (error) {
        console.error('Error with category:', error);
        this.showNotification(error.message, 'error');
      }
    },
    resetCategoryForm() {
      this.newCategoryName = '';
      this.newCategoryType = '';
      this.newCategoryIcon = '';
      this.editingCategoryId = null;
    },
    editCategory(category) {
      this.editingCategoryId = category.id;
      this.newCategoryName = category.name;
      this.newCategoryType = category.type;
      this.newCategoryIcon = category.icon || '';
      
      // Scroll the form into view
      this.$nextTick(() => {
        const form = document.querySelector('.add-category-form');
        if (form) {
          form.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    },
    async deleteCategory(categoryId) {
      if (!confirm('Are you sure you want to delete this category?')) return;

      try {
        const category = this.categories.find(c => c.id === categoryId);
        if (!category) {
          this.showNotification('Category not found', 'error');
          return;
        }

        // Check for items using this category
        const itemsInCategory = this.allItems.filter(item => item.category === category.name);
        if (itemsInCategory.length > 0) {
          const itemsList = itemsInCategory.map(item => item.name).join(', ');
          this.showNotification(
            `Cannot delete category "${category.name}" because it has the following items: ${itemsList}. Please reassign or delete these items first.`,
            'error'
          );
          return;
        }

        const response = await fetch(`http://localhost:8000/api/categories/${categoryId}`, {
          method: 'DELETE'
        });

        if (!response.ok) {
          const contentType = response.headers.get('content-type');
          let errorMessage = 'Failed to delete category';
          
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
          } else {
            const textError = await response.text();
            errorMessage = textError || errorMessage;
          }
          
          throw new Error(errorMessage);
        }

        // Remove the category from local state immediately
        this.categories = this.categories.filter(c => c.id !== categoryId);
        
        this.showNotification(`Category "${category.name}" deleted successfully`);
        window.dispatchEvent(new CustomEvent('categories-updated'));
      } catch (error) {
        console.error('Error deleting category:', error);
        this.showNotification(error.message, 'error');
      }
    },
    getCategoryType(categoryName) {
      const category = this.categories.find(cat => cat.name === categoryName);
      return category ? category.type : null;
    },
    formatCategoryType(type) {
      if (!type) return '';
      
      // Convert underscore to space and capitalize each word
      return type.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    },
    initWebSocket() {
      const wsUrl = `ws://${window.location.hostname}:8000/ws/orders`;
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected in ItemEditor');
        this.wsConnected = true;
        // Initial fetch of data when connection is established
        this.fetchItems();
        this.loadCategories();
      };
      
      this.ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received in ItemEditor:', data);

          if (data.type === 'stock_update') {
            // For stock updates, update the specific item first for immediate feedback
            // This avoids waiting for a full API call and makes the UI more responsive
            
            // Find the item in our current list
            const itemIndex = this.items.findIndex(item => item.id === data.item_id);
            if (itemIndex !== -1) {
              // Update the item directly in the array
              const updatedItem = {...this.items[itemIndex]};
              updatedItem.stock = data.new_quantity;
              this.$set(this.items, itemIndex, updatedItem);
              
              // If this is the currently selected item, update it too
              if (this.selectedItem && this.selectedItem.id === data.item_id) {
                this.selectedItem = {...this.selectedItem, stock: data.new_quantity};
              }
              
              // Emit events to notify other components
              this.$emit('item-updated');
              window.dispatchEvent(new CustomEvent('stock-updated'));
              
              // After immediate update, schedule a background refresh
              setTimeout(() => {
                this.fetchItems().catch(err => {
                  console.error('Error refreshing items after stock update:', err);
                });
              }, 1000);
            } else {
              // If item not found in current list, do a full refresh
              await this.fetchItems();
              this.$emit('item-updated');
              window.dispatchEvent(new CustomEvent('stock-updated'));
            }
          } else if (data.type === 'menu_update') {
            // For menu updates, we need to refresh everything
            await this.fetchItems();
            await this.loadCategories();
            this.$emit('item-updated');
            window.dispatchEvent(new CustomEvent('stock-updated'));
          } else if (data.type === 'category_update') {
            // For category updates, refresh both to ensure consistency
            await this.loadCategories();
            await this.fetchItems();
            window.dispatchEvent(new CustomEvent('categories-updated'));
            window.dispatchEvent(new CustomEvent('stock-updated'));
          }
        } catch (error) {
          console.error('Error processing WebSocket message in ItemEditor:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected in ItemEditor');
        this.wsConnected = false;
        // Try to reconnect after 5 seconds
        setTimeout(() => {
          this.initWebSocket();
        }, 5000);
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error in ItemEditor:', error);
        this.wsConnected = false;
      };
    },
  },
  async mounted() {
    await this.loadCategories();
    window.addEventListener('categories-updated', this.loadCategories);
    await this.fetchItems();
    
    if (this.allItems.length === 0 && !this.hasImported) {
      this.showNotification('Importing menu items...', 'info');
      try {
        await importMenuItems();
        this.showNotification('Menu items imported successfully!', 'success');
        this.hasImported = true;
        await this.fetchItems();
      } catch (error) {
        console.error('Error importing menu:', error);
        this.showNotification('Error importing menu items', 'error');
      }
    }
    // Initialize WebSocket connection
    this.initWebSocket();
  },
  beforeUnmount() {
    window.removeEventListener('categories-updated', this.loadCategories);
    if (this.ws) {
      this.ws.close();
    }
  }
}
</script>

<style scoped>
.item-editor {
  padding: 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.header h2 {
  color: #d12f7a;
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}

.header-buttons {
  display: flex;
  gap: 15px;
}

.add-item-button {
  background: #d12f7a;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(209, 47, 122, 0.2);
}

.add-item-button:hover {
  background: #b82d67;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(209, 47, 122, 0.3);
}

.add-item-button i {
  font-size: 18px;
}

.add-category-button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(76, 175, 80, 0.2);
}

.add-category-button:hover {
  background: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(76, 175, 80, 0.3);
}

/* Category Filter */
.category-filter {
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.category-filter label {
  font-weight: 500;
  color: #666;
}

.category-filter select {
  padding: 10px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 15px;
  color: #333;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
}

.category-filter select:hover {
  border-color: #d12f7a;
}

.category-filter select:focus {
  outline: none;
  border-color: #d12f7a;
  box-shadow: 0 0 0 3px rgba(209, 47, 122, 0.1);
}

/* Item Form */
.item-form {
  /* Remove or comment out the old item-form styles since we're now using a modal */
  /* These styles can be safely removed or adjusted to work with our new modal */
  display: none; /* Hide the old form style */
}

/* Keep the rest of the styles for inputs, etc. */

/* Items List */
.items-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.item-card {
  background: white;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

.item-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.item-info {
  padding: 20px;
}

.item-info h4 {
  margin: 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.item-price {
  color: #d12f7a;
  font-size: 18px;
  font-weight: 600;
  margin: 8px 0;
}

.item-category {
  color: #666;
  font-size: 14px;
  margin: 5px 0 0;
}

.item-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.item-card:hover .item-actions {
  opacity: 1;
}

.edit-button, .delete-button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.edit-button {
  background: rgba(255, 255, 255, 0.9);
  color: #4CAF50;
}

.edit-button:hover {
  background: #4CAF50;
  color: white;
  transform: rotate(15deg);
}

.delete-button {
  background: rgba(255, 255, 255, 0.9);
  color: #f44336;
}

.delete-button:hover {
  background: #f44336;
  color: white;
  transform: rotate(-15deg);
}

/* Notifications */
.notification {
  padding: 15px 25px;
  border-radius: 12px;
  margin-bottom: 25px;
  text-align: center;
  font-weight: 500;
  animation: slideIn 0.3s ease;
}

.notification.success {
  background: #4CAF50;
  color: white;
}

.notification.error {
  background: #f44336;
  color: white;
}

/* Loading State */
.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 18px;
}

/* Disabled States */
button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none !important;
}

/* Animations */
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

/* Responsive Design */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .header-buttons {
    flex-direction: column;
  }

  .add-item-button,
  .add-category-button {
    width: 100%;
  }

  .items-list {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  .form-actions {
    flex-direction: column;
  }

  .save-button, .cancel-button {
    width: 100%;
  }

  .category-modal-content {
    width: 95%;
    margin: 10px;
  }
}

@media (max-width: 480px) {
  .item-editor {
    padding: 15px;
  }

  .item-form {
    padding: 20px;
  }

  .items-list {
    grid-template-columns: 1fr;
  }
}

/* Category Modal */
.category-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.category-modal-content {
  background: white;
  border-radius: 15px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.add-category-form {
  margin-bottom: 30px;
}

.categories-list {
  margin-top: 20px;
}

.categories-list h4 {
  margin-bottom: 15px;
  color: #333;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f8f8f8;
  border-radius: 8px;
  margin-bottom: 8px;
}

.delete-category-btn {
  background: none;
  border: none;
  color: #f44336;
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  transition: all 0.3s ease;
}

.delete-category-btn:hover {
  background: rgba(244, 67, 54, 0.1);
  color: #d32f2f;
  transform: scale(1.1);
}

.icon-preview {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding: 10px;
  background: #f8f8f8;
  border-radius: 8px;
}

.icon-preview i {
  font-size: 24px;
  color: #d12f7a;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-type {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #f0f0f0;
  color: #666;
}

.category-info i {
  width: 20px;
  text-align: center;
  color: #d12f7a;
}

/* Add these new styles */
.category-actions {
  display: flex;
  gap: 8px;
}

.edit-category-btn {
  background: none;
  border: none;
  color: #4CAF50;
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  transition: all 0.3s ease;
}

.edit-category-btn:hover {
  background: rgba(76, 175, 80, 0.1);
  color: #45a049;
  transform: scale(1.1);
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.add-category-form h4 {
  color: #d12f7a;
  margin-bottom: 20px;
}

/* Add/Edit Item Modal Styles */
.item-form-modal {
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
  backdrop-filter: blur(4px);
}

.item-form-modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #d12f7a;
  color: white;
  padding: 15px 20px;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.modal-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.close-modal-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-modal-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 20px;
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

/* Adjust existing item-form styles to work with the modal */
.form-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Form styles for the modal */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #444;
}

.form-input {
  width: 85%;
  padding: 12px 15px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 15px;
  transition: all 0.3s ease;
}

.form-input:hover {
  border-color: #d12f7a;
}

.form-input:focus {
  outline: none;
  border-color: #d12f7a;
  box-shadow: 0 0 0 3px rgba(209, 47, 122, 0.1);
}

.form-help {
  color: #666;
  font-size: 13px;
  margin-top: 5px;
}

/* Image Preview */
.image-preview {
  max-width: 200px;
  max-height: 200px;
  border-radius: 10px;
  margin-top: 15px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.save-button, .cancel-button {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-button {
  background: #d12f7a;
  color: white;
  flex: 1;
}

.save-button:hover {
  background: #b82d67;
  transform: translateY(-2px);
}

.cancel-button {
  background: #f0f0f0;
  color: #666;
  padding: 12px 30px;
}

.cancel-button:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
}
</style> 