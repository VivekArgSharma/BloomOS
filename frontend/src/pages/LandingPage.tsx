import { useNavigate } from 'react-router-dom'

export function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="landing-page">
      {/* Background video (blurred) */}
      <video autoPlay muted loop playsInline className="landing-bg-video">
        <source src="/bg-video.mp4" type="video/mp4" />
      </video>

      {/* White wash overlay */}
      <div className="landing-overlay" />

      {/* Nav: wordmark only */}
      <nav className="landing-nav">
        <div className="landing-wordmark">
          Bloom<em>OS</em>
        </div>
      </nav>

      {/* Hero: full viewport, centered */}
      <main className="landing-hero">
        <div className="landing-hero-inner">
          <h1 className="landing-headline">
            Your plant is<br />
            <em>talking.</em>
          </h1>
          <p className="landing-tagline">We help you listen.</p>
          <button className="landing-cta" onClick={() => navigate('/dashboard')}>
            Get started
            <svg
              width="14"
              height="14"
              viewBox="0 0 16 16"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="3" y1="8" x2="13" y2="8" />
              <polyline points="9,4 13,8 9,12" />
            </svg>
          </button>
        </div>
      </main>

      {/* Footer: one line */}
      <footer className="landing-footer">
        <div className="landing-footer-mark">
          Bloom<em>OS</em> · 2026
        </div>
        <div className="landing-status">
          <div className="landing-status-dot" />
          All systems calm
        </div>
      </footer>
    </div>
  )
}
