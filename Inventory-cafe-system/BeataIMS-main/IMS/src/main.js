import { createApp } from 'vue';
import App from './App.vue';
import router from './router/router';
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import './assets/styles.css';
import 'primeicons/primeicons.css';

const app = createApp(App);

app.use(router);
app.use(Toast); // Add Toastification

app.mount('#app');
