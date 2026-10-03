import api from './api'

export const uploadCustomClothing = async (formData) => {
  const response = await api.post('/user-clothing', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

export const getUserClothing = async () => {
  const response = await api.get('/user-clothing')
  return response.data
}

export const deleteUserClothing = async (id) => {
  const response = await api.delete(`/user-clothing/${id}`)
  return response.data
}
