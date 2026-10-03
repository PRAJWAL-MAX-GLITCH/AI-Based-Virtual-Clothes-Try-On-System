import api from './api'

export const getHistory = async (page = 1, limit = 20) => {
  const response = await api.get('/history', {
    params: { page, limit }
  })
  return response.data
}

export const getHistoryItem = async (id) => {
  const response = await api.get(`/history/${id}`)
  return response.data
}

export const getHistoryResultUrl = async (id) => {
  const response = await api.get(`/history/${id}/result`)
  return response.data
}

export const deleteHistoryItem = async (id) => {
  const response = await api.delete(`/history/${id}`)
  return response.data
}
