import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { AuthRequired } from '../components/AuthRequired'
import { BadgesDisplay } from '../components/BadgesDisplay'
import { CreateGardenForm } from '../components/CreateGardenForm'
import { useAuth } from '../context/AuthContext'
import { createGarden, fetchGardens, fetchUserStats, fetchWeather } from '../services/api'

export function DashboardPage() {
  const { user, loading } = useAuth()
  const queryClient = useQueryClient()
  const gardensQuery = useQuery({ queryKey: ['gardens'], queryFn: fetchGardens, enabled: Boolean(user) })
  const weatherQuery = useQuery({ queryKey: ['weather', 'dashboard'], queryFn: () => fetchWeather('Bengaluru'), enabled: Boolean(user) })
  const statsQuery = useQuery({ queryKey: ['user-stats'], queryFn: fetchUserStats, enabled: Boolean(user) })

  const createMutation = useMutation({
    mutationFn: createGarden,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['gardens'] }),
  })

  const gardens = gardensQuery.data ?? []
  const totalPlants = gardens.reduce((sum, garden) => sum + garden.plant_count, 0)
  const avgHealth = gardens.length ? Math.round(gardens.reduce((sum, garden) => sum + garden.health_score, 0) / gardens.length) : 0

  if (loading) {
    return <section className="panel"><p>Loading account...</p></section>
  }

  if (!user) {
    return <AuthRequired message="Sign in first so PlantIQ can load your gardens, ownership-aware analytics, and uploads." />
  }

  return (
    <div className="grid-layout dashboard-layout">
      <section className="panel spotlight dashboard-spotlight page-panel-full">
        <div className="section-head">
          <div>
            <p className="eyebrow">Overview</p>
            <h2>Define the future of your plant system</h2>
          </div>
          <span className="pill">{weatherQuery.data?.summary ?? 'Loading weather'}</span>
        </div>
        <div className="spotlight-content">
          <div className="panel-intro">
            <p className="section-copy">Your gardens, plant count, health, and weather in one view.</p>
            {statsQuery.data && (
              <div className="stats-mini">
                <span>Photos: {statsQuery.data.total_photos_uploaded}</span>
                <span>Thriving: {statsQuery.data.plants_at_health_90_plus}</span>
                <span>Tasks completed: {statsQuery.data.total_tasks_completed}</span>
              </div>
            )}
          </div>
          <div className="metric-row">
            <article>
              <strong>{gardens.length}</strong>
              <span>Gardens</span>
            </article>
            <article>
              <strong>{totalPlants}</strong>
              <span>Plants</span>
            </article>
            <article>
              <strong>{avgHealth}</strong>
              <span>Avg health score</span>
            </article>
          </div>
        </div>
      </section>

      <section className="panel dashboard-gardens">
        <div className="section-head">
          <div>
            <p className="eyebrow">Gardens</p>
            <h3>Multi-zone care management</h3>
          </div>
        </div>
        <p className="section-copy">Open any garden to manage plants, analytics, and quick-add.</p>
        <div className="stack-list">
          {gardens.length === 0 ? (
            <p className="muted">No gardens yet. Create one above to begin your plant care journey.</p>
          ) : null}
          {gardens.map((garden) => (
            <Link key={garden.id} className="garden-card" to={`/garden/${garden.id}`}>
              <div>
                <strong>{garden.name}</strong>
                <p>{garden.location_type} {garden.city ? `· ${garden.city}` : ''}</p>
              </div>
              <div className="garden-meta">
                <span>{garden.plant_count} plants</span>
                <span>{garden.health_score} health</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <div className="dashboard-side-stack">
        <CreateGardenForm onSubmit={async (payload) => createMutation.mutateAsync(payload)} />

        <BadgesDisplay />
      </div>
    </div>
  )
}
