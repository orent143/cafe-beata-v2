<template>
  <div class="items">
    <!-- Blended Frappes -->
    <div class="item" v-for="item in blendedFrappes" :key="item.name" @click="goToConfirmOrder(item)">
      <img :src="require(`@/assets/${item.image}`)" :alt="item.name" />
      <span>{{ item.name }}</span>
    </div>
  </div>
</template>

<script>
export default {
  props: ['blendedFrappes'],
  methods: {
    goToConfirmOrder(item) {
      // Redirect to ConfirmOrder page with item details as query parameters
      this.$router.push({
        name: "ConfirmOrder",
        query: {
          name: item.name,
          price: item.price,
          image: item.image,
        },
      });
    },
  },
};
</script>

<style scoped>
/* Styling for Blended Frappes component */
.items {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 18px;
}

.item {
  text-align: center;
  background-color: #f8d2e4;
  border-radius: 50%;
  padding: 20px;
  transition: transform 0.3s ease;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 200px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

.item img {
  width: 120px;
  height: 120px;
  object-fit: contain;
}

.item:hover img {
  transform: scale(1.1);
}

.item span {
  font-weight: bold;
  color: #333;
  font-size: 14px;
  text-align: center;
  display: block;
  line-height: 1.3;
  margin-top: 10px;
}
</style>
