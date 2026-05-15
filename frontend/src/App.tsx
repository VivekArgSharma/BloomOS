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
      <div className="site-nav">
        <Link to="/" className="site-brand">PlantIQ</Link>
        <div className="site-nav-links">
          {navItems.map((item) => {
            const active = location.pathname === item.to
            return (
              <Link key={item.to} to={item.to} className={active ? 'site-nav-link active' : 'site-nav-link'}>
                {item.label}
              </Link>
            )
          })}
        </div>
      </div>
      <header className="hero-bar">
        <div className="hero-grid">
          <div className="hero-copy">
            <p className="hero-kicker">Root &amp; Ink System</p>
            <h1>
              <span>Proper care</span>
              <span>for living</span>
              <span>collections</span>
            </h1>
            <p className="hero-summary">
              PlantIQ brings your gardens, plant diaries, care tasks, and AI analysis into one grounded workspace built like a modern botanical ledger.
            </p>
            <div className="hero-note">
              <Leaf size={16} />
              <span>{user ? `Signed in as ${user.email}` : 'Sign in to unlock AI analysis, uploads, and personalized care.'}</span>
            </div>
            <div className="hero-actions">
              <Link to="/" className="button-link hero-action">Open dashboard</Link>
              {user ? <button className="ghost-button hero-action" onClick={signOut}>Sign out</button> : <Link to="/auth" className="ghost-button hero-action">Connect account</Link>}
            </div>
          </div>
          <div className="hero-aside">
            <div className="hero-aside-card">
              <strong>Daily care</strong>
              <p className="body-on-green">Track plant health, task rhythm, and growing conditions with a warmer, more readable control room.</p>
            </div>
            <div className="hero-aside-card">
              <strong>Photo insight</strong>
              <p className="body-on-green">Upload real plant imagery, preview AI findings, and turn each check-in into a lasting diary entry.</p>
            </div>
          </div>
        </div>
        <div className="hero-brandmark" aria-hidden="true">PlantIQ</div>
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
