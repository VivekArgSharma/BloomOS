import { useQuery } from '@tanstack/react-query'

import { useAuth } from '../context/AuthContext'
import { fetchUserBadges } from '../services/api'

export function BadgesDisplay() {
  const { user } = useAuth()
  const badgesQuery = useQuery({ queryKey: ['badges'], queryFn: fetchUserBadges, enabled: Boolean(user) })

  const badges = badgesQuery.data?.badges ?? []
  const totalUnlocked = badgesQuery.data?.total_unlocked ?? 0
  const totalAvailable = badgesQuery.data?.total_available ?? 0

  if (badgesQuery.isLoading) {
    return (
      <section className="panel">
        <p className="muted">Loading badges...</p>
      </section>
    )
  }

  return (
    <section className="panel">
      <div className="section-head">
        <div>
          <p className="eyebrow">Achievements</p>
          <h3>Your badges ({totalUnlocked}/{totalAvailable})</h3>
        </div>
      </div>
      <div className="badges-grid">
        {badges.map((badge) => (
          <div key={badge.id} className={`badge-card ${badge.unlocked ? 'unlocked' : 'locked'}`}>
            <span className="badge-icon">{badge.icon}</span>
            <div className="badge-info">
              <strong>{badge.name}</strong>
              <p>{badge.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}