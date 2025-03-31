import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from './components/LoginPage.vue';
import DashboardPage from './components/DashboardPage.vue';
import ConfirmOrder from './components/ConfirmOrder.vue'; // Import the ConfirmOrder component
import OrderIDPage from './components/OrderIDPage.vue'; // Import the OrderIDPage component
import OrderHistory from './components/OrderHistory.vue'; // Import OrderHistory component
import OrderDetails from './components/OrderDetails.vue'; // Import OrderDetails component
import UserProfileCafe from './components/UserProfileCafe.vue'; // Import the renamed UserProfileCafe component
import CreateAccountPage from './components/CreateAccountPage.vue'; 
import ForgotPassword from '@/components/ForgotPassword.vue'; // Make sure the path is correct
import PrivacyAndPolicy from './components/PrivacyAndPolicy.vue'; // Import PrivacyAndPolicy component
import AdminPage from './admin/AdminPage.vue'; 
import NotificationsPage from './admin/NotificationsPage.vue';
import ChangePassword from './components/ChangePassword.vue';
import OrderRecord from './components/OrderRecord.vue';  // Ensure this is correctly imported
import UserNotifications from './components/UserNotifications.vue';
import CafeBeata from './components/CafeBeata.vue';

const routes = [

  {
    path: '/cafe-beata',
    name: 'CafeBeata',
    component: CafeBeata,
  },



  {
    path: '/user-notifications',
    name: 'UserNotifications',
    component: UserNotifications,
  },
  
  {
    path: '/',
    redirect: '/cafe-beata',  // Set this to redirect to login as default
  },

  {
    path: '/order-record',
    name: 'OrderRecord',
    component: OrderRecord,
  },

  {
    path: '/reset-password/:token',
    name: 'reset-password',
    component: ChangePassword,
  },

  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },

  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
  },

  {
    path: '/notifications', 
    name: 'Notifications',
    component: NotificationsPage, 
  },

  {
    path: '/admin', 
    name: 'AdminPage',
    component: AdminPage,
  },

  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    beforeEnter: (to, from, next) => {
      if (localStorage.getItem('loggedIn') === 'true') {
        next();
      } else {
        next({ name: 'Login' });
      }
    },
  },
  {
    path: '/confirm-order', 
    name: 'ConfirmOrder',
    component: ConfirmOrder,
    props: route => ({
      name: route.query.name,   
      price: route.query.price,
      image: route.query.image, 
    }),
  },
  {
    path: '/order-id',
    name: 'OrderIDPage',
    component: OrderIDPage,
    props: true,
  },
  {
    path: '/create-account',  
    name: 'CreateAccount',
    component: CreateAccountPage,
  },

  {
    path: '/order-history',
    name: 'OrderHistory',
    component: OrderHistory,
  },

  {
    path: '/order-details',
    name: 'OrderDetails',
    component: OrderDetails,
    props: route => ({
      orderId: route.query.orderId,
      date: route.query.date,
      billName: route.query.billName,
      total: route.query.total,
      items: JSON.parse(route.query.items || '[]'),
    }),
  },

  {
    path: '/user-profile-cafe', 
    name: 'UserProfileCafe',
    component: UserProfileCafe,  
  },

  {
    path: '/privacy-policy', 
    name: 'PrivacyPolicy',
    component: PrivacyAndPolicy,
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
