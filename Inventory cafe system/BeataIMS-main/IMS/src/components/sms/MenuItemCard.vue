<template>
  <div class="menu-item-card" :class="{ 'to-be-made': isToBeMade }">
    <div class="item-image-container">
      <img 
        :src="imageSrc" 
        :alt="item.name" 
        class="menu-image" 
      />
    </div>

    <div class="item-details">
      <h3>{{ item.name }}</h3>
      <p class="price">₱{{ formattedPrice }}</p>

      <p class="stock" 
         :class="{ 'low-stock': !isToBeMade && item.stock <= 5, 'to-be-made-tag': isToBeMade }">
        {{ isToBeMade ? 'To Be Made (∞)' : `Stock: ${item.stock}` }}
      </p>

      <div class="item-controls">
        <button 
          class="add-btn"
          @click="emitAdd"
          :class="{ 
            'selected': selected,
            'to-be-made-btn': isToBeMade 
          }"
          :disabled="shouldDisableButton"
        >
          {{ selected ? 'Added' : 'Add' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { getImageUrl } from '@/api/config.js';

export default {
  name: 'MenuItemCard',
  props: {
    item: Object,
    selected: Boolean
  },
  computed: {
    isToBeMade() {
      return this.item.process_type === 'To Be Made';
    },
    formattedPrice() {
      return `${Number(this.item.price || 0).toFixed(2)}`;
    },
    shouldDisableButton() {
      return !this.isToBeMade && this.item.stock <= 0;
    },
    // Computed property for image source with fallback to placeholder
    imageSrc() {
      if (this.item.image) {
        // If the image is already a full URL (from backend API), use it directly
        return this.item.image;
      } else {
        // If no image, use a placeholder
        return '/placeholder-product.jpg';
      }
    }
  },
  methods: {
    emitAdd() {
      this.$emit('add', { 
        ...this.item, 
        price: Number(this.item.price)
      });
    }
  }
};
</script>

<style scoped>
.menu-item-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.item-image-container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.menu-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ddd;
  transition: transform 0.3s ease;
}

.menu-image:hover {
  transform: scale(1.05);
}

.item-details {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

h3 {
  margin: 0;
  color: #333;
  font-size: 1.2em;
  text-align: center;
}

.price {
  color: #E54F70;
  font-weight: bold;
  font-size: 1.1em;
  margin: 8px 0;
  text-align: center;
}

.stock {
  text-align: center;
  margin: 5px 0;
}

.low-stock {
  color: red;
  font-weight: bold;
}

.item-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
  width: 100%;
}

.quantity-input {
  width: 60px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
}

.add-btn {
  padding: 8px 15px;
  background-color: #E54F70;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: 0.3s;
  min-width: 80px;
}

.add-btn.selected {
  background-color: #e67e22;
}

.add-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.menu-item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.to-be-made .quantity-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(23, 162, 184, 0.2);
}

.to-be-made .add-btn {
  background-color: #E54F70;
  opacity: 1 !important;
  cursor: pointer !important;
}

.to-be-made .add-btn:hover {
  background-color: #138496;
}

.to-be-made .quantity-input:disabled {
  opacity: 1;
  background-color: #f8fdff;
  cursor: text;
}
</style>
