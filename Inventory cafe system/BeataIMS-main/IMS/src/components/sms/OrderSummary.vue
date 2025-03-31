<template>
  <div class="order-summary">
    <h2>Order Summary</h2>
    <div v-if="items.length > 0" class="summary-items">
      <ul>
        <li v-for="(item, index) in items" :key="index">
          <div class="item-details">
            <span>{{ item.quantity }}x {{ item.name }}</span>
            <span class="item-price">₱{{ getItemPrice(item) }}</span>
          </div>
          <div class="item-controls">
            <button @click="decreaseQuantity(item)" :disabled="item.quantity <= 1">-</button>
            <button @click="increaseQuantity(item)">+</button>
            <button @click="removeItem(index)" class="remove-btn">Remove</button> <!-- Remove Button -->
          </div>
        </li>
      </ul>
    </div>
    <div v-else class="empty-message">No items selected</div>
    <div class="summary-totals">
      <p><strong>Total Items:</strong> {{ totalItems }}</p>
      <p><strong>Total Amount:</strong> ₱{{ totalAmount.toFixed(2) }}</p>
    </div>
    <p><strong>Payment Method:</strong> {{ paymentMethod }}</p>
  </div>
</template>

<script>
export default {
  name: 'OrderSummary',
  props: {
    items: {
      type: Array,
      required: true,
      default: () => []
    },
    paymentMethod: {
      type: String,
      required: true,
      default: 'Cash'
    },
    totalAmount: {
      type: Number,
      required: true,
      default: 0
    }
  },
  computed: {
    totalItems() {
      return this.items.reduce((sum, item) => sum + (item.quantity || 0), 0);
    }
  },
  methods: {
    getItemPrice(item) {
      return (item.quantity * (item.price || 0)).toFixed(2);
    },
    increaseQuantity(item) {
      item.quantity += 1;
      this.$emit('update-items', this.items);
    },
    decreaseQuantity(item) {
      if (item.quantity > 1) {
        item.quantity -= 1;
        this.$emit('update-items', this.items);
      }
    },
    removeItem(index) {
      this.items.splice(index, 1); // Remove the item from the list
      this.$emit('update-items', this.items); // Update the parent component
    }
  }
};
</script>

<style scoped>
.order-summary {
  margin-top: 30px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-items {
  margin-bottom: 20px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.5em;
}

.summary-items ul {
  list-style: none;
  padding: 0;
}

.summary-items li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.empty-message {
  color: #666;
  font-style: italic;
  padding: 10px 0;
}

.item-details {
  display: grid;
  justify-content: space-between;
  align-items: center;
}

.item-price {
  color: #E54F70;
  font-weight: bold;
}

.item-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.item-controls button {
  padding: 5px 10px;
  background-color: #E54F70;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.item-controls button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.remove-btn {
  background-color: #FF4D4D;
  padding: 5px 10px;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.remove-btn:hover {
  background-color: #E53935;
}

.summary-totals {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  padding: 10px 0;
}

.payment-method {
  margin-top: 20px;
  font-weight: bold;
  color: #333;
}
</style>
