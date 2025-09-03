import React, { useState, useEffect } from 'react';
import { Heart } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import OfferCard from './OfferCard';

const WatchlistView = () => {
  const [watchlistItems, setWatchlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/user/watchlist', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch watchlist');
      }

      const data = await response.json();
      setWatchlistItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleWatchlistUpdate = (offerId, isAdding, newItem = null) => {
    if (isAdding && newItem) {
      setWatchlistItems(prev => [...prev, newItem]);
    } else {
      setWatchlistItems(prev => prev.filter(item => item.offer_id !== offerId));
    }
  };

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return `$${parseFloat(price).toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="main">
        <div className="section-header">
          <h2>My Watchlist</h2>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your watchlist...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="main">
        <div className="section-header">
          <h2>My Watchlist</h2>
        </div>
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={fetchWatchlist} className="retry-button">Try Again</button>
        </div>
      </div>
    );
  }

  // Convert watchlist items to offer format for OfferCard
  const convertToOfferFormat = (item) => ({
    id: item.offer_id,
    title: item.product_title,
    url: item.product_url,
    last_price: item.current_price,
    source: item.source,
    image_url: item.product_image_url,
    created_at: item.created_at
  });

  return (
    <div className="main">
      <div className="section-header">
        <h2>My Watchlist</h2>
        <p className="section-subtitle">
          {watchlistItems.length} {watchlistItems.length === 1 ? 'item' : 'items'} saved
        </p>
      </div>

      {watchlistItems.length === 0 ? (
        <div className="empty-state">
          <Heart size={48} />
          <h3>Your watchlist is empty</h3>
          <p>Start adding items to your watchlist to track prices and availability.</p>
        </div>
      ) : (
        <div className="offers-grid">
          {watchlistItems.map((item) => (
            <OfferCard
              key={item.id}
              offer={convertToOfferFormat(item)}
              userWatchlist={watchlistItems}
              onWatchlistUpdate={handleWatchlistUpdate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default WatchlistView;
