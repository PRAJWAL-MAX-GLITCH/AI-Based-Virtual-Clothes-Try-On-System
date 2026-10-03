import React, { useState, useEffect, useCallback } from 'react'
import { Search, SlidersHorizontal, X, Frown, Loader2 } from 'lucide-react'
import { getClothingCatalog } from '../services/clothingService'
import ClothingCard from '../components/clothing/ClothingCard'
import './ClothingPage.css'

const CATEGORIES = ['All', 't-shirt', 'shirt', 'hoodie', 'jacket', 'dress', 'top']
const COLORS = ['All', 'black', 'white', 'red', 'blue', 'green', 'grey', 'navy', 'beige', 'brown', 'pink', 'purple']
const SORT_MAP = {
  'Recommended': '',
  'Newest': 'newest',
  'Price: Low to High': 'price_asc',
  'Price: High to Low': 'price_desc',
  'Name: A-Z': 'name_asc',
}

export default function ClothingPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedColor, setSelectedColor] = useState('All')
  const [availability, setAvailability] = useState('All')
  const [sortBy, setSortBy] = useState('Recommended')
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false)

  const [clothes, setClothes] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 1 })

  const fetchClothing = useCallback(async (page = 1) => {
    setIsLoading(true)
    setError(null)
    try {
      const params = { page, limit: 12 }
      if (searchTerm) params.search = searchTerm
      if (selectedCategory !== 'All') params.category = selectedCategory
      if (selectedColor !== 'All') params.color = selectedColor
      if (availability === 'Available') params.available = true
      if (SORT_MAP[sortBy]) params.sort = SORT_MAP[sortBy]

      const data = await getClothingCatalog(params)
      setClothes(data.data.items || [])
      setPagination({
        page: data.data.page || 1,
        total: data.data.total || 0,
        pages: data.data.pages || 1
      })
    } catch (err) {
      setError('Failed to load clothing catalog. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [searchTerm, selectedCategory, selectedColor, availability, sortBy])

  useEffect(() => {
    const debounce = setTimeout(() => fetchClothing(1), 400)
    return () => clearTimeout(debounce)
  }, [fetchClothing])

  const handleClearFilters = () => {
    setSearchTerm('')
    setSelectedCategory('All')
    setSelectedColor('All')
    setAvailability('All')
    setSortBy('Recommended')
  }

  return (
    <div className="clothing-page animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Explore Clothing</h1>
          <p className="page-desc">Choose an outfit and see how it looks with virtual try-on.</p>
        </div>
      </div>

      <div className="catalog-layout">
        <aside className={`catalog-filters ${isMobileFiltersOpen ? 'mobile-open' : ''}`}>
          <div className="filters-header hidden-desktop">
            <h3>Filters</h3>
            <button onClick={() => setIsMobileFiltersOpen(false)} className="btn-icon"><X size={20} /></button>
          </div>

          <div className="filter-group">
            <h4 className="filter-title">Search</h4>
            <div className="search-wrapper">
              <Search size={18} className="search-icon" />
              <input
                type="text"
                placeholder="Search clothing..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
          </div>

          <div className="filter-group">
            <h4 className="filter-title">Category</h4>
            <div className="filter-options">
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  className={`filter-pill ${selectedCategory === cat ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="filter-group">
            <h4 className="filter-title">Color</h4>
            <select value={selectedColor} onChange={(e) => setSelectedColor(e.target.value)} className="filter-select">
              {COLORS.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
            </select>
          </div>

          <div className="filter-group">
            <h4 className="filter-title">Availability</h4>
            <div className="filter-radio-group">
              <label className="radio-label">
                <input type="radio" name="availability" checked={availability === 'All'} onChange={() => setAvailability('All')} /> All
              </label>
              <label className="radio-label">
                <input type="radio" name="availability" checked={availability === 'Available'} onChange={() => setAvailability('Available')} /> Available Only
              </label>
            </div>
          </div>

          <button onClick={handleClearFilters} className="btn-clear-filters">Clear All Filters</button>
        </aside>

        <main className="catalog-main">
          <div className="catalog-toolbar">
            <button className="btn-mobile-filter hidden-desktop" onClick={() => setIsMobileFiltersOpen(true)}>
              <SlidersHorizontal size={18} /> Filters
            </button>
            <div className="catalog-results-count">
              {isLoading ? 'Loading...' : `Showing ${pagination.total} result${pagination.total !== 1 ? 's' : ''}`}
            </div>
            <div className="catalog-sort">
              <span className="sort-label">Sort by:</span>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
                {Object.keys(SORT_MAP).map(k => <option key={k}>{k}</option>)}
              </select>
            </div>
          </div>

          {isLoading ? (
            <div className="catalog-empty-state">
              <Loader2 size={40} className="animate-spin text-primary" />
              <p className="mt-4 text-muted">Loading catalog...</p>
            </div>
          ) : error ? (
            <div className="catalog-empty-state">
              <Frown size={48} className="empty-icon" />
              <h3>Something went wrong</h3>
              <p>{error}</p>
              <button onClick={() => fetchClothing(1)} className="btn-primary-sm mt-4">Retry</button>
            </div>
          ) : clothes.length > 0 ? (
            <>
              <div className="clothing-grid">
                {clothes.map(item => <ClothingCard key={item._id} item={item} />)}
              </div>
              {pagination.pages > 1 && (
                <div className="pagination-bar mt-6">
                  <button disabled={pagination.page <= 1} onClick={() => fetchClothing(pagination.page - 1)} className="btn-secondary">Previous</button>
                  <span className="text-muted">Page {pagination.page} of {pagination.pages}</span>
                  <button disabled={pagination.page >= pagination.pages} onClick={() => fetchClothing(pagination.page + 1)} className="btn-secondary">Next</button>
                </div>
              )}
            </>
          ) : (
            <div className="catalog-empty-state">
              <Frown size={48} className="empty-icon" />
              <h3>No clothing found</h3>
              <p>Try changing your search or filters.</p>
              <button onClick={handleClearFilters} className="btn-primary-sm mt-4">Clear Filters</button>
            </div>
          )}
        </main>
      </div>

      {isMobileFiltersOpen && <div className="mobile-backdrop" onClick={() => setIsMobileFiltersOpen(false)} />}
    </div>
  )
}
