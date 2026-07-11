import { useEffect, useState } from 'react'
import api from '../lib/api'
import { Search, MapPin, Building2, Send, Loader } from 'lucide-react'

export default function Jobs() {
  const [jobs,     setJobs]     = useState([])
  const [selected, setSelected] = useState(new Set())
  const [search,   setSearch]   = useState('')
  const [loading,  setLoading]  = useState(true)
  const [applying, setApplying] = useState(false)
  const [results,  setResults]  = useState(null)

  useEffect(() => { fetchJobs() }, [])

  const fetchJobs = async (q = '') => {
    setLoading(true)
    try {
      const res = await api.get('/jobs/', { params: { search: q, limit: 30 } })
      setJobs(res.data.jobs || [])
    } catch {}
    setLoading(false)
  }

  const toggleSelect = (job_id) => {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(job_id)) next.delete(job_id)
      else if (next.size < 10) next.add(job_id)
      return next
    })
  }

  const handleSearch = (e) => {
    e.preventDefault()
    fetchJobs(search)
  }

  const handleApply = async () => {
    if (selected.size === 0) return
    setApplying(true)
    setResults(null)
    try {
      const res = await api.post('/apply/', { job_ids: [...selected] })
      setResults(res.data.results)
      setSelected(new Set())
    } catch (err) {
      setResults([{
        status:  'failed',
        message: err.response?.data?.detail || 'Something went wrong'
      }])
    }
    setApplying(false)
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Browse Jobs</h1>
          <p className="text-sm text-gray-500 mt-1">
            Select up to 10 jobs — we'll tailor your resume and apply automatically.
          </p>
        </div>
        {selected.size > 0 && (
          <button onClick={handleApply} disabled={applying}
            className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5
                       rounded-lg text-sm font-medium hover:bg-indigo-700 transition
                       disabled:opacity-50">
            {applying
              ? <><Loader size={15} className="animate-spin"/> Applying...</>
              : <><Send size={15}/> Apply to {selected.size} job{selected.size > 1 ? 's' : ''}</>
            }
          </button>
        )}
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <div className="flex-1 relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"/>
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search jobs, companies..."
            className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
        </div>
        <button type="submit"
          className="bg-gray-900 text-white px-5 py-2.5 rounded-lg text-sm
                     font-medium hover:bg-gray-700 transition">
          Search
        </button>
      </form>

      {/* Results banner */}
      {results && (
        <div className="mb-6 bg-white border border-gray-200 rounded-xl p-4">
          <h3 className="font-semibold text-gray-900 mb-3">Application Results</h3>
          <div className="space-y-2">
            {results.map((r, i) => (
              <div key={i} className={`flex items-center gap-3 text-sm p-2.5 rounded-lg ${
                r.status === 'applied'  ? 'bg-green-50  text-green-700'  :
                r.status === 'skipped' ? 'bg-yellow-50 text-yellow-700' :
                'bg-red-50 text-red-700'
              }`}>
                <span className="font-medium capitalize">{r.status}</span>
                {r.job_title && <span>{r.job_title} at {r.company}</span>}
                {r.sent_to  && <span className="ml-auto text-xs">→ {r.sent_to}</span>}
                {r.message  && <span className="ml-auto text-xs">{r.message}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Job Cards */}
      {loading ? (
        <div className="flex justify-center py-20">
          <Loader size={24} className="animate-spin text-indigo-500"/>
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          No jobs found. Try scraping new jobs from the Dashboard.
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map(job => {
            const isSelected = selected.has(job.job_id)
            return (
              <div key={job.job_id} onClick={() => toggleSelect(job.job_id)}
                className={`bg-white border rounded-xl p-5 cursor-pointer transition ${
                  isSelected
                    ? 'border-indigo-500 ring-2 ring-indigo-100'
                    : 'border-gray-200 hover:border-gray-300'
                }`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 text-sm truncate">
                      {job.job_title}
                    </h3>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="flex items-center gap-1 text-xs text-gray-500">
                        <Building2 size={12}/> {job.company}
                      </span>
                      {job.location && (
                        <span className="flex items-center gap-1 text-xs text-gray-500">
                          <MapPin size={12}/> {job.location}
                        </span>
                      )}
                      {job.level && (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                          {job.level}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-400 mt-2 line-clamp-2">
                      {job.description?.slice(0, 150)}...
                    </p>
                  </div>
                  <div className={`w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 transition ${
                    isSelected ? 'bg-indigo-600 border-indigo-600' : 'border-gray-300'
                  }`}>
                    {isSelected && (
                      <svg viewBox="0 0 20 20" fill="white" className="w-full h-full p-0.5">
                        <path fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"/>
                      </svg>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Floating apply bar */}
      {selected.size > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white
                        px-6 py-3 rounded-full shadow-lg flex items-center gap-4 text-sm">
          <span>{selected.size} job{selected.size > 1 ? 's' : ''} selected</span>
          <button onClick={handleApply} disabled={applying}
            className="bg-indigo-500 hover:bg-indigo-400 px-4 py-1.5 rounded-full
                       font-medium transition disabled:opacity-50">
            {applying ? 'Applying...' : 'Apply Now'}
          </button>
          <button onClick={() => setSelected(new Set())}
            className="text-gray-400 hover:text-white transition text-xs">
            Clear
          </button>
        </div>
      )}
    </div>
  )
}