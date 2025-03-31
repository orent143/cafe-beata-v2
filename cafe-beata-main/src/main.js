import { createApp } from 'vue';
import App from './App.vue';
import router from './router';  // Import router.js

// Import Font Awesome CSS
import '@fortawesome/fontawesome-free/css/all.css';
import '@fortawesome/fontawesome-free/css/fontawesome.css';

const app = createApp(App);

app.use(router);  // Make sure the router is used
app.mount('#app');
