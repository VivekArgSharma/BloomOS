import type { ReactNode } from 'react'
import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { Flower2, LayoutDashboard, Leaf, MessageCircle, Users } from 'lucide-react'

import { AuthPage } from './pages/AuthPage'
import { CommunityPage } from './pages/CommunityPage'
import { CommunityProfilePage } from './pages/CommunityProfilePage'
import { useAuth } from './context/AuthContext'
import { DashboardPage } from './pages/DashboardPage'
import { GardenPage } from './pages/GardenPage'
import { PlantPage } from './pages/PlantPage'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/community', label: 'Community', icon: Users },
  { to: '/auth', label: 'Account', icon: Flower2 },
]

function Shell({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { user, signOut } = useAuth()

  return (
    <div className="app-shell">
      <div className="site-nav-wrap">
        <div className="site-nav top-strip">
          <Link to="/" className="site-brand">PlantIQ</Link>
          <div className="site-nav-links desktop-nav">
            {navItems.map((item) => {
              const active = location.pathname === item.to || location.pathname.startsWith(`${item.to}/`)
              return (
                <Link key={item.to} to={item.to} className={active ? 'site-nav-link active' : 'site-nav-link'}>
                  {item.label}
                </Link>
              )
            })}
          </div>
          <div className="nav-meta desktop-nav-meta">
            <span className="meta-chip">AI care engine</span>
            {user ? <button className="ghost-button subtle-button" onClick={signOut}>Sign out</button> : <Link to="/auth" className="ghost-button subtle-button">Sign in</Link>}
          </div>
        </div>

        <header className="hero-bar site-hero">
          <div className="hero-grid adwise-hero-grid">
            <div className="hero-copy">
              <p className="hero-kicker">Organic-digital plant intelligence</p>
              <h1>
                <span>The uncanny</span>
                <span>garden as</span>
                <span>interface.</span>
              </h1>
              <p className="hero-summary">
                PlantIQ turns gardens, plant diaries, image analysis, task planning, and community sharing into one sleek ecosystem that feels alive, intelligent, and deeply considered.
              </p>
              <div className="hero-actions">
                <Link to="/" className="button-link hero-action">Open workspace</Link>
                <Link to="/community" className="ghost-button hero-action">Explore community</Link>
              </div>
            </div>

            <div className="hero-mosaic">
              <div className="mosaic-card mosaic-large">
                <span className="mosaic-eyebrow">Daily environment</span>
                <strong>Eco visual studio</strong>
                <p>Health analysis, adaptive planning, and context-aware care live inside a darker, richer system.</p>
                <div className="mosaic-stats">
                  <span>10x clarity</span>
                  <span>98% signal</span>
                  <span>140+ logs</span>
                </div>
              </div>
              <div className="mosaic-card mosaic-small right-top">
                <span className="mosaic-eyebrow">Active module</span>
                <strong>Plant intelligence</strong>
              </div>
              <div className="mosaic-card mosaic-small right-bottom">
                <span className="mosaic-eyebrow">Live account</span>
                <strong>{user ? user.email : 'Connect to unlock uploads'}</strong>
                <p>{user ? 'Authenticated and ready for analysis, journaling, and community posting.' : 'Sign in to persist your care system.'}</p>
              </div>
            </div>
          </div>
          <div className="hero-brandmark" aria-hidden="true">PlantIQ</div>
        </header>
      </div>

      <main className="page-frame">{children}</main>

      <nav className="mobile-nav">
        {navItems.map((item) => {
          const Icon = item.icon
          const active = location.pathname === item.to || location.pathname.startsWith(`${item.to}/`)
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
        <Route path="/community" element={<CommunityPage />} />
        <Route path="/community/profile/:username" element={<CommunityProfilePage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/garden/:gardenId" element={<GardenPage />} />
        <Route path="/plant/:plantId" element={<PlantPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  )
}
