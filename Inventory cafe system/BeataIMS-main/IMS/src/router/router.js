import { createRouter, createWebHistory } from 'vue-router';
import { authGuard } from '@/auth/authGuard';

//ims
import HomeIMS from '@/views/ims/HomeIMS.vue';
import Products from '@/views/ims/Products.vue';
import ViewInventoryVue from '@/views/ims/ViewInventory.vue';
import ViewDetailsVue from '@/views/ims/ViewDetails.vue';
import Suppliers from '@/views/ims/Suppliers.vue';
import CreateOrder from '@/views/ims/CreateOrder.vue';
import ReportsIMS from '@/views/ims/ReportsIMS.vue';
import Category from '@/views/ims/Category.vue';
import CreateProductVue from '@/views/ims/CreateProduct.vue';
import ProductSales from '@/views/ims/Sales.vue';
import StockVue from '@/views/ims/Stock.vue';
import OrdersHistory from '@/views/ims/OrderHistory.vue';
import SummaryReport from '@/views/ims/reports/SummaryReport.vue';
import LowStockReport from '@/views/ims/reports/LowStockReport.vue';
import DailySalesReport from '@/views/ims/reports/DailySalesReport.vue';
import OrderDetailsVue from '@/views/ims/OrderDetails.vue';

//admin
import Dashboard from '@/views/admin/Dashboard.vue';
import Users from '@/views/admin/Users.vue';

import Welcome from '@/views/Welcome.vue'; 
import Login from '@/views/Login.vue'; 
import Profile from '@/views/Profile.vue';

const routes = [
  { path: '/', component: Welcome, meta: { public: true } }, 
  { path: '/login', component: Login, meta: { public: true } }, 
  { path: '/profile', component: Profile }, 
  { path: '/homeims', component: HomeIMS, meta: { requiresAuth: true } },
  { path: '/products', component: Products, meta: { requiresAuth: true } },
  { path: '/viewinventory', component: ViewInventoryVue, meta: { requiresAuth: true } },
  { path: '/viewdetails/:id', name: 'ViewDetailsVue', component: ViewDetailsVue, meta: { requiresAuth: true } },
  { path: '/stocks', component: StockVue, meta: { requiresAuth: true } },
  { path: '/create', component: CreateProductVue, meta: { requiresAuth: true } },
  { path: '/productsales', component: ProductSales, meta: { requiresAuth: true } },
  { path: '/suppliers', component: Suppliers, meta: { requiresAuth: true } },
  { path: '/vieworderdetails/:id', name: 'ViewOrderDetails', component: OrderDetailsVue, meta: { requiresAuth: true } },
  { path: '/category', component: Category, meta: { requiresAuth: true } },
  { path: '/reportsims', component: ReportsIMS, meta: { requiresAuth: true } },
  { path: '/reportsims/summary', component: SummaryReport, meta: { requiresAuth: true } },
  { path: '/reportsims/lowStock', component: LowStockReport, meta: { requiresAuth: true } },
  { path: '/reportsims/dailySales', component: DailySalesReport, meta: { requiresAuth: true } },
  { path: '/createorder', component: CreateOrder, meta: { requiresAuth: true } },
  { path: '/ordershistory', component: OrdersHistory, meta: { requiresAuth: true } },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true, adminOnly: true } },
  { path: '/users', component: Users, meta: { requiresAuth: true, adminOnly: true } }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard
router.beforeEach(authGuard);

export default router;