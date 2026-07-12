import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { Eye, EyeOff, Check, Loader } from 'lucide-react'

export default function ResetPassword() {
  const navigate  = useNavigate()
  const [password, setPassword] = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')
  const [done,     setDone]     = useState(false)

  const handleReset = async (e) => {
    e.preventDefault()
    if (password.length < 8)      { setError('Password must be at least 8 characters'); return }
    if (password !== confirm)      { setError('Passwords do not match'); return }
    if (!/[A-Z]/.test(password))  { setError('Password must contain an uppercase letter'); return }
    if (!/[0-9]/.test(password))  { setError('Password must contain a number'); return }
    if (!/[^A-Za-z0-9]/.test(password)) { setError('Password must contain a special character'); return }

    setLoading(true)
    setError('')

    const { error } = await supabase.auth.updateUser({ password })

    if (error) { setError(error.message); setLoading(false) }
    else {
      setDone(true)
      setTimeout(() => navigate('/login'), 3000)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50
                    flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 w-full max-w-md">
        {done ? (
          <div className="text-center py-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center
                            justify-center mx-auto mb-4">
              <Check size={24} className="text-green-600"/>
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Password updated!</h2>
            <p className="text-gray-500 text-sm">Redirecting you to sign in...</p>
          </div>
        ) : (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900">Set new password</h2>
              <p className="text-gray-500 text-sm mt-1">
                Choose a strong password for your account.
              </p>
            </div>
            <form onSubmit={handleReset} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600
                                text-sm px-4 py-2.5 rounded-lg">
                  {error}
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <div className="relative">
                  <input type={showPass ? 'text' : 'password'}
                    value={password} onChange={e => setPassword(e.target.value)}
                    required placeholder="Min 8 characters"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2.5
                               pr-10 text-sm focus:outline-none focus:ring-2
                               focus:ring-indigo-500"/>
                  <button type="button" onClick={() => setShowPass(!showPass)}
                    className="absolute right-3 top-1/2 -translate-y-1/2
                               text-gray-400 hover:text-gray-600">
                    {showPass ? <EyeOff size={16}/> : <Eye size={16}/>}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm Password
                </label>
                <input type="password" value={confirm}
                  onChange={e => setConfirm(e.target.value)}
                  required placeholder="Repeat password"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5
                             text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
              </div>
              <button type="submit" disabled={loading}
                className="w-full bg-indigo-600 text-white rounded-lg py-2.5 text-sm
                           font-medium hover:bg-indigo-700 transition disabled:opacity-50
                           flex items-center justify-center gap-2">
                {loading
                  ? <><Loader size={15} className="animate-spin"/> Updating...</>
                  : 'Update password'
                }
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}