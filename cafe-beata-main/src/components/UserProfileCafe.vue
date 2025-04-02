<template>
  <div class="profile-container">
    <div class="profile-card">
      <!-- Back Button Container -->
      <div class="back-button-container">
        <button @click="goToDashboard" class="back-to-dashboard-button">
          <i class="fa fa-arrow-left"></i>
        </button>
      </div>

      <h2>PROFILE</h2>

      <!-- Avatar Section with Upload Button -->
      <div class="avatar-container">
        <div class="avatar-wrapper">
          <!-- Profile Image -->
          <img :src="getAvatarUrl(user.avatar)" alt="Avatar" class="avatar-img" />
          <!-- Upload Button with Pencil Icon -->
          <button @click="triggerFileInput" class="upload-icon-btn">
            <i class="fa fa-pencil"></i>
          </button>
          <!-- Hidden File Input for Avatar Upload -->
          <input type="file" ref="fileInput" @change="uploadAvatar" style="display: none;" />
        </div>
        
        <!-- Profile Information -->
        <div class="profile-info">
          <p class="username">{{ user.username }}</p>
          <p class="email">{{ user.email }}</p>

          <!-- Line between Email and Course -->
          <hr class="divider" />

          <!-- Display Course and Gender with left alignment -->
          <div class="left-aligned">
            <p class="course"><strong>Course:</strong> {{ user.course }}</p>
            <p class="gender"><strong>Gender:</strong> {{ user.gender }}</p>
          </div>
        </div>
      </div>

      <!-- Profile Edit Section -->
      <div v-if="isEditing">
        <div class="form-group">
          <label>Username:</label>
          <input v-model="user.username" type="text" disabled />
        </div>
        <div class="form-group">
          <label>E-mail:</label>
          <input v-model="user.email" type="email" disabled />
        </div>
        <div class="form-group">
          <label>Course:</label>
          <input v-model="user.course" type="text" />
        </div>
        <div class="form-group">
          <label>Gender:</label>
          <select v-model="user.gender">
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <button @click="saveChanges" class="save-button">Save Changes</button>
        <button @click="cancelEdit" class="cancel-button">Cancel</button>
      </div>

      <!-- Default View - View Profile Button -->
      <div v-else>
        <button @click="toggleEdit" class="edit-button">Edit Profile</button>
      </div>
    </div>
  </div>
</template>



<script>
export default {
  data() {
    return {
      user: {
        avatar: '', // Removed hardcoded default avatar
        username: '',
        email: '',
        course: '',
        gender: '',
      },
      isEditing: false,
      isDarkMode: localStorage.getItem('darkMode') === 'true', // Load Dark Mode preference
    };
  },
  mounted() {
    const userEmail = localStorage.getItem('userEmail');
    if (userEmail) {
      this.user.email = userEmail;
      this.loadProfile(); // Load profile on mount
    }

    // Ensure dark mode is applied when page loads
    if (localStorage.getItem('darkMode') === 'true') {
      this.isDarkMode = true; 
      document.body.classList.add('dark-mode');
    }
  },
  methods: {
    // Toggle Dark Mode and save preference
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
      localStorage.setItem('darkMode', this.isDarkMode);

      // Apply or remove dark mode class
      if (this.isDarkMode) {
        document.body.classList.add('dark-mode');
      } else {
        document.body.classList.remove('dark-mode');
      }
    },

   getAvatarUrl(avatar) {
  return avatar ? `http://127.0.0.1:8000${avatar}` : ''; // Removed default.png reference


    },

    toggleEdit() {
      this.isEditing = !this.isEditing;
    },

    async saveChanges() {
  try {
    const formData = new FormData();
    formData.append('username', this.user.username);
    formData.append('email', this.user.email);
    
    // Only add course and gender if they exist, otherwise send empty values
    // This will make the profile update work even when these fields aren't filled
    formData.append('course', this.user.course || '');
    formData.append('gender', this.user.gender || '');
    formData.append('avatar', this.user.avatar);

    const response = await fetch(`http://127.0.0.1:8000/profile/${encodeURIComponent(this.user.email)}`, {
      method: 'PUT',
      body: formData,
    });

    const data = await response.json();
    if (response.ok) {
      this.isEditing = false;
      alert('Profile updated successfully');
    } else {
      alert(data.detail);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred while saving your profile.');
      }   
    },  

    cancelEdit() {
      this.isEditing = false;
    },

    async loadProfile() {
  try {
    const response = await fetch(`http://127.0.0.1:8000/profile/${encodeURIComponent(this.user.email)}`);
    const data = await response.json();
    if (response.ok) {
      this.user = data;
      if (!this.user.avatar) {
        this.user.avatar = ''; // Removed default.png reference
      }
    } else {
      alert(data.detail);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to load profile.');

      }
    },

    uploadAvatar(event) {
  const file = event.target.files[0];
  if (file) {
    const formData = new FormData();
    formData.append("avatar", file);

    fetch(`http://127.0.0.1:8000/profile/upload-avatar/${encodeURIComponent(this.user.email)}`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message === "Avatar uploaded successfully") {
          this.user.avatar = data.avatar_url || ""; // Removed default.png reference
          this.saveChanges();
        } else {
          alert(data.detail || "Failed to upload avatar.");
        }
      })
      .catch((error) => {
        console.error("Error uploading avatar:", error);
        alert("An error occurred while uploading the avatar.");
          });
      }
    },

    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    goToDashboard() {
      this.$router.push({ name: 'Dashboard' });
    },
  },
};
</script>






