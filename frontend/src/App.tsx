import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Layout
import Layout from './components/Layout'

// Pages
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import DigitalTwin from './pages/DigitalTwin'
import GapAnalysis from './pages/GapAnalysis'
import LearningRoadmap from './pages/LearningRoadmap'
import CareerAlignment from './pages/CareerAlignment'
import Assessments from './pages/Assessments'
import Profile from './pages/Profile'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="digital-twin" element={<DigitalTwin />} />
        <Route path="gap-analysis" element={<GapAnalysis />} />
        <Route path="learning" element={<LearningRoadmap />} />
        <Route path="careers" element={<CareerAlignment />} />
        <Route path="assessments" element={<Assessments />} />
        <Route path="profile" element={<Profile />} />
      </Route>
      
      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
