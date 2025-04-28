<template>
  <div>
    <!-- Overlay for the Edit Product form -->
    <div class="form-overlay" v-if="isVisible"></div>

    <!-- Edit Product Form -->
    <div class="popout-form" v-if="isVisible">
      <div class="form-header">
        <h2>Edit Product</h2>
        <button class="close-btn" @click="closeForm">x</button>
      </div>

      <form @submit.prevent="confirmAndSubmit" class="form-container">
        <div class="form-group">
          <label for="name">Product Name</label>
          <input 
            id="name" 
            v-model="product.ProductName" 
            placeholder="Item Name" 
            required 
          />
        </div>

        <div class="form-group">
          <label for="unitPrice">Unit Price</label>
          <input 
            id="unitPrice" 
            v-model="product.UnitPrice" 
            type="number" 
            placeholder="Unit Price" 
            required 
            min="0" 
            step="0.01" 
          />
        </div>

        <div class="form-group">
          <label for="category">Category</label>
          <select 
            id="category" 
            v-model="product.CategoryID" 
            required
          >
            <option value="" disabled>Select Category</option>
            <option 
              v-for="category in categories" 
              :key="category.id" 
              :value="category.id"
            >
              {{ category.CategoryName }}
            </option>
          </select>
        </div>

        <div class="form-group image-section">
          <label for="image">Product Image</label>
          <div class="image-upload-container">
            <label for="image" class="image-upload">
              <input 
                type="file" 
                id="image" 
                @change="handleFileUpload" 
                accept="image/*"
              />
              <img 
                v-if="imagePreview" 
                :src="imagePreview" 
                class="preview-image" 
                alt="Product preview"
              />
              <span v-if="!imagePreview" class="upload-text">
                Upload New Image
              </span>
            </label>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="add-item-btn">Update Product</button>
        </div>
      </form>
    </div>

    <!-- Confirmation Modal -->
    <div class="modal-overlay" v-if="showConfirmModal">
      <div class="confirmation-modal">
        <div class="modal-content">
          <h3>Confirm Update</h3>
          <p>Are you sure you want to update this product?</p>
          <div class="modal-actions">
            <button @click="cancelSubmit" class="cancel-btn">Cancel</button>
            <button @click="confirmSubmit" class="confirm-btn">Confirm</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';
import { INVENTORY_API, CATEGORIES_API, API_BASE_URL } from '@/api/config.js';

