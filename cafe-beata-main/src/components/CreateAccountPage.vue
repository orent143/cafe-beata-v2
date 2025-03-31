<template>
  <div class="create-account-page">
    <div class="form-container">
      <h1>Create Account</h1>

      <!-- Sign-Up Form -->
      <form @submit.prevent="handleSignUp" class="signup-form">
        <!-- Name Field -->
        <div class="input-container">
          <input 
            type="text" 
            v-model="name" 
            placeholder="Name" 
            required 
          />
        </div>

        <!-- Email Field -->
        <div class="input-container">
          <input 
            type="email" 
            v-model="email" 
            placeholder="E-mail" 
            required 
          />
        </div>

        <!-- Password Field -->
        <div class="input-container">
          <div class="password-container">
            <input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="password" 
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

        
        <!-- Terms and Conditions with Checkbox -->
        <div class="terms-container">
          <input type="checkbox" v-model="agreeToTerms" id="termsCheckbox" required />
          <label for="termsCheckbox">
            By continuing, you agree to UIC Cafe Beàta's 
            <router-link to="/privacy-policy" class="terms-link" @click="saveFormData">Privacy Policy</router-link>.
          </label>
        </div>

        <!-- Error Message -->
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

        <!-- Sign Up Button (Disabled Until Checkbox is Checked) -->
        <button type="submit" class="sign-up-button" :disabled="!agreeToTerms">Sign Up</button>
      </form>

      <!-- Sign In Link -->
      <div class="sign-in-link">
        <p>Already have an account? <router-link to="/login" @click="goToLogin">Sign In</router-link></p>
      </div>
    </div>

    <!-- Success Popup -->
    <div v-if="showSuccessPopup" class="success-popup-overlay">
      <div class="success-popup">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h2>Account Created Successfully!</h2>
        <p>Welcome to UIC Cafe Beàta, {{ name }}!</p>
        <p class="redirect-message">You will be redirected to the login page shortly...</p>
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
        <button @click="closePopup" class="close-button">
          <span>Continue</span>
          <i class="fas fa-arrow-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      name: "",
      email: "",
      password: "",
      errorMessage: "",
      showSuccessPopup: false,
      agreeToTerms: false, // Checkbox value
      showPassword: false, // Add this for password visibility toggle
    };
  },

  created() {
    // Ensure dark mode is not applied on this page
    document.body.classList.remove("dark-mode");
    
    // Restore form data if available
    this.restoreFormData();
  },

  methods: {
    saveFormData() {
      // Save form data to localStorage before navigating to privacy policy
      localStorage.setItem('createAccount_name', this.name);
      localStorage.setItem('createAccount_email', this.email);
      localStorage.setItem('createAccount_password', this.password);
    },
    
    restoreFormData() {
      // Restore form data from localStorage if available
      const savedName = localStorage.getItem('createAccount_name');
      const savedEmail = localStorage.getItem('createAccount_email');
      const savedPassword = localStorage.getItem('createAccount_password');
      
      if (savedName) this.name = savedName;
      if (savedEmail) this.email = savedEmail;
      if (savedPassword) this.password = savedPassword;
    },
    
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    async handleSignUp() {
      if (!this.agreeToTerms) {
        this.errorMessage = "You must agree to the Privacy Policy to continue.";
        return;
      }

      const emailRegex = /^[a-zA-Z0-9]+(_\d{12})?@uic\.edu\.ph$/;
      if (!emailRegex.test(this.email)) {
        this.errorMessage = "Email must be a valid UIC Email.";
        return;
      }

      const username = this.name.trim();

      try {
        // First, check if the username already exists in the backend
        const usernameCheckResponse = await fetch("http://127.0.0.1:8000/check-username", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: username,
          }),
        });

        const usernameCheckData = await usernameCheckResponse.json();
        if (usernameCheckResponse.ok && usernameCheckData.exists) {
          this.errorMessage = "Username already exists. Please choose a different one.";
          return;
        }

        // If the username doesn't exist, proceed with account creation
        const response = await fetch("http://127.0.0.1:8000/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
            username: username,
          }),
        });

        const data = await response.json();
        if (response.ok) {
          this.showSuccessPopup = true;
          localStorage.setItem('userName', username);  
          localStorage.setItem('userEmail', this.email);
          // Clear the form data from localStorage after successful signup
          this.clearFormData();
          setTimeout(() => {
            this.$router.push({ name: "Login" });
          }, 2000);
        } else {
          console.error("Error response data:", data);
          this.errorMessage = data.detail;
        }
      } catch (error) {
        console.error("Error during account creation:", error);
        this.errorMessage = "An error occurred. Please try again.";
      }
    },

    goToLogin() {
      // Clear form data when navigating to login
      this.clearFormData();
      this.$router.push({ name: "Login" });
    },

    closePopup() {
      this.showSuccessPopup = false;
      this.$router.push({ name: "Login" });
    },
    
    clearFormData() {
      // Remove form data from localStorage
      localStorage.removeItem('createAccount_name');
      localStorage.removeItem('createAccount_email');
      localStorage.removeItem('createAccount_password');
    },
  },
  
  beforeUnmount() {
    // Clean up localStorage when component is unmounted (except when going to privacy policy)
    if (!this.$route || this.$route.path !== '/privacy-policy') {
      this.clearFormData();
    }
  },
};
</script>

