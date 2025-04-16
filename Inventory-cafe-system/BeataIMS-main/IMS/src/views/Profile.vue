<template>
  <div class="overlay" v-if="isProfileOpen">
    <div class="modal-profile">
      <div class="modal-header">
        <h2>User Profile</h2>
        <button class="close-btn" @click="closeProfile">&times;</button>
      </div>

      <div class="modal-content">
        <div v-if="user" class="profile-content">
          <div class="profile-left">
            <p><strong>Name:</strong> {{ user.username }}</p>
            <p><strong>Email:</strong> {{ user.email || `${user.username}@cafebeata.com` }}</p>
            <p><strong>Role:</strong> {{ user.role }}</p>
            <p><strong>Joined:</strong> {{ formatDate(user.date_added || user.created_at) }}</p>
          </div>

          <div class="profile-right">
            <div class="profile-pic-container">
              <img :src="profileImage" alt="Profile Picture" class="profile-pic" @error="handleImageError" />
              
              <!-- Upload button that appears on hover -->
              <div class="upload-overlay">
                <label for="profile-pic-upload" class="upload-btn">
                  <i class="pi pi-camera"></i>
                </label>
                <input
                  id="profile-pic-upload"
                  type="file"
                  accept="image/*"
                  @change="handleProfilePicUpload"
                  class="hidden-input"
                />
              </div>
            </div>
            <h3>{{ user.username }}</h3>
            
            <!-- Show upload status messages -->
            <div v-if="uploadStatus" :class="['status-message', uploadStatus.type]">
              {{ uploadStatus.message }}
            </div>
          </div>
        </div>

        <div class="profile-actions">
          <button @click="logout" class="logout">Logout</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { logout } from "@/auth/authGuard";
import userService from "@/api/userService";

export default {
  name: 'Profile',
  props: {
    isProfileOpen: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      user: null,
      defaultAvatar: "https://www.pngmart.com/files/22/User-Avatar-Profile-PNG.png",
      uploadStatus: null,
      isUploading: false
    };
  },
  computed: {
    profileImage() {
      if (this.user?.profile_pic) {
        return this.user.profile_pic;
      }
      return this.defaultAvatar;
    }
  },
  methods: {
    async fetchUserData() {
      try {
        this.uploadStatus = null;
        const storedUser = JSON.parse(localStorage.getItem('user'));
        if (storedUser && storedUser.user_id) {
          const response = await userService.getUserById(storedUser.user_id);
          if (response && response.user) {
            this.user = response.user;
            console.log("User data loaded:", this.user);
          }
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    },
    closeProfile() {
      this.$emit('close-profile');
    },
    handleImageError(event) {
      console.error('Profile image failed to load:', event.target.src);
      event.target.src = this.defaultAvatar;
    },
    async handleProfilePicUpload(event) {
      try {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validate file type and size
        if (!file.type.match('image.*')) {
          this.uploadStatus = { 
            type: 'error', 
            message: 'Please select an image file.' 
          };
          return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
          this.uploadStatus = { 
            type: 'error', 
            message: 'The image must be less than 5MB.' 
          };
          return;
        }
        
        this.isUploading = true;
        this.uploadStatus = { 
          type: 'info', 
          message: 'Uploading profile picture...' 
        };
        
        // Get the current user ID
        const storedUser = JSON.parse(localStorage.getItem('user'));
        if (!storedUser || !storedUser.user_id) {
          throw new Error("User information not available.");
        }
        
        // Create a FormData object with the user information and file
        const formData = new FormData();
        formData.append('username', this.user.username);
        formData.append('email', this.user.email || `${this.user.username}@cafebeata.com`);
        formData.append('role', this.user.role);
        formData.append('profile_pic', file);
        
        // Update the user via API
        const response = await userService.updateUser(storedUser.user_id, formData);
        console.log("Profile picture update response:", response);
        
        if (response && response.success) {
          this.uploadStatus = { 
            type: 'success', 
            message: 'Profile picture updated successfully!' 
          };
          
          // Refresh user data to get the updated profile picture URL
          await this.fetchUserData();
        } else {
          throw new Error("Failed to update profile picture.");
        }
      } catch (error) {
        console.error('Error updating profile picture:', error);
        this.uploadStatus = { 
          type: 'error', 
          message: `Error: ${error.message || 'Failed to update profile picture'}` 
        };
      } finally {
        this.isUploading = false;
      }
    },
    logout() {
      logout(this.$router);
    },
    formatDate(dateString) {
      if (!dateString) return "N/A";
      return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric"
      });
    }
  },
  mounted() {
    this.fetchUserData();
  },
  watch: {
    isProfileOpen(newVal) {
      if (newVal) {
        this.fetchUserData();
      }
    }
  }
};
</script>

<style scoped>
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-profile {
  background: white;
  width: 90%;
  max-width: 500px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  color: white;
  background: linear-gradient(to right, #e54f6f7e, #ed959821, rgba(0, 0, 0, 0.863)),
              url('@/assets/background.jpg') center/cover no-repeat;
  border-bottom: 1px solid #eee;
  border-top-left-radius: 10px;  
  border-top-right-radius: 10px; 
}

.modal-header h2{
  color: white;
  font-family: 'Arial', sans-serif;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: white;
}

.modal-content {
  padding: 20px;
}

.profile-content {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.profile-left {
  flex: 1;
  text-align: left;
}

.profile-left p {
  margin: 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.profile-right {
  text-align: center;
}

.profile-pic-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
  border-radius: 50%;
  overflow: hidden;
}

.profile-pic {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.upload-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.6);
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.profile-pic-container:hover .upload-overlay {
  opacity: 1;
}

.upload-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.upload-btn i {
  color: #333;
  font-size: 16px;
}

.hidden-input {
  display: none;
}

.status-message {
  margin-top: 10px;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.status-message.error {
  background-color: #f8d7da;
  color: #721c24;
}

.status-message.success {
  background-color: #d4edda;
  color: #155724;
}

.status-message.info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.profile-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

button {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  transition: opacity 0.2s;
}

button:hover {
  opacity: 0.9;
}

.logout {
  background: #dc3545;
}

.open-profile {
  margin: 20px;
}

@media (max-width: 600px) {
  .profile-content {
    flex-direction: column-reverse;
  }
  
  .profile-right {
    margin-bottom: 20px;
  }
}
</style>