<template>
  <div class="items">
    <!-- Hot Chocolate Drinks -->
    <div class="item" v-for="item in hotChocolateDrinks" :key="item.name" @click="goToConfirmOrder(item)">
      <img :src="require(`@/assets/${item.image}`)" :alt="item.name" />
      <span>{{ item.name }}</span>
    </div>

    <!-- Iced Chocolate Drinks -->
    <div class="item" v-for="item in icedChocolateDrinks" :key="item.name" @click="goToConfirmOrder(item)">
      <img :src="require(`@/assets/${item.image}`)" :alt="item.name" />
      <span>{{ item.name }}</span>
    </div>
  </div>
</template>

<script>
export default {
  props: ['chocolateDrinks'],
  computed: {
    hotChocolateDrinks() {
      return this.chocolateDrinks.filter(item => /hot|warm|steamed/i.test(item.name));
    },
    icedChocolateDrinks() {
      return this.chocolateDrinks.filter(item => /cold|iced|frozen/i.test(item.name));
    }
  },
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
/* Styling for Chocolate Drinks component */
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
