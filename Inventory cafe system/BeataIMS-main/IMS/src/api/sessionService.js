import axios from 'axios';
import { API_BASE_URL } from './config';
import { getUser, saveUser, isSessionExpired } from '@/auth/authGuard';

// Session activity tracking
let lastActivity = Date.now();
let sessionCheckInterval = null;

/**
 * Track user activity
 */
function trackActivity() {
  lastActivity = Date.now();
}

/**
 * Initialize activity tracking
 */
function initActivityTracking() {
  // Track mouse movement and clicks
  window.addEventListener('mousemove', trackActivity);
  window.addEventListener('mousedown', trackActivity);
  window.addEventListener('click', trackActivity);
  
  // Track keyboard activity
  window.addEventListener('keydown', trackActivity);
  
  // Track touches for mobile
  window.addEventListener('touchstart', trackActivity);
  window.addEventListener('touchmove', trackActivity);
  
  // Track scrolling
  window.addEventListener('scroll', trackActivity);
}

/**
 * Check if user has been inactive
 * @param {number} inactiveTimeMs - Inactive time in milliseconds
 * @returns {boolean} - True if user is inactive
 */
function isUserInactive(inactiveTimeMs = 30 * 60 * 1000) { // Default 30 minutes
  return (Date.now() - lastActivity) > inactiveTimeMs;
}

/**
 * Ping the server to keep session alive
 * @returns {Promise<boolean>} - True if ping successful
 */
async function pingServer() {
  try {
    // Make a request to root endpoint to keep session alive
    await axios.get(`${API_BASE_URL}/`);
    return true;
  } catch (error) {
    console.error('Error pinging server:', error);
    return false;
  }
}

/**
 * Start session monitoring
 * @param {Function} logoutCallback - Function to call when session expires
 */
function startSessionMonitor(logoutCallback) {
  // Stop any existing interval
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval);
  }
  
  // Initialize activity tracking
  initActivityTracking();
  
  // Set initial activity timestamp
  trackActivity();
  
  // Check session every minute
  sessionCheckInterval = setInterval(async () => {
    const user = getUser();
    
    // If no user, stop monitoring
    if (!user) {
      clearInterval(sessionCheckInterval);
      return;
    }
    
    // Check if session is expired
    if (isSessionExpired()) {
      clearInterval(sessionCheckInterval);
      if (logoutCallback) logoutCallback();
      return;
    }
    
    // Check if user is inactive for too long (30 minutes)
    if (isUserInactive()) {
      clearInterval(sessionCheckInterval);
      if (logoutCallback) logoutCallback();
      return;
    }
    
    // Ping server every 10 minutes to keep session alive
    const tenMinutes = 10 * 60 * 1000;
    if ((Date.now() - lastActivity) < tenMinutes) {
      await pingServer();
      
      // Extend the session expiration time
      const user = getUser();
      if (user) {
        // Update the expiry time (+8 hours from now)
        saveUser(user);
      }
    }
  }, 60000); // Check every minute
}

/**
 * Stop session monitoring
 */
function stopSessionMonitor() {
  if (sessionCheckInterval) {
    clearInterval(sessionCheckInterval);
    sessionCheckInterval = null;
  }
  
  // Remove event listeners
  window.removeEventListener('mousemove', trackActivity);
  window.removeEventListener('mousedown', trackActivity);
  window.removeEventListener('click', trackActivity);
  window.removeEventListener('keydown', trackActivity);
  window.removeEventListener('touchstart', trackActivity);
  window.removeEventListener('touchmove', trackActivity);
  window.removeEventListener('scroll', trackActivity);
}

export default {
  startSessionMonitor,
  stopSessionMonitor,
  trackActivity,
  isUserInactive,
  pingServer
}; 