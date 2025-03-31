<template>
  <div class="menu-section">
    <!-- Header with Category Filter -->
    <div class="menu-header">
      <h2>Menu Items</h2>
      <select v-model="selectedCategory" class="category-filter">
        <option value="">All Categories</option>
        <option v-for="category in categories" :key="category.id" :value="category.CategoryName">
          {{ category.CategoryName }}
        </option>
      </select>
    </div>

    <!-- Loading/Error Message -->
    <div v-if="loading">Loading menu items...</div>
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <!-- Menu Items Grid -->
    <div v-if="filteredMenuItems.length > 0" class="items-grid">
      <MenuItemCard
        v-for="menuItem in filteredMenuItems"
        :key="menuItem.id"
        :item="{
          id: menuItem.id,
          name: menuItem.name,
          price: menuItem.price,
          stock: menuItem.stock,
          process_type: menuItem.process_type,
          image: menuItem.image,
          category: menuItem.category,
          status: menuItem.status
        }"
        :quantity="getItemQuantity(menuItem)"
        :selected="isItemSelected(menuItem)"
        @add="addOrUpdateItem(menuItem)"
        @update:quantity="updateQuantity(menuItem, $event)"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import MenuItemCard from './MenuItemCard.vue';
import { ORDERS_API, CATEGORIES_API } from '@/api/config.js';
import { useToast } from 'vue-toastification';

export default {
  name: 'OrderItemSelector',
  components: { MenuItemCard },
  props: {
    items: {
      type: Array,
      required: true
    },
    menuItems: {
      type: Array,
      required: true
    }
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  data() {
    return {
      loading: false,
      errorMessage: '',
      categories: [],  // Categories fetched from the backend
      selectedCategory: ''  // The selected category for filtering
    };
  },
  mounted() {
    this.fetchMenuItems();
    this.fetchCategories();
  },
  computed: {
    // Filtered menu items based on selected category
    filteredMenuItems() {
      if (!this.selectedCategory) return this.menuItems;
      return this.menuItems.filter(item => item.category === this.selectedCategory);
    }
  },
  methods: {
    // Fetch categories from the backend
    async fetchCategories() {
      try {
        const response = await axios.get(`${CATEGORIES_API}/`);
        this.categories = response.data;
      } catch (error) {
        console.error('Error fetching categories:', error.response?.data?.detail || error.message);
        this.errorMessage = 'Failed to load categories.';
        this.toast.error('Failed to load categories');
      }
    },

    // Fetch menu items
    async fetchMenuItems() {
      try {
        this.loading = true;
        const response = await axios.get(`${ORDERS_API}/menu_items/all`);
        const mappedMenuItems = response.data.map(item => ({
          id: item.id,
          name: item.name,
          price: item.price,
          stock: item.process_type === 'To Be Made' ? '∞' : item.stock,
          process_type: item.process_type,
          image: item.image,
          category: item.category,
          status: item.process_type === 'To Be Made' ? 'Available' : (item.stock > 0 ? 'In Stock' : 'Out of Stock')
        }));

        this.$emit('update:menuItems', mappedMenuItems);
        if (!mappedMenuItems.length) {
          this.errorMessage = 'No menu items found.';
          this.toast.warning('No menu items found');
        }
      } catch (error) {
        console.error('Error fetching menu items:', error.response?.data?.detail || error.message);
        this.errorMessage = 'Failed to load menu items.';
        this.toast.error('Failed to load menu items');
      } finally {
        this.loading = false;
      }
    },

    getItemQuantity(menuItem) {
      const existingItem = this.items.find(item => item.id === menuItem.id);
      return existingItem ? existingItem.quantity : 1;
    },

    isItemSelected(menuItem) {
      return this.items.some(item => item.id === menuItem.id);
    },

    addOrUpdateItem(menuItem) {
      if (menuItem.process_type !== 'To Be Made' && menuItem.stock <= 0) {
        this.toast.error('This item is out of stock');
        return;
      }

      const updatedItems = [...this.items];
      const existingItem = updatedItems.find(item => item.id === menuItem.id);

      if (existingItem) {
        if (menuItem.process_type !== 'To Be Made' && existingItem.quantity >= menuItem.stock) {
          this.toast.error('Cannot exceed available stock');
          return;
        }
        existingItem.quantity = this.getItemQuantity(menuItem);
      } else {
        updatedItems.push({
          id: menuItem.id,
          name: menuItem.name,
          price: menuItem.price,
          quantity: 1,
          process_type: menuItem.process_type,
          status: menuItem.status,
          category: menuItem.category
        });
      }

      this.$emit('update:items', updatedItems);
    },

    updateQuantity(menuItem, quantity) {
      if (menuItem.process_type !== 'To Be Made' && quantity > menuItem.stock) {
        this.toast.error('Cannot exceed available stock');
        return;
      }

      const updatedItems = this.items.map(item =>
        item.id === menuItem.id ? { ...item, quantity } : item
      );
      this.$emit('update:items', updatedItems);
    }
  }
};
</script>

<style scoped>
.menu-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-filter {
  padding: 10px;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  cursor: pointer;
  font-size: 15px;
  color: #333;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5em;
}
</style>
