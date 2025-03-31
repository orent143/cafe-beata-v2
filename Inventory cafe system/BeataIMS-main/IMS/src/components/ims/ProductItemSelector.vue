<!-- ProductItemSelector.vue -->
<template>
    <div class="product-item-selector">
      <h2>Raw Materials / Stocks Needed</h2>
      <div class="items-list">
        <div v-for="(item, index) in items" :key="index" class="item-row">
          <div class="form-group">
            <select v-model="item.stockId" class="form-input" @change="updateItem(index)">
              <option value="">Select Stock Item</option>
              <option v-for="stock in stockItems" 
                      :key="stock.id" 
                      :value="stock.id">
                {{ stock.name }} (Available: {{ stock.quantity }})
              </option>
            </select>
          </div>
          
          <div class="form-group quantity">
            <input 
              type="number" 
              v-model.number="item.quantity" 
              min="1" 
              class="form-input"
              @input="updateItem(index)"
            />
          </div>
          
          <button @click="removeItem(index)" class="remove-btn" 
                  v-if="items.length > 1">×</button>
        </div>
      </div>
      
      <button @click="addNewItem" class="add-btn">+ Add Raw Material</button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ProductItemSelector',
    props: {
      items: {
        type: Array,
        required: true
      },
      stockItems: {
        type: Array,
        required: true
      }
    },
    methods: {
      addNewItem() {
        this.$emit('update:items', [...this.items, { stockId: '', quantity: 1 }])
      },
      removeItem(index) {
        const newItems = this.items.filter((_, i) => i !== index)
        this.$emit('update:items', newItems)
      },
      updateItem(index) {
        this.$emit('update:items', [...this.items])
      }
    }
  }
  </script>
  
  <style scoped>
  .product-item-selector {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .items-list {
    margin-bottom: 20px;
  }
  
  .item-row {
    display: grid;
    grid-template-columns: 3fr 1fr auto;
    gap: 10px;
    margin-bottom: 10px;
    align-items: center;
  }
  
  .form-group {
    margin: 0;
  }
  
  .quantity {
    width: 100px;
  }
  
  .remove-btn {
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
  }
  
  .add-btn {
    background: #E54F70;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
  }
  
  button:hover {
    background-color: #a33950;
  }
  </style>
  