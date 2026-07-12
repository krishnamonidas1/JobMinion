import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Eye, EyeOff, Check, X, AlertCircle, Loader } from 'lucide-react'

function PasswordRule({ met, text }) {
  return (
    <div className={`flex items-center gap-1.5 text-xs ${met ? 'text-green-600' : 'text-gray-400'}`}>
      {met ? <Check size={12}/> : <X size={12}/>}
      {text}
    </div>
  )
}

function getPasswordStrength(password) {
  const rules = {
    length:    password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    number:    /[0-9]/.test(password),
    special:   /[^A-Za-z0-9]/.test(password),
  }
  const score = Object.values(rules).filter(Boolean).length
  return { rules, score }
}

const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong']
const strengthColor = ['', 'bg-red-400', 'bg-yellow-400', 'bg-blue-400', 'bg-green-500']

export default function Register() {
  const { signUpWithEmail, signInWithGoogle } = useAuth()
  const navigate = useNavigate()

  const [fullName,  setFullName]  = useState('')
  const [email,     setEmail]     = useState('')
  const [password,  setPassword]  = useState('')
  const [confirm,   setConfirm]   = useState('')
  const [showPass,  setShowPass]  = useState(false)
  const [showConf,  setShowConf]  = useState(false)
  const [error,     setError]     = useState('')
  const [success,   setSuccess]   = useState('')
  const [loading,   setLoading]   = useState(false)
  const [touched,   setTouched]   = useState({})

  const { rules, score } = getPasswordStrength(password)
  const allRulesMet       = Object.values(rules).every(Boolean)
  const passwordsMatch    = password === confirm && confirm.length > 0

  const validate = () => {
    if (!fullName.trim())      return 'Full name is required'
    if (!email.includes('@'))  return 'Enter a valid email address'
    if (!allRulesMet)          return 'Password does not meet requirements'
    if (!passwordsMatch)       return 'Passwords do not match'
    return null
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    const validationError = validate()
    if (validationError) { setError(validationError); return }

    setLoading(true)
    setError('')

    const { error } = await signUpWithEmail(email, password, fullName)

    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      setSuccess('Account created! Please check your email to verify your account before signing in.')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50
                    flex items-center justify-center px-4 py-8">
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-7">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-indigo-600
                          rounded-xl mb-3">
            <span className="text-white text-xl font-bold">J</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Create your account</h1>
          <p className="text-gray-500 text-sm mt-1">
            Join JobMinion — automate your job search
          </p>
        </div>

        {/* Google */}
        <button onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-3 border border-gray-300
                     rounded-lg py-2.5 text-sm font-medium text-gray-700
                     hover:bg-gray-50 transition mb-5">
          <img src="https://www.google.com/favicon.ico" className="w-4 h-4" alt="Google"/>
          Continue with Google
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="flex-1 h-px bg-gray-200"/>
          <span className="text-xs text-gray-400">or register with email</span>
          <div className="flex-1 h-px bg-gray-200"/>
        </div>

        {success ? (
          <div className="bg-green-50 border border-green-200 rounded-xl p-5 text-center">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center
                            justify-center mx-auto mb-3">
              <Check size={20} className="text-green-600"/>
            </div>
            <p className="text-green-800 font-medium text-sm">Check your email</p>
            <p className="text-green-600 text-xs mt-1">{success}</p>
            <Link to="/login"
              className="inline-block mt-4 text-sm text-indigo-600 hover:underline">
              Go to Sign in
            </Link>
          </div>
        ) : (
          <form onSubmit={handleRegister} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 text-sm
                              px-4 py-2.5 rounded-lg flex items-center gap-2">
                <AlertCircle size={15}/>
                {error}
              </div>
            )}

            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input type="text" value={fullName}
                onChange={e => setFullName(e.target.value)}
                onBlur={() => setTouched(t => ({...t, fullName: true}))}
                required placeholder="Krishnamoni Das"
                className={`w-full border rounded-lg px-3 py-2.5 text-sm
                            focus:outline-none focus:ring-2 focus:ring-indigo-500
                            focus:border-transparent ${
                  touched.fullName && !fullName.trim()
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-300'
                }`}/>
              {touched.fullName && !fullName.trim() && (
                <p className="text-xs text-red-500 mt-1">Full name is required</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email address
              </label>
              <input type="email" value={email}
                onChange={e => setEmail(e.target.value)}
                onBlur={() => setTouched(t => ({...t, email: true}))}
                required autoComplete="email" placeholder="you@gmail.com"
                className={`w-full border rounded-lg px-3 py-2.5 text-sm
                            focus:outline-none focus:ring-2 focus:ring-indigo-500
                            focus:border-transparent ${
                  touched.email && !email.includes('@')
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-300'
                }`}/>
              {touched.email && !email.includes('@') && (
                <p className="text-xs text-red-500 mt-1">Enter a valid email address</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <input type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  onBlur={() => setTouched(t => ({...t, password: true}))}
                  required autoComplete="new-password" placeholder="Create a strong password"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5 pr-10
                             text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500
                             focus:border-transparent"/>
                <button type="button" onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2
                             text-gray-400 hover:text-gray-600">
                  {showPass ? <EyeOff size={16}/> : <Eye size={16}/>}
                </button>
              </div>

              {/* Strength bar */}
              {password.length > 0 && (
                <div className="mt-2">
                  <div className="flex gap-1 mb-1">
                    {[1,2,3,4].map(i => (
                      <div key={i}
                        className={`h-1 flex-1 rounded-full transition-all ${
                          i <= score ? strengthColor[score] : 'bg-gray-200'
                        }`}/>
                    ))}
                  </div>
                  <p className={`text-xs font-medium ${
                    score <= 1 ? 'text-red-500' :
                    score === 2 ? 'text-yellow-500' :
                    score === 3 ? 'text-blue-500' : 'text-green-500'
                  }`}>{strengthLabel[score]}</p>
                  <div className="mt-2 grid grid-cols-2 gap-1">
                    <PasswordRule met={rules.length}    text="At least 8 characters"/>
                    <PasswordRule met={rules.uppercase} text="One uppercase letter"/>
                    <PasswordRule met={rules.number}    text="One number"/>
                    <PasswordRule met={rules.special}   text="One special character"/>
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <input type={showConf ? 'text' : 'password'}
                  value={confirm}
                  onChange={e => setConfirm(e.target.value)}
                  onBlur={() => setTouched(t => ({...t, confirm: true}))}
                  required autoComplete="new-password" placeholder="Repeat your password"
                  className={`w-full border rounded-lg px-3 py-2.5 pr-10 text-sm
                              focus:outline-none focus:ring-2 focus:ring-indigo-500
                              focus:border-transparent ${
                    touched.confirm && confirm && !passwordsMatch
                      ? 'border-red-300 bg-red-50'
                      : touched.confirm && passwordsMatch
                      ? 'border-green-400'
                      : 'border-gray-300'
                  }`}/>
                <button type="button" onClick={() => setShowConf(!showConf)}
                  className="absolute right-3 top-1/2 -translate-y-1/2
                             text-gray-400 hover:text-gray-600">
                  {showConf ? <EyeOff size={16}/> : <Eye size={16}/>}
                </button>
              </div>
              {touched.confirm && confirm && !passwordsMatch && (
                <p className="text-xs text-red-500 mt-1">Passwords do not match</p>
              )}
              {touched.confirm && passwordsMatch && (
                <p className="text-xs text-green-600 mt-1 flex items-center gap-1">
                  <Check size={11}/> Passwords match
                </p>
              )}
            </div>

            <button type="submit" disabled={loading}
              className="w-full bg-indigo-600 text-white rounded-lg py-2.5 text-sm
                         font-medium hover:bg-indigo-700 transition disabled:opacity-50
                         flex items-center justify-center gap-2 mt-2">
              {loading
                ? <><Loader size={15} className="animate-spin"/> Creating account...</>
                : 'Create account'
              }
            </button>

            <p className="text-xs text-gray-400 text-center">
              By creating an account you agree to our Terms of Service
            </p>
          </form>
        )}

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-indigo-600 hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}