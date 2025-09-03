import { useAuth } from '../contexts/AuthContext'
import { Package, LogOut, User } from 'lucide-react'

const Navigation = () => {
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    // Force redirect to home page after logout
    window.location.href = '/'
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo">
            <Package className="logo-icon" />
            <h1>BestPRICE</h1>
          </div>
        </div>
        
        {user && (
          <div className="header-right">
            <div className="user-info">
              <User className="user-icon" />
              <span className="user-name">{user.full_name}</span>
            </div>
            <button className="logout-button" onClick={handleLogout}>
              <LogOut size={18} />
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

export default Navigation
