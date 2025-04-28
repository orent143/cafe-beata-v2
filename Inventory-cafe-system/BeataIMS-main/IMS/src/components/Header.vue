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
          <div class="notification-dropdown">
            <i class="pi pi-bell notification-icon" @click="toggleNotifications"></i>
            <span v-if="unreadNotifications > 0" class="notification-badge">{{ unreadNotifications }}</span>
            <div v-if="showNotifications" class="notification-menu">
              <div class="notification-header">
                <h3>Notifications</h3>
                <button @click="markAllAsRead" class="mark-read-btn">Mark all as read</button>
              </div>
              <div class="notification-list">
                <div v-if="notifications.length === 0" class="no-notifications">
                  No notifications
                </div>
                <div v-for="(notification, index) in notifications" 
                    :key="index" 
                    :class="['notification-item', { 'unread': !notification.read }]">
                  <div class="notification-content">
                    <div class="notification-title">{{ notification.title }}</div>
                    <div class="notification-message">{{ notification.message }}</div>
                    <div class="notification-time">{{ formatTimeAgo(notification.timestamp) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="profile-dropdown">
            <div class="profile-image-container" @mouseenter="showDropdown = true">
              <img 
                v-if="userProfilePic" 
                :src="userProfilePic" 
                alt="Profile" 
                class="profile-image"
                @error="handleImageError"
              />
              <i v-else class="pi pi-user profile-icon"></i>
            </div>
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
import userService from '@/api/userService';

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
      isSidebarCollapsed: false,
      userProfilePic: null,
      defaultAvatar: "https://www.pngmart.com/files/22/User-Avatar-Profile-PNG.png",
      showNotifications: false,
      notifications: [],
      unreadNotifications: 0
    };
  },
  created() {
    this.fetchUserData();
    this.loadNotifications();
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
    },
    async fetchUserData() {
      try {
        const storedUser = JSON.parse(localStorage.getItem('user'));
        if (storedUser && storedUser.user_id) {
          const response = await userService.getUserById(storedUser.user_id);
          if (response && response.user) {
            this.userProfilePic = response.user.profile_pic;
            console.log("User profile picture loaded:", this.userProfilePic);
          }
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    },
    handleImageError(event) {
      event.target.src = this.defaultAvatar;
    },
    toggleNotifications() {
      this.showNotifications = !this.showNotifications;
      if (this.showNotifications) {
        this.loadNotifications();
      }
    },
    loadNotifications() {
      const userName = localStorage.getItem("userName");
      if (userName) {
        const userNotificationsKey = `user_notifications_${userName}`;
        const storedNotifications = JSON.parse(localStorage.getItem(userNotificationsKey)) || [];
        this.notifications = storedNotifications;
        this.unreadNotifications = this.notifications.filter(notification => !notification.read).length;
      } else {
        this.notifications = [
          {
            title: "Low Stock Alert",
            message: "Several items are running low on stock. Check inventory.",
            timestamp: new Date(Date.now() - 1800000).toISOString(),
            read: false
          },
          {
            title: "New Order",
            message: "New order received from customer Emily.",
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            read: true
          },
          {
            title: "System Update",
            message: "System will be updated tonight at 12 AM.",
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            read: true
          }
        ];
        this.unreadNotifications = this.notifications.filter(notification => !notification.read).length;
      }
    },
    markAllAsRead() {
      const userName = localStorage.getItem("userName");
      if (userName) {
        const userNotificationsKey = `user_notifications_${userName}`;
        this.notifications.forEach(notification => {
          notification.read = true;
        });
        localStorage.setItem(userNotificationsKey, JSON.stringify(this.notifications));
      } else {
        this.notifications.forEach(notification => {
          notification.read = true;
        });
      }
      this.unreadNotifications = 0;
    },
    formatTimeAgo(timestamp) {
      const now = new Date();
      const diff = now - new Date(timestamp);
      const minutes = Math.floor(diff / 1000 / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);

      if (days > 0) return `${days} day${days > 1 ? "s" : ""} ago`;
      if (hours > 0) return `${hours} hour${hours > 1 ? "s" : ""} ago`;
      if (minutes > 0) return `${minutes} minute${minutes > 1 ? "s" : ""} ago`;
      return "Just now";
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
  gap: 10px;
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
  
  .profile-image-container {
    position: relative;
    cursor: pointer;
    width: 35px;
    height: 35px;
    border-radius: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f0f0f0;
  }

  .profile-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
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
  margin-right: 10px;
  
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

.notification-dropdown {
  position: relative;
}

.notification-icon {
    margin-left: 10px;
    color: #333; 
    cursor: pointer;
    font-size: 17px; 
  }

.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: #ff4757;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.notification-menu {
  position: absolute;
  top: 35px;
  right: -10px;
  background: white;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  width: 300px;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease-in-out;
  max-height: 400px;
  overflow: hidden;
  z-index: 1000;
}

.notification-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.notification-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.mark-read-btn {
  background: none;
  border: none;
  color: #E54F70;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
}

.notification-list {
  overflow-y: auto;
  max-height: 350px;
}

.notification-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  transition: background 0.2s;
}

.notification-item:hover {
  background: #f9f9f9;
}

.notification-item.unread {
  background: #F8F8FF;
  border-left: 3px solid #E54F70;
}

.notification-title {
  font-weight: bold;
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
}

.notification-message {
  font-size: 13px;
  color: #666;
  margin-bottom: 5px;
  line-height: 1.4;
}

.notification-time {
  font-size: 11px;
  color: #999;
}

.no-notifications {
  padding: 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
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

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
