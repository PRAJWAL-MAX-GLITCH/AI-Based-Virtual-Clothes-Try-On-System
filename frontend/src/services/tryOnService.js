import api from './api'

export const runTryOn = async (personImageId, clothingId) => {
  const response = await api.post('/tryon', {
    person_image_id: personImageId,
    clothing_id: clothingId
  })
  return response.data
}