<style scoped> 
.profile-info {
  margin-bottom: 20px;
}

.profile-info p {
  font-size: 18px;
  color: #333;
}

.profile-info strong {
  color: #007bff;
}

.divider {
  margin: 20px 0;
  border: 0;
  border-top: 2px solid #333;
  width: 100%; /* Make it span the entire container width */
  box-sizing: border-box; /* Include padding in the width calculation */
  margin-left: 0; /* Reset the margin */
}

.left-aligned p {
  text-align: left;
  margin: 5px 0;
}

.dark-mode .profile-container {
  background-color: #222 !important; /* Dark background */
}

.dark-mode .profile-card {
  background-color: #333 !important; /* Dark profile card */
  color: white !important; /* Light text */
}

/* Dark Mode - Text Adjustments */
.dark-mode h2,
.dark-mode label,
.dark-mode .profile-info p,
.dark-mode .about-me p {
  color: white !important; /* Ensure text is light */
}

/* Dark Mode - Avatar Border */
.dark-mode .avatar-img {
  border: 3px solid white !important;
}

/* Dark Mode - Input Fields */
.dark-mode input,
.dark-mode select,
.dark-mode textarea {
  background-color: #444 !important;
  color: white !important;
  border: 1px solid #666 !important;
}

/* Dark Mode - Buttons */
.dark-mode button {
  background-color: #white !important;
  color: white !important;
}

.dark-mode button:hover {
  background-color: #777 !important;
}

/* Dark Mode - Profile Info Highlight */
.dark-mode .profile-info strong {
  color: rgb(151, 15, 90) !important; /* Make the strong text more visible */
}

.profile-container {
  position: relative; /* Ensure this is positioned so that absolute elements inside it can be correctly aligned */
  padding: 30px;
  background-color: white;
  height: 100vh; /* Auto height to fit the content */
  max-height: 95vh; /* Maximum height to avoid overflowing */
  overflow-y: auto; /* Enable scrolling if content exceeds the height */
  transition: height 0.3s ease;  /* Smooth transition when height changes */
}

h2 {
  font-size: 28px;
  color: #333;
  text-align: center;
}

.profile-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;  /* Ensure it takes up the full width */
  max-width: 600px;  /* Limit the width on larger screens */
  margin: 20px auto;
  position: relative; /* Ensure the buttons can be positioned relative to this container */
  border: 1px solid #E54F70;
}

/* Back Button Container - Position it at the top-left of the profile container */
.back-button-container {
  position: absolute;
  top: 10px;
  left: 10px; /* Position it at the very top-left corner */
  z-index: 1; /* Ensure it stays above other content */
}

/* Back Button Styling */
.back-to-dashboard-button {
  background-color: transparent;
  color: rgb(0, 0, 0);
  padding: 0;
  font-size: 20px;
  border: none;
  cursor: pointer;
}

