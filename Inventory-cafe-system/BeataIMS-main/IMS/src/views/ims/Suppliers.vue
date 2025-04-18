<template>
  <Header 
    :isSidebarCollapsed="isSidebarCollapsed" 
    @toggle-sidebar="handleSidebarToggle"
    v-model:searchQuery="searchTerm"
    @update:searchQuery="filterSuppliers"
  />

<SideBar :isCollapsed="isSidebarCollapsed" />
<div class="app-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <div class="header-container">
      <div class="header-title">
      <h1 class="products-header">Suppliers List</h1>
      <p class="sub-description">
        Manage supplier information including contact details and email. Use the action buttons to edit or remove entries.
      </p>
    </div>
      <div class="header-actions">
        <button @click="toggleAddForm" class="add-product-btn">Add</button>
      </div>
    </div>

    <div class="inventory-container">
      <table class="supplier-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Contacts</th>
            <th>Email</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="supplier in filteredSuppliers" :key="supplier.id">
            <td>{{ supplier.suppliername }}</td>
            <td>{{ supplier.contactinfo }}</td>
            <td>{{ supplier.email }}</td>
            <td>
              <button class="action-btn edit" @click="editSupplier(supplier)">
                <i class="pi pi-pencil"></i>
              </button>
              <button class="action-btn delete" @click="confirmDelete(supplier.id)">
                <i class="pi pi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="modal-overlay" v-if="showConfirmModal">
      <div class="confirmation-modal">
        <div class="modal-content">
          <h3>Confirm Deletion</h3>
          <p>Are you sure you want to delete this supplier?</p>
          <div class="modal-actions">
            <button @click="confirmSubmit" class="confirm-btn">Yes</button>
            <button @click="cancelSubmit" class="cancel-btn">No</button>
          </div>
        </div>
      </div>
    </div>

    <add-supplier 
      v-if="showAddForm" 
      :isVisible="showAddForm" 
      @close="toggleAddForm" 
      @add="addSupplier"
    />

    <edit-supplier
      v-if="showEditForm"
      :isVisible="showEditForm"
      :supplierToEdit="selectedSupplier"
      @save="saveSupplier"
      @close="closeForm"
    />
  </div>
</template>

<script>
import axios from 'axios';
import AddSupplier from '@/components/ims/AddSupplier.vue';
import EditSupplier from '@/components/ims/EditSupplier.vue';
import SideBar from '@/components/ims/SideBar.vue'; 
import Header from '@/components/Header.vue'; 
import { useToast } from 'vue-toastification';
import { SUPPLIERS_API } from '@/api/config.js';

export default {
  components: {
    AddSupplier,
    EditSupplier,
    SideBar,
    Header
  },
  data() {
    return {
      isSidebarCollapsed: false,
      searchTerm: '',
      selectedStatus: '',
      showFilterDropdown: false,
      showAddForm: false,
      showEditForm: false,
      showConfirmModal: false,
      selectedSupplier: null,
      selectedSupplierID: null,
      suppliers: [],  
      filteredSuppliers: [],
      toast: useToast(),   
    };
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed;
    },
    toggleFilterDropdown() {
      this.showFilterDropdown = !this.showFilterDropdown;
    },
    toggleAddForm() {
      this.showAddForm = !this.showAddForm;
    },
    toggleEditForm() {
      this.showEditForm = !this.showEditForm;
    },
    async fetchSuppliers() {
      try {
        const response = await axios.get(`${SUPPLIERS_API}/`);  
        this.suppliers = response.data; 
        this.filterSuppliers();
      } catch (error) {
        console.error("Error fetching suppliers:", error);
        this.toast.error("Failed to load suppliers. Please try again.");
      }
    },
    filterSuppliers() {
      this.filteredSuppliers = this.suppliers.filter((supplier) => {
        const matchesSearchTerm = supplier.suppliername.toLowerCase().includes(this.searchTerm.toLowerCase());
        const matchesStatus = this.selectedStatus ? supplier.status === this.selectedStatus : true;
        return matchesSearchTerm && matchesStatus;
      });
    },
    async addSupplier(newSupplier) {
      await this.fetchSuppliers(); 
      this.toggleAddForm();
    },
    editSupplier(supplier) {
      this.selectedSupplier = supplier;
      this.toggleEditForm();
    },
    saveSupplier(updatedSupplier) {
      const index = this.suppliers.findIndex(supplier => supplier.id === updatedSupplier.id);
      if (index !== -1) {
        this.suppliers[index] = updatedSupplier; 
        this.filterSuppliers(); 
      }
      this.toggleEditForm();
    },
    confirmDelete(supplierID) {
      this.selectedSupplierID = supplierID;
      this.showConfirmModal = true;
    },
    cancelSubmit() {
      this.showConfirmModal = false;
      this.selectedSupplierID = null;
    },
    confirmSubmit() {
      this.showConfirmModal = false;
      this.removeSupplier(this.selectedSupplierID);
    },
    async removeSupplier(supplierId) {
      try {
        await axios.delete(`${SUPPLIERS_API}/suppliers/${supplierId}`);
        this.fetchSuppliers();
        this.toast.success('Supplier deleted successfully!');
      } catch (error) {
        console.error("Error deleting supplier:", error);
        this.toast.error('Error deleting supplier.');
      }
    },
    closeForm() {
      this.selectedSupplier = null; 
      this.toggleEditForm(); 
    }
  },
  created() {
    this.fetchSuppliers();
  },
  watch: {
    searchTerm: 'filterSuppliers',
    selectedStatus: 'filterSuppliers'
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



.inventory-container {
  position: relative;
  flex-grow: 1;
  height: 37dvw;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);

  background-color: #ffffff;
  border-radius: 15px;
  overflow-y: auto;
  margin-left: 5px;
  padding: 0;
}

.supplier-table {
  width: 100%;
  border-collapse: collapse;
}

.supplier-table th,
.supplier-table td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #ddd;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.supplier-table tbody {
  font-size: 15px;
}

.supplier-table th {
  background-color: #f4f4f4;
  padding: 13px;
  color: #333;
  font-weight: bold;
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
  background-color: #D9D9D9;
}

.filter-btn {
  padding: 8px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 19px;
  color: #333;
  transition: color 0.3s;
}

.filter-container {
  position: relative;
}

.dropdown {
  position: absolute;
  top: 35px;
  left: 0;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  padding: 10px;
  z-index: 10;
  width: 8dvw;
}

.filter-select {
  padding: 8px;
  font-size: 14px;
  border-radius: 5px;
  width: 100%;
  margin-bottom: 10px;
}

.add-product-btn {
  padding: 8px 12px;
  background-color: #E54F70;
  color: #dbdbdb;
  border: none;
  border-radius: 10px;
  width: 70px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
}

.add-product-btn:hover {
  background-color: #ed9598;
}

.action-btn {
  padding: 8px;
  background-color: transparent;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
  margin-right: 10px;
  width: 35px;
  height: 35px;
  align-items: center;
  justify-content: center;
}

.action-btn.edit {
  color: #1976d2;
}

.action-btn.delete {
  color: #dc3545;
}

.action-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.action-btn:active {
  background-color: rgba(0, 0, 0, 0.2);
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