<style scoped>
/* Styling for Create Account Page */

.terms-container {
  display: flex;
  align-items: center;
  font-size: 14px;
  margin-top: -10px; /* Adjust position slightly higher */
}

.terms-container input {
  margin-right: 4px;
  width: 14px;
  height: 14px;
}

.terms-link {
  color: #ff1493;
  text-decoration: none;
  font-weight: bold;
}

.terms-link:hover {
  text-decoration: underline;
}

/* Add more space below terms & conditions */
.terms-container {
  margin-bottom: 15px; /* Increase spacing between Terms and Sign In */
}

/* Disabled button style */
button:disabled {
  background: gray;
  cursor: not-allowed;
}

.create-account-page {
  background-image: url("@/assets/Uicbackroundblur.png"); /* Same as LoginPage.vue */
  background-size: cover;
  background-position: center;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.form-container {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 0 20px rgba(255, 105, 180, 0.8);
  width: 100%;
  max-width: 400px;
  text-align: center;
  backdrop-filter: blur(10px);
}

h1 {
  font-size: 26px;
  color: #d63384;
  margin-bottom: 20px;
  font-weight: bold;
  text-shadow: 0 0 8px rgba(255, 105, 180, 0.6);
}

/* Input fields with glowing effect */
.input-container {
  margin-bottom: 20px;
}

.password-container {
  position: relative;
  width: 84%;
  max-width: 320px;
  display: flex;
  align-items: center;
  margin: 0 auto;
}

.password-container input {
  width: 100%;
  padding-right: 40px; /* Make space for the button */
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

input, select {
  width: 74%;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #ff69b4;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
  transition: all 0.3s ease;
  max-width: 320px; /* Adjust the max width for the inputs */
}

input:focus, select:focus {
  outline: none;
  border-color: #d63384;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.8);
}

/* Sign Up Button with glowing pink effect */
.sign-up-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  background: linear-gradient(135deg, #ff1493, #ff69b4);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.8);
  transition: all 0.3s ease;
  max-width: 320px;
}

.sign-up-button:hover {
  background: linear-gradient(135deg, #d63384, #ff1493);
  box-shadow: 0 0 20px rgba(255, 20, 147, 1);
}

/* Error message */
.error {
  color: red;
  font-size: 14px;
  margin-top: 10px;
}

/* Sign In Link */
.sign-in-link {
  margin-top: 20px;
  font-size: 14px;
}

.sign-in-link a {
  color: #ff1493;
  text-decoration: none;
  font-weight: bold;
}

.sign-in-link a:hover {
  text-decoration: underline;
  text-shadow: 0 0 5px rgba(255, 20, 147, 0.8);
}

/* Success Popup */
.success-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

.success-popup {
  background: white;
  border-radius: 15px;
  padding: 30px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 5px 30px rgba(0, 0, 0, 0.3);
  position: relative;
  animation: slideIn 0.4s ease-out;
}

.success-icon {
  font-size: 60px;
  color: #4CAF50;
  margin-bottom: 15px;
}

.success-popup h2 {
  color: #333;
  margin-bottom: 10px;
  font-size: 24px;
}

.success-popup p {
  color: #666;
  margin-bottom: 15px;
  font-size: 16px;
}

.redirect-message {
  font-size: 14px;
  color: #888;
  font-style: italic;
}

.progress-bar {
  height: 4px;
  background-color: #f0f0f0;
  border-radius: 2px;
  margin: 15px 0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff1493, #ff69b4);
  width: 0%;
  animation: progressFill 2s linear forwards;
}

.close-button {
  background: linear-gradient(135deg, #ff1493, #ff69b4);
  color: white;
  border: none;
  border-radius: 25px;
  padding: 10px 25px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.close-button span {
  margin-right: 8px;
}

.close-button:hover {
  background: linear-gradient(135deg, #d63384, #ff1493);
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(255, 20, 147, 0.4);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes progressFill {
  from { width: 0%; }
  to { width: 100%; }
}

/* Mobile Responsive Adjustments */
@media (max-width: 768px) {
  .form-container {
    width: 85%;
    padding: 20px;
  }

  h1 {
    font-size: 24px;
  }

  input {
    font-size: 14px;
  }

  .sign-up-button {
    font-size: 14px;
    padding: 10px;
  }
}
</style>