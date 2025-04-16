<template>
  <header class="dashboard-header">
    <div class="header-content">
      <div class="header-left">
        <button class="sidebar-toggle" @click="toggleSidebar">☰</button>
        <div class="logo">
          <span class="logo-text">Cafe Beata</span>
        </div>
      </div>
      <div class="header-right">
        <div class="search-bar">
          <i class="pi pi-search search-icon"></i>
          <input
            type="text"
            placeholder="Search"
            v-model="localSearchQuery"
            @input="updateSearchQuery"
          />
        </div>
        <div class="profile">
          <i class="pi pi-bell notification-icon"></i>
          <div class="profile-dropdown">
            <i class="pi pi-user profile-icon" @mouseenter="showDropdown = true"></i>
            <div v-if="showDropdown" class="dropdown-menu" @mouseleave="showDropdown = false">
              <a class="dropdown-item" @click="openProfile">View Profile</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
  <Profile 
    :isProfileOpen="isProfileOpen" 
    @close-profile="closeProfile"
  />
</template>

<script>
import Profile from '@/views/Profile.vue';
export default {
  components: {
    Profile
  },
  props: {
    searchQuery: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      localSearchQuery: this.searchQuery,
      showDropdown: false,
      isProfileOpen: false,
      isSidebarCollapsed: false
    };
  },
  methods: {
    openProfile() {
      this.isProfileOpen = true;
      this.showDropdown = false;
      document.body.style.overflow = 'hidden';
    },
    closeProfile() {
      this.isProfileOpen = false;
      document.body.style.overflow = 'auto';
    },
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
      this.$emit('toggle-sidebar', this.isSidebarCollapsed);
    },
    updateSearchQuery() {
      this.$emit('update:searchQuery', this.localSearchQuery);
    }
  }
};
</script>

<style scoped>
.dashboard-header {
  position: sticky;
  top: 0;
  background-image: linear-gradient(to right, #E54F70, #ed9598);
  padding: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.sidebar-toggle {
  color: #000;
  background-color: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  font-size: 25px;
  font-weight: 900;
  transition: background-color 0.3s;
}

.sidebar-toggle:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.search-bar input {
    padding: 8px 30px 8px 30px; 
    border: 1px solid #94949400;
    border-radius: 10px; 
    width: 130px; 
    font-size: 14px; 
    font-weight: bold; 
    color: #333; 
    background-color: #F5F5F5; 
  }
  
  .search-bar input:focus {
    border-color: #007BF6; 
    outline: none;
  }
  
  .profile {
    display: flex;
    align-items: center;
    gap: 15px;
  }
  
  .profile-pic {
    border-radius: 50%;
    margin-left: 10px; 
  }
  
  .logo-text {
    font-family: 'Inknut Antiqua', serif;
    font-size: 30px; 
    font-weight: bolder;
    color: white;
    text-shadow: 
      1px 1px 0#940358, 
      -1px 1px 0 #940358,
      1px -1px 0 #940358,
      -1px -1px 0 #940358,
      0px 1px 0 #940358,
      0px -1px 0 #940358,
      1px 0px 0 #940358,
      -1px 0px 0 #940358;
    line-height: 1.2;   
  }

.header-right {
  display: flex;
  align-items: center;
}

.search-bar {
    position: relative; 
    display: flex; 
    align-items: center; 
  }
  
  .search-icon {
    position: absolute;
    left: 10px; 
    top: 50%;
    transform: translateY(-50%);
    color: #333; 
    pointer-events: none; 
  }

.search-bar input {
  padding: 8px 30px;
  border: 1px solid #ccc;
  border-radius: 10px;
  width: 150px;
  font-size: 14px;
}

.profile {
  display: flex;
  align-items: center;
  gap: 15px;
  position: relative;
}
  .profile-icon {
    margin-right: 10px; 
    color: #333; 
    cursor: pointer; 
    font-size: 17px; 
  }
  
  .profile-dropdown {
  position: relative;
}

.notification-icon {
    margin-left: 10px;
    color: #333; 
    cursor: pointer;
    font-size: 17px; 
  }

.dropdown-menu {
  position: absolute;
  top: 35px;
  right: 0;
  background: white;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
  width: 150px;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease-in-out;
}

.dropdown-item {
  padding: 10px;
  text-align: left;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: background 0.2s ease-in-out;
}

.dropdown-item:hover {
  background: #f0f0f0;
}
</style>
