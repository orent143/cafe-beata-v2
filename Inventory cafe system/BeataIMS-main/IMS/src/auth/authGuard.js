// authGuard.js - Authentication and route protection utilities

/**
 * Check if the user is authenticated
 * @returns {Object|null} The user object if authenticated, null otherwise
 */
export function getUser() {
  const userJson = localStorage.getItem('user');
  if (!userJson) return null;
  
  try {
    const user = JSON.parse(userJson);
    if (!user || !user.user_id || !user.username || !user.role) {
      return null;
    }
    return user;
  } catch (error) {
    console.error('Error parsing user data:', error);
    return null;
  }
}

/**
 * Check if user has permission for a specific route
 * @param {string} route - The route path
 * @returns {boolean} - Whether user has permission
 */
export function hasPermission(route) {
  const user = getUser();
  if (!user) return false;
  
  // Admin routes
  const adminRoutes = ['/dashboard', '/users'];
  // Staff and admin routes
  const staffRoutes = [
    '/homeims', '/products', '/viewinventory', '/stocks',
    '/create', '/productsales', '/suppliers', '/category',
    '/reportsims', '/createorder', '/ordershistory'
  ];
  
  if (user.role === 'admin') {
    return true; // Admins can access all routes
  } else if (user.role === 'cafe_staff') {
    return !adminRoutes.includes(route); // Staff can't access admin routes
  }
  
  return false;
}

/**
 * Middleware function to check authentication for router
 * @param {Object} to - Target route
 * @param {Object} from - Source route
 * @param {Function} next - Next function to call
 */
export function authGuard(to, from, next) {
  const publicPages = ['/', '/login'];
  const authRequired = !publicPages.includes(to.path);
  const user = getUser();
  
  if (authRequired && !user) {
    // Not logged in, redirect to login
    return next({
      path: '/login',
      query: { redirect: to.path }
    });
  } else if (authRequired && !hasPermission(to.path)) {
    // No permission
    return next(user.role === 'admin' ? '/dashboard' : '/homeims');
  }
  
  next();
}

/**
 * Save user data to localStorage with expiration
 * @param {Object} userData - User data to save
 */
export function saveUser(userData) {
  // Add expiration time (8 hours)
  const eightHoursFromNow = new Date();
  eightHoursFromNow.setHours(eightHoursFromNow.getHours() + 8);
  
  const userWithExpiry = {
    ...userData,
    expiry: eightHoursFromNow.getTime()
  };
  
  localStorage.setItem('user', JSON.stringify(userWithExpiry));
}

/**
 * Check if stored user session is expired
 * @returns {boolean} Whether the session is expired
 */
export function isSessionExpired() {
  const user = getUser();
  if (!user || !user.expiry) return true;
  
  return new Date().getTime() > user.expiry;
}

/**
 * Log out user
 * @param {Object} router - Vue Router instance
 */
export function logout(router) {
  localStorage.removeItem('user');
  if (router) {
    router.push('/login');
  }
} 