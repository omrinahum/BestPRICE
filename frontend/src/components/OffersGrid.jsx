import { useState, useEffect, useRef } from 'react'
import { Package } from 'lucide-react'
import OfferCard from './OfferCard'
import FiltersPanel from './FiltersPanel'
import Pagination from './Pagination'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'

const OffersGrid = ({ offers, loading, pagination, onOfferClick, onFiltersChange, onPageChange }) => {
  const { isAuthenticated, token } = useAuth()
  const [userWatchlist, setUserWatchlist] = useState([])
  const [watchlistLoading, setWatchlistLoading] = useState(false)
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 20,
    sort_by: 'last_price',
    sort_order: 'asc',
    min_price: '',
    max_price: '',
    source: '',
    min_rating: ''
  })

  // Track if watchlist has been fetched to prevent duplicate calls
  const watchlistFetched = useRef(false)
  
  // Fetch user watchlist once when component mounts or auth changes
  useEffect(() => {
    const fetchWatchlist = async () => {
      if (!isAuthenticated || !token) {
        setUserWatchlist([])
        watchlistFetched.current = false
        return
      }
      
      // Prevent duplicate calls
      if (watchlistFetched.current) return
      
      setWatchlistLoading(true)
      watchlistFetched.current = true
      
      try {
        const response = await axios.get('/user/watchlist', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setUserWatchlist(response.data)
      } catch (error) {
        console.error('Error fetching watchlist:', error)
        setUserWatchlist([])
        watchlistFetched.current = false // Reset on error
      } finally {
        setWatchlistLoading(false)
      }
    }

    fetchWatchlist()
  }, [isAuthenticated, token])

  const handleWatchlistUpdate = (offerId, isAdding, newItem = null) => {
    // Update local state optimistically - no API call needed!
    if (isAdding && newItem) {
      setUserWatchlist(prev => [...prev, newItem])
    } else {
      setUserWatchlist(prev => prev.filter(item => item.offer_id !== offerId))
    }
  }

  const handleFiltersChange = (newFilters) => {
    const updatedFilters = { ...filters, ...newFilters, page: 1 } // Reset to page 1 when filters change
    setFilters(updatedFilters)
    onFiltersChange(updatedFilters)
  }

  return (
    <div className="offers-section">
      <FiltersPanel 
        filters={filters}
        onFiltersChange={handleFiltersChange}
        offerCount={pagination.total_count}
      />
      
      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading offers...</p>
        </div>
      ) : !offers || offers.length === 0 ? (
        <div className="empty-state">
          <Package className="empty-icon" />
          <h3>No offers found</h3>
          <p>Try adjusting your search terms or filters</p>
        </div>
      ) : (
        <>
          <div className="offers-grid">
            {offers.map((offer) => (
              <OfferCard
                key={offer.id}
                offer={offer}
                onClick={() => onOfferClick(offer)}
                userWatchlist={userWatchlist}
                onWatchlistUpdate={handleWatchlistUpdate}
              />
            ))}
          </div>
          
          <Pagination
            currentPage={pagination.page}
            totalPages={pagination.total_pages}
            totalItems={pagination.total_count}
            itemsPerPage={pagination.page_size}
            onPageChange={onPageChange}
          />
        </>
      )}
    </div>
  )
}

export default OffersGrid
