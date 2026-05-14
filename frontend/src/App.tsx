import type { ReactNode } from 'react'
import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { Flower2, LayoutDashboard, Leaf, MessageCircle } from 'lucide-react'

import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'
import { GardenPage } from './pages/GardenPage'
import { PlantPage } from './pages/PlantPage'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/auth', label: 'Auth', icon: Flower2 },
]

function Shell({ children }: { children: ReactNode }) {
  const location = useLocation()
  return (
    <div className="app-shell">
      <header className="hero-bar">
        <div>
          <p className="eyebrow">PlantIQ</p>
          <h1>Adaptive care for every corner of your garden.</h1>
        </div>
        <div className="hero-note">
          <Leaf size={18} />
          <span>Catalog-first onboarding keeps Gemini costs optional.</span>
        </div>
      </header>
      <main className="page-frame">{children}</main>
      <nav className="mobile-nav">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = location.pathname === item.to
          return (
            <Link key={item.to} to={item.to} className={active ? 'nav-item active' : 'nav-item'}>
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          )
        })}
        <a className="nav-item" href="#chat-anchor">
          <MessageCircle size={18} />
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
