import { useState, useEffect } from 'react'
import { X, TrendingUp, TrendingDown } from 'lucide-react'

const PriceHistoryModal = ({ offer, onClose }) => {
  const [priceHistory, setPriceHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchPriceHistory = async () => {
      try {
        const response = await fetch(`http://localhost:8000/offers/price/${offer.id}`)
        
        if (!response.ok) {
          throw new Error('Failed to fetch price history')
        }
        
        const data = await response.json()
        setPriceHistory(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    if (offer) {
      fetchPriceHistory()
    }
  }, [offer])

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getPriceChange = (current, previous) => {
    if (!previous) return null
    const change = current - previous
    const percentage = (change / previous) * 100
    return { change, percentage }
  }

  if (!offer) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Price History</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="modal-body">
          <div className="offer-summary">
            <img src={offer.image_url} alt={offer.title} className="offer-thumbnail" />
            <div className="offer-details">
              <h3>{offer.title}</h3>
              <p className="offer-price">
                ${offer.last_price} {offer.currency}
              </p>
              <p className="offer-source">Source: {offer.source}</p>
            </div>
          </div>

          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading price history...</p>
            </div>
          ) : error ? (
            <div className="error-message">
              <p>{error}</p>
            </div>
          ) : priceHistory.length === 0 ? (
            <div className="empty-state">
              <p>No price history available for this offer.</p>
            </div>
          ) : (
            <div className="price-history">
              <h3>Price Changes</h3>
              <div className="price-history-list">
                {priceHistory.map((entry, index) => {
                  const priceChange = index < priceHistory.length - 1 
                    ? getPriceChange(entry.price, priceHistory[index + 1].price)
                    : null

                  return (
                    <div key={entry.id} className="price-entry">
                      <div className="price-info">
                        <span className="price-amount">${entry.price}</span>
                        <span className="price-date">{formatDate(entry.date)}</span>
                      </div>
                      {priceChange && (
                        <div className={`price-change ${priceChange.change >= 0 ? 'increase' : 'decrease'}`}>
                          {priceChange.change >= 0 ? (
                            <TrendingUp size={16} />
                          ) : (
                            <TrendingDown size={16} />
                          )}
                          <span>
                            {priceChange.change >= 0 ? '+' : ''}${Math.abs(priceChange.change).toFixed(2)} 
                            ({priceChange.change >= 0 ? '+' : ''}{priceChange.percentage.toFixed(1)}%)
                          </span>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PriceHistoryModal
