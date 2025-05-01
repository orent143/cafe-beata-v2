<template>
  <Header />
  <sidebar />
  <div class="app-container">
    <div class="dashboard-container">  
      <div class="user-management-container">
        <div class="header-section">
          <h2 class="section-title">User Management</h2>
         
        </div>

        <!-- User List Table -->
        <div class="content-section">
          <div class="user-table-container">
            <table class="user-table">
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Username</th>
                  <th>Role</th>
                  <th>Profile Picture</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td class="username-cell">{{ user.username }}</td>
                  <td>
                    <span :class="['role-badge', user.role === 'admin' ? 'admin-role' : 'staff-role']">
                      {{ user.role === 'cafe_staff' ? 'Cafe Staff' : user.role }}
                    </span>
                  </td>
                  <td>
                    <div class="avatar-container">
                      <img 
  :src="user.profile_pic || defaultAvatar" 
  :alt="user.username" 
  class="profile-pic"
  @error="handleImageError"
/>
                    </div>
                  </td>
                  <td>
                    <div class="action-buttons">
                      <button class="btn-status" @click="toggleStatus(user)">
                        <i class="pi pi-sync"></i> Toggle Status
                      </button>
                      <button class="btn-view" @click="viewUserDetails(user)">
                        <i class="pi pi-eye"></i> View Details
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Add User Form -->
          <div class="add-user-section">
            <div class="add-user-form">
              <h3 class="form-title">Add New User</h3>
              <form @submit.prevent="addUser" enctype="multipart/form-data">
                <div class="form-group">
                  <label for="username">Username</label>
                  <input id="username" v-model="newUser.username" type="text" placeholder="Enter username" required />
                </div>
                
                <div class="form-group">
                  <label for="password">Password</label>
                  <input id="password" v-model="newUser.password" type="password" placeholder="Enter password" required />
                </div>
                
                <div class="form-group">
                  <label for="email">Email</label>
                  <input id="email" v-model="newUser.email" type="email" placeholder="Enter email" required />
                </div>
                
                <div class="form-group">
                  <label for="role">User Role</label>
                  <select id="role" v-model="newUser.role" required>
                    <option value="" disabled selected>Select role</option>
                    <option value="admin">Admin</option>
                    <option value="cafe_staff">Cafe Staff</option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label for="profile_pic">Profile Picture</label>
                  <div class="file-input-container">
                    <input 
                      id="profile_pic" 
                      ref="addUserFileInput"
                      type="file" 
                      @change="handleFileUpload" 
                      accept="image/*"
                      class="file-input"
                    />
                    <label for="profile_pic" class="file-label" @click.prevent="triggerAddUserFileInput">
                      <i class="pi pi-upload"></i>
                      {{ newUser.profile_pic ? newUser.profile_pic.name : 'Choose an image' }}
                    </label>
                  </div>
                </div>
                
                <button type="submit" class="btn-submit">
                  <i class="pi pi-user-plus"></i> Add User
                </button>
              </form>
            </div>
          </div>
        </div>

        <!-- User Details Modal -->
        <div v-if="selectedUser" class="user-details-modal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>User Details</h3>
              <button class="btn-close" @click="closeModal">
                <i class="pi pi-times"></i>
              </button>
            </div>
            
            <div class="modal-body">
              <div class="user-avatar">
                <img 
                  :src="selectedUser.profile_pic || defaultAvatar" 
                  :alt="selectedUser.username" 
                  class="detail-profile-pic"
                  @error="handleImageError"
                />
              </div>
              
              <div class="user-info">
                <p class="info-item"><strong>Username:</strong> {{ selectedUser.username }}</p>
                <p class="info-item"><strong>Email:</strong> {{ selectedUser.email || `${selectedUser.username}@cafebeata.com` }}</p>
                <p class="info-item"><strong>Role:</strong> {{ selectedUser.role }}</p>
                <p class="info-item"><strong>Status:</strong> {{ selectedUser.status || 'Active' }}</p>
              </div>
            </div>
            
            <div class="modal-footer">
              <button class="btn-edit" @click="openEditMode">
                <i class="pi pi-pencil"></i> Edit
              </button>
              <button class="btn-delete" @click="confirmDelete(selectedUser.id)">
                <i class="pi pi-trash"></i> Delete
              </button>
            </div>
          </div>
        </div>

        <!-- Edit User Modal -->
        <div v-if="editMode" class="user-details-modal">
          <div class="simple-modal-content edit-modal">
            <h3>Edit User</h3>
            <button class="modal-close" @click="closeEditMode">
              <i class="pi pi-times"></i>
            </button>
            
            <div v-if="isLoading" class="loading-overlay">
              <div class="spinner"></div>
              <p>Updating user...</p>
            </div>
            
            <form @submit.prevent="updateUser" class="edit-form">
              <div class="form-group">
                <label for="edit-username">Username</label>
                <input id="edit-username" v-model="editedUser.username" type="text" required />
              </div>
              
              <div class="form-group">
                <label for="edit-email">Email</label>
                <input id="edit-email" v-model="editedUser.email" type="email" required />
              </div>
              
              <div class="form-group">
                <label for="edit-role">Role</label>
                <select id="edit-role" v-model="editedUser.role" required>
                  <option value="admin">Admin</option>
                  <option value="cafe_staff">Cafe Staff</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="edit-status">Status</label>
                <select id="edit-status" v-model="editedUser.status">
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="edit-profile-pic">Profile Picture</label>
                <div class="file-upload-container">
                  <div class="current-image-preview" v-if="selectedUser && selectedUser.profile_pic">
                    <img 
                      :src="previewImage || selectedUser.profile_pic" 
                      :alt="editedUser.username"
                      class="profile-preview"
                      @error="handleImageError"
                    />
                  </div>
                  <div class="file-input-wrapper">
                    <button type="button" class="file-select-btn" @click="triggerFileInput">
                      <i class="pi pi-upload"></i> 
                      {{ editedUser.profile_pic ? 'Change Image' : 'Select Image' }}
                    </button>
                    <input 
                      id="edit-profile-pic" 
                      ref="fileInput"
                      type="file" 
                      @change="handleEditProfilePic" 
                      accept="image/*"
                      class="file-input"
                    />
                  </div>
                  <div class="selected-file-name" v-if="profilePicName">
                    Selected: {{ profilePicName }}
                  </div>
                </div>
              </div>
              
              <div class="edit-actions">
                <button type="button" class="btn-cancel" @click="closeEditMode">Cancel</button>
                <button @click.prevent="updateUser">Save</button>
              </div>
            </form>
          </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <div v-if="showDeleteConfirm" class="user-details-modal">
          <div class="simple-modal-content">
            <h3>User Details</h3>
            
            <div class="simple-user-avatar">
              <img 
                :src="selectedUser.profile_pic || defaultAvatar" 
                :alt="selectedUser.username" 
                class="simple-profile-pic"
                @error="handleImageError"
              />
            </div>
            
            <div class="simple-info">
              <p><strong>Username:</strong> {{ selectedUser.username }}</p>
              <p><strong>Email:</strong> {{ selectedUser.email || `${selectedUser.username}@cafebeata.com` }}</p>
              <p><strong>Role:</strong> {{ selectedUser.role }}</p>
              <p><strong>Status:</strong> {{ selectedUser.status || 'Active' }}</p>
            </div>
            
            <div class="simple-actions">
              <button class="btn-simple-edit" @click="openEditMode">
                <i class="pi pi-pencil"></i> Edit
              </button>
              <button class="btn-simple-delete" @click="deleteUser(selectedUser.id)">
                <i class="pi pi-trash"></i> Delete
              </button>
            </div>
            
            <button class="modal-close" @click="closeModal">
              <i class="pi pi-times"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import sidebar from '@/components/admin/sidebar.vue';
