import { useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { AuthRequired } from '../components/AuthRequired'
import { IssueBreakdown } from '../components/IssueBreakdown'
import { TrendChart } from '../components/TrendChart'
import { useAuth } from '../context/AuthContext'
import { createPlant, fetchCatalog, fetchGardenAnalytics, fetchGardenPlants, fetchGardens, identifyPlant } from '../services/api'
import type { CatalogItem } from '../types'

export function GardenPage() {
  const { gardenId = '' } = useParams()
  const { user, loading } = useAuth()
  const queryClient = useQueryClient()
  const [searchHint, setSearchHint] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [identifiedPlant, setIdentifiedPlant] = useState<CatalogItem | null>(null)
  const [identifyMessage, setIdentifyMessage] = useState('Upload a plant photo or type a hint to identify and add a new plant.')

  const gardensQuery = useQuery({ queryKey: ['gardens'], queryFn: fetchGardens, enabled: Boolean(user) })
  const plantsQuery = useQuery({ queryKey: ['garden-plants', gardenId], queryFn: () => fetchGardenPlants(gardenId), enabled: Boolean(gardenId && user) })
  const analyticsQuery = useQuery({ queryKey: ['garden-analytics', gardenId], queryFn: () => fetchGardenAnalytics(gardenId), enabled: Boolean(gardenId && user) })
  const catalogQuery = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalog, enabled: Boolean(user) })

  const addPlantMutation = useMutation({
    mutationFn: createPlant,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['garden-plants', gardenId] })
      queryClient.invalidateQueries({ queryKey: ['garden-analytics', gardenId] })
      queryClient.invalidateQueries({ queryKey: ['gardens'] })
      setIdentifiedPlant(null)
      setSelectedFile(null)
      setSearchHint('')
      setIdentifyMessage('Plant added successfully. You can upload its first progress photo from the plant detail page.')
    },
  })

  const identifyMutation = useMutation({
    mutationFn: identifyPlant,
    onSuccess: (data) => {
      setIdentifiedPlant(data.plant)
      setIdentifyMessage(`${Math.round(data.confidence * 100)}% confidence - ${data.rationale}`)
    },
  })

  const garden = (gardensQuery.data ?? []).find((item) => item.id === gardenId)
  const catalog = catalogQuery.data ?? []
  const analytics = analyticsQuery.data

  if (loading) {
    return <section className="panel"><p>Loading account...</p></section>
  }

  if (!user) {
    return <AuthRequired message="Sign in to manage gardens, identify plants from photos, and save everything to Supabase." />
  }

  return (
    <div className="grid-layout">
      <section className="panel spotlight">
        <p className="eyebrow">Garden View</p>
        <h2>{garden?.name ?? 'Garden'}</h2>
        <p className="muted">{garden?.location_type} conditions with both instant catalog add and real image-based onboarding.</p>
        {analytics ? (
          <div className="metric-row compact analytics-metrics">
            <article>
              <strong>{analytics.overall_health}</strong>
              <span>Overall health</span>
            </article>
            <article>
              <strong>{analytics.average_completion_rate}%</strong>
              <span>Task follow-through</span>
            </article>
            <article>
              <strong>{analytics.plants_in_recovery}</strong>
              <span>In recovery</span>
            </article>
          </div>
        ) : null}
      </section>

      {analytics ? <TrendChart title="Garden health curve" subtitle="Last 7 check-ins" points={analytics.health_history} max={10} /> : null}

      <section className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Photo Onboarding</p>
            <h3>Identify from a real image</h3>
          </div>
        </div>
        <div className="form-panel">
          <input value={searchHint} onChange={(event) => setSearchHint(event.target.value)} placeholder="Optional hint, e.g. basil or monstera" />
          <input type="file" accept="image/*" onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} />
          <button onClick={() => identifyMutation.mutate({ file: selectedFile, searchHint })} disabled={!selectedFile && !searchHint}>
            {identifyMutation.isPending ? 'Identifying...' : 'Identify plant'}
          </button>
          <p className="status-text">{identifyMessage}</p>
          {identifiedPlant ? (
            <div className="identified-card">
              <strong>{identifiedPlant.common_name}</strong>
              <p className="muted">{identifiedPlant.species_name}</p>
              <small>{identifiedPlant.care_profile.light} light - water every {identifiedPlant.care_profile.water_interval_days} days</small>
              <button
                onClick={() =>
                  addPlantMutation.mutate({
                    garden_id: gardenId,
                    common_name: identifiedPlant.common_name,
                    species_name: identifiedPlant.species_name,
                    source: selectedFile ? 'image' : 'catalog',
                    care_profile: identifiedPlant.care_profile,
                  })
                }
              >
                Add identified plant
              </button>
            </div>
          ) : null}
        </div>
      </section>

      {analytics ? (
        <section className="panel analytics-panel">
          <div className="section-head">
            <div>
              <p className="eyebrow">Garden Analytics</p>
              <h3>Plant-by-plant performance</h3>
            </div>
          </div>
          <div className="stack-list">
            {analytics.plant_snapshots.map((item) => (
              <div key={item.plant_id} className="score-row-card">
                <div>
                  <strong>{item.common_name}</strong>
                  <p className="muted">{item.recovery_mode ? 'Recovery mode active' : 'Stable growth cycle'}</p>
                </div>
                <div className="score-bars">
                  <div>
                    <span>Health</span>
                    <div className="bar-track">
                      <div className="bar-fill" style={{ width: `${item.health_score * 10}%` }} />
                    </div>
                  </div>
                  <div>
                    <span>Tasks</span>
                    <div className="bar-track faint">
                      <div className="bar-fill warm" style={{ width: `${item.completion_rate}%` }} />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="insight-note">{analytics.recommended_focus}</p>
        </section>
      ) : null}

      {analytics ? <IssueBreakdown items={analytics.issue_breakdown} /> : null}

      <section className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Plants</p>
            <h3>Current residents</h3>
          </div>
        </div>
        <div className="plant-grid">
          {(plantsQuery.data ?? []).map((plant) => (
            <Link key={plant.id} className="plant-card" to={`/plant/${plant.id}`}>
              <strong>{plant.common_name}</strong>
              <span>{plant.species_name}</span>
              <small>Health {plant.current_health_score}/10</small>
            </Link>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Quick Add</p>
            <h3>Seed from the preloaded catalog</h3>
          </div>
        </div>
        <div className="catalog-grid">
          {catalog.slice(0, 8).map((item) => (
            <button
              key={item.id}
              className="catalog-card action"
              onClick={() =>
                addPlantMutation.mutate({
                  garden_id: gardenId,
                  common_name: item.common_name,
                  species_name: item.species_name,
                  source: 'catalog',
                  care_profile: item.care_profile,
                })
              }
            >
              <p>{item.common_name}</p>
              <span>{item.species_name}</span>
              <small>Add instantly</small>
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
