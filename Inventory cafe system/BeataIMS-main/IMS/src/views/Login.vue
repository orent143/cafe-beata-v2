<template>
  <div class="login-page">
    <div class="login-container">
      <h1>Cafe Beata</h1>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username</label>
          <input type="text" id="username" v-model="username" required />
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
  text-align: center;
  padding: 0 5%;
}

.login-container {
  background: rgba(255, 255, 255, 0.979);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.795);
  text-align: center;
  max-width: 400px;
  width: 100%;
  animation: fadeIn 1s ease-in-out;
}

.login-container h1 {
  margin-bottom: 2rem;
  color: #E54F70;

    text-shadow: 
      1px 1px 0#fbf1f3, 
      -1px 1px 0 #fbf1f3,
      1px -1px 0 #fbf1f3,
      -1px -1px 0 #fbf1f3,
      0px 1px 0 #fbf1f3,
      0px -1px 0 #fbf1f3,
      1px 0px 0 #fbf1f3,
      -1px 0px 0 #fbf1f3;
    line-height: 1.2; /* Adjust line-height for better spacing */
  font-family: 'Inknut Antiqua', serif;
    font-size: 50px;
}

.input-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
  font-family: 'Poppins', sans-serif;
  font-weight: bolder;
}

.input-group input {
  width: 95%;
  padding: 0.75rem;
  border: 1px solid #ffffff;
  background-color: #D9D9D9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.input-group input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 5px rgba(255, 50, 186, 0.5);
}

.login-btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 8px;
  background-color:#E54F70 ;
  color: #ffffff;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  font-family: 'Poppins', sans-serif;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.forgot-password {
  margin-top: 1rem;
  color: var(--primary-color);
  cursor: pointer;
  font-family: 'Poppins', sans-serif;
  text-decoration: underline;
}

.forgot-password:hover {
  color: var(--accent-color);
}
</style>