export default {
  emits: ['close', 'update'],

  props: {
    isVisible: Boolean,
    itemToEdit: Object
  },
  data() {
    return {
      product: {
        ProductID: null,  // Changed from id to ProductID
        ProductName: '',
        UnitPrice: 0,
        CategoryID: '',
        Image: ''
      },
      categories: [],
      showConfirmModal: false,
      selectedImage: null,
      imagePreview: null
    };
  },
  methods: {
    closeForm() {
      this.$emit('close');
    },
    async confirmAndSubmit() {
      this.showConfirmModal = true;
    },
    cancelSubmit() {
      this.showConfirmModal = false;
    },
    confirmSubmit() {
      this.showConfirmModal = false;
      this.updateProduct();
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedImage = file;
        this.imagePreview = URL.createObjectURL(file);
      }
    },
    async updateProduct() {
      const toast = useToast();
      try {
        if (!this.product.ProductID) {
          console.error("Product ID is missing!");
          toast.error("Product ID is missing!");
          return; 
        }

        const formData = new FormData();
        
        // Ensure all form values are properly converted to their expected types
        if (this.product.ProductName) {
          formData.append("ProductName", this.product.ProductName);
        }
        
        if (this.product.UnitPrice) {
          formData.append("UnitPrice", parseFloat(this.product.UnitPrice));
        }
        
        if (this.product.CategoryID) {
          formData.append("CategoryID", parseInt(this.product.CategoryID));
        }

        if (this.selectedImage) {
          formData.append("Image", this.selectedImage);
        }

        // Update API endpoint to match FastAPI route
        const response = await axios.put(
          `${INVENTORY_API}/inventoryproduct/${this.product.ProductID}`,
          formData,
          {
            headers: { 
              "Content-Type": "multipart/form-data"
            }
          }
        );
        if (response.data.message) {
          toast.success(response.data.message);
          
          // Update image preview if new image was returned
          if (response.data.Image) {
            this.product.Image = response.data.Image;
            this.imagePreview = `${API_BASE_URL}${response.data.Image}`;
          }

          this.$emit("update", this.product);
          this.closeForm();
        }
      } catch (error) {
        console.error("Error updating product:", error);
        if (error.response?.status === 404) {
          toast.error("Product not found");
        } else {
          toast.error(error.response?.data?.detail || "Failed to update product");
        }
      }
    }
  },
  
  created() {
    if (this.itemToEdit) {
      this.product = {
        ProductID: this.itemToEdit.ProductID || this.itemToEdit.id, // Handle both ID formats
        ProductName: this.itemToEdit.ProductName,
        UnitPrice: this.itemToEdit.UnitPrice,
        CategoryID: this.itemToEdit.CategoryID,
        Image: this.itemToEdit.Image
      };
      
      this.imagePreview = this.product.Image 
        ? `${API_BASE_URL}${this.product.Image}`
        : null;
    }

    axios.get(`${CATEGORIES_API}`)
      .then(response => {
        this.categories = response.data;
      })
      .catch(error => {
        console.error("Error fetching categories:", error);
      });
  },
  watch: {
    itemToEdit: {
      deep: true,
      handler(newValue) {
        if (newValue) {
          this.product = {
            ProductID: newValue.ProductID || newValue.id, // Handle both ID formats
            ProductName: newValue.ProductName,
            UnitPrice: newValue.UnitPrice,
            CategoryID: newValue.CategoryID,
            Image: newValue.Image
          };
          
          this.imagePreview = newValue?.Image 
            ? `${API_BASE_URL}${newValue.Image}`
            : null;
        }
      }
    }
  }
};
</script>


<style scoped>
.form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent background */
  z-index: 999; /* Ensure it's on top of other elements */
}

/* Edit Product Form */
.popout-form {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.459);
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 400px;
  z-index: 1000;
}


.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-header h2 {
  font-size: 25px;
  font-family: "Arial", sans-serif;
  font-weight: 1000;
  color: #000000;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 17px;
  color: #333;
  cursor: pointer;
  font-weight: 1000;
}

.form-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group {
  width: 100%;
}

label {
  font-weight: 600;
  font-size: 14px;
}
.image-section {
  display: flex;
  flex-direction: column;
  grid-column: span 2;
  gap: 10px;
  width: 100%;
}

.image-upload-container {
  display: flex;
  justify-content: center;
  width: 100%;
  margin-bottom: 15px;
}

.image-upload {
  position: relative;
  width: 100%;
  max-width: 210%; 
  height: 120px; 
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px dashed #ccc;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  background-color: #f9f9f9;
}


input,
select {
  padding: 10px;
  font-size: 14px;
  border-radius: 12px;
  width: 85%;
  border: 1px solid #ccc;
}

.image-upload:hover {
  border-color: #E54F70;
  background: #fff5f7;
}

.image-upload input[type="file"] {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  opacity: 0;
  cursor: pointer;
}
.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.upload-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #666;
  font-size: 14px;
  text-align: center;
  width: 100%;
}
.upload-text::before {
  content: '+';
  display: block;
  font-size: 24px;
  margin-bottom: 5px;
  color: #E54F70;
}

.form-actions {
  display: flex;
  justify-content: center;
  width: 100%;
  margin-top: 20px;
  grid-column: span 2;
}

.add-item-btn {
  padding: 10px 20px;
  background-color: #E54F70;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-item-btn:hover {
  background-color: #a33950;
}

.add-item-btn:focus {
  outline: none;
}

.notification {
  background-color: #dff0d8;
  color: #3c763d;
  padding: 10px;
  border-radius: 5px;
  text-align: center;
  margin-top: 10px;
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