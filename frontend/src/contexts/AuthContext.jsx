import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }, [token])

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        try {
          // Verify token is still valid by making a request to a protected endpoint
          const response = await axios.get('http://localhost:8000/auth/me', {
            headers: { Authorization: `Bearer ${storedToken}` }
          })
          setUser(response.data)
          setToken(storedToken)
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('token')
          setToken(null)
          setUser(null)
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:8000/auth/login', {
        username,
        password
      })

      const { access_token, token_type } = response.data
      
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // Get user data after successful login
      const userResponse = await axios.get('http://localhost:8000/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      })
      setUser(userResponse.data)
      
      return { success: true }
    } catch (error) {
      let message = 'Login failed'
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          message = error.response.data.detail.map(err => err.msg).join(', ')
        } else {
          message = error.response.data.detail
        }
      }
      return { success: false, error: message }
    }
  }

  const register = async (username, email, password, fullName) => {
    try {
      const response = await axios.post('http://localhost:8000/auth/register', {
        username,
        email,
        password,
        full_name: fullName
      })

      const userData = response.data
      
      // After registration, login to get token
      const loginResult = await login(username, password)
      return loginResult
      
    } catch (error) {
      let message = 'Registration failed'
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          message = error.response.data.detail.map(err => err.msg).join(', ')
        } else {
          message = error.response.data.detail
        }
      }
      return { success: false, error: message }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    delete axios.defaults.headers.common['Authorization']
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
