import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogOut, Briefcase, FileText, LayoutDashboard } from 'lucide-react'

export default function Navbar() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <Link to="/dashboard" className="text-xl font-bold text-indigo-700">
        JobMinion
      </Link>

      {user && (
        <div className="flex items-center gap-6">
          <Link to="/dashboard"
            className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-indigo-600 transition">
            <LayoutDashboard size={16}/> Dashboard
          </Link>
          <Link to="/jobs"
            className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-indigo-600 transition">
            <Briefcase size={16}/> Browse Jobs
          </Link>
          <Link to="/applications"
            className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-indigo-600 transition">
            <FileText size={16}/> Applications
          </Link>
          <div className="flex items-center gap-3 ml-4 pl-4 border-l border-gray-200">
            <span className="text-sm text-gray-500 truncate max-w-[180px]">
              {user.email}
            </span>
            <button onClick={handleSignOut}
              className="flex items-center gap-1 text-sm text-red-500 hover:text-red-700 transition">
              <LogOut size={15}/> Sign out
            </button>
          </div>
        </div>
      )}
    </nav>
  )
}