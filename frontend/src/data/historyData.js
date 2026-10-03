/**
 * Mock data for History Page (Stage 8)
 * Matches expected backend schema.
 */

export const mockHistory = [
  {
    id: "history-1",
    personImageId: "person-1",
    clothingId: "c1",
    clothingSource: "catalog",
    clothingName: "Classic Black T-Shirt",
    clothingCategory: "t-shirt",
    resultImage: null,
    status: "completed",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() // 2 hours ago
  },
  {
    id: "history-2",
    personImageId: "person-1",
    clothingId: "custom-1",
    clothingSource: "my-clothes",
    clothingName: "My Favorite Red Hoodie",
    clothingCategory: "hoodie",
    resultImage: null,
    status: "completed",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() // 1 day ago
  },
  {
    id: "history-3",
    personImageId: "person-2",
    clothingId: "c4",
    clothingSource: "catalog",
    clothingName: "Blue Denim Jacket",
    clothingCategory: "jacket",
    resultImage: null,
    status: "failed",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString() // 2 days ago
  },
  {
    id: "history-4",
    personImageId: "person-1",
    clothingId: "c11",
    clothingSource: "catalog",
    clothingName: "Elegant Black Dress",
    clothingCategory: "dress",
    resultImage: null,
    status: "completed",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString() // 3 days ago
  },
  {
    id: "history-5",
    personImageId: "person-3",
    clothingId: "custom-2",
    clothingSource: "my-clothes",
    clothingName: "Vintage Leather Jacket",
    clothingCategory: "jacket",
    resultImage: null,
    status: "completed",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 96).toISOString() // 4 days ago
  }
]
