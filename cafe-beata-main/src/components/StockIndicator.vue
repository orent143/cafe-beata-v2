<template>
  <div class="stock-indicator" :class="{ 'out-of-stock': isOutOfStock }">
    <div v-if="isOutOfStock" class="out-of-stock-overlay">
      Unavailable
    </div>
    <span v-else-if="isLowStock" class="stock-status low-stock">
      Low Stock
    </span>
  </div>
</template>

<script>
export default {
  name: 'StockIndicator',
  props: {
    itemId: {
      type: Number,
      required: true
    },
    quantity: {
      type: Number,
      required: true
    },
    minStockLevel: {
      type: Number,
      default: 10
    }
  },
  computed: {
    isOutOfStock() {
      return this.quantity === 0;
    },
    isLowStock() {
      return !this.isOutOfStock && this.quantity <= this.minStockLevel;
    }
  }
};
</script>

<style scoped>
.stock-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

.stock-status {
  position: absolute;
  top: 10px;
  right: 10px;
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  background-color: rgba(255, 255, 255, 0.9);
}

.low-stock {
  color: #ff9800;
  border: 1px solid #ff9800;
}

.out-of-stock-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-25deg);
  font-size: 1.8rem;
  font-weight: 900;
  color: rgba(217, 30, 24, 0.85);
  text-transform: uppercase;
  white-space: nowrap;
  letter-spacing: 1px;
  border: 3px solid rgba(217, 30, 24, 0.85);
  border-radius: 8px;
  padding: 4px 12px;
  
  /* Create the rubber stamp effect */
  background-color: transparent;
  text-shadow: 
    -1px -1px 0 rgba(255,255,255,0.3),
    1px -1px 0 rgba(255,255,255,0.3),
    -1px 1px 0 rgba(255,255,255,0.3),
    1px 1px 0 rgba(255,255,255,0.3);
  box-shadow: 
    inset 0 0 10px rgba(0,0,0,0.2),
    0 0 8px rgba(0,0,0,0.1);
  z-index: 10;
  
  /* Add distressed texture effect */
  -webkit-mask-image: url('data:image/svg+xml;utf8,<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><filter id="noiseFilter"><feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1 0"/></filter><rect width="100%" height="100%" filter="url(%23noiseFilter)"/></svg>');
  mask-image: url('data:image/svg+xml;utf8,<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><filter id="noiseFilter"><feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1 0"/></filter><rect width="100%" height="100%" filter="url(%23noiseFilter)"/></svg>');
  opacity: 0.95;
}
</style> 