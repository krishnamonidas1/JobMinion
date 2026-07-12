import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar         from './components/Navbar'
import Login          from './pages/Login'
import Register       from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword  from './pages/ResetPassword'
import Dashboard      from './pages/Dashboard'
import Jobs           from './pages/Jobs'
import Applications   from './pages/Applications'
import Preferences    from './pages/Preferences'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"/>
    </div>
  )
  return user ? children : <Navigate to="/login" replace/>
}

function AppRoutes() {
  const { user } = useAuth()
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar/>
      <Routes>
        <Route path="/"                element={<Navigate to={user ? '/dashboard' : '/login'} replace/>}/>
        <Route path="/login"           element={<Login/>}/>
        <Route path="/register"        element={<Register/>}/>
        <Route path="/forgot-password" element={<ForgotPassword/>}/>
        <Route path="/reset-password"  element={<ResetPassword/>}/>
        <Route path="/dashboard"       element={<PrivateRoute><Dashboard/></PrivateRoute>}/>
        <Route path="/jobs"            element={<PrivateRoute><Jobs/></PrivateRoute>}/>
        <Route path="/applications"    element={<PrivateRoute><Applications/></PrivateRoute>}/>
        <Route path="/preferences"     element={<PrivateRoute><Preferences/></PrivateRoute>}/>
      </Routes>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes/>
      </AuthProvider>
    </BrowserRouter>
  )
}