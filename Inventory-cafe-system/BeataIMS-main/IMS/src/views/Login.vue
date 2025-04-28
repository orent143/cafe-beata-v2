<template>
  <div class="login-page">
    <div class="login-container">
      <div class="header-title">
      <h1>Welcome back</h1>
      <p class="sub-description">
        Enter your credentials below to login to your account
      </p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username</label>
          <input type="text" id="username" v-model="username" placeholder="sampleuser123" required />
        </div>
        <div class="input-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <button type="submit" class="login-btn">Login</button>
      </form>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p class="forgot-password" @click="handleForgotPassword">Forgot Password?</p>
    </div>
  </div>
</template>

<script>
import { useToast } from "vue-toastification"; 
import { saveUser } from "@/auth/authGuard";
import userService from "@/api/userService";

export default {
  data() {
    return {
      username: "",
      password: "",
      errorMessage: "",
    };
  },
  setup() {
    const toast = useToast(); 
    return { toast };
  },
  methods: {
    async handleLogin() {
      try {
        const userData = await userService.login({
          username: this.username,
          password: this.password,
        });

        // Use our saveUser function to store with expiration
        saveUser(userData);

        this.toast.success("Login successful!", {
          position: "top-right",
          timeout: 3000,
        });

        const redirectPath = this.$route.query.redirect; 
        if (userData.role === "admin") {
          this.$router.push("/dashboard");
        } else if (userData.role === "cafe_staff") {
          if (redirectPath === "homesms") {
            this.$router.push("/homesms");
          } else {
            this.$router.push("/homeims");
          }
        }
      } catch (error) {
        this.errorMessage = error.response?.data?.detail || "Invalid username or password";
        this.toast.error(this.errorMessage, { position: "top-right", timeout: 3000 });
      }
    },
    async handleForgotPassword() {
      try {
        const email = prompt("Please enter your email address:");
        if (email) {
          await userService.requestPasswordReset(email);
          this.toast.success("Password reset email sent!", {
            position: "top-right",
            timeout: 3000,
          });
        }
      } catch (error) {
        this.toast.error("Failed to send password reset email.", {
          position: "top-right",
          timeout: 3000,
        });
      }
    },
  },
};
</script>

<style scoped>
:root {
  --primary-color: #FF32BA;
  --secondary-color: #FF32BA;
  --accent-color: #e74c3c;
}

.login-page {
  height: 100vh;
  background: linear-gradient(to right, #e54f6f7e, #ed959821, rgba(0, 0, 0, 0.863)),
              url('@/assets/Image_20250311_143559_347.jpeg') center/cover no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5%;
}
.header-title {
  display: flex;
  flex-direction: column;
  width: 100%;
  text-align: center; /* Add this line */
  margin-bottom: 1rem; /* Add this line */
}
.sub-description {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  margin-bottom: 15px;
}
.login-container {
  background: rgba(255, 255, 255, 0.979);
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.795);
  text-align: center;
  max-width: 24rem;
  width: 80%;
  animation: fadeIn 1s ease-in-out;
  border: 1px solid #00000075; /* Added border color */

}

.login-container h1 {
    font-size: 30px;
    margin-bottom: 0.5rem;
    font-weight: 650;
    color: #7e2a3c;
}

.input-group {
  margin-bottom: 1.5rem;
  text-align: left;
  width: 100%;
}

.input-group label {
  width: 90%;
  display: block;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
  font-weight: 500;
  font-size: .875rem;
}

.input-group input {
  width: 90%;
  padding: 0.55rem;
  border: 1px solid #0000001e; /* Added border color */
  background-color: transparent;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .05);
  border-radius: 8px;
  font-size: .875rem;
  transition: border-color 0.3s;
}



.login-btn {
  width: 90%;
  padding: 0.55rem;
  border: 1px solid #0000001e; /* Added border color */
  background-color:#E54F70;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, .05);
  border-radius: 8px;
  color: white; 
  font-size: 1rem;
  transition: border-color 0.3s;
  cursor: pointer;
}

.login-btn:hover {
  transform: translateY(-2px);
  background-color: #802e3f;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.forgot-password {
  margin-top: 1rem;
  color: var(--primary-color);
  cursor: pointer;
  text-decoration: underline;
}

.forgot-password:hover {
  color: var(--accent-color);
}
</style>