import Header from '@/components/Header.vue';
import { useToast } from "vue-toastification";
import userService from "@/api/userService";
import axios from "axios";

export default {
  name: 'UserManagement',
  components: {
    sidebar,
    Header
  },
  data() {
    return {
      searchQuery: '',
      selectedUser: null,
      users: [],
      newUser: {
        username: '',
        password: '',
        email: '',
        role: '',
        profile_pic: null
      },
      showNotification: false,
      toast: useToast(),
      defaultAvatar: 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png',
      editMode: false,
      editedUser: {
        username: '',
        role: '',
        status: 'Active',
        profile_pic: null
      },
      profilePicName: '',
      showDeleteConfirm: false,
      isLoading: false,
      previewImage: null,
      imageErrorCounts: 0
    };
  },

  computed: {
    filteredUsers() {
      if (!this.searchQuery) return this.users;
      
      return this.users.filter((user) =>
        user.username.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
  },

  created() {
    this.getUsers(); 
  },

  methods: {
    getUsers() {
      this.isLoading = true;
      userService.getAllUsers()
        .then(response => {
          this.users = response.users;
          console.log('Loaded users data:', this.users);

          
          this.isLoading = false;
        })
        .catch(error => {
          console.error('Error loading users:', error);
          this.isLoading = false;
        });
    },

    handleImageError(event) {
  console.warn('Image failed to load:', event.target.src);
  event.target.src = this.defaultAvatar;

  this.imageErrorCounts++;
  if (this.imageErrorCounts > 3) {
    console.log('Multiple image errors. Refreshing user data.');
    this.getUsers();
    this.imageErrorCounts = 0;
  }
},

async toggleStatus(user) {
  try {
    // Toggle the status locally
    const newStatus = user.status === 'Active' ? 'Inactive' : 'Active';

    // Prepare the data to send to the backend
    const userData = { status: newStatus };

    console.log("Sending data to backend:", userData);

    // Call the backend PUT method
    const response = await userService.updateUser(user.id, userData);

    if (response && response.success) {
      // Update the status in the local user list
      user.status = newStatus;

      this.toast.success(`${user.username}'s status updated to ${newStatus}`, {
        timeout: 3000,
        position: "top-right",
      });
    } else {
      throw new Error(response?.detail || "Failed to update status");
    }
  } catch (error) {
    console.error("Error updating user status:", error);
    this.toast.error(`Failed to update status: ${error.message || "Unknown error"}`, {
      timeout: 3000,
      position: "top-right",
    });
  }
},
    viewUserDetails(user) {
      this.selectedUser = user; 
    },

    closeModal() {
      this.selectedUser = null; 
      this.editMode = false;
      this.showDeleteConfirm = false;
    },

    handleFileUpload(event) {
      this.newUser.profile_pic = event.target.files[0];
    },

    async addUser() {
      try {
        // Check username is not empty
        if (!this.newUser.username.trim()) {
          this.toast.error("Username cannot be empty", {
            timeout: 3000,
            position: "top-right"
          });
          return;
        }

        // First check if username already exists in current users list
        const existingUser = this.users.find(
          user => user.username.toLowerCase() === this.newUser.username.toLowerCase()
        );
        
        if (existingUser) {
          this.toast.error("A user with this username already exists", {
            timeout: 3000,
            position: "top-right"
          });
          return;
        }

        // Use the provided email or generate a unique one if not provided
        const email = this.newUser.email.trim() || `${this.newUser.username}@cafebeata.com`;

        // Check if a profile picture was uploaded
        if (this.newUser.profile_pic) {
          // Create FormData to handle file upload
          const formData = new FormData();
          formData.append('username', this.newUser.username);
          formData.append('password', this.newUser.password);
          formData.append('role', this.newUser.role);
          formData.append('email', email);
          formData.append('profile_pic', this.newUser.profile_pic);
          
          console.log('Creating user with FormData and profile picture');
          
          // Create user with FormData
          const response = await userService.createUser(formData);
          console.log('Create user response:', response);
          
          // Get the new user details
          if (response && response.success && response.user_id) {
            await this.getUsers(); // Refresh the full user list to include the new user
          }
        } else {
          // Create a JSON object for users without profile pictures
          const userData = {
            username: this.newUser.username,
            password: this.newUser.password,
            role: this.newUser.role,
            email: email
          };

          console.log('Creating user with JSON data:', userData);

          // Create user with JSON data
          const response = await userService.createUser(userData);
          console.log('Create user response:', response);

          // Get the new user details
          if (response && response.success && response.user_id) {
            await this.getUsers(); // Refresh the full user list
          }
        }
        
        // Clear the form
        this.newUser = { username: '', password: '', email: '', role: '', profile_pic: null };

        this.toast.success("User added successfully!", {
          timeout: 3000,
          position: "top-right",
          closeOnClick: true,
        });
      } catch (error) {
        console.error('Error creating user:', error);
        
        let errorMessage = "Error creating user";
        if (error.response) {
          console.error('Error status:', error.response.status);
          console.error('Error headers:', error.response.headers);
          console.error('Error data:', error.response.data);
          
          if (error.response.data?.detail) {
            errorMessage += `: ${error.response.data.detail}`;
          }
        } else if (error.request) {
          console.error('No response received:', error.request);
          errorMessage += `: No response from server`;
        } else if (error.message) {
          errorMessage += `: ${error.message}`;
        }
        
        this.toast.error(errorMessage, {
          timeout: 5000,
          position: "top-right",
          closeOnClick: true,
        });
      }
    },
    
    async deleteUser(userId) {
      try {
        if (confirm("Are you sure you want to delete this user?")) {
          await userService.deleteUser(userId);
          // Remove the user from the local array
          this.users = this.users.filter(user => user.id !== userId);
          this.closeModal();
          this.toast.success("User deleted successfully", {
            timeout: 3000,
            position: "top-right",
            closeOnClick: true,
          });
        }
      } catch (error) {
        this.toast.error("Error deleting user: " + (error.response?.data?.detail || error.message), {
          timeout: 5000,
          position: "top-right",
          closeOnClick: true,
        });
        console.error('Error deleting user:', error);
      }
    },

    openEditMode() {
      // Make a copy of the selected user with all necessary fields
      this.editedUser = { 
        ...this.selectedUser,
        email: this.selectedUser.email || `${this.selectedUser.username}@cafebeata.com`,
        status: this.selectedUser.status || 'Active'
      };
      console.log('Selected user data:', this.selectedUser);
      console.log('Edited user data:', this.editedUser);
      this.profilePicName = this.selectedUser.profile_pic ? this.selectedUser.profile_pic.split('/').pop() : '';
      this.editMode = true;
    },

    handleEditProfilePic(event) {
      const file = event.target.files[0];
      if (file) {
        this.editedUser.profile_pic = file;
        this.profilePicName = file.name;
        
        // Create a preview of the image
        const reader = new FileReader();
        reader.onload = (e) => {
          this.previewImage = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },

    async updateUser() {
  try {
    this.isLoading = true;

    // Prepare user data
    const userData = new FormData();
    userData.append('username', this.editedUser.username);
    userData.append('email', this.editedUser.email || `${this.editedUser.username}@cafebeata.com`);
    userData.append('role', this.editedUser.role);
    userData.append('status', this.editedUser.status || 'Active');

    // Only append profile_pic if a new file was selected
    if (this.editedUser.profile_pic instanceof File) {
      userData.append('profile_pic', this.editedUser.profile_pic);
    }

    // Send PUT request to update the user
    const response = await userService.updateUser(this.selectedUser.id, userData);

    if (response && response.success) {
      // Update the user in the local array
      const index = this.users.findIndex(user => user.id === this.selectedUser.id);
      if (index !== -1) {
        // Keep existing profile_pic if no new one was uploaded
        const updatedUser = {
          ...this.users[index],
          username: this.editedUser.username,
          email: this.editedUser.email || `${this.editedUser.username}@cafebeata.com`,
          role: this.editedUser.role,
          status: this.editedUser.status || 'Active'
        };
        
        // Update profile_pic only if a new one was uploaded
        if (this.editedUser.profile_pic instanceof File) {
          updatedUser.profile_pic = response.profile_pic || updatedUser.profile_pic;
        }
        
        this.users[index] = updatedUser;
      }

      this.closeEditMode();
      this.toast.success("User updated successfully!", {
        timeout: 3000,
        position: "top-right",
      });
    } else {
      throw new Error(response?.detail || "Failed to update user");
    }
  } catch (error) {
    console.error("Error updating user:", error);
    this.toast.error(`Failed to update user: ${error.message || "Unknown error"}`, {
      timeout: 3000,
      position: "top-right",
    });
  } finally {
    this.isLoading = false;
  }
},

    confirmDelete(userId) {
      this.selectedUser = this.users.find(user => user.id === userId);
      this.showDeleteConfirm = true;
    },

    closeEditMode() {
      this.editMode = false;
    },

    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    triggerAddUserFileInput() {
      this.$refs.addUserFileInput.click();
    },
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  margin-left: 230px;
  transition: all 0.3s ease;
}

.dashboard-container {
  flex-grow: 1;
  border-radius: 15px;
  overflow: hidden;
  padding: 20px;
}

.user-management-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e9ecef;
}

.section-title {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}

.search-container {
  position: relative;
  width: 300px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-input {
  width: 100%;
  padding: 10px 10px 10px 35px;
  border-radius: 8px;
  border: 1px solid #ced4da;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #E54F70;
  box-shadow: 0 0 0 2px rgba(229, 79, 112, 0.25);
}

.content-section {
  display: flex;
  gap: 20px;
  height: calc(100% - 60px);
}

.user-table-container {
  flex: 3;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.add-user-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.add-user-form {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.form-title {
  font-size: 18px;
  color: #333;
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eeeeee;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.add-user-form input,
.add-user-form select {
  width: 90%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ced4da;
  font-size: 14px;
  transition: border-color 0.2s;
}

.add-user-form input:focus,
.add-user-form select:focus {
  outline: none;
  border-color: #E54F70;
  box-shadow: 0 0 0 2px rgba(229, 79, 112, 0.25);
}

.file-input-container {
  position: relative;
}

.file-input {
  position: absolute;
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  z-index: -1;
}

.file-label {
  display: block;
  width: 90%;
  padding: 10px;
  background: #f8f9fa;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 14px;
  color: #495057;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-label:hover {
  background-color: #e9ecef;
}

.file-label i {
  margin-right: 5px;
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background-color: #E54F70;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-submit:hover {
  background-color: #d4445f;
}

.user-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.user-table th,
.user-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #eeeeee;
}

.user-table th {
  font-weight: 600;
  color: #495057;
  background-color: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 10;
}

.user-table tr:hover {
  background-color: #f8f9fa;
}

.username-cell {
  font-weight: 500;
}

.avatar-container {
  display: flex;
  justify-content: center;
}

.profile-pic {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
  border: 2px solid #eeeeee;
}

.role-badge {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 500;
}

.admin-role {
  background-color: #f8d7da;
  color: #721c24;
}

.staff-role {
  background-color: #d1ecf1;
  color: #0c5460;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.btn-status,
.btn-view {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}

.btn-status {
  background-color: #fdf7d1;
  color: #856404;
}

.btn-view {
  background-color: #d6ebff;
  color: #004085;
}

.btn-status:hover {
  background-color: #f7e29d;
}

.btn-view:hover {
  background-color: #b9daff;
}

.user-details-modal {
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
}

.modal-content {
  background-color: white;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #6c757d;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  width: 100%;
  display: flex;
  justify-content: center;
}

.detail-profile-pic {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 50%;
  border: 3px solid #e9ecef;
}

.user-info {
  width: 100%;
}

.info-item {
  padding: 10px 0;
  margin: 0;
  border-bottom: 1px solid #f1f1f1;
}

.info-item:last-child {
  border-bottom: none;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-edit,
.btn-delete {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-edit {
  background-color: #fddeeb;
  color: #e83e8c;
}

.btn-delete {
  background-color: #f8d7da;
  color: #721c24;
}

.btn-edit:hover {
  background-color: #f7cde0;
}

.btn-delete:hover {
  background-color: #f5c6cb;
}

/* Simple modal content matching screenshot */
.simple-modal-content {
  background-color: white;
  border-radius: 8px;
  width: 350px;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 20px;
}

.simple-modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 18px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.simple-user-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.simple-profile-pic {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  background-color: #eee;
}

.simple-info {
  margin-bottom: 20px;
}

.simple-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #333;
}

.simple-actions {
  display: flex;
  justify-content: center;
  border-top: 1px solid #eee;
  padding-top: 15px;
  gap: 10px;
}

.btn-simple-edit, .btn-simple-delete {
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.btn-simple-edit {
  background-color: #f7f7f7;
  color: #333;
}

.btn-simple-delete {
  background-color: #f8d7da;
  color: #721c24;
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #777;
}

/* Edit form styles */
.edit-modal {
  width: 400px;
}

.edit-form {
  width: 100%;
}

.file-upload-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.current-image-preview {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
}

.profile-preview {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 50%;
  border: 2px solid #E54F70;
}

.file-input-wrapper {
  position: relative;
  overflow: hidden;
  display: inline-block;
}

.file-select-btn {
  background-color: #E54F70;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-select-btn:hover {
  background-color: #d84666;
}

.file-input {
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.selected-file-name {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-cancel {
  background: #f1f1f1;
  color: #333;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}

.btn-save {
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.btn-save:hover {
  background: #218838;
}

@media (max-width: 992px) {
  .content-section {
    flex-direction: column;
  }
  
  .add-user-section {
    order: -1;
  }
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-radius: 8px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-left-color: #E54F70;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Edit User Modal Styles */
.edit-modal {
  width: 450px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 20px;
  position: relative;
}

.edit-modal h3 {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.edit-modal .modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 18px;
  color: #777;
  cursor: pointer;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.edit-form .form-group {
  display: flex;
  flex-direction: column;
}

.edit-form .form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
  margin-bottom: 5px;
}

.edit-form .form-group input,
.edit-form .form-group select {
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.edit-form .form-group input:focus,
.edit-form .form-group select:focus {
  outline: none;
  border-color: #E54F70;
  box-shadow: 0 0 0 2px rgba(229, 79, 112, 0.25);
}

.edit-form .file-upload-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.edit-form .file-select-btn {
  background-color: #E54F70;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-form .file-select-btn:hover {
  background-color: #d84666;
}

.edit-form .selected-file-name {
  font-size: 12px;
  color: #666;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.edit-actions .btn-cancel {
  background: #f1f1f1;
  color: #333;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
}

.edit-actions .btn-save {
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.edit-actions .btn-save:hover {
  background: #218838;
}
</style>
  