import type { ReactNode } from 'react'
import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { Flower2, LayoutDashboard, Leaf, MessageCircle } from 'lucide-react'

import { AuthPage } from './pages/AuthPage'
import { useAuth } from './context/AuthContext'
import { DashboardPage } from './pages/DashboardPage'
import { GardenPage } from './pages/GardenPage'
import { PlantPage } from './pages/PlantPage'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/auth', label: 'Account', icon: Flower2 },
]

function Shell({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { user, signOut } = useAuth()
  return (
    <div className="app-shell">
      <header className="hero-bar">
        <div>
          <p className="eyebrow">PlantIQ</p>
          <h1>Proper care of your Plants</h1>
        </div>
        <div className="hero-note">
          <Leaf size={16} />
          <span>{user ? `Signed in as ${user.email}` : 'Sign in to unlock AI analysis, uploads, and personalized care.'}</span>
        </div>
        {user ? <button className="ghost-button hero-action" onClick={signOut}>Sign out</button> : null}
      </header>
      <main className="page-frame">{children}</main>
      <nav className="mobile-nav">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = location.pathname === item.to
          return (
            <Link key={item.to} to={item.to} className={active ? 'nav-item active' : 'nav-item'}>
              <Icon size={16} />
              <span>{item.label}</span>
            </Link>
          )
        })}
        <a className="nav-item" href="#chat-anchor">
          <MessageCircle size={16} />
          <span>Chat</span>
        </a>
      </nav>
    </div>
  )
}

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/garden/:gardenId" element={<GardenPage />} />
        <Route path="/plant/:plantId" element={<PlantPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  )
}
