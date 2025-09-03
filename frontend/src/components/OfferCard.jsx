import { ExternalLink, TrendingUp, Star, User, Package, Heart } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useState, useEffect } from 'react'
import axios from 'axios'

const OfferCard = ({ offer, onClick, userWatchlist, onWatchlistUpdate }) => {
  const { isAuthenticated, token } = useAuth()
  const [isInWatchlist, setIsInWatchlist] = useState(false)
  const [isWatchlistLoading, setIsWatchlistLoading] = useState(false)
  const handleCardClick = () => {
    window.open(offer.url, '_blank')
  }

  const handlePriceHistoryClick = (e) => {
    e.stopPropagation()
    onClick(offer)
  }

  // Check if offer is in watchlist using passed watchlist data
  useEffect(() => {
    if (!isAuthenticated || !userWatchlist) {
      setIsInWatchlist(false)
      return
    }
    
    const isInList = userWatchlist.some(item => item.offer_id === offer.id)
    setIsInWatchlist(isInList)
  }, [isAuthenticated, userWatchlist, offer.id])

  const handleWatchlistToggle = async (e) => {
    e.stopPropagation()
    
    if (!isAuthenticated) {
      alert('Please login to add items to your watchlist')
      return
    }

    setIsWatchlistLoading(true)
    
    try {
      if (isInWatchlist) {
        // Remove from watchlist
        await axios.delete(`http://localhost:8000/user/watchlist/${offer.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setIsInWatchlist(false)
        // Update parent state
        if (onWatchlistUpdate) {
          onWatchlistUpdate(offer.id, false)
        }
      } else {
        // Add to watchlist
        const response = await axios.post('http://localhost:8000/user/watchlist', {
          offer_id: offer.id,
          product_title: offer.title,
          product_url: offer.url
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setIsInWatchlist(true)
        // Update parent state with new item
        if (onWatchlistUpdate) {
          onWatchlistUpdate(offer.id, true, response.data)
        }
      }
    } catch (error) {
      console.error('Error toggling watchlist:', error)
      alert('Failed to update watchlist. Please try again.')
    } finally {
      setIsWatchlistLoading(false)
    }
  }

  return (
    <div className="offer-card" onClick={handleCardClick}>
      <div className="offer-image">
        {offer.image_url ? (
          <img src={offer.image_url} alt={offer.title} />
        ) : (
          <div className="no-image">
            <Package className="no-image-icon" />
          </div>
        )}
        <div className="offer-source">
          <span className="source-badge">{offer.source}</span>
        </div>
      </div>

      <div className="offer-content">
        <h3 className="offer-title" title={offer.title}>
          {offer.title}
        </h3>

        <div className="offer-price">
          <span className="price-amount">
            {offer.currency} {parseFloat(offer.last_price).toFixed(2)}
          </span>
        </div>

        <div className="offer-details">
          {offer.seller && (
            <div className="seller-info">
              <User className="seller-icon" size={14} />
              <span>{offer.seller}</span>
            </div>
          )}
          
          {offer.rating && (
            <div className="rating-info">
              <Star className="rating-icon" size={14} fill="gold" />
              <span>{offer.rating.toFixed(1)}</span>
            </div>
          )}
        </div>

        <div className="offer-actions">          
          <button 
            className="action-button price-history-button"
            onClick={handlePriceHistoryClick}
            title="View price history"
          >
            <TrendingUp size={14} />
            History
          </button>

          <button 
            className="action-button external-link-button"
            onClick={(e) => {
              e.stopPropagation()
              window.open(offer.url, '_blank')
            }}
            title="View on external site"
          >
            <ExternalLink size={14} />
            View
          </button>
          
          {isAuthenticated && (
            <button 
              className={`action-button watchlist-button ${isInWatchlist ? 'in-watchlist' : ''}`}
              onClick={handleWatchlistToggle}
              disabled={isWatchlistLoading}
              title={isInWatchlist ? 'Remove from watchlist' : 'Add to watchlist'}
            >
              <Heart size={14} fill={isInWatchlist ? 'currentColor' : 'none'} />
              {isWatchlistLoading ? '...' : (isInWatchlist ? 'Saved' : 'Save')}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default OfferCard

