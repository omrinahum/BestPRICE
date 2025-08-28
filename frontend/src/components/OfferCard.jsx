import { ExternalLink, TrendingUp, Star, User, Package } from 'lucide-react'

const OfferCard = ({ offer, onClick }) => {
  const handleCardClick = () => {
    window.open(offer.url, '_blank')
  }

  const handlePriceHistoryClick = (e) => {
    e.stopPropagation()
    onClick(offer)
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
            <TrendingUp size={16} />
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
            <ExternalLink size={16} />
            View
          </button>
        </div>
      </div>
    </div>
  )
}

export default OfferCard

