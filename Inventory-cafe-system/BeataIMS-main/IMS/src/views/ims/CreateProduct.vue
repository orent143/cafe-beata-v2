<template> 
  <Header :isSidebarCollapsed="isSidebarCollapsed" @toggle-sidebar="handleSidebarToggle" />

  <SideBar :isCollapsed="isSidebarCollapsed" />
  
  <div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="main-container">
      <div class="header-container">
        <h1 class="header">Create Product</h1>
      </div>
      <div class="content-wrapper">
        <div class="product-details">
          <h2>Product Details</h2>
          
          <div class="form-group">
            <label>Product ID</label>
            <input v-model="product.ProductID" type="text" required class="form-input" placeholder="Enter Product ID" />
          </div>

          <div class="form-group">
            <label>Product Name</label>
            <input v-model="product.ProductName" type="text" required class="form-input" placeholder="Enter Product Name" />
          </div>

          <div class="form-group">
            <label>Unit Price (₱)</label>
            <input v-model.number="product.UnitPrice" type="number" min="0" step="0.01" required class="form-input" />
          </div>

          <div class="form-group">
            <label>Category</label>
            <select v-model="product.CategoryID" class="form-input" required>
              <option value="" disabled>Select Category</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.CategoryName }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Process Type</label>
            <select v-model="product.ProcessType" class="form-input" required @change="handleProcessTypeChange">
              <option value="Ready-Made">Ready Made</option>
              <option value="To Be Made">To Be Made</option>
            </select>
          </div>

          <!-- Threshold Field (only for Ready-Made) -->
          <div class="form-group" v-if="product.ProcessType === 'Ready-Made'">
            <label>Threshold</label>
            <input v-model.number="product.Threshold" type="number" min="0" step="1" required class="form-input" placeholder="Enter Threshold" />
          </div>

          <div class="form-group">
            <label>Product Image</label>
            <div class="image-upload-container">
              <div class="image-preview" v-if="imagePreview">
                <img :src="imagePreview" alt="Preview" />
                <button type="button" class="remove-image-btn" @click="removeImage">Remove</button>
              </div>
              <div class="upload-area" v-else>
                <input 
                  type="file" 
                  @change="handleImageUpload"
                  accept="image/*"
                  class="file-input"
                  id="imageInput"
                />
                <label for="imageInput" class="upload-label">
                  <i class="fas fa-cloud-upload-alt"></i>
                  <span>Click to upload image</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="summary-section">
          <h2>Product Summary</h2>
          <div class="summary-details">
            <p><strong>Product ID:</strong> {{ product.ProductID || 'N/A' }}</p>
            <p><strong>Product Name:</strong> {{ product.ProductName || 'N/A' }}</p>
            <p><strong>Category:</strong> {{ selectedCategoryName }}</p>
            <p><strong>Unit Price:</strong> ₱{{ product.UnitPrice.toFixed(2) }}</p>
            <p><strong>Process Type:</strong> {{ product.ProcessType }}</p>
            <p v-if="product.ProcessType === 'Ready-Made'"><strong>Threshold:</strong> {{ product.Threshold }}</p>
          </div>

          <div class="form-actions">
            <button type="button" @click="resetForm" class="reset-btn">Reset</button>
            <button type="button" @click="showConfirmModal = true" class="submit-btn">Create Product</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirmation Modal -->
  <div class="modal-overlay" v-if="showConfirmModal">
    <div class="confirmation-modal">
      <div class="modal-content">
        <h3>Confirm Creation</h3>
        <p>Are you sure you want to create this product?</p>
        <div class="modal-actions">
          <button @click="showConfirmModal = false" class="cancel-btn">Cancel</button>
          <button @click="confirmSubmit" class="confirm-btn">Confirm</button>
        </div>
      </div>
    </div>
  </div>
</template>

---

### ✅ **Updated Script Logic**

