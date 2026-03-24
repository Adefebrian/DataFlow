import { Component, ErrorInfo, ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import { UploadPage }           from './pages/UploadPage'
import { DashboardPage }        from './pages/DashboardPage'
import { JobDetailPage }        from './pages/JobDetailPage'
import { LoginPage }            from './pages/LoginPage'
import { LandingPage }          from './pages/LandingPage'
import { MyDashboardPage }      from './pages/MyDashboardPage'
import { CustomAnalyticsPage }  from './pages/CustomAnalyticsPage'
import { AuthProvider, useAuth } from './hooks/useAuth'
import { ThemeProvider, useTheme } from './hooks/useTheme'
import { DashboardProvider } from './hooks/useDashboard'
import { Sparkles, BarChart3, Upload, LogOut, Home, LayoutDashboard, Sun, Moon, SlidersHorizontal } from 'lucide-react'

// ─── Error Boundary ───────────────────────────────────────────────────────────
class ErrorBoundary extends Component<
  { children: ReactNode },
  { error: Error | null }
> {
  state = { error: null as Error | null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('App crash:', error, info)
  }

  render() {
    if (this.state.error) {
      const err = this.state.error
      return (
        <div style={{
          minHeight: '100vh', display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          background: '#080810', color: '#e0e0e0', padding: 32, textAlign: 'center',
        }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
          <h2 style={{ color: '#D4AF37', marginBottom: 8, fontSize: 20 }}>
            Something went wrong
          </h2>
          <pre style={{
            color: '#888', marginBottom: 24, maxWidth: 560,
            fontSize: 12, whiteSpace: 'pre-wrap', textAlign: 'left',
            background: 'rgba(255,255,255,0.04)', padding: '12px 16px',
            borderRadius: 8, border: '1px solid rgba(255,255,255,0.06)',
          }}>
            {err.message}
          </pre>
          <button
            onClick={() => { this.setState({ error: null }); window.location.reload() }}
            style={{
              background: '#D4AF37', color: '#000', border: 'none',
              borderRadius: 12, padding: '12px 28px',
              fontWeight: 700, cursor: 'pointer', fontSize: 14,
            }}
          >
            Reload Page
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

// ─── Theme Toggle ─────────────────────────────────────────────────────────────
function ThemeToggle() {
  const { theme, toggle } = useTheme()
  return (
    <button
      onClick={toggle}
      className="flex items-center justify-center w-8 h-8 rounded-xl transition-all"
      style={{
        background: 'var(--bg-input)',
        border: '1px solid var(--border-faint)',
        color: 'var(--text-muted)',
      }}
      title={theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}
    >
      {theme === 'dark'
        ? <Sun  className="w-3.5 h-3.5" style={{ color: 'var(--gold)' }} />
        : <Moon className="w-3.5 h-3.5" style={{ color: 'var(--gold)' }} />}
    </button>
  )
}

// ─── NavLink ──────────────────────────────────────────────────────────────────
function NavLink({ to, icon: Icon, label }: { to: string; icon: any; label: string }) {
  const location = useLocation()
  const isActive =
    location.pathname === to ||
    (to !== '/' && to !== '/app' && location.pathname.startsWith(to))
  return (
    <Link to={to} className={`nav-link flex items-center gap-2 ${isActive ? 'active' : ''}`}>
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </Link>
  )
}

// ─── Auth Guard ───────────────────────────────────────────────────────────────
function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

// ─── App Shell ────────────────────────────────────────────────────────────────
function AppShell() {
  const { logout, user, isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen">
      {isAuthenticated && (
        <nav
          className="glass sticky top-0 z-50 px-6 py-4"
          style={{
            borderRadius: 0,
            borderTop: 'none', borderLeft: 'none', borderRight: 'none',
            borderBottom: '1px solid rgba(212,175,55,0.08)',
          }}
        >
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#D4AF37] to-[#996515] flex items-center justify-center shadow-md shadow-yellow-900/30 group-hover:shadow-lg transition-all duration-200">
                <Sparkles className="w-5 h-5 text-black" />
              </div>
              <span className="text-xl font-bold gradient-text">DataFlow</span>
            </Link>

            {/* Nav */}
            <div className="flex items-center gap-1">
              <NavLink to="/app"       icon={Upload}             label="Upload"    />
              <NavLink to="/jobs"      icon={BarChart3}          label="Jobs"      />
              <NavLink to="/custom"    icon={SlidersHorizontal}  label="Custom"    />
              <NavLink to="/dashboard" icon={LayoutDashboard}    label="Dashboard" />
              <NavLink to="/"          icon={Home}               label="Home"      />
            </div>

            {/* Right: theme + user + logout */}
            <div
              className="flex items-center gap-2 pl-4"
              style={{ borderLeft: '1px solid rgba(212,175,55,0.1)' }}
            >
              <ThemeToggle />
              <div className="flex items-center gap-2 ml-1">
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center"
                  style={{
                    background: 'rgba(212,175,55,0.15)',
                    border: '1px solid rgba(212,175,55,0.2)',
                  }}
                >
                  <span
                    className="text-xs font-bold leading-none"
                    style={{ color: 'var(--gold)' }}
                  >
                    {user?.username?.[0]?.toUpperCase() ?? '?'}
                  </span>
                </div>
                <span
                  className="text-sm hidden sm:block"
                  style={{ color: 'var(--text-muted)' }}
                >
                  {user?.username}
                </span>
              </div>
              <button
                onClick={logout}
                className="btn-outline p-2 rounded-lg"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </nav>
      )}

      <main className="max-w-7xl mx-auto px-6 py-8">
        <Routes>
          <Route path="/app"         element={<ProtectedRoute><UploadPage /></ProtectedRoute>} />
          <Route path="/jobs"        element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/jobs/:jobId" element={<ProtectedRoute><JobDetailPage /></ProtectedRoute>} />
          <Route path="/custom"      element={<ProtectedRoute><CustomAnalyticsPage /></ProtectedRoute>} />
          <Route path="/dashboard"   element={<ProtectedRoute><MyDashboardPage /></ProtectedRoute>} />
          <Route path="*"            element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

// ─── Root ─────────────────────────────────────────────────────────────────────
function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ThemeProvider>
          <AuthProvider>
            <DashboardProvider>
              <Routes>
                <Route path="/"      element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/*"     element={<AppShell />} />
              </Routes>
            </DashboardProvider>
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
