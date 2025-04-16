<template>
  <div id="app">
    <router-view />  
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'; 
import { onMounted, onUnmounted } from 'vue';
import { getUser, isSessionExpired, logout } from '@/auth/authGuard';
import sessionService from '@/api/sessionService';

const router = useRouter();

// Handle session expiration
const handleSessionExpiration = () => {
  // Show a message and redirect to login
  console.log('Session expired or user inactive');
  logout(router);
};

onMounted(() => {
  // Check if the user is already authenticated
  const user = getUser();
  if (user) {
    // Check if the session is expired
    if (isSessionExpired()) {
      // Session expired, clear storage and redirect to login
      logout(router);
    } else {
      // Start session monitoring
      sessionService.startSessionMonitor(handleSessionExpiration);
      
      // Session valid, redirect to appropriate dashboard if on root page
      if (router.currentRoute.value.path === '/') {
        if (user.role === 'admin') {
          router.push('/dashboard');
        } else {
          router.push('/homeims');
        }
      }
    }
  } else {
    // Not authenticated, redirect to welcome page if not already on login
    if (router.currentRoute.value.path !== '/login' &&
        router.currentRoute.value.path !== '/') {
      router.push('/');
    }
  }
});

onUnmounted(() => {
  // Stop session monitoring when app is unmounted
  sessionService.stopSessionMonitor();
});
</script>

<style scoped>
/* Global styles */
:root {
  --primary-color: #E54F70;
  --secondary-color: #ed9598;
  --accent-color: #e74c3c;
  --background-color: #f5f5f5;
  --text-color: #333;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Poppins', sans-serif;
  color: var(--text-color);
  background-color: var(--background-color);
}

#app {
  height: 100vh;
  width: 100%;
}
</style>
