<template>
  <div>
    <!-- Overlay for the Add Supplier form -->
    <div class="form-overlay" v-if="isVisible"></div>

    <!-- Pop-out form for adding Supplier -->
    <div class="popout-form" v-if="isVisible">
      <div class="form-header">
        <h2>Add Supplier</h2>
        <button @click="closeForm" class="close-btn">x</button>
      </div>
      <form @submit.prevent="confirmAndSubmit" class="form-container">
        <div class="form-group">
          <label for="suppliername">Name:</label>
          <input v-model="newSupplier.suppliername" id="suppliername" type="text" placeholder="Supplier Name" required />
        </div>

        <div class="form-group">
          <label for="contactinfo">Contacts:</label>
          <input v-model="newSupplier.contactinfo" id="contactinfo" type="text" placeholder="Contacts" required />
        </div>

        <div class="form-group">
          <label for="email">Email:</label>
          <input v-model="newSupplier.email" id="email" type="email" placeholder="Email" required />
        </div>

        <div class="form-actions">
          <button type="submit" class="add-item-btn">Add Supplier</button>
        </div>
      </form>
    </div>

    <!-- Confirmation Modal for Supplier addition -->
    <div class="modal-overlay" v-if="showConfirmModal">
      <div class="confirmation-modal">
        <div class="modal-content">
          <h3>Confirm Addition</h3>
          <p>Are you sure you want to add this supplier?</p>
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
import { SUPPLIERS_API } from '@/api/config.js';

export default {
  props: {
    isVisible: Boolean,
  },
  setup() {
    const toast = useToast();
    return { toast };
  },
  data() {
    return {
      newSupplier: {
        suppliername: '',
        contactinfo: '',
        email: ''
      },
      showConfirmModal: false,
      isFormVisible: false,
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
      this.submitForm();
    },
    async submitForm() {
      try {
        if (!this.newSupplier.suppliername || !this.newSupplier.contactinfo || !this.newSupplier.email) {
          this.toast.error("All fields are required!");
          return;
        }

        const response = await axios.post(
          `${SUPPLIERS_API}/suppliers/`,  
          new URLSearchParams({
            suppliername: this.newSupplier.suppliername.trim(),
            contactinfo: this.newSupplier.contactinfo.trim(),
            email: this.newSupplier.email.trim()
          })
        );

        this.toast.success('Supplier added successfully!');
        this.$emit('add', response.data);
        this.closeForm();
      } catch (error) {
        this.toast.error('Error adding supplier.');
        console.error("Error adding supplier:", error.response?.data || error.message);
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
  grid-template-columns: 1fr 1fr; 
  gap: 15px; 
  width: 100%;
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

input,
select {
  padding: 10px;
  font-size: 14px;
  border-radius: 12px;
  width: 85%;
  border: 1px solid #ccc;
}

select {
  padding-right: 10px;
}

.form-actions {
  display: flex;
  justify-content: center; 
  width: 100%;
  margin-top: 10px; 
  grid-column: span 2; 
}

.add-item-btn {
  padding: 10px 20px;
  background-color: #E54F70;
  color: #dbdbdb;
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