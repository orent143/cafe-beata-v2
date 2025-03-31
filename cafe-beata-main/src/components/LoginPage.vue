<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo as Admin Button -->
      <div class="logo-container" @click="redirectToAdminPage" style="cursor: pointer;">
        <img src="@/assets/uic-logo.png" alt="University Logo" class="logo" />
      </div>

      <h1 class="title">UIC Cafe Beàta</h1>
      <form v-if="!isAdminLogin" @submit.prevent="handleLogin" class="login-form">
        <div class="input-container">
          <label for="username"></label>
          <input 
            type="text" 
            v-model="username" 
            id="username" 
            placeholder="UIC Email" 
            required 
          />
        </div>
        <div class="input-container">
          <label for="password"></label>
          <div class="password-container">
            <input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="password" 
              id="password" 
              placeholder="Password" 
              required 
            />
            <button 
              type="button" 
              class="show-password-btn" 
              @click="togglePassword"
              v-show="password.length > 0"
            >
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
        </div>
        <button type="submit" class="login-button">Login</button>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      </form>

      <p class="create-account-link">
        Don't have an account? <router-link to="/create-account">Create one</router-link>
      </p>
      <p class="forgot-password-link">
        <router-link to="/forgot-password">Forgot Password?</router-link>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "LoginPage",
  data() {
    return {
      username: "",
      password: "",
      errorMessage: "",
      showPassword: false,
    };
  },

  created() {
    // Ensure dark mode is not applied on this page
    document.body.classList.remove("dark-mode");
  },


  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    // Handle regular user login
   async handleLogin() {
  const emailRegex = /^[a-zA-Z0-9]+(_\d{12})?@uic\.edu\.ph$/;

  if (!emailRegex.test(this.username)) {
    this.errorMessage = "Invalid UIC Email";
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: this.username, password: this.password }),
    });
    const data = await response.json();
    console.log('Login response:', data);  // Log the response to check if username is included

    if (response.ok) {
      localStorage.setItem("loggedIn", "true");
      localStorage.setItem("userEmail", this.username);

      // Ensure that the correct username is saved
      if (data.username) {
        localStorage.setItem("userName", data.username);  // Save username here
      }

      this.$router.push({ name: "Dashboard" });
    } else {
      this.errorMessage = data.detail || "An error occurred. Please try again.";
    }
  } catch (error) {
    console.error("Error during login:", error);
    this.errorMessage = "An unexpected error occurred. Please try again.";
      }
    },

    // Redirect to AdminPage
    redirectToAdminPage() {
      this.$router.push({ name: "AdminPage" }); // Redirect to AdminPage.vue
    },
  },
};
</script>

<style scoped>
/* Logo as Admin Button Style */
.logo-container {
  cursor: pointer; /* Ensure the logo is clickable */
  margin-top: 20px;
}

.logo {
  width: 60%;
  max-width: 220px;
  height: auto;
  margin-bottom: 20px;
}

.terms-text {
  margin-top: 20px;
  font-size: 14px;
  text-align: center;
}

.terms-link {
  color:#ff1493;
  text-decoration: none;
  font-weight: bold;
}

.terms-link:hover {
  text-decoration: underline;
}

.forgot-password-link {
  margin-top: 15px;
  font-size: 14px;
}

.forgot-password-link a {
  color: #ff1493;
  text-decoration: none;
  font-weight: bold;
}

.forgot-password-link a:hover {
  text-decoration: underline;
  text-shadow: 0 0 5px rgba(255, 20, 147, 0.8);
}

.login-page {
  background-image: url("@/assets/Uicbackround.png"); /* Background image path */
  background-size: cover;
  background-position: center;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px; /* Prevents content from touching screen edges */
}

/* Login Container */
.login-container {
  background: rgba(255, 255, 255, 0.9); /* Slightly more opaque for better contrast */
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); /* Adds subtle shadow */
}

/* Logo */
.logo {
  width: 60%;
  max-width: 220px;
  height: auto;
  margin-bottom: 20px;
}

/* Title */
.title {
  font-family: "Arial", sans-serif;
  color: #d12f7a;
  font-size: 24px;
  margin-bottom: 15px;
  font-weight: bold;
  text-shadow: 0 0 8px rgba(255, 105, 180, 0.6);
}

/* Input Fields */
.input-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 15px;
}

.password-container {
  position: relative;
  width: 120%;
  max-width: 320px;
  display: flex;
  align-items: center;
}

.password-container input {
  width: 100%;
  padding-right: 40px; /* Make space for the button */
  text-align: left;
  padding-left: 12px;
}

.show-password-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  width: auto;
  box-shadow: none;
  color: #888;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 20%;
}

.show-password-btn:hover {
  color: #ff1493;
}

.show-password-btn i {
  font-size: 14px;
}

input {
  width: 110%;
  max-width: 320px;
  padding: 12px;
  margin-top: 5px;
  border: 2px solid #ff1493;
  border-radius: 8px;
  text-align: left;
  padding-left: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
}

/* Glowing effect when focused */
input:focus {
  outline: none;
  border-color: #ff1493; /* Pink border when focused */
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.8); /* Glowing pink effect */
}

/* Button with glowing effect */
button {
  width: 78%;
  background-color: #d12f7a;
  color: white;
  padding: 12px;
  font-size: 16px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s;
  max-width: 320px;
}

button:hover {
  background-color: #b82d67;
}

/* Glowing effect for the "Login" button */
button {
  width: 100%; /* Ensures it aligns with the input fields */
  max-width: 320px;
  background: linear-gradient(135deg, #ff1493, #ff69b4);
  color: white;
  border: none;
  padding: 12px;
  font-size: 16px;
  border-radius: 15px;
  cursor: pointer;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.8);
  transition: all 0.3s ease;
}

button:hover {
  background: linear-gradient(135deg, #d63384, #ff1493);
  box-shadow: 0 0 20px rgba(255, 20, 147, 1);
}

/* Error message */
.error {
  color: red;
  font-size: 14px;
  margin-top: 10px;
}

/* Create Account Link */
.create-account-link {
  margin-top: 20px;
  font-size: 14px;
}

.create-account-link a {
  color: #ff1493;
  text-decoration: none;
  font-weight: bold;
}

.create-account-link a:hover {
  text-decoration: underline;
  text-shadow: 0 0 5px rgba(255, 20, 147, 0.8);
}

/* 📱 Mobile Responsive Adjustments */
@media (max-width: 768px) {
  .logo {
    width: 50%;
    max-width: 180px;
  }

  .title {
    font-size: 22px;
  }

  .login-container {
    width: 85%;
    padding: 20px;
  }

  input {
    font-size: 14px;
  }

  button {
    font-size: 14px;
  }
}

/* Extra Small Screens (iPhone SE, very small phones) */
@media (max-width: 480px) {
  .logo {
    width: 45%;
    max-width: 150px;
  }

  .title {
    font-size: 20px;
  }

  .login-container {
    width: 90%;
    padding: 15px;
  }

  input {
    font-size: 14px;
    padding: 10px;
  }

  button {
    font-size: 14px;
    padding: 10px;
  }
}
</style>