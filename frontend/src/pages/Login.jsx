import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Eye, EyeOff, AlertCircle, Loader } from 'lucide-react'

const MAX_ATTEMPTS  = 5
const LOCKOUT_MS    = 5 * 60 * 1000   // 5 minutes

export default function Login() {
  const { signInWithGoogle, signInWithEmail } = useAuth()
  const navigate = useNavigate()

  const [email,       setEmail]       = useState('')
  const [password,    setPassword]    = useState('')
  const [showPass,    setShowPass]    = useState(false)
  const [rememberMe,  setRememberMe]  = useState(false)
  const [error,       setError]       = useState('')
  const [loading,     setLoading]     = useState(false)
  const [attempts,    setAttempts]    = useState(0)
  const [lockedUntil, setLockedUntil] = useState(null)
  const [countdown,   setCountdown]   = useState(0)

  // Restore remembered email
  useEffect(() => {
    const saved = localStorage.getItem('jobminion_email')
    if (saved) { setEmail(saved); setRememberMe(true) }
  }, [])

  // Countdown timer for lockout
  useEffect(() => {
    if (!lockedUntil) return
    const interval = setInterval(() => {
      const remaining = Math.ceil((lockedUntil - Date.now()) / 1000)
      if (remaining <= 0) {
        setLockedUntil(null)
        setAttempts(0)
        setCountdown(0)
        clearInterval(interval)
      } else {
        setCountdown(remaining)
      }
    }, 1000)
    return () => clearInterval(interval)
  }, [lockedUntil])

  const isLocked = lockedUntil && Date.now() < lockedUntil

  const handleEmail = async (e) => {
    e.preventDefault()
    if (isLocked) return

    setLoading(true)
    setError('')

    const { error } = await signInWithEmail(email, password)

    if (error) {
      const newAttempts = attempts + 1
      setAttempts(newAttempts)

      if (newAttempts >= MAX_ATTEMPTS) {
        const until = Date.now() + LOCKOUT_MS
        setLockedUntil(until)
        setError(`Too many failed attempts. Please wait 5 minutes before trying again.`)
      } else {
        setError(`Invalid email or password. ${MAX_ATTEMPTS - newAttempts} attempt${MAX_ATTEMPTS - newAttempts !== 1 ? 's' : ''} remaining.`)
      }
      setLoading(false)
      return
    }

    // Success
    if (rememberMe) localStorage.setItem('jobminion_email', email)
    else            localStorage.removeItem('jobminion_email')

    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50
                    flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-indigo-600
                          rounded-xl mb-3">
            <span className="text-white text-xl font-bold">J</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome back</h1>
          <p className="text-gray-500 text-sm mt-1">Sign in to JobMinion</p>
        </div>

        {/* Lockout warning */}
        {isLocked && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4
                          flex items-start gap-2">
            <AlertCircle size={16} className="text-red-500 mt-0.5 flex-shrink-0"/>
            <p className="text-sm text-red-600">
              Account temporarily locked. Try again in {Math.floor(countdown / 60)}:
              {String(countdown % 60).padStart(2, '0')}
            </p>
          </div>
        )}

        {/* Google */}
        <button onClick={signInWithGoogle} disabled={isLocked}
          className="w-full flex items-center justify-center gap-3 border border-gray-300
                     rounded-lg py-2.5 text-sm font-medium text-gray-700
                     hover:bg-gray-50 transition mb-5 disabled:opacity-50">
          <img src="https://www.google.com/favicon.ico" className="w-4 h-4" alt="Google"/>
          Continue with Google
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="flex-1 h-px bg-gray-200"/>
          <span className="text-xs text-gray-400">or sign in with email</span>
          <div className="flex-1 h-px bg-gray-200"/>
        </div>

        <form onSubmit={handleEmail} className="space-y-4">
          {error && !isLocked && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-sm
                            px-4 py-2.5 rounded-lg flex items-center gap-2">
              <AlertCircle size={15}/>
              {error}
            </div>
          )}

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email address
            </label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
              placeholder="you@gmail.com"
              disabled={isLocked}
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm
                         focus:outline-none focus:ring-2 focus:ring-indigo-500
                         focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400"/>
          </div>

          {/* Password */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <Link to="/forgot-password"
                className="text-xs text-indigo-600 hover:underline">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <input
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                placeholder="••••••••"
                disabled={isLocked}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 pr-10
                           text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500
                           focus:border-transparent disabled:bg-gray-50"/>
              <button type="button" onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400
                           hover:text-gray-600">
                {showPass ? <EyeOff size={16}/> : <Eye size={16}/>}
              </button>
            </div>
          </div>

          {/* Remember me */}
          <div className="flex items-center gap-2">
            <input type="checkbox" id="remember" checked={rememberMe}
              onChange={e => setRememberMe(e.target.checked)}
              className="w-4 h-4 text-indigo-600 border-gray-300 rounded
                         focus:ring-indigo-500 cursor-pointer"/>
            <label htmlFor="remember" className="text-sm text-gray-600 cursor-pointer">
              Remember me
            </label>
          </div>

          <button type="submit" disabled={loading || isLocked}
            className="w-full bg-indigo-600 text-white rounded-lg py-2.5 text-sm
                       font-medium hover:bg-indigo-700 transition disabled:opacity-50
                       flex items-center justify-center gap-2">
            {loading
              ? <><Loader size={15} className="animate-spin"/> Signing in...</>
              : 'Sign in'
            }
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="text-indigo-600 hover:underline font-medium">
            Create one
          </Link>
        </p>
      </div>
    </div>
  )
}