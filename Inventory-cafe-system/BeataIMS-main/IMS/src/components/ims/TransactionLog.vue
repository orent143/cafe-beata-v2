<template> 
  <div v-if="isVisible" class="modal-overlay">
    <div class="transaction-log-modal">
      <div class="modal-header">
        <h2>Transaction History</h2>
        <button @click="$emit('close')" class="close-btn">
          <i class="pi pi-times"></i>
        </button>
      </div>
      <div class="transaction-log-content">
        <table class="transaction-table">
          <thead>
            <tr>
              <th>Product Name</th>
              <th>Transaction Type</th>
              <th>Quantity</th>
              <th>Date & Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transaction in transactions" :key="transaction.id">
              <td>{{ transaction.product_name }}</td>
              <td>
                <span :class="'transaction-type ' + transaction.transaction_type.toLowerCase()">
                  {{ transaction.transaction_type }}
                </span>
              </td>
              <td :class="{
                'quantity-added': transaction.quantity > 0, 
                'quantity-removed': transaction.quantity < 0
              }">
                {{ transaction.quantity > 0 ? '+' : ''}}{{ transaction.quantity }}
              </td>
              <td>{{ formatDate(transaction.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useToast } from 'vue-toastification';
import { STOCK_API } from '@/api/config.js';

export default {
  name: 'TransactionLog',
  props: {
    isVisible: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      transactions: [],
      toast: useToast()
    };
  },
  methods: {
    async fetchTransactions() {
      try {
        const response = await axios.get(`${STOCK_API}/inventory-transactions`);
        this.transactions = response.data;
      } catch (error) {
        console.error('Error fetching transactions:', error);
        this.toast.error('Failed to load transaction history');
      }
    },
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString();
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-PH', {
        style: 'currency',
        currency: 'PHP',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    }
  },
  watch: {
    isVisible(newValue) {
      if (newValue) {
        this.fetchTransactions();
      }
    }
  }
};
</script>

<style scoped>
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

.transaction-log-modal {
  background: white;
  border-radius: 10px;
  width: 90%;
  max-width: 900px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.modal-header h2 {
  color: #333;
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #E54F70;
}

.transaction-log-content {
  padding: 20px;
}

.transaction-table {
  width: 100%;
  border-collapse: collapse;
}

.transaction-table th,
.transaction-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.transaction-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.transaction-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.transaction-type.add {
  background-color: #E8F5E9;
  color: #4CAF50;
}

.transaction-type.update {
  background-color: #E3F2FD;
  color: #2196F3;
}

.quantity-added {
  color: #4CAF50;
  font-weight: 500;
}

.quantity-removed {
  color: #FF9800;
  font-weight: 500;
}
</style>