<template>
  <Header />
  <SideBar />
  <div class="app-container">
    <div class="header-container">
      <button class="back-btn" @click="$router.go(-1)">Back</button>
      <div class="header-separator">
      <div class="title-section">
        <h1 class="products-header">{{ categoryName }}</h1>
        <span class="date-display">{{ date }}</span>
      </div>
      <button class="export-btn" @click="exportCategoryReport">
        <i class="pi pi-download"></i> Export CSV
      </button>
    </div>
    </div>

    <div class="inventory-container">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading category details...</p>
      </div>
      
      <div v-else-if="products.length === 0" class="no-data-container">
        <p>No products found for this category.</p>
      </div>
      
      <div v-else>
        <div class="table-container">
          <table class="stock-table">
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Original Quantity</th>
                <th>Unit Price</th>
                <th>Quantity Sold</th>
                <th>Total Amount</th>
                
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in products" :key="product.product_id">
                <td>{{ product.product_name }}</td>
                <td>{{ product.beginning_quantity }}</td>
                <td>₱{{ parseFloat(product.unit_price).toFixed(2) }}</td>
                <td>{{ product.quantity_sold }}</td>
                <td>₱{{ parseFloat(product.total_amount).toFixed(2) }}</td>
                
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="totals-container">
        <div class="totals-item">
          <span>Total Items Sold:</span>
          <span>{{ totalItems }}</span>
        </div>
        <div class="totals-item">
          <span>Total Sales:</span>
          <span>₱{{ parseFloat(totalAmount).toFixed(2) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SideBar from "@/components/ims/SideBar.vue";
import Header from "@/components/Header.vue";
import { SALES_API } from "@/api/config.js";

export default {
  components: {
    SideBar,
    Header,
  },
  data() {
    return {
      categoryName: this.$route.params.categoryName,
      date: this.$route.params.date,
      products: [],
      totalItems: 0,
      totalAmount: 0,
      loading: false,
      fallbackImage: "https://via.placeholder.com/100",
    };
  },
  methods: {
    async fetchCategoryDetails() {
      try {
        this.loading = true;
        const response = await axios.get(`${SALES_API}/sales/category-report`, {
          params: { date: this.date },
        });

        const category = response.data.categories.find(
          (cat) => cat.category_name === this.categoryName
        );

        if (category) {
          this.products = category.products;
          this.totalItems = category.total_items;
          this.totalAmount = category.total_amount;
        } else {
          this.products = [];
          this.totalItems = 0;
          this.totalAmount = 0;
        }
      } catch (error) {
        console.error("Error fetching category details:", error);
      } finally {
        this.loading = false;
      }
    },
    exportCategoryReport() {
      if (!this.products.length) {
        this.toast.warning("No data to export");
        return;
      }

      try {
        const headers = ["Product Name", "Quantity Sold", "Total Amount"];
        const data = this.products.map((product) => [
          product.product_name,
          product.quantity_sold,
          parseFloat(product.total_amount).toFixed(2),
        ]);

        const csvContent = [headers.join(","), ...data.map((row) => row.join(","))].join("\n");

        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `category-report-${this.categoryName}-${this.date}.csv`;
        a.click();

        this.toast.success("Report exported successfully");
      } catch (error) {
        console.error("Error exporting report:", error);
        this.toast.error("Failed to export report");
      }
    },
  },
  created() {
    this.fetchCategoryDetails();
  },
};
</script>
  <style scoped>
  .app-container {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    margin-left: 230px;
    height: 100%;
  }
  
  .header-container {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-left: 18px;
    width: 95%;
  }
  .title-section {
  display: flex;
  flex-direction: column;
  margin-bottom: 5px;
}
.products-header {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
  margin-bottom: 0; /* <-- Add this */
}
  .date-display {
  font-size: 14px;
  color: #6c757d;
}

.export-btn {
  background-color: #E54F70;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
  .back-btn {
    padding: 10px 20px;
  background: white;
  border: 2px solid #E54F70;
  border-radius: 8px;
  color: #E54F70;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
  }
  
  .back-btn:hover {
    background: #E54F70;
  color: white;
  transform: translateX(-5px);
  }
  
  .header-separator {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }
  .inventory-container {
    position: relative;
    height: 37dvw;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    background-color: #ffffff;
    border-radius: 15px;
    overflow-y: auto;
    margin-left: 5px;
  }
  
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 200px;
  }
  
  .loading-spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #E54F70;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin-bottom: 10px;
  }
  
  .no-data-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
    font-size: 18px;
    color: #666;
  }
  
  .stock-table {
  width: 100%;
  border-collapse: collapse;
}

.stock-table th,
.stock-table td {
  padding: 15px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.stock-table tbody {
  font-size: 15px;
}

.stock-table th {
  background-color: #f4f4f4;
  padding: 15px;
  color: #343a40;
  font-weight: bold;
}
.stock-table td {
    color: #333;
    padding: 15px;
    font-weight: 500;
}

.table-container {
  flex-grow: 1;
  overflow-y: auto;
  border-radius: 15px;
}
  
  .product-image {
    width: 50px;
    height: 50px;
    object-fit: cover;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
  }
  .totals-container {
  display: flex;
  justify-content: space-between;
  padding: 18px 25px;
  background-color: #f8f9fa;
  margin-top: auto; 
  border-bottom-right-radius: 15px;
  border-bottom-left-radius: 15px;
  position: sticky;
  bottom: 0;
  box-shadow: 0 -3px 10px rgba(0, 0, 0, 0.05);
  border-top: 1px solid #e9ecef;
}

.totals-item {
  width: 30%;
  font-weight: 600;
  color: #343a40;
  font-size: 15px;
}


.totals-item span {
  font-weight: bold;
  margin-right: 5px;
}
  .product-image:hover {
    transform: scale(1.1);
  }
  
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
  </style>