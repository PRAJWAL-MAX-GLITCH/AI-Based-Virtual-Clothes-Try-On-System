export const MAX_IMAGE_SIZE_MB = 5
export const MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

export const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/webp'
]

export function validateClothingImage(file) {
  if (!file) {
    return { valid: false, error: 'No file selected.' }
  }

  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return { valid: false, error: 'Unsupported file type. Please upload a JPG, PNG, or WEBP.' }
  }

  if (file.size > MAX_IMAGE_SIZE_BYTES) {
    return { valid: false, error: `Image must be smaller than ${MAX_IMAGE_SIZE_MB} MB.` }
  }

  return { valid: true, error: null }
}
