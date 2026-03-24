import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  user_id: string
  username: string
  email?: string
  api_key: string
}

interface AuthContextType {
  user: User | null
  apiKey: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const API_BASE = 'http://localhost:8000'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser]     = useState<User | null>(null)
  const [apiKey, setApiKey] = useState<string | null>(() => localStorage.getItem('api_key'))
  const [checked, setChecked] = useState(false)   // has startup validation run?

  // On mount: validate stored key once. If server is down, keep the key anyway
  // (don't aggressively log the user out just because the server is offline).
  useEffect(() => {
    const stored = localStorage.getItem('api_key')
    if (!stored) {
      setChecked(true)
      return
    }
    // Try to validate, but don't clear the key on network errors
    fetch(`${API_BASE}/auth/me`, { headers: { 'X-API-Key': stored } })
      .then(res => {
        if (res.ok) {
          return res.json().then(data => {
            setUser({ ...data, api_key: stored })
            setApiKey(stored)
          })
        }
        // Only clear on an explicit 401 (bad key), not on network errors
        if (res.status === 401) {
          localStorage.removeItem('api_key')
          setApiKey(null)
          setUser(null)
        }
        // For other status codes (500, etc.) — keep the stored key
      })
      .catch(() => {
        // Network error / server down — keep user logged in optimistically
        // They'll get a proper error when they try to use the API
      })
      .finally(() => setChecked(true))
  }, [])

  const login = async (username: string, password: string): Promise<void> => {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })

    if (!response.ok) {
      let detail = 'Login failed'
      try {
        const body = await response.json()
        detail = body.detail || detail
      } catch { /* ignore */ }
      throw new Error(detail)
    }

    const data = await response.json()
    const key  = data.api_key as string
    localStorage.setItem('api_key', key)
    setApiKey(key)
    setUser({ user_id: data.user_id, username: data.username, api_key: key })
  }

  const register = async (username: string, email: string, password: string): Promise<void> => {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    })

    if (!response.ok) {
      let detail = 'Registration failed'
      try {
        const body = await response.json()
        detail = body.detail || detail
      } catch { /* ignore */ }
      throw new Error(detail)
    }

    const data = await response.json()
    const key  = data.api_key as string
    localStorage.setItem('api_key', key)
    setApiKey(key)
    setUser({ user_id: data.user_id, username: data.username, api_key: key })
  }

  const logout = () => {
    setUser(null)
    setApiKey(null)
    localStorage.removeItem('api_key')
  }

  // Don't render children until the startup key check is done.
  // This prevents a flash of the login page when the user is already authenticated.
  if (!checked) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#080810',
      }}>
        <div style={{
          width: 32, height: 32,
          border: '2px solid rgba(212,175,55,0.2)',
          borderTop: '2px solid #D4AF37',
          borderRadius: '50%',
          animation: 'spin 0.7s linear infinite',
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    )
  }

  return (
    <AuthContext.Provider value={{
      user,
      apiKey,
      isAuthenticated: !!apiKey,
      login,
      register,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}

export function useApiKey() {
  return useAuth().apiKey
}
