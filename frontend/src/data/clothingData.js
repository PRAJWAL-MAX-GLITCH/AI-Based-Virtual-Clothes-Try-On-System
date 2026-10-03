/**
 * Mock data for Clothing Catalog (Stage 5)
 * Matches expected backend schema.
 */

export const mockClothing = [
  {
    _id: "c1",
    name: "Classic Black T-Shirt",
    category: "t-shirt",
    description: "A comfortable and versatile black t-shirt made from 100% organic cotton. Perfect for everyday wear.",
    price: 799,
    color: "Black",
    sizes: ["S", "M", "L", "XL"],
    image: null,
    available: true,
    created_at: "2026-09-01T10:00:00Z"
  },
  {
    _id: "c2",
    name: "White Oxford Shirt",
    category: "shirt",
    description: "Crisp white oxford shirt ideal for formal occasions and smart-casual looks.",
    price: 1499,
    color: "White",
    sizes: ["M", "L", "XL"],
    image: null,
    available: true,
    created_at: "2026-09-02T11:00:00Z"
  },
  {
    _id: "c3",
    name: "Urban Grey Hoodie",
    category: "hoodie",
    description: "Cozy oversized grey hoodie with a soft fleece lining. Features a kangaroo pocket.",
    price: 1999,
    color: "Grey",
    sizes: ["S", "M", "L"],
    image: null,
    available: true,
    created_at: "2026-09-03T09:30:00Z"
  },
  {
    _id: "c4",
    name: "Blue Denim Jacket",
    category: "jacket",
    description: "Classic blue denim jacket with subtle fading and bronze hardware.",
    price: 2499,
    color: "Blue",
    sizes: ["M", "L", "XL", "XXL"],
    image: null,
    available: true,
    created_at: "2026-09-04T14:15:00Z"
  },
  {
    _id: "c5",
    name: "Red Summer Dress",
    category: "dress",
    description: "Flowy red summer dress with a floral pattern and adjustable straps.",
    price: 1799,
    color: "Red",
    sizes: ["XS", "S", "M"],
    image: null,
    available: false,
    created_at: "2026-09-05T16:45:00Z"
  },
  {
    _id: "c6",
    name: "Striped Navy Top",
    category: "top",
    description: "Nautical-inspired striped navy top with a boat neckline.",
    price: 899,
    color: "Blue",
    sizes: ["S", "M", "L"],
    image: null,
    available: true,
    created_at: "2026-09-06T08:20:00Z"
  },
  {
    _id: "c7",
    name: "Basic White T-Shirt",
    category: "t-shirt",
    description: "The essential white crewneck t-shirt. Breathable and lightweight.",
    price: 699,
    color: "White",
    sizes: ["S", "M", "L", "XL", "XXL"],
    image: null,
    available: true,
    created_at: "2026-09-07T10:10:00Z"
  },
  {
    _id: "c8",
    name: "Black Leather Jacket",
    category: "jacket",
    description: "Premium faux-leather biker jacket with asymmetrical zip closure.",
    price: 3499,
    color: "Black",
    sizes: ["M", "L"],
    image: null,
    available: true,
    created_at: "2026-08-20T12:00:00Z"
  },
  {
    _id: "c9",
    name: "Maroon Pullover Hoodie",
    category: "hoodie",
    description: "Warm maroon pullover hoodie with ribbed cuffs and hem.",
    price: 1899,
    color: "Red",
    sizes: ["S", "M", "L", "XL"],
    image: null,
    available: true,
    created_at: "2026-08-25T15:30:00Z"
  },
  {
    _id: "c10",
    name: "Grey Casual Shirt",
    category: "shirt",
    description: "Lightweight grey linen blend shirt for a relaxed summer vibe.",
    price: 1299,
    color: "Grey",
    sizes: ["M", "L", "XL"],
    image: null,
    available: false,
    created_at: "2026-08-28T09:00:00Z"
  },
  {
    _id: "c11",
    name: "Elegant Black Dress",
    category: "dress",
    description: "Sleek midi-length black dress suitable for evening events.",
    price: 2299,
    color: "Black",
    sizes: ["S", "M", "L"],
    image: null,
    available: true,
    created_at: "2026-09-02T13:45:00Z"
  },
  {
    _id: "c12",
    name: "White Graphic Top",
    category: "top",
    description: "White crop top featuring a subtle abstract art print.",
    price: 999,
    color: "White",
    sizes: ["XS", "S", "M"],
    image: null,
    available: true,
    created_at: "2026-09-05T11:20:00Z"
  }
]

export const getClothingCategories = () => [
  't-shirt', 'shirt', 'hoodie', 'jacket', 'top', 'dress'
]

export const getClothingColors = () => [
  'Black', 'White', 'Blue', 'Red', 'Grey'
]
