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
      // Check if userData is FormData
      const isFormData = userData instanceof FormData;
      const apiEndpoint = `${API_URL}/users/${userId}`;
      
      console.log('Updating user at URL:', apiEndpoint);
      console.log('Updating user with data:', isFormData ? 'FormData (binary)' : userData);
      
      if (isFormData) {
        console.log('Updating user with FormData (binary)');
        
        // Use native fetch API instead of axios
        const response = await fetch(apiEndpoint, {
          method: 'PUT',
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
        console.log('Update user response:', data);
        
        // Process profile picture URL if exists in the response
        if (data && data.user && data.user.profile_pic) {
          data.user.profile_pic = getImageUrl(data.user.profile_pic);
        }
        
        return data;
      } else {
        // For JSON data
        console.log('Updating user with JSON data:', userData);
        
        // Use native fetch API instead of axios
        const response = await fetch(apiEndpoint, {
          method: 'PUT',
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
        console.log('Update user response:', data);
        
        // Process profile picture URL if exists in the response
        if (data && data.user && data.user.profile_pic) {
          data.user.profile_pic = getImageUrl(data.user.profile_pic);
        }
        
        return data;
      }
    } catch (error) {
      console.error('Update user error:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
        console.error('Error status:', error.response.status);
      } else if (error.request) {
        console.error('Error request:', error.request);
      }
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