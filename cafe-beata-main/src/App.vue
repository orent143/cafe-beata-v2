<template>
  <div id="app">
    <router-view></router-view> <!-- This is where the routed component will be displayed -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      isDarkMode: localStorage.getItem("darkMode") === "true" && localStorage.getItem("loggedIn") === "true",
      isLoggedIn: localStorage.getItem("loggedIn") === "true",
    };
  },
  watch: {
    isDarkMode(newValue) {
      localStorage.setItem("darkMode", newValue); // Save preference in localStorage
      document.body.classList.toggle("dark-mode", newValue);
    },
  },
  created() {
    this.applyDarkModeBasedOnRoute();
  },
  methods: {
    applyDarkModeBasedOnRoute() {
      // Don't apply dark mode for excluded pages like login, create-account, and forgot-password
      const excludedPages = ['/login', '/create-account', '/forgot-password'];
      
      if (!this.isLoggedIn || excludedPages.includes(this.$route.path)) {
        document.body.classList.remove("dark-mode");
      } else {
        if (this.isDarkMode) {
          document.body.classList.add("dark-mode");
        }
      }
    },
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
    },
    logout() {
      localStorage.setItem("loggedIn", "false"); // Mark user as logged out
      localStorage.setItem("darkMode", "false"); // Turn off dark mode on logout
      this.isDarkMode = false; // Update local data to reflect the logout state
      this.isLoggedIn = false; // Update login status
      document.body.classList.remove("dark-mode"); // Remove dark mode class on logout
      this.$router.push('/login'); // Redirect to the login page
    }
  }
};
</script>

<style>
/* Default Light Mode */
body {
  background-color: #ffffff;
  color: #000000;
}

/* 🌙 Dark Mode */
.dark-mode {
  background-color: #121212;
  color: #ffffff;
}

/* 🌙 Dark Mode - Buttons */
.dark-mode button {
  background-color: #333;
  color: #fff;
  border: 1px solid #555;
}

/* 🌙 Dark Mode - Input Fields */
.dark-mode input {
  background-color: #222;
  color: #fff;
  border: 1px solid #555;
}

/* 🌙 Dark Mode - Sidebar & Time */
.dark-mode .sidebar,
.dark-mode .sidebar-category h3,
.dark-mode .sidebar-category ul li {
  color: #ffffff;
}

.dark-mode .live-time {
  color: #ffffff;
}
</style>
