import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { createPlant, fetchCatalog, fetchGardenPlants, fetchGardens } from '../services/api'

export function GardenPage() {
  const { gardenId = '' } = useParams()
  const queryClient = useQueryClient()
  const gardensQuery = useQuery({ queryKey: ['gardens'], queryFn: fetchGardens })
  const plantsQuery = useQuery({ queryKey: ['garden-plants', gardenId], queryFn: () => fetchGardenPlants(gardenId), enabled: Boolean(gardenId) })
  const catalogQuery = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalog })

  const addPlantMutation = useMutation({
    mutationFn: createPlant,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['garden-plants', gardenId] }),
  })

  const garden = (gardensQuery.data ?? []).find((item) => item.id === gardenId)
  const catalog = catalogQuery.data ?? []

  return (
    <div className="grid-layout">
      <section className="panel spotlight">
        <p className="eyebrow">Garden View</p>
        <h2>{garden?.name ?? 'Garden'}</h2>
        <p className="muted">{garden?.location_type} conditions with catalog-powered onboarding for the most common plants.</p>
      </section>

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
