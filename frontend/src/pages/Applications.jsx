import { useEffect, useState } from 'react'
import api from '../lib/api'
import { CheckCircle, Clock, XCircle, Mail, Loader } from 'lucide-react'

export default function Applications() {
  const [applications, setApplications] = useState([])
  const [loading,      setLoading]      = useState(true)

  useEffect(() => {
    api.get('/apply/history').then(res => {
      setApplications(res.data.applications || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const statusIcon = (status) => ({
    applied:    <CheckCircle size={16} className="text-green-500"/>,
    processing: <Clock       size={16} className="text-yellow-500"/>,
    failed:     <XCircle     size={16} className="text-red-500"/>,
    pending:    <Clock       size={16} className="text-gray-400"/>,
  }[status] || <Clock size={16} className="text-gray-400"/>)

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">My Applications</h1>
      <p className="text-sm text-gray-500 mb-6">
        All jobs you've applied to via JobMinion.
      </p>

      {loading ? (
        <div className="flex justify-center py-20">
          <Loader size={24} className="animate-spin text-indigo-500"/>
        </div>
      ) : applications.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          No applications yet. Browse jobs to get started.
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map(app => (
            <div key={app.id} className="bg-white border border-gray-200 rounded-xl p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    {statusIcon(app.status)}
                    <h3 className="font-semibold text-gray-900 text-sm">
                      {app.jobs?.job_title || 'Unknown Role'}
                    </h3>
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5 ml-6">
                    {app.jobs?.company}
                    {app.jobs?.location && ` · ${app.jobs.location}`}
                  </p>
                  {app.recipient_email && (
                    <div className="flex items-center gap-1.5 mt-2 ml-6">
                      <Mail size={12} className="text-gray-400"/>
                      <span className="text-xs text-gray-500">
                        Sent to {app.recipient_email}
                      </span>
                      <span className="text-xs text-gray-400">({app.email_source})</span>
                    </div>
                  )}
                </div>
                <div className="text-right flex-shrink-0">
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                    app.status === 'applied'    ? 'bg-green-100  text-green-700'  :
                    app.status === 'processing' ? 'bg-yellow-100 text-yellow-700' :
                    app.status === 'failed'     ? 'bg-red-100    text-red-700'    :
                    'bg-gray-100 text-gray-600'
                  }`}>{app.status}</span>
                  <p className="text-xs text-gray-400 mt-1.5">
                    {new Date(app.created_at).toLocaleDateString('en-IN', {
                      day: 'numeric', month: 'short', year: 'numeric'
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}