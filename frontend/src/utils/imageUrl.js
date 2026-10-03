/**
 * Constructs a full URL for images stored on the backend.
 * 
 * @param {string} path - The relative path returned by the backend (e.g., 'uploads/image.jpg' or 'results/abc.png')
 * @returns {string} The full absolute URL pointing to the backend's static file endpoint.
 */
export function getImageUrl(path) {
  if (!path) return ''
  
  // If it's already an absolute URL (e.g., external or data URI), return as is
  if (path.startsWith('http') || path.startsWith('data:')) {
    return path
  }

  // Remove leading slash if present to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

  // The backend exposes static files via /static/<path>
  const token = localStorage.getItem('access_token')
  let url = `${baseUrl}/static/${cleanPath}`
  if (token) {
    url += `?token=${token}`
  }
  return url
}
