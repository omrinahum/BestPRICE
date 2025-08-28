import { useEffect, useRef, useState } from 'react'
import { Filter, SortAsc, SortDesc, ChevronDown } from 'lucide-react'

const FiltersPanel = ({ filters, onFiltersChange, offerCount }) => {
  const [localMin, setLocalMin] = useState(filters.min_price || '')
  const [localMax, setLocalMax] = useState(filters.max_price || '')
  const [localSource, setLocalSource] = useState(filters.source || '')
  const [localMinRating, setLocalMinRating] = useState(filters.min_rating || '')
  const [collapsed, setCollapsed] = useState(true)
  const debounceRef = useRef(null)

  // Sync from parent only when values actually differ to avoid loops
  useEffect(() => {
    const minFromProps = filters.min_price || ''
    const maxFromProps = filters.max_price || ''
    const sourceFromProps = filters.source || ''
    const minRatingFromProps = filters.min_rating || ''
    if (minFromProps !== localMin) setLocalMin(minFromProps)
    if (maxFromProps !== localMax) setLocalMax(maxFromProps)
    if (sourceFromProps !== localSource) setLocalSource(sourceFromProps)
    if (minRatingFromProps !== localMinRating) setLocalMinRating(minRatingFromProps)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.min_price, filters.max_price, filters.source, filters.min_rating])

  // Debounce user typing; only fire when values changed vs current filters
  useEffect(() => {
    const minFromProps = filters.min_price || ''
    const maxFromProps = filters.max_price || ''
    const sourceFromProps = filters.source || ''
    const minRatingFromProps = filters.min_rating || ''
    const changed = localMin !== minFromProps || localMax !== maxFromProps || 
                   localSource !== sourceFromProps || localMinRating !== minRatingFromProps
    if (!changed) return

    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      onFiltersChange({ 
        min_price: localMin, 
        max_price: localMax, 
        source: localSource,
        min_rating: localMinRating,
        page: 1 
      })
    }, 800)
    return () => clearTimeout(debounceRef.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [localMin, localMax, localSource, localMinRating])

  const handleSortChange = (sortBy) => {
    const newSortOrder = filters.sort_by === sortBy && filters.sort_order === 'asc' ? 'desc' : 'asc'
    onFiltersChange({ sort_by: sortBy, sort_order: newSortOrder, page: 1 })
  }

  const clearFilters = () => {
    setLocalMin('')
    setLocalMax('')
    setLocalSource('')
    setLocalMinRating('')
    onFiltersChange({
      min_price: '',
      max_price: '',
      source: '',
      min_rating: '',
      sort_by: 'last_price',
      sort_order: 'asc',
      page: 1,
    })
  }

  return (
    <div className={`filters-panel ${collapsed ? 'collapsed' : ''}`}>
      <button className="filters-header" onClick={() => setCollapsed((c) => !c)} aria-expanded={!collapsed} aria-controls="filters-content">
        <div className="filters-title">
          <Filter size={16} />
          <span>Filters</span>
        </div>
        <div className="filters-header-right">
          <span className="offer-count">{offerCount} offers</span>
          <ChevronDown size={16} className={`collapse-arrow ${collapsed ? '' : 'open'}`} />
        </div>
      </button>

      <div id="filters-content" className="filters-content">
        <div className="filters-row">
          <div className="filter-group">
            <label>Price Range</label>
            <div className="price-inputs">
              <input
                type="number"
                placeholder="Min"
                value={localMin}
                onChange={(e) => setLocalMin(e.target.value)}
                className="price-input"
                inputMode="numeric"
              />
              <span className="price-separator">-</span>
              <input
                type="number"
                placeholder="Max"
                value={localMax}
                onChange={(e) => setLocalMax(e.target.value)}
                className="price-input"
                inputMode="numeric"
              />
            </div>
          </div>

          <div className="filter-group">
            <label>Source</label>
            <select
              value={localSource}
              onChange={(e) => setLocalSource(e.target.value)}
              className="source-select"
            >
              <option value="">All Sources</option>
              <option value="dummyjson">DummyJSON</option>
              <option value="ebay">eBay</option>
              <option value="amazon">Amazon</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Min Rating</label>
            <input
              type="number"
              placeholder="Any"
              min="0"
              max="5"
              step="0.1"
              value={localMinRating}
              onChange={(e) => setLocalMinRating(e.target.value)}
              className="rating-input"
            />
          </div>

          <div className="filter-group">
            <label>Sort by</label>
            <div className="sort-buttons">
              <button
                className={`sort-button ${filters.sort_by === 'last_price' ? 'active' : ''}`}
                onClick={() => handleSortChange('last_price')}
              >
                Price
                {filters.sort_by === 'last_price' && (
                  filters.sort_order === 'asc' ? <SortAsc size={12} /> : <SortDesc size={12} />
                )}
              </button>
              <button
                className={`sort-button ${filters.sort_by === 'rating' ? 'active' : ''}`}
                onClick={() => handleSortChange('rating')}
              >
                Rating
                {filters.sort_by === 'rating' && (
                  filters.sort_order === 'asc' ? <SortAsc size={12} /> : <SortDesc size={12} />
                )}
              </button>
            </div>
          </div>

          <button className="clear-filters-button" onClick={clearFilters}>
            Clear
          </button>
        </div>
      </div>
    </div>
  )
}

export default FiltersPanel
