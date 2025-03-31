<template>
  <!-- No changes to template section -->
</template>

<script>
export default {
  data() {
    return {
      stockItems: [],
      stockSearchQuery: '',
      selectedCategory: '',
    };
  },
  computed: {
    filteredStockItems() {
      return this.stockItems.filter(item => {
        const itemName = (item.name || '').toLowerCase();
        const searchQuery = (this.stockSearchQuery || '').toLowerCase();
        const itemCategory = item.category || '';
        
        const matchesSearch = itemName.includes(searchQuery);
        const matchesCategory = !this.selectedCategory || itemCategory === this.selectedCategory;
        
        return matchesSearch && matchesCategory;
      });
    }
  },
  methods: {
    // No changes to methods section
  }
};
</script>

<style>
  /* No changes to style section */
</style> 