```javascript
<script>
import axios from 'axios';
import SideBar from '@/components/ims/SideBar.vue';
import Header from '@/components/Header.vue';
import { useToast } from 'vue-toastification';
import { INVENTORY_API, CATEGORIES_API } from '@/api/config.js';

export default {
  components: { SideBar, Header },
  data() {
    return {
      isSidebarCollapsed: false,
      product: {
        ProductID: "",
        ProductName: "",
        CategoryID: null,
        UnitPrice: 0,
        ProcessType: "Ready-Made",
        Threshold: null,   // ✅ New threshold field
        Image: null,
      },
      categories: [],
      showConfirmModal: false,
      toast: useToast(),
      imagePreview: null,
    };
  },
  computed: {
    selectedCategoryName() {
      const category = this.categories.find(cat => cat.id === this.product.CategoryID);
      return category ? category.CategoryName : 'N/A';
    }
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    async fetchCategories() {
      try {
        const response = await axios.get(`${CATEGORIES_API}`);
        this.categories = response.data;
      } catch (error) {
        this.toast.error("Failed to fetch categories.");
      }
    },
    handleProcessTypeChange() {
      // Reset threshold if switching to 'To Be Made'
      if (this.product.ProcessType === "To Be Made") {
        this.product.Threshold = null;
      }
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.product.Image = file;
        this.imagePreview = URL.createObjectURL(file);
      }
    },
    removeImage() {
      this.product.Image = null;
      this.imagePreview = null;
    },
    async confirmSubmit() {
      this.showConfirmModal = false;
      try {
        const formData = new FormData();
        formData.append("ProductID", this.product.ProductID);
        formData.append("ProductName", this.product.ProductName);
        formData.append("CategoryID", this.product.CategoryID);
        formData.append("UnitPrice", this.product.UnitPrice);
        formData.append("ProcessType", this.product.ProcessType);

        if (this.product.ProcessType === "Ready-Made") {
          formData.append("Threshold", this.product.Threshold);
        }

        if (this.product.Image) {
          formData.append("Image", this.product.Image);
        }

        const response = await axios.post(
          `${INVENTORY_API}/inventoryproduct/`,
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        this.toast.success(response.data.message || "Product created successfully!");
        this.resetForm();
      } catch (error) {
        this.toast.error(error.response?.data?.detail || "Failed to create product.");
      }
    },
    resetForm() {
      this.product = {
        ProductID: "",
        ProductName: "",
        CategoryID: null,
        UnitPrice: 0,
        ProcessType: "Ready-Made",
        Threshold: null,
        Image: null,
      };
      this.imagePreview = null;
    }
  },
  created() {
    this.fetchCategories();
  }
};
</script>


<style scoped>
.app-container {
  display: flex;
  transition: all 0.3s ease;
  height: 100vh;
}

.app-container.sidebar-collapsed .main-container {
  margin-left: 70px; /* Adjust space when collapsed */
}

.app-container .main-container {
  flex-grow: 1;
  margin-left: 230px; /* Space when sidebar is expanded */
  transition: margin-left 0.3s ease;
  padding: 20px;
}

.main-container {
  width: calc(100% - 230px);
}

.sidebar-collapsed .main-container {
  width: calc(100% - 70px);
}

/* Smooth transition for content wrapper */
.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 30px;
  transition: all 0.3s ease;
}

.header{  
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}

.product-details {
  background: #fff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.summary-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
  padding: 20px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #111111;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 6px;
  background-color: #f9f9f9;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #FF32BA; 
  box-shadow: 0 0 5px rgba(255, 50, 186, 0.5); 
  outline: none;
}

textarea.form-input {
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 25px;
}

.submit-btn {
  background: #E54F70;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.submit-btn:hover {
  background-color: #c0425d; 
}

.reset-btn {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.reset-btn:hover {
  background-color: #5a6268; 
}

button:focus {
  outline: none;
}

.header-container h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 15px;
}

.product-details h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #444;
  margin-bottom: 20px;
}

.select-category {
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 2px solid #ddd;
  padding: 12px;
  font-size: 1rem;
  color: #333;
  width: 100%;
  transition: all 0.3s ease;
}

.select-category:focus {
  border-color: #FF32BA;
  box-shadow: 0 0 5px rgba(255, 50, 186, 0.5);
  outline: none;
}
.stock-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.add-stock-btn, .remove-stock-btn {
  margin-top: 5px;
  padding: 5px;
  cursor: pointer;
  border-color: #E54F70;
  box-shadow: 0 0 5px rgba(255, 50, 186, 0.5);
  outline: none;
  color: #f9f9f9;
}
.form-group button{
  display: flex;
  border-radius: 5px;
  color:#ffffff;
  background-color: #E54F70;
}
.product-details select {
  font-size: 1rem;
  color: #333;
  padding: 12px;
  width: 100%;
  border-radius: 6px;
  background-color: #f9f9f9;
  border: 2px solid #ddd;
  transition: all 0.3s ease;
}

.product-details select:focus {
  border-color: #FF32BA;
  box-shadow: 0 0 5px rgba(255, 50, 186, 0.5);
  outline: none;
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

.image-upload-container {
  width: 100%;
  min-height: 200px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 200px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.remove-image-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-weight: bold;
  font-size: 16px;
  color: #E54F70;
}

.remove-image-btn:hover {
  background: rgba(229, 79, 112, 0.8);
  color: white;
}

.upload-area {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-input {
  display: none;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: #666;
}

.upload-label i {
  font-size: 2rem;
  color: #E54F70;
}

.upload-label:hover {
  color: #E54F70;
}

@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .main-container {
    margin-left: 0;
  }
}
</style>