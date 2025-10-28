import { useState } from 'react'
import './App.css'
import SearchForm from './components/SearchForm'
import OffersGrid from './components/OffersGrid'
import PriceHistoryModal from './components/PriceHistoryModal'
import Navigation from './components/Navigation'
import Login from './components/Login'
import Register from './components/Register'
import ProtectedRoute from './components/ProtectedRoute'
import Sidebar from './components/Sidebar'
import WatchlistView from './components/WatchlistView'
import BestDealsPage from './components/BestDealsPage'
import { useAuth } from './contexts/AuthContext'
import { Search, Package, TrendingUp, X } from 'lucide-react'

function App() {
  const { isAuthenticated, loading: authLoading } = useAuth()
  const [currentSearch, setCurrentSearch] = useState(null)
  const [offers, setOffers] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 20,
    total_count: 0,
    total_pages: 0
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedOffer, setSelectedOffer] = useState(null)
  const [showPriceHistory, setShowPriceHistory] = useState(false)
  const [showWelcome, setShowWelcome] = useState(true)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState('login') // 'login' or 'register'
  const [currentView, setCurrentView] = useState('search') // 'search', 'watchlist', or 'best-deals'
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const handleSearch = async (searchData) => {
    setLoading(true)
    setError(null)
    setShowWelcome(false)
    try {
      console.log('Sending search request:', searchData)
      
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(searchData),
      })
      
      console.log('Response status:', response.status)
      console.log('Response headers:', response.headers)
      
      if (!response.ok) {
        const errorData = await response.json()
        console.error('Error response:', errorData)
        throw new Error(errorData.detail || 'Search failed')
      }
      
      const searchResult = await response.json()
      console.log('Search result:', searchResult)
      setCurrentSearch(searchResult)
      
      // Reset pagination to page 1 for new search
      await fetchOffers(searchResult.id, { page: 1 })
    } catch (err) {
      console.error('Search error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fetchOffers = async (searchId, filters = {}) => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        search_id: searchId,
        page: filters.page || pagination.page,
        page_size: filters.page_size || pagination.page_size,
        sort_by: filters.sort_by || 'last_price',
        sort_order: filters.sort_order || 'asc',
      })
      
      if (filters.min_price) params.append('min_price', filters.min_price)
      if (filters.max_price) params.append('max_price', filters.max_price)
      if (filters.source) params.append('source', filters.source)
      if (filters.min_rating) params.append('min_rating', filters.min_rating)
      
      const url = `http://localhost:8000/offers/?${params}`
      console.log('Fetching offers from:', url)
      
      const token = localStorage.getItem('token')
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      console.log('Offers response status:', response.status)
      
      if (!response.ok) {
        const errorData = await response.json()
        console.error('Offers error response:', errorData)
        throw new Error(errorData.detail || 'Failed to fetch offers')
      }
      
      const responseData = await response.json()
      console.log('Offers data:', responseData)
      
      setOffers(responseData.offers || [])
      setPagination({
        page: responseData.pagination?.page || 1,
        page_size: responseData.pagination?.page_size || 20,
        total_count: responseData.pagination?.total_count || 0,
        total_pages: responseData.pagination?.total_pages || 0,
        sort_by: filters.hasOwnProperty('sort_by') ? filters.sort_by : (pagination.sort_by || 'last_price'),
        sort_order: filters.hasOwnProperty('sort_order') ? filters.sort_order : (pagination.sort_order || 'asc'),
        min_price: filters.hasOwnProperty('min_price') ? filters.min_price : (pagination.min_price || ''),
        max_price: filters.hasOwnProperty('max_price') ? filters.max_price : (pagination.max_price || ''),
        source: filters.hasOwnProperty('source') ? filters.source : (pagination.source || ''),
        min_rating: filters.hasOwnProperty('min_rating') ? filters.min_rating : (pagination.min_rating || '')
      })
    } catch (err) {
      console.error('Fetch offers error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handlePageChange = (newPage) => {
    if (currentSearch) {
      // Preserve current sorting and filtering state when changing pages
      const currentFilters = {
        page: newPage,
        sort_by: pagination.sort_by,
        sort_order: pagination.sort_order,
        min_price: pagination.min_price,
        max_price: pagination.max_price,
        source: pagination.source,
        min_rating: pagination.min_rating
      }
      fetchOffers(currentSearch.id, currentFilters)
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

  const handleGetStarted = () => {
    if (isAuthenticated) {
      setShowWelcome(false)
    } else {
      setAuthMode('login')
      setShowAuthModal(true)
    }
  }

  const handleCloseAuthModal = () => {
    setShowAuthModal(false)
    // If user just logged in, hide welcome screen
    if (isAuthenticated) {
      setShowWelcome(false)
    }
  }

  const handleAuthSuccess = () => {
    setShowAuthModal(false)
    setShowWelcome(false)
  }

  const handleSwitchAuthMode = () => {
    setAuthMode(authMode === 'login' ? 'register' : 'login')
  }

  const handleWatchlistClick = () => {
    setCurrentView('watchlist')
    setShowWelcome(false)
  }

  const handleSearchClick = () => {
    setCurrentView('search')
  }

  const handleBestDealsClick = () => {
    setCurrentView('best-deals')
    setShowWelcome(false)
  }

  if (authLoading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <Navigation />
      
      <div className="app-layout">
        <Sidebar 
          onWatchlistClick={handleWatchlistClick}
          onSearchClick={handleSearchClick}
          onBestDealsClick={handleBestDealsClick}
          currentView={currentView}
        />
        
        <main className="main-content">
          {showWelcome ? (
            <div className="welcome-section">
              <div className="welcome-content">
                <h1>Welcome to BestPRICE</h1>
                <p>Find the best prices across multiple sources. Compare prices, track history, and make informed purchasing decisions.</p>
                <div className="welcome-features">
                  <div className="feature">
                    <Search className="feature-icon" />
                    <span>Smart Search</span>
                  </div>
                  <div className="feature">
                    <TrendingUp className="feature-icon" />
                    <span>Price Tracking</span>
                  </div>
                  <div className="feature">
                    <Package className="feature-icon" />
                    <span>Multiple Sources</span>
                  </div>
                </div>
                <button className="get-started-button" onClick={handleGetStarted}>
                  Get Started
                </button>
              </div>
            </div>
          ) : (
            <ProtectedRoute>
              {currentView === 'search' ? (
                <>
                  <SearchForm onSearch={handleSearch} loading={loading} />
                  
                  {error && (
                    <div className="error-message">
                      <p>{error}</p>
                    </div>
                  )}

                  {currentSearch && (
                    <div className="search-results">
                      <OffersGrid 
                        offers={offers}
                        loading={loading}
                        pagination={pagination}
                        onOfferClick={handleOfferClick}
                        onFiltersChange={(filters) => fetchOffers(currentSearch.id, filters)}
                        onPageChange={handlePageChange}
                      />
                    </div>
                  )}

                  {showPriceHistory && selectedOffer && (
                    <PriceHistoryModal
                      offer={selectedOffer}
                      onClose={handleClosePriceHistory}
                    />
                  )}
                </>
              ) : currentView === 'watchlist' ? (
                <WatchlistView />
              ) : (
                <BestDealsPage />
              )}
            </ProtectedRoute>
          )}
        </main>
      </div>


      {/* Authentication Modal */}
      {showAuthModal && (
        <div className="modal-overlay">
          <div className="auth-modal">
            <button className="auth-modal-close" onClick={handleCloseAuthModal}>
              <X size={24} />
            </button>
            {authMode === 'login' ? (
              <Login 
                onSwitchToRegister={handleSwitchAuthMode}
                onClose={handleCloseAuthModal}
                onSuccess={handleAuthSuccess}
              />
            ) : (
              <Register 
                onSwitchToLogin={handleSwitchAuthMode}
                onClose={handleCloseAuthModal}
                onSuccess={handleAuthSuccess}
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
