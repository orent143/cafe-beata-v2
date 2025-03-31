<template>
  <div class="reset-password-page">
    <div class="form-container">
      <h1>Change Your Password</h1>

      <form @submit.prevent="handleResetPassword">
        <!-- New Password Field -->
        <div class="input-container">
          <input 
            type="password" 
            v-model="newPassword" 
            placeholder="New Password" 
            required 
          />
        </div>

        <!-- Confirm Password Field -->
        <div class="input-container">
          <input 
            type="password" 
            v-model="confirmPassword" 
            placeholder="Confirm Password" 
            required 
          />
        </div>

        <!-- Error Message -->
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

        <!-- Success Message -->
        <p v-if="successMessage" class="success">{{ successMessage }}</p>

        <!-- Change Password Button -->
        <button type="submit">Change Password</button>
      </form>
    </div>
  </div>
</template>


<script>
export default {
  data() {
    return {
      newPassword: "",
      confirmPassword: "",
      errorMessage: "",
      successMessage: "",
      token: this.$route.params.token, // Extract the token from the URL
    };
  },
  methods: {
    async handleResetPassword() {
      const token = this.token;  // Extract token from the URL

      if (!token) {
        this.errorMessage = "Invalid or missing token.";
        return;
      }

      if (this.newPassword !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match.";
        return;
      }

      try {
        const response = await fetch(`http://127.0.0.1:8000/reset-password/${token}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            newPassword: this.newPassword,  // Only send the new password
          }),
        });

        const data = await response.json();

        if (response.ok) {
          this.successMessage = data.message;
          this.errorMessage = "";
        } else {
          this.errorMessage = data.detail || "An error occurred. Please try again.";
          this.successMessage = "";
        }
      } catch (error) {
        console.error("Error during password reset:", error);
        this.errorMessage = "An unexpected error occurred.";
        this.successMessage = "";
      }
    }
  },
};
</script>


<style scoped>
/* Styling for Reset Password Page */
.success {
  color: green;
  font-size: 14px;
  margin-top: 10px;
}

.reset-password-page {
  background-image: url("@/assets/Uicbackroundblur.png");
  background-size: cover;
  background-position: center;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.form-container {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 0 20px rgba(255, 105, 180, 0.8);
  width: 85%;
  max-width: 400px;
  text-align: center;
  backdrop-filter: blur(10px);
}

h1 {
  font-size: 26px;
  color: #d63384;
  margin-bottom: 20px;
  font-weight: bold;
}

.input-container {
  margin-bottom: 20px;
}

input {
  width: 85%;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #ff69b4;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(255, 105, 180, 0.5);
}

button {
  background-color: #ff69b4;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
