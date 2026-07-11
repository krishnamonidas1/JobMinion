import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../lib/api'
import { Upload, Briefcase, CheckCircle, Clock, AlertCircle, RefreshCw } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const [resume,       setResume]       = useState(null)
  const [applications, setApplications] = useState([])
  const [uploading,    setUploading]    = useState(false)
  const [uploadMsg,    setUploadMsg]    = useState('')
  const [scraping,     setScraping]     = useState(false)
  const [scrapeMsg,    setScrapeMsg]    = useState('')

  useEffect(() => {
    fetchResume()
    fetchApplications()
  }, [])

  const fetchResume = async () => {
    try {
      const res = await api.get('/resume/me')
      setResume(res.data)
    } catch { setResume(null) }
  }

  const fetchApplications = async () => {
    try {
      const res = await api.get('/apply/history')
      setApplications(res.data.applications || [])
    } catch {}
  }

  const handleResumeUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    setUploadMsg('')
    const form = new FormData()
    form.append('file', file)
    try {
      await api.post('/resume/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadMsg('Resume uploaded and parsed successfully!')
      fetchResume()
    } catch (err) {
      setUploadMsg(err.response?.data?.detail || 'Upload failed. Please try again.')
    }
    setUploading(false)
  }

  const handleScrape = async () => {
    setScraping(true)
    setScrapeMsg('Scraping LinkedIn for new jobs...')
    try {
      await api.post('/scraper/run', {
        queries:  ['Python Developer', 'Software Engineer', 'MCA Fresher'],
        location: 'India',
        limit:    5
      })
      const poll = setInterval(async () => {
        try {
          const status = await api.get('/scraper/status')
          if (!status.data.running) {
            clearInterval(poll)
            const result = status.data.last_result
            if (result?.error) {
              setScrapeMsg(`Error: ${result.error}`)
            } else {
              setScrapeMsg(`Done! ${result?.total_saved || 0} new jobs added.`)
            }
            setScraping(false)
          }
        } catch { clearInterval(poll); setScraping(false) }
      }, 5000)
    } catch (err) {
      setScrapeMsg(err.response?.data?.detail || 'Scraping failed')
      setScraping(false)
    }
  }

  const stats = {
    total:      applications.length,
    applied:    applications.filter(a => a.status === 'applied').length,
    processing: applications.filter(a => a.status === 'processing').length,
    failed:     applications.filter(a => a.status === 'failed').length,
  }

  const firstName = user?.user_metadata?.full_name?.split(' ')[0]
               || user?.email?.split('@')[0] || ''

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back{firstName ? `, ${firstName}` : ''}
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Your AI job application agent is ready.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Applied',  value: stats.total,      icon: Briefcase,   color: 'indigo' },
          { label: 'Successful',     value: stats.applied,    icon: CheckCircle, color: 'green'  },
          { label: 'Processing',     value: stats.processing, icon: Clock,       color: 'yellow' },
          { label: 'Failed',         value: stats.failed,     icon: AlertCircle, color: 'red'    },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className={`text-${color}-500 mb-2`}><Icon size={20}/></div>
            <div className="text-2xl font-bold text-gray-900">{value}</div>
            <div className="text-xs text-gray-500 mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Resume Card */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-1">Your Resume</h2>
          <p className="text-sm text-gray-500 mb-4">
            Upload your resume PDF — we'll parse and use it for all applications.
          </p>
          {resume ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-green-700 font-medium">✓ Resume on file</p>
              <p className="text-xs text-green-600 mt-0.5">{resume.file_name}</p>
              <p className="text-xs text-gray-400 mt-0.5">
                Name: {resume.parsed_data?.name || 'N/A'}
              </p>
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-yellow-700">No resume uploaded yet</p>
            </div>
          )}
          {uploadMsg && (
            <p className={`text-sm mb-3 ${
              uploadMsg.includes('success') ? 'text-green-600' : 'text-red-500'
            }`}>{uploadMsg}</p>
          )}
          <label className="flex items-center justify-center gap-2 w-full border-2
                            border-dashed border-gray-300 rounded-lg py-3 cursor-pointer
                            hover:border-indigo-400 hover:bg-indigo-50 transition text-sm text-gray-500">
            <Upload size={16}/>
            {uploading ? 'Uploading...' : resume ? 'Replace resume (PDF)' : 'Upload resume (PDF)'}
            <input type="file" accept=".pdf" className="hidden"
                   onChange={handleResumeUpload} disabled={uploading}/>
          </label>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-1">Quick Actions</h2>
          <p className="text-sm text-gray-500 mb-4">
            Start your automated job search pipeline.
          </p>
          <div className="space-y-3">
            <Link to="/jobs"
              className="flex items-center gap-3 w-full bg-indigo-600 text-white
                         rounded-lg px-4 py-3 text-sm font-medium hover:bg-indigo-700 transition">
              <Briefcase size={16}/> Browse & Select Jobs
            </Link>
            <Link to="/applications"
              className="flex items-center gap-3 w-full bg-gray-100 text-gray-700
                         rounded-lg px-4 py-3 text-sm font-medium hover:bg-gray-200 transition">
              <CheckCircle size={16}/> View My Applications
            </Link>
          </div>
        </div>
      </div>

      {/* Scraper Card */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-gray-900">Job Database</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              Scrape LinkedIn for fresh job listings.
            </p>
            {scrapeMsg && (
              <p className="text-sm text-indigo-600 mt-2">{scrapeMsg}</p>
            )}
          </div>
          <button onClick={handleScrape} disabled={scraping}
            className="flex items-center gap-2 bg-gray-900 text-white px-4 py-2.5
                       rounded-lg text-sm font-medium hover:bg-gray-700 transition
                       disabled:opacity-50">
            <RefreshCw size={15} className={scraping ? 'animate-spin' : ''}/>
            {scraping ? 'Scraping...' : 'Scrape New Jobs'}
          </button>
        </div>
      </div>

      {/* Recent Applications */}
      {applications.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Recent Applications</h2>
          <div className="divide-y divide-gray-100">
            {applications.slice(0, 5).map(app => (
              <div key={app.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {app.jobs?.job_title || 'Unknown Role'}
                  </p>
                  <p className="text-xs text-gray-500">{app.jobs?.company}</p>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  app.status === 'applied'    ? 'bg-green-100  text-green-700'  :
                  app.status === 'processing' ? 'bg-yellow-100 text-yellow-700' :
                  app.status === 'failed'     ? 'bg-red-100    text-red-700'    :
                  'bg-gray-100 text-gray-600'
                }`}>{app.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}