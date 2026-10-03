import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Search, History, AlertTriangle, Loader2 } from 'lucide-react'
import HistoryCard from '../components/history/HistoryCard'
import { getHistory, deleteHistoryItem } from '../services/historyService'
import { useToast } from '../context/ToastContext'
import './HistoryPage.css'

const LIMIT = 8

export default function HistoryPage() {
  const { showToast } = useToast()
  const [historyData, setHistoryData] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [itemToDelete, setItemToDelete] = useState(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const fetchHistory = useCallback(async (page) => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getHistory(page, LIMIT)
      setHistoryData(data.data.items || [])
      setTotalPages(data.data.pages || 1)
      setCurrentPage(data.data.page || 1)
    } catch (err) {
      setError('Failed to load history. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { fetchHistory(1) }, [fetchHistory])

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return
    setIsDeleting(true)
    try {
      await deleteHistoryItem(itemToDelete._id || itemToDelete.id)
      setHistoryData(prev => prev.filter(i => (i._id || i.id) !== (itemToDelete._id || itemToDelete.id)))
      showToast('History item deleted.', 'success')
      setItemToDelete(null)
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to delete item.'
      showToast(msg, 'error')
    } finally {
      setIsDeleting(false)
    }
  }

  const filteredData = searchTerm
    ? historyData.filter(item =>
        (item.clothing_name || item.clothingName || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.clothing_category || item.clothingCategory || '').toLowerCase().includes(searchTerm.toLowerCase())
      )
    : historyData

  return (
    <div className="history-page animate-fade-in">
      <div className="page-header flex-between align-center">
        <div>
          <h1 className="page-title">Try-On History</h1>
          <p className="page-desc">Browse and manage your past virtual try-ons.</p>
        </div>
        <Link to="/try-on" className="btn-primary hidden-mobile">New Try-On</Link>
      </div>

      <div className="history-search-bar mb-6">
        <div className="search-wrapper" style={{ maxWidth: '400px' }}>
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search history..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="catalog-empty-state mt-8">
          <Loader2 size={40} className="animate-spin text-primary" />
          <p className="mt-4 text-muted">Loading history...</p>
        </div>
      ) : error ? (
        <div className="catalog-empty-state mt-8">
          <h3>Something went wrong</h3>
          <p>{error}</p>
          <button onClick={() => fetchHistory(1)} className="btn-primary-sm mt-4">Retry</button>
        </div>
      ) : filteredData.length > 0 ? (
        <>
          <div className="history-grid">
            {filteredData.map(item => (
              <HistoryCard
                key={item._id || item.id}
                item={item}
                onDelete={setItemToDelete}
              />
            ))}
          </div>

          {!searchTerm && totalPages > 1 && (
            <div className="pagination-bar mt-6">
              <button disabled={currentPage <= 1} onClick={() => fetchHistory(currentPage - 1)} className="btn-secondary">Previous</button>
              <span className="text-muted">Page {currentPage} of {totalPages}</span>
              <button disabled={currentPage >= totalPages} onClick={() => fetchHistory(currentPage + 1)} className="btn-secondary">Next</button>
            </div>
          )}
        </>
      ) : (
        <div className="catalog-empty-state mt-8">
          <History size={48} className="empty-icon" />
          <h3>{searchTerm ? 'No results found' : 'No try-on history yet'}</h3>
          <p>{searchTerm ? 'Try a different search term.' : 'Start your first virtual try-on!'}</p>
          {!searchTerm && <Link to="/try-on" className="btn-primary mt-4" style={{ display: 'inline-flex' }}>Start Try-On</Link>}
        </div>
      )}

      {itemToDelete && (
        <div className="modal-overlay">
          <div className="dialog-box animate-scale-in">
            <div className="dialog-icon-warning">
              <AlertTriangle size={24} />
            </div>
            <h3>Delete this history item?</h3>
            <p>This will permanently remove this try-on record and its result image.</p>
            <div className="dialog-actions mt-6">
              <button onClick={() => setItemToDelete(null)} className="btn-secondary flex-1" disabled={isDeleting}>Cancel</button>
              <button onClick={handleDeleteConfirm} className="btn-danger flex-1" disabled={isDeleting}>
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
