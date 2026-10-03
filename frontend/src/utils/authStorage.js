/**
 * Centralized authentication storage for frontend.
 * 
 * NOTE: Currently uses mock storage for UI testing.
 * Will be replaced with actual JWT storage in Stage 10.
 */

const USER_KEY = 'vto_mock_user'
const AUTH_KEY = 'vto_is_authed'

export const authStorage = {
  /** Check if user is authenticated */
  isAuthenticated: () => {
    return localStorage.getItem(AUTH_KEY) === 'true'
  },

  /** Get current user data */
  getUser: () => {
    try {
      const user = localStorage.getItem(USER_KEY)
      return user ? JSON.parse(user) : null
    } catch {
      return null
    }
  },

  /** Save auth state (mock login) */
  setAuth: (userData) => {
    localStorage.setItem(AUTH_KEY, 'true')
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
  },

  /** Clear auth state (logout) */
  clearAuth: () => {
    localStorage.removeItem(AUTH_KEY)
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem('access_token') // For future JWT
  }
}
