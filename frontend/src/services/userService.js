import api from './api'

export const getUserProfile = async () => {
  const response = await api.get('/users/me')
  return response.data
}

export const updateUserProfile = async (profileData) => {
  const response = await api.put('/users/me', profileData)
  return response.data
}

export const changePassword = async (passwordData) => {
  // passwordData: { current_password, new_password }
  const response = await api.patch('/users/me/password', passwordData)
  return response.data
}

export const deactivateAccount = async () => {
  const response = await api.delete('/users/me')
  return response.data
}
