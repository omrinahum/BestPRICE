import { useState } from 'react'
import { Package } from 'lucide-react'
import OfferCard from './OfferCard'
import FiltersPanel from './FiltersPanel'
import Pagination from './Pagination'

const OffersGrid = ({ offers, loading, pagination, onOfferClick, onFiltersChange, onPageChange }) => {
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

  const handleFiltersChange = (newFilters) => {
    const updatedFilters = { ...filters, ...newFilters, page: 1 } // Reset to page 1 when filters change
    setFilters(updatedFilters)
    onFiltersChange(updatedFilters)
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading offers...</p>
      </div>
    )
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
