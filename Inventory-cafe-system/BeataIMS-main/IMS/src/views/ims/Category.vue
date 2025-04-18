<template>
  <Header 
    :isSidebarCollapsed="isSidebarCollapsed" 
    @toggle-sidebar="handleSidebarToggle"
    v-model:searchQuery="searchTerm"
    @update:searchQuery="updateSearchTerm"
  />

<SideBar :isCollapsed="isSidebarCollapsed" />
<div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <div class="header-title">
      <h1 class="products-header">Categories</h1>
      <p class="sub-description">
        Organize your products into categories. Edit or delete existing categories, or add new ones to improve product management.
      </p>
    </div>
      <div class="header-actions">
        <button @click="toggleAddForm" class="add-product-btn">Add</button>
      </div>
    </div>

    <AddCategory 
      v-if="showAddForm" 
      @add="addCategory" 
      :isVisible="showAddForm" 
      @close="toggleAddForm"
      class="add-category-form" 
    />
    <div class="category-container">
      <div class="category-list">
        <div v-for="category in filteredCategories" :key="category.id" class="category-card">
          <img 
  :src="getCategoryImage(category)" 
  :alt="category.CategoryName"
  @error="handleImageError"
  class="category-image"
/>

    <h3>{{ category.CategoryName }}</h3>
          <div class="category-actions">
            <button @click="setEditCategory(category)" class="action-btn edit-btn">
              <i class="pi pi-pencil"></i>
            </button>
            <button @click="confirmDelete(category.id)" class="action-btn remove-btn">
              <i class="pi pi-trash"></i>
            </button>
        </div>
        </div>
      </div>
    </div>

    <div class="modal-overlay" v-if="showConfirmModal">
      <div class="confirmation-modal">
        <div class="modal-content">
          <h3>Confirm Deletion</h3>
          <p>Are you sure you want to delete this category?</p>
          <div class="modal-actions">
            <button @click="confirmSubmit" class="confirm-btn">Yes</button>
            <button @click="cancelSubmit" class="cancel-btn">No</button>
          </div>
        </div>
      </div>
    </div>

    <EditCategory 
      v-if="editingCategory" 
      :category="editingCategory" 
      @save="saveCategory" 
      @close="toggleEditForm"
    />
  </div>
</template>

<script>
import axios from 'axios';
import AddCategory from '@/components/ims/AddCategory.vue';
import EditCategory from '@/components/ims/EditCategory.vue';
import SideBar from '@/components/ims/SideBar.vue';
import Header from '@/components/Header.vue';
import { useToast } from 'vue-toastification';
import { CATEGORIES_API, API_BASE_URL, getImageUrl } from '@/api/config.js';

export default {
  components: {
    AddCategory,
    EditCategory,
    SideBar,
    Header
  },
  data() {
    return {
      isSidebarCollapsed: false,
      categories: [],  
      showAddForm: false,
      editingCategory: null,
      searchTerm: '',
      showConfirmModal: false,
      selectedCategoryId: null,
      toast: useToast(),
      fallbackImage: 'https://via.placeholder.com/100',
      loading: false
    };
  },
  computed: {
    filteredCategories() {
      return this.categories.filter(category =>
        category.CategoryName.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
  },
  created() {
    this.fetchCategories(); 
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    updateSearchTerm(query) {
      this.searchTerm = query;
    },
    toggleEditForm() {
      this.editingCategory = null;
    },
    toggleAddForm() {
      this.showAddForm = !this.showAddForm;
    },
    getCategoryImage(category) {
      if (!category.ImagePath) {
        return this.fallbackImage;
      }

      if (category.ImagePath.startsWith('http')) {
        return category.ImagePath;
      }

      return getImageUrl(category.ImagePath);
    },
    handleImageError(event) {
      event.target.src = this.fallbackImage;
    },
    async fetchCategories() {
      try {
        this.loading = true;
        const response = await axios.get(`${CATEGORIES_API}/`);
        console.log("Fetched Categories:", response.data); 
        
        this.categories = response.data.map(category => ({
          ...category,
          imageUrl: this.getCategoryImage(category)
        }));
        this.loading = false;
      } catch (error) {
        console.error("Error fetching categories:", error);
        this.toast.error('Error fetching categories');
        this.loading = false;
      }
    },
    async addCategory(newCategory) {
      await this.fetchCategories(); 
      this.toggleAddForm();
    },
    setEditCategory(category) {
      this.editingCategory = { ...category };
    },
    async saveCategory() {
      await this.fetchCategories(); 
      this.editingCategory = null;
    },
    confirmDelete(categoryId) {
      this.selectedCategoryId = categoryId;
      this.showConfirmModal = true;
    },
    cancelSubmit() {
      this.showConfirmModal = false;
      this.selectedCategoryId = null;
    },
    confirmSubmit() {
      this.showConfirmModal = false;
      this.removeCategory(this.selectedCategoryId);
    },
    async removeCategory(categoryId) {
      try {
        await axios.delete(`${CATEGORIES_API}/categories/${categoryId}`);
        this.categories = this.categories.filter(cat => cat.id !== categoryId);
        this.toast.success('Category deleted successfully!');
      } catch (error) {
        console.error("Error deleting category:", error.response?.data || error.message);
        this.toast.error('Error deleting category.');
      }
    },
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
.category-container {
  flex-grow: 1;
  background-color: #EFEFEF;
  border-radius: 25px;
  overflow-y: auto; 
  margin-left: 5px;
  padding: 20px;
  height: calc(100vh - 120px); 
  max-height: 40dvw;
}
.category-container::-webkit-scrollbar {
  width: 6px;
}

.category-container::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 3px;
}

.category-container::-webkit-scrollbar-track {
  background: transparent;
}
.category-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
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

.main-content {
  flex-grow: 1; 
  transition: margin-left 0.3s ease; 
  height: calc(100vh - 60px); 
  overflow-y: auto; 
}

.category-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  overflow-y: auto; 
}

.category-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color:#dfdfdf;
  padding: 15px;
  height: 230px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  position: relative;
}

.category-card h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #333;
}

.category-actions {
  position: absolute;
  top: 10px;
  right: 10px;
}

.action-btn {
  padding: 8px;
  background-color: transparent;
  color: #333;
  border: none;
  cursor: pointer;
  font-size: 18px;
  margin: 0 5px;
}

.action-btn:hover {
  color: #FF32BA;
}

.edit-btn i, .remove-btn i {
  font-size: 15px;
}

.search-container {
  position: relative;
  margin-right: 3px;
}

.search-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #333;
  pointer-events: none;
}

.search-bar {
  padding: 8px 30px 8px 8px;
  border: 1px solid #94949400;
  border-radius: 10px;
  width: 130px;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  background-color: #d9d9d9;
}

.add-product-btn {
  padding: 8px 12px;
  background-color: #E54F70;
  color: #dbdbdb;
  border: none;
  border-radius: 10px;
  width: 100px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
}

.add-product-btn:hover {
  background-color: #ed9598;
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
</style>
