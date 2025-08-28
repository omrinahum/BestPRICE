import { useState } from 'react'
import { Search as SearchIcon } from 'lucide-react'

const SearchForm = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch({ query: query.trim() })
    }
  }

  return (
    <div className="search-form">
      <form onSubmit={handleSubmit}>
        <div className="search-input-group">
          <SearchIcon className="search-input-icon" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for products (e.g., 'iPhone 15', 'Samsung TV')"
            className="search-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={loading || !query.trim()}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default SearchForm

