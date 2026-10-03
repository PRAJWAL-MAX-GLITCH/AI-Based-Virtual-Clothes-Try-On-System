/**
 * Temporary mock data for Dashboard UI testing (Stage 4).
 * Will be replaced by real backend API calls later.
 */

export const mockDashboardStats = {
  totalTryOns: 12,
  savedResults: 8,
  myClothes: 4,
  availableClothing: 24
}

export const mockRecentTryOns = [
  {
    id: 'try_1',
    clothingName: 'Black Basic T-Shirt',
    category: 'Top',
    date: 'Today, 10:30 AM',
    status: 'Completed',
    thumbnail: null // Placeholder for missing images
  },
  {
    id: 'try_2',
    clothingName: 'Classic Denim Jacket',
    category: 'Outerwear',
    date: 'Yesterday',
    status: 'Completed',
    thumbnail: null
  },
  {
    id: 'try_3',
    clothingName: 'White Summer Dress',
    category: 'Dress',
    date: 'Sep 3, 2026',
    status: 'Completed',
    thumbnail: null
  }
]
