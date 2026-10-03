import api from './api'

export const uploadUserImage = async (formData) => {
  const response = await api.post('/uploads/user-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

export const uploadCatalogImage = async (formData) => {
  const response = await api.post('/uploads/clothing-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}
