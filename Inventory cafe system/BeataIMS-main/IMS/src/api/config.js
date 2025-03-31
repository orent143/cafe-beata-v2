// API configuration for the Inventory system

// Base URL for the backend API
export const API_BASE_URL = "http://127.0.0.1:8001";
export const API_URL = `${API_BASE_URL}/api`;
export const AUTH_URL = `${API_BASE_URL}/Auth`;

// Specific API endpoints
export const INVENTORY_API = `${API_URL}/inventory`;
export const SALES_API = `${API_URL}/sales`;
export const ORDERS_API = `${API_URL}/orders`;
export const ORDER_SUMMARY_API = `${API_URL}/ordersummary`;
export const STOCK_API = `${API_URL}/stock`;
export const REPORTS_API = `${API_URL}/reports`;
export const CATEGORIES_API = `${API_URL}/categories`;
export const SUPPLIERS_API = `${API_URL}/suppliers`;
export const ACTIVITY_LOGS_API = `${API_URL}/activity_logs`;
export const USERS_API = `${API_URL}/users`;

// Helper function for image URLs
export function getImageUrl(path) {
    if (!path) return null;
    
    // Log to help with debugging
    console.log('Original path:', path);
    
    // If the path already starts with http, it's already a full URL
    if (path.startsWith('http')) {
        return path;
    }
    
    // Handle full paths with uploads directory
    if (path.includes('uploads/profile_pics/')) {
        // For full paths, ensure we don't duplicate the uploads directory
        return `${API_BASE_URL}/${path}`;
    }
    
    // If path is just a filename, add the appropriate directory
    if (!path.includes('/')) {
        return `${API_BASE_URL}/uploads/profile_pics/${path}`;
    }
    
    // For any other path, ensure correct formatting
    return `${API_BASE_URL}/${path.startsWith('/') ? path.substring(1) : path}`;
}

// Helper function to get the authorization header
export function getAuthHeader() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user && user.token) {
        return { Authorization: `Bearer ${user.token}` };
    }
    return {};
}

// Default axios config (if needed)
export const axiosConfig = {
    baseURL: API_URL,
    timeout: 10000, // 10 second timeout
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: false // Disable sending credentials to avoid CORS preflight issues
}; 