/* Icon size inside the button */
.back-to-dashboard-button i {
  font-size: 20px;
  margin: 0; /* Remove extra margin from icon */
}

/* Avatar Section */
.avatar-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
}

.avatar-wrapper {
  position: relative;
}

.avatar-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 3px solid #333;
}

.upload-icon-btn {
  position: absolute;
  bottom: 0px; /* Place it at the bottom of the circle */
  right: 0px; /* Place it at the right edge of the circle */
  background-color: rgb(255, 255, 255); /* No background */
  border: none; /* No border */
  padding: 0; /* Remove padding to make it fit the icon */
  cursor: pointer;
  font-size: 20px; /* Set size for the pencil icon */
  color: #007bff; /* Set color for the pencil icon */
  width: 30px; /* Set width of the clickable area */
  height: 30px; /* Set height of the clickable area */
  border-radius: 50%; /* Make the clickable area circular */
  display: flex;
  justify-content: center; /* Center the icon inside the button */
  align-items: center; /* Center the icon vertically */
}

.upload-icon-btn i {
  font-size: 20px;
  color: rgb(235, 175, 175);
}

/* Profile Information */
.profile-info {
  text-align: center;
}

.username {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.email {
  font-size: 14px;
  color: #555;
}

/* Form Styling */
.form-group {
  margin-top: 15px;
}

label {
  font-size: 16px;
  color: #555;
}

input,
select,
textarea {
  margin-top: 5px;
  padding: 12px;
  font-size: 16px;
  width: 95%;
  border-radius: 6px;
  border: 1px solid #ccc;
}

textarea {
  resize: vertical;
}

button {
  margin-top: 10px;
  padding: 12px;
  font-size: 16px;
  background-color: rgb(53, 42, 47);
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  width: 100%;
}

button:hover {
  background-color: rgb(68, 63, 57);
}

.save-button,
.cancel-button {
  background-color: rgb(31, 32, 31);
}

.save-button:hover,
.cancel-button:hover {
  background-color: rgb(26, 27, 27);
}

.edit-button {
  padding: 1px 1px;
  font-size: 10px;
  background-color: transparent;
  color: #FFF;
  border: 2px solid #d12f7a;
  cursor: pointer;
  position: relative;
  z-index: 0;
  border-radius: 5px;
  text-transform: uppercase;
}

.edit-button::after {
  content: "";
  z-index: -1;
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: rgb(31, 32, 31);
  left: 0;
  top: 0;
  border-radius: 10px;
}

.edit-button::before {
  content: "";
  background: linear-gradient(
    45deg,
    #FF0000, #FF7300, #FFFB00, #48FF00,
    #00FFD5, #002BFF, #FF00C8, #FF0000
  );
  position: absolute;
  top: -2px;
  left: -2px;
  background-size: 600%;
  z-index: -1;
  width: calc(100% + 4px);
  height: calc(100% + 4px);
  filter: blur(8px);
  animation: glowing 20s linear infinite;
  transition: opacity .3s ease-in-out;
  border-radius: 10px;
  opacity: 0;
}

.edit-button:hover::before {
  opacity: 1;
}

.edit-button {
  color: white;
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
}

.edit-button:hover {
  background-color: #0056b3;
}

.profile-info {
  margin-bottom: 20px;
}

.profile-info p {
  font-size: 18px;
  color: #333;
}

.profile-info strong {
  color: rgb(114, 53, 68);
}

.about-me {
  margin-top: 30px;
  text-align: center;
}

.about-me p {
  font-size: 16px;
  color: #555;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .profile-container {
    padding: 10px; /* Adjust padding for smaller screens */
  }

  /* Ensure the profile card stays centered with proper margins */
  .profile-card {
    margin: 60px auto;
    padding: 50px;
    width: auto;  /* Make the profile card responsive */
    max-width: none; /* Remove any max-width on smaller screens */
  }

  /* Back Button - position at top-left on mobile */
  .back-button-container {
    top: 10px;
    left: 10px; /* Position back button at the top-left of the screen */
  }

  /* Ensure edit button stays at the bottom */
  .edit-button {
    font-size: 14px; /* Slightly smaller font for mobile */
    margin-top: 20px; /* Add margin between content and button */
  }
}


</style>
