/**
 * Utility helpers — formatting, validation, storage.
 * Expand in future stages.
 */

/** Format a date string to a readable format */
export function formatDate(dateStr, options = {}) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric', ...options
  })
}

/** Truncate long text */
export function truncate(str, max = 60) {
  if (!str) return ''
  return str.length > max ? str.slice(0, max) + '…' : str
}

/** Get initials from a name */
export function getInitials(name = '') {
  return name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
}

/** Build a full API URL for a stored file path */
export function getFileUrl(path) {
  if (!path) return null
  const base = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:5000'
  return `${base}/api/v1/static/${path}`
}

/** Safe localStorage helpers */
export const storage = {
  get:    (key) => { try { return JSON.parse(localStorage.getItem(key)) } catch { return null } },
  set:    (key, val) => localStorage.setItem(key, JSON.stringify(val)),
  remove: (key) => localStorage.removeItem(key),
}
