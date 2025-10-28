import { useState, useEffect, useRef } from 'react'
import { TrendingUp, Package, RefreshCw } from 'lucide-react'
import OfferCard from './OfferCard'
import PriceHistoryModal from './PriceHistoryModal'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'

const BestDealsPage = () => {
  const { isAuthenticated, token } = useAuth()
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedOffer, setSelectedOffer] = useState(null)
  const [showPriceHistory, setShowPriceHistory] = useState(false)
  const [userWatchlist, setUserWatchlist] = useState([])
  const [watchlistLoading, setWatchlistLoading] = useState(false)
  
  const watchlistFetched = useRef(false)

  // Fetch deals from API
  const fetchDeals = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/deals/recent')
      
      if (!response.ok) {
        throw new Error('Failed to fetch deals')
      }
      
      const data = await response.json()
      setDeals(data)
    } catch (err) {
      console.error('Error fetching deals:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Fetch user watchlist
  const fetchWatchlist = async () => {
    if (!isAuthenticated || !token) {
      setUserWatchlist([])
      watchlistFetched.current = false
      return
    }
    
    if (watchlistFetched.current) return
    
    setWatchlistLoading(true)
    watchlistFetched.current = true
    
    try {
      const response = await axios.get('http://localhost:8000/user/watchlist', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUserWatchlist(response.data)
    } catch (error) {
      console.error('Error fetching watchlist:', error)
      setUserWatchlist([])
      watchlistFetched.current = false
    } finally {
      setWatchlistLoading(false)
    }
  }

  // Fetch deals on mount
  useEffect(() => {
    fetchDeals()
  }, [])

  // Fetch watchlist when auth changes
  useEffect(() => {
    fetchWatchlist()
  }, [isAuthenticated, token])

  const handleWatchlistUpdate = (offerId, isAdding, newItem = null) => {
    if (isAdding && newItem) {
      setUserWatchlist(prev => [...prev, newItem])
    } else {
      setUserWatchlist(prev => prev.filter(item => item.offer_id !== offerId))
    }
  }

  const handleOfferClick = (offer) => {
    setSelectedOffer(offer)
    setShowPriceHistory(true)
  }

  const handleClosePriceHistory = () => {
    setShowPriceHistory(false)
    setSelectedOffer(null)
  }

  const handleRefresh = () => {
    fetchDeals()
  }

  // Loading state
  if (loading) {
    return (
      <div className="best-deals-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Finding the best deals...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="best-deals-page">
        <div className="error-state">
          <h2>Oops! Something went wrong</h2>
          <p>{error}</p>
          <button className="retry-button" onClick={handleRefresh}>
            <RefreshCw size={16} />
            Try Again
          </button>
        </div>
      </div>
    )
  }

  // Empty state
  if (deals.length === 0) {
    return (
      <div className="best-deals-page">
        <div className="empty-state">
          <Package className="empty-icon" size={64} />
          <h2>No Deals Found</h2>
          <p>We haven't found any deals in the last 48 hours.</p>
          <p>Check back soon or perform some searches to help us find great deals!</p>
          <button className="refresh-button" onClick={handleRefresh}>
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>
    )
  }

  // Main content with deals
  return (
    <div className="best-deals-page">
      <div className="best-deals-header">
        <div className="header-content">
          <div className="header-title-section">
            <span className="fire-emoji">🔥</span>
            <div>
              <h1>Best Deals</h1>
              <p className="header-subtitle">
                Top {deals.length} deals found in the last 48 hours
              </p>
            </div>
          </div>
          <button className="refresh-button" onClick={handleRefresh}>
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      <div className="deals-grid">
        {deals.map((deal) => (
          <div key={deal.id} className="deal-card-wrapper">
            <OfferCard
              offer={deal}
              onClick={handleOfferClick}
              userWatchlist={userWatchlist}
              onWatchlistUpdate={handleWatchlistUpdate}
            />
            {deal.discount_percentage > 0 && (
              <div className="deal-badge">
                {deal.discount_percentage.toFixed(0)}% below average
              </div>
            )}
          </div>
        ))}
      </div>

      {showPriceHistory && selectedOffer && (
        <PriceHistoryModal
          offer={selectedOffer}
          onClose={handleClosePriceHistory}
        />
      )}
    </div>
  )
}

export default BestDealsPage

