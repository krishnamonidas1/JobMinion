import { useState } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { Loader, ArrowLeft, Check } from 'lucide-react'

export default function ForgotPassword() {
  const [email,   setEmail]   = useState('')
  const [loading, setLoading] = useState(false)
  const [sent,    setSent]    = useState(false)
  const [error,   setError]   = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`
    })

    if (error) { setError(error.message); setLoading(false) }
    else        { setSent(true);           setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50
                    flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 w-full max-w-md">

        <Link to="/login"
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700
                     mb-6 transition">
          <ArrowLeft size={15}/> Back to sign in
        </Link>

        {sent ? (
          <div className="text-center py-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center
                            justify-center mx-auto mb-4">
              <Check size={24} className="text-green-600"/>
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Check your email</h2>
            <p className="text-gray-500 text-sm">
              We sent a password reset link to <strong>{email}</strong>.
              Check your inbox and follow the link.
            </p>
            <p className="text-xs text-gray-400 mt-3">
              Didn't receive it? Check your spam folder.
            </p>
          </div>
        ) : (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900">Forgot your password?</h2>
              <p className="text-gray-500 text-sm mt-1">
                Enter your email and we'll send you a reset link.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600
                                text-sm px-4 py-2.5 rounded-lg">
                  {error}
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email address
                </label>
                <input type="email" value={email}
                  onChange={e => setEmail(e.target.value)}
                  required placeholder="you@gmail.com"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2.5
                             text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
              </div>
              <button type="submit" disabled={loading}
                className="w-full bg-indigo-600 text-white rounded-lg py-2.5 text-sm
                           font-medium hover:bg-indigo-700 transition disabled:opacity-50
                           flex items-center justify-center gap-2">
                {loading
                  ? <><Loader size={15} className="animate-spin"/> Sending...</>
                  : 'Send reset link'
                }
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}