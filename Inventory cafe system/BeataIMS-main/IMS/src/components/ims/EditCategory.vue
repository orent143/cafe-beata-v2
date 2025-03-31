<template>
  <div>
    <!-- Overlay for the Edit Category form -->
    <div class="form-overlay" v-if="category"></div>

    <!-- Pop-out form for editing Category -->
    <div class="popout-form" v-if="category">
      <div class="form-header">
        <h2>Edit Category</h2>
        <button @click="closeForm" class="close-btn">x</button>
      </div>
      <form @submit.prevent="confirmAndSubmit" class="form-container">
        <div class="form-group">
          <label for="categoryName">Category Name:</label>
          <input v-model="editedCategory.CategoryName" id="categoryName" type="text" placeholder="Category Name" required />
        </div>

        <div class="form-group image-section">
          <label for="categoryImage">Category Image:</label>
          <div class="image-upload-container">
            <label for="categoryImage" class="image-upload">
              <input 
                type="file" 
                id="categoryImage" 
                @change="handleImageChange" 
                accept="image/*"
                class="image-input"
              />
              <img 
                v-if="imagePreview || editedCategory.Image" 
                :src="imagePreview || editedCategory.Image" 
                alt="Category Preview"
                class="preview-image"
              />
              <span v-if="!imagePreview && !editedCategory.Image" class="upload-text">Upload New Image</span>
            </label>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="save-category-btn">Save Category</button>
        </div>
      </form>
    </div>

    <!-- Confirmation Modal for Category edit -->
    <div class="modal-overlay" v-if="showConfirmModal">
      <div class="confirmation-modal">
        <div class="modal-content">
          <h3>Confirm Edit</h3>
          <p>Are you sure you want to edit this category?</p>
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
import { CATEGORIES_API } from '@/api/config.js';

export default {
  props: {
    category: Object
  },
  data() {
    return {
      editedCategory: { ...this.category },
      imagePreview: null,
      newImage: null,
      showConfirmModal: false    };
  },
  methods: {
    async confirmAndSubmit() {
      this.showConfirmModal = true;
    },
    cancelSubmit() {
      this.showConfirmModal = false;
    },
    async confirmSubmit() {
      this.showConfirmModal = false;
      await this.submitForm();
    },
    handleImageChange(event) {
      const file = event.target.files[0];
      if (file) {
        this.newImage = file;
        this.imagePreview = URL.createObjectURL(file);
      }
    },
    async submitForm() {
      const toast = useToast();
      try {
        const formData = new FormData();
        formData.append('CategoryName', this.editedCategory.CategoryName);
        if (this.newImage) {
          formData.append('Image', this.newImage);
        }

        await axios.put(
          `${CATEGORIES_API}/categories/${this.category.id}`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        );

        toast.success('Category updated successfully!');
        this.$emit("save", { 
          ...this.editedCategory,
          Image: this.imagePreview || this.editedCategory.Image 
        });
        this.closeForm();
      } catch (error) {
        toast.error('Error updating category.');
        console.error("Error updating category:", error);
      }
    },
    closeForm() {
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview);
      }
      this.$emit("close");
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
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;  /* Larger z-index to ensure it overlays other content */
  display: block; /* Ensure it's visible */
}

/* Popout form styling */
.popout-form {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.459);
  position: fixed; 
  right: 50%;
  top: 50%;
  transform: translate(50%, -50%);
  width: 400px;
  max-width: 100%;
  z-index: 1000; 
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-header h2 {
  font-size: 25px;
  font-family: 'Arial', sans-serif;
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
  grid-template-columns: 1fr;
  gap: 15px;
}

.form-group {
  width: 100%;
}

label {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 5px;
  display: block;
  color: #272727;
}

input {
  padding: 10px;
  font-size: 14px;
  border-radius: 12px;
  width: 95%;
  border: 1px solid #ccc;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.save-category-btn {
  padding: 10px 20px;
  background-color: #E54F70;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.save-category-btn:hover {
  background-color: #a33950;
}

.save-category-btn:focus {
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
</style>