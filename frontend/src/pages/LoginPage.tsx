import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Sparkles, Lock, User, Mail, ArrowLeft, Eye, EyeOff, ChevronRight } from 'lucide-react'

export function LoginPage() {
  const [isLogin, setIsLogin]     = useState(true)
  const [username, setUsername]   = useState('')
  const [email, setEmail]         = useState('')
  const [password, setPassword]   = useState('')
  const [showPw, setShowPw]       = useState(false)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState('')
  const { login, register }       = useAuth()
  const navigate                  = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) {
      setError('Please fill in all fields')
      return
    }
    setError('')
    setLoading(true)
    try {
      if (isLogin) {
        await login(username.trim(), password)
      } else {
        if (!email.trim()) { setError('Email is required'); setLoading(false); return }
        await register(username.trim(), email.trim(), password)
      }
      navigate('/app')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = () => {
    setUsername('admin')
    setPassword('admin123')
    setError('')
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute -top-40 -left-20 w-[500px] h-[500px] rounded-full bg-[#D4AF37]/4 blur-[130px]" />
        <div className="absolute -bottom-20 -right-20 w-[400px] h-[400px] rounded-full bg-[#00CED1]/3 blur-[110px]" />
      </div>

      <div className="w-full max-w-[380px] relative z-10 fade-in">

        {/* Back link */}
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-gray-500 hover:text-[#D4AF37] text-sm mb-7 transition-colors group"
        >
          <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" />
          Back to home
        </Link>

        {/* Logo */}
        <div className="text-center mb-7">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-[#D4AF37] to-[#996515] mb-4 shadow-xl shadow-yellow-900/25">
            <Sparkles className="w-7 h-7 text-black" />
          </div>
          <h1 className="text-2xl font-bold gradient-text mb-1">DataFlow</h1>
          <p className="text-gray-500 text-sm">
            {isLogin ? 'Sign in to your account' : 'Create a new account'}
          </p>
        </div>

        {/* Card */}
        <div className="glass p-7">
          <form onSubmit={handleSubmit} noValidate>
            <div className="space-y-4">

              {/* Username field */}
              <div>
                <label className="block text-xs text-gray-500 mb-1.5 font-medium">Username</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none z-10" />
                  <input
                    type="text"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    className="input-gold pl-9"
                    placeholder="Enter username"
                    autoComplete="username"
                    autoCapitalize="none"
                    spellCheck={false}
                  />
                </div>
              </div>

              {/* Email (register only) */}
              {!isLogin && (
                <div>
                  <label className="block text-xs text-gray-500 mb-1.5 font-medium">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none z-10" />
                    <input
                      type="email"
                      value={email}
                      onChange={e => setEmail(e.target.value)}
                      className="input-gold pl-9"
                      placeholder="Enter email"
                      autoComplete="email"
                    />
                  </div>
                </div>
              )}

              {/* Password field */}
              <div>
                <label className="block text-xs text-gray-500 mb-1.5 font-medium">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none z-10" />
                  <input
                    type={showPw ? 'text' : 'password'}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="input-gold pl-9 pr-10"
                    placeholder="Enter password"
                    autoComplete={isLogin ? 'current-password' : 'new-password'}
                  />
                  <button
                    type="button"
                    tabIndex={-1}
                    onClick={() => setShowPw(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-300 transition-colors p-0.5"
                    aria-label={showPw ? 'Hide password' : 'Show password'}
                  >
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Error message */}
              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm leading-relaxed">
                  {error}
                </div>
              )}

              {/* Submit button */}
              <button
                type="submit"
                disabled={loading}
                className="btn-gold w-full flex items-center justify-center gap-2 py-3 mt-1"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-black/25 border-t-black rounded-full animate-spin" />
                ) : (
                  <>
                    {isLogin ? 'Sign In' : 'Create Account'}
                    <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Toggle login/register */}
          <div className="mt-5 pt-5 border-t border-white/5 text-center">
            <p className="text-gray-500 text-sm">
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <button
                type="button"
                onClick={() => { setIsLogin(v => !v); setError('') }}
                className="text-[#D4AF37] hover:text-[#F4E4BA] font-medium transition-colors"
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </button>
            </p>
          </div>
        </div>

        {/* Demo credentials — subtle, clickable */}
        <button
          type="button"
          onClick={fillDemo}
          className="w-full mt-3 py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 text-xs text-gray-500 hover:text-[#D4AF37] transition-colors group"
        >
          <span>Demo:</span>
          <span className="text-gray-400 group-hover:text-[#D4AF37] font-mono transition-colors">admin / admin123</span>
          <span className="text-gray-600 group-hover:text-[#D4AF37] transition-colors">— click to fill</span>
        </button>

      </div>
    </div>
  )
}
