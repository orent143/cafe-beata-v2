import axios from 'axios';
import { API_URL, API_BASE_URL, AUTH_URL, getImageUrl } from './config.js';

// Create axios instance with default configuration
const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false // Important to disable for CORS
});

/**
 * User service for authentication and user management
 */
export default {
  /**
   * Login with username and password
   * @param {Object} credentials - Login credentials object
   * @returns {Promise} - Promise with login response
   */
  async login(credentials) {
    try {
      const response = await axiosInstance.post(`${AUTH_URL}/login/`, credentials);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get user by ID
   * @param {number} userId - User ID
   * @returns {Promise} - Promise with user data
   */
  async getUserById(userId) {
    try {
      const response = await axiosInstance.get(`${API_URL}/users/${userId}`);
      
      // Process profile picture URL if exists
      if (response.data && response.data.user && response.data.user.profile_pic) {
        response.data.user.profile_pic = getImageUrl(response.data.user.profile_pic);
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get all users
   * @returns {Promise} - Promise with users data
   */
  async getAllUsers() {
    try {
      const response = await axiosInstance.get(`${API_URL}/users/`);
      
      // Process profile pictures
      if (response.data && response.data.users) {
        response.data.users.forEach(user => {
          if (user.profile_pic) {
            user.profile_pic = getImageUrl(user.profile_pic);
          }
        });
      }
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create a new user
   * @param {Object} userData - User data object or FormData
   * @returns {Promise} - Promise with created user
   */
  async createUser(userData) {
    try {
      // Check if userData is FormData
      const isFormData = userData instanceof FormData;
      const apiEndpoint = `${API_URL}/users/`;
      
      console.log('Creating user at URL:', apiEndpoint);
      
      if (isFormData) {
        console.log('Creating user with FormData (binary)');
        
        // Use native fetch API instead of axios
        const response = await fetch(apiEndpoint, {
          method: 'POST',
          body: userData,
          credentials: 'include', // Add credentials
          mode: 'cors' // Ensure CORS mode
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error('Server error response:', errorData);
          throw new Error(`Server returned ${response.status}: ${errorData.detail || response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Create user response:', data);
        return data;
      } else {
        // For JSON data
        console.log('Creating user with JSON data:', userData);
        
        // Use native fetch API
        const response = await fetch(apiEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          credentials: 'include', // Add credentials
          mode: 'cors', // Ensure CORS mode
          body: JSON.stringify(userData)
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error('Server error response:', errorData);
          throw new Error(`Server returned ${response.status}: ${errorData.detail || response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Create user response:', data);
        return data;
      }
    } catch (error) {
      console.error('Create user error:', error);
      throw error;
    }
  },

  /**
   * Update an existing user
   * @param {number} userId - User ID
   * @param {Object} userData - User data to update
   * @returns {Promise} - Promise with updated user
   */
  async updateUser(userId, userData) {
    try {
      const isFormData = userData instanceof FormData;
      const apiEndpoint = `${API_URL}/users/${userId}`;
  
      if (isFormData) {
        // Check if there's an actual file in the FormData
        const fileEntry = userData.get('profile_pic');
        if (!fileEntry || (fileEntry instanceof File && fileEntry.size === 0)) {
          // Remove empty file entry to keep existing image
          userData.delete('profile_pic');
        }
  
        const response = await fetch(apiEndpoint, {
          method: 'PUT',
          body: userData,
          mode: 'cors',
        });
  
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Server returned ${response.status}: ${errorData.detail || response.statusText}`);
        }
  
        return await response.json();
      } else {
        // For JSON data, ensure profile_pic is not included if not changed
        if (!userData.profile_pic) {
          delete userData.profile_pic; // Remove profile_pic if it's null/undefined
        }
  
        const response = await fetch(apiEndpoint, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userData),
        });
  
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Server returned ${response.status}: ${errorData.detail || response.statusText}`);
        }
  
        return await response.json();
      }
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete a user
   * @param {number} userId - User ID
   * @returns {Promise} - Promise with delete result
   */
  async deleteUser(userId) {
    try {
      const response = await axiosInstance.delete(`${API_URL}/users/${userId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Upload profile picture
   * @param {number} userId - User ID
   * @param {File} file - Profile picture file
   * @returns {Promise} - Promise with upload result
   */
  async uploadProfilePicture(userId, file) {
    try {
      const formData = new FormData();
      formData.append('profile_pic', file);
      
      const response = await axiosInstance.post(
        `${API_URL}/users/${userId}/profile-pic`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Request password reset
   * @param {string} email - User email
   * @returns {Promise} - Promise with request result
   */
  async requestPasswordReset(email) {
    try {
      const response = await axiosInstance.post(`${AUTH_URL}/forgot-password/`, { email });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}; 