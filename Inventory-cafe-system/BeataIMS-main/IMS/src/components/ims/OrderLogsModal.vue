<template>
    <div v-if="isVisible" class="modal-overlay">
      <div class="transaction-log-modal">
        <div class="modal-header">
          <h2>Order Transaction Logs</h2>
          <button @click="$emit('close')" class="close-btn">
            <i class="pi pi-times"></i>
          </button>
        </div>
        <div class="transaction-log-content">
          <table class="transaction-table">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Order ID</th>
                <th>Action</th>
                <th>Performed By</th>
                <th>Date</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.log_id">
                <td>{{ log.log_id }}</td>
                <td>{{ log.history_id }}</td>
                <td>{{ log.action_type }}</td>
                <td>{{ log.performed_by }}</td>
                <td>{{ formatDate(log.performed_at) }}</td>
                <td>{{ log.remarks }}</td>
              </tr>
              <tr v-if="logs.length === 0">
                <td colspan="6" class="text-center">No logs available</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { ORDER_SUMMARY_API } from '@/api/config.js';
  import { getAuthHeader } from '@/api/config.js';
  
  export default {
    name: 'OrderLogsModal',
    props: {
      isVisible: Boolean,
      logs: Array
    },
    data() {
      return {
      };
    },
    watch: {
  isVisible(newVal) {
    if (newVal) {
      console.log("Modal is visible, fetching logs...");
      this.fetchLogs();
    }
  }
},
    methods: {
        async fetchLogs() {
  try {
    const response = await axios.get(`${ORDER_SUMMARY_API}/orders/history-logs`, {
      headers: getAuthHeader() // Include the authorization header
    });
    console.log('Fetched logs:', response.data); // Check the response
    this.logs = response.data; 
  } catch (error) {
    console.error('Failed to fetch order logs:', error);
    this.toast.error('Failed to load logs. Please try again.');
    this.logs = [];
  }
},
      formatDate(dateString) {
        return new Date(dateString).toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
    }
  };
  </script>

  <style scoped>
  /* Same modal styles from inventory modal */
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
  </style>
  