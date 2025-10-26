import { useState, useEffect } from 'react'
import { X, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

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
      month: 'short',
      day: 'numeric'
    })
  }

  const formatFullDate = (dateString) => {
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

  const getPriceStats = () => {
    if (priceHistory.length === 0) return null
    
    const prices = priceHistory.map(h => parseFloat(h.price))
    const minPrice = Math.min(...prices)
    const maxPrice = Math.max(...prices)
    const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length
    
    const firstPrice = parseFloat(priceHistory[0].price)
    const lastPrice = parseFloat(priceHistory[priceHistory.length - 1].price)
    const totalChange = lastPrice - firstPrice
    const totalChangePercent = (totalChange / firstPrice) * 100
    
    return { minPrice, maxPrice, avgPrice, totalChange, totalChangePercent }
  }

  const formatChartData = () => {
    return priceHistory.map(entry => ({
      date: formatDate(entry.fetched_at),
      fullDate: formatFullDate(entry.fetched_at),
      price: parseFloat(entry.price)
    }))
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: 0, fontWeight: 'bold', color: '#0e5f58' }}>
            ${payload[0].value.toFixed(2)}
          </p>
          <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>
            {payload[0].payload.fullDate}
          </p>
        </div>
      )
    }
    return null
  }

  if (!offer) return null

  const stats = getPriceStats()
  const chartData = formatChartData()

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-content">
            <h2>Price History</h2>
            <p className="modal-subtitle">
              {offer.title.length > 60 ? offer.title.substring(0, 60) + '...' : offer.title}
            </p>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        
        <div className="modal-body">
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
              <BarChart3 size={48} />
              <p>No price history available for this offer.</p>
              <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
                Price history will accumulate as this item is tracked over time.
              </p>
            </div>
          ) : (
            <div className="price-history">
              {/* Price Chart */}
              <div className="price-chart">
                <div className="chart-header">
                  <h3>Price Trend (Last 60 Days)</h3>
                  {stats && (
                    <span className={`price-change-badge ${stats.totalChange >= 0 ? 'positive' : 'negative'}`}>
                      {stats.totalChange >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                      {stats.totalChange >= 0 ? '+' : ''}${Math.abs(stats.totalChange).toFixed(2)} 
                      ({stats.totalChange >= 0 ? '+' : ''}{stats.totalChangePercent.toFixed(1)}%)
                    </span>
                  )}
                </div>
                
                <ResponsiveContainer width="100%" height={240}>
                  <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 11, fill: '#666' }}
                      stroke="#999"
                      interval="preserveStartEnd"
                    />
                    <YAxis 
                      domain={['auto', 'auto']}
                      tick={{ fontSize: 11, fill: '#666' }}
                      stroke="#999"
                      tickFormatter={(value) => `$${value.toFixed(0)}`}
                      width={50}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#0e5f58" 
                      strokeWidth={2.5}
                      dot={false}
                      activeDot={{ r: 5, fill: '#0e5f58' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Price Statistics */}
              {stats && (
                <div className="price-stats">
                  <div className="stat-item">
                    <span className="stat-label">Lowest Price</span>
                    <span className="stat-value">${stats.minPrice.toFixed(2)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Highest Price</span>
                    <span className="stat-value">${stats.maxPrice.toFixed(2)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Average Price</span>
                    <span className="stat-value">${stats.avgPrice.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PriceHistoryModal
