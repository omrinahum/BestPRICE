# BestPRICE Frontend

A clean, responsive React application for finding the best prices across multiple sources. Built with Vite and React.

## Features

- **Search Interface**: Clean search form with real-time validation
- **Offers Grid**: Responsive grid layout displaying product offers
- **Price History**: Modal view showing price trends over time
- **Filtering & Sorting**: Server-side filtering by price range and sorting options
- **Responsive Design**: Mobile-first design that works on all devices
- **Error Handling**: Comprehensive error states and loading indicators

## Tech Stack

- **React 19**: Latest React with hooks and modern patterns
- **Vite**: Fast build tool and development server
- **Lucide React**: Beautiful, customizable icons
- **CSS3**: Modern styling with Flexbox and Grid
- **Fetch API**: Native browser API for HTTP requests

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## API Integration

The frontend integrates with the following FastAPI endpoints:

- `POST /search/` - Create a new search
- `GET /offers` - Fetch offers with filtering and pagination
- `GET /offers/price/{offer_id}` - Get price history for an offer
- `GET /health` - Health check endpoint

### Data Models

#### Search
```javascript
{
  id: number,
  query: string,
  normalized_query: string,
  created_at: string
}
```

#### Offer
```javascript
{
  id: number,
  title: string,
  last_price: string,
  currency: string,
  url: string,
  source: string,
  source_offer_id: string,
  seller?: string,
  image_url?: string,
  rating?: number,
  created_at: string
}
```

#### Price History
```javascript
{
  id: number,
  price: string,
  currency: string,
  fetched_at: string
}
```

## Project Structure

```
src/
├── components/
│   ├── SearchForm.jsx          # Search input component
│   ├── OffersGrid.jsx          # Main offers display
│   ├── OfferCard.jsx           # Individual offer card
│   ├── FiltersPanel.jsx        # Filtering and sorting controls
│   └── PriceHistoryModal.jsx   # Price history modal
├── App.jsx                     # Main application component
├── App.css                     # Application styles
├── index.css                   # Global styles
└── main.jsx                    # Application entry point
```

## Features in Detail

### Search Functionality
- Real-time input validation
- Loading states during search
- Error handling with user-friendly messages
- Search result display with query information

### Offers Display
- Responsive grid layout (1 column on mobile, auto-fill on desktop)
- Product images with fallback for missing images
- Price, seller, and rating information
- Source badges for each offer
- External link buttons to view products

### Filtering & Sorting
- Price range filtering (min/max)
- Sort by price (ascending/descending)
- Sort by date (ascending/descending)
- Clear filters functionality
- Server-side filtering for performance

### Price History
- Modal popup with detailed price information
- Price change calculations and percentages
- Chronological price history list
- Loading and error states

### Responsive Design
- Mobile-first approach
- Breakpoints at 768px and 480px
- Flexible grid system
- Touch-friendly interface elements

## Styling

The application uses a modern, clean design with:

- **Color Scheme**: Purple gradient theme with green accents
- **Typography**: System font stack for optimal readability
- **Spacing**: Consistent 8px grid system
- **Shadows**: Subtle shadows for depth and hierarchy
- **Animations**: Smooth transitions and hover effects

## Error Handling

- Network error handling with retry options
- Validation error display
- Loading states for all async operations
- Empty state handling for no results
- Graceful degradation for missing data

## Performance

- Lazy loading of components
- Optimized re-renders with React hooks
- Efficient state management
- Minimal bundle size
- Fast development server with HMR

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

- Functional components with hooks
- Consistent naming conventions
- Proper prop validation
- Clean, readable code structure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the BestPRICE application suite.
