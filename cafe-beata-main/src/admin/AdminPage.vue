<template>
  <div class="admin-page">
    <div class="admin-container">
      <!-- Back Button inside the container -->
      <button @click="goBack" class="back-button">
        ←
      </button>

      <div class="logo-container">
        <img src="@/assets/uic-logo.png" alt="University Logo" class="logo" />
      </div>
      <h1 class="title">Admin Login</h1>
      <form @submit.prevent="handleAdminLogin" class="login-form">
        <div class="input-container">
          <label for="admin-password"></label>
          <input 
            type="password" 
            v-model="adminPassword" 
            id="admin-password" 
            placeholder="Enter Admin Password" 
            required
          />
        </div>
        <button type="submit" class="admin-button">Login as Admin</button>
        <p v-if="adminErrorMessage" class="error">{{ adminErrorMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminPage",
  data() {
    return {
      adminPassword: "",
      adminErrorMessage: "",
    };
  },
  methods: {
    handleAdminLogin() {
      const adminPassword = "admin123"; // Replace this with a secure method to fetch the admin password

      if (this.adminPassword === adminPassword) {
        localStorage.setItem("loggedIn", "true");
        localStorage.setItem("isAdmin", "true"); // Store a flag for admin access
        this.$router.push({ name: "Notifications" }); // Redirect to the Notifications page
      } else {
        this.adminErrorMessage = "Incorrect admin password!";
      }
    },

    // Go back to the login page
    goBack() {
      this.$router.push({ name: "Login" }); // Redirect back to LoginPage
    }
  },
};
</script>

<style scoped>
/* Admin Login Page Styles */
.admin-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; /* Full viewport height */
  background-image: url("@/assets/Uicbackround.png"); /* Background image path */
  background-size: cover;
  background-position: center;
}

.admin-container {
  background: rgba(255, 255, 255, 0.9); /* Similar to login container */
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for the container */
}

.back-button {
  align-self: flex-start; /* Align it to the top-left inside the container */
  background: none;
  border: none;
  font-size: 24px;
  color: #d12f7a;
  cursor: pointer;
  transition: color 0.3s ease;
  margin-bottom: 20px; /* Space between the button and other content */
}

.back-button:hover {
  color: #b82d67; /* Slightly darker color on hover */
}

.logo-container {
  margin-bottom: 20px;
}

.logo {
  width: 60%;
  max-width: 220px;
  height: auto;
}

.title {
  font-family: "Arial", sans-serif;
  color: #d12f7a;
  font-size: 24px;
  margin-bottom: 15px;
  font-weight: bold;
  text-shadow: 0 0 8px rgba(255, 105, 180, 0.6);
}

.input-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 15px;
}

input {
  width: 120%;
  max-width: 320px;
  padding: 12px;
  margin-top: 5px;
  border: 2px solid #ff1493;
  border-radius: 8px;
  text-align: center;
  font-size: 16px;
  transition: all 0.3s ease;
}

input:focus {
  outline: none;
  border-color: #ff1493;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.8);
}

.admin-button {
  margin-top: 20px;
  background-color: #d12f7a;
  color: white;
  padding: 12px 20px;
  border-radius: 10px;
  cursor: pointer;
  width: 100%;
  max-width: 320px;
}

.admin-button:hover {
  background-color: #b82d67;
}

.error {
  color: red;
  font-size: 14px;
  margin-top: 10px;
}

/* Glowing effect for the Login Button */
.admin-button {
  background: linear-gradient(135deg, #ff1493, #ff69b4);
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.8);
}

.admin-button:hover {
  background: linear-gradient(135deg, #d63384, #ff1493);
  box-shadow: 0 0 20px rgba(255, 20, 147, 1);
}
</style>
