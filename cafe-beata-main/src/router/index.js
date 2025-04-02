import { createRouter, createWebHistory } from 'vue-router';
import DashboardPage from '@/components/DashboardPage.vue';
import LoginPage from '@/components/LoginPage.vue';
import CreateAccountPage from '@/components/CreateAccountPage.vue';
import ConfirmOrder from '@/components/ConfirmOrder.vue';
import OrderIDPage from '@/components/OrderIDPage.vue';
import OrderDetails from '@/components/OrderDetails.vue';
import OrderHistory from '@/components/OrderHistory.vue';
import UserNotifications from '@/components/UserNotifications.vue';
import ChangePassword from '@/components/ChangePassword.vue';
import ForgotPassword from '@/components/ForgotPassword.vue';
import UserProfileCafe from '@/components/UserProfileCafe.vue';
import NotificationsPage from '@/components/NotificationsPage.vue';
import PrivacyAndPolicy from '@/components/PrivacyAndPolicy.vue';

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardPage
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/create-account',
    name: 'CreateAccount',
    component: CreateAccountPage
  },
  {
    path: '/confirm-order',
    name: 'ConfirmOrder',
    component: ConfirmOrder
  },
  {
    path: '/order-id',
    name: 'OrderID',
    component: OrderIDPage
  },
  {
    path: '/order-details',
    name: 'OrderDetails',
    component: OrderDetails
  },
  {
    path: '/order-history',
    name: 'OrderHistory',
    component: OrderHistory
  },
  // Removing dedicated page route for UserNotifications since it's now integrated in the dashboard
  // {
  //   path: '/user-notifications',
  //   name: 'UserNotifications',
  //   component: UserNotifications
  // },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: ChangePassword
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword
  },
  {
    path: '/user-profile',
    name: 'UserProfile',
    component: UserProfileCafe
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: NotificationsPage
  },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: PrivacyAndPolicy
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router; 