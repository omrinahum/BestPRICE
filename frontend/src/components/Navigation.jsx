import { useAuth } from '../contexts/AuthContext'
import { Package, LogOut, User } from 'lucide-react'

const Navigation = () => {
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <Package className="logo-icon" />
          <h1>BestPRICE</h1>
        </div>
        <p className="tagline">Find the best prices across multiple sources</p>
        
        {user && (
          <div className="nav-user">
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
