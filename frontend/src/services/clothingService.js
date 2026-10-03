import api from './api'

export const getClothingCatalog = async (params = {}) => {
  const response = await api.get('/clothing', { params })
  return response.data
}

export const getClothingById = async (id) => {
  const response = await api.get(`/clothing/${id}`)
  return response.data
}
