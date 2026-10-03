/** Validation helpers for forms */

export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function isStrongPassword(pw) {
  return pw && pw.length >= 8
}

export function validateLoginForm({ email, password }) {
  const errors = {}
  if (!email)               errors.email    = 'Email is required'
  else if (!isValidEmail(email)) errors.email = 'Invalid email address'
  if (!password)            errors.password = 'Password is required'
  return errors
}

export function validateRegisterForm({ name, email, password, confirmPassword, terms }) {
  const errors = {}
  
  if (!name || name.trim().length < 2) errors.name = 'Name must be at least 2 characters'
  
  if (!email) errors.email = 'Email is required'
  else if (!isValidEmail(email)) errors.email = 'Invalid email address'
  
  if (!password) errors.password = 'Password is required'
  else if (!isStrongPassword(password)) errors.password = 'Password must be at least 8 characters'
  
  if (password !== confirmPassword) errors.confirmPassword = 'Passwords do not match'
  
  if (!terms) errors.terms = 'You must accept the terms and conditions'
  
  return errors
}
