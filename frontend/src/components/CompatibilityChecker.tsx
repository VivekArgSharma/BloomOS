import { useState } from 'react'

import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../context/AuthContext'
import { fetchGardenPlants, fetchPlantCompatibility } from '../services/api'

type Props = {
  gardenId: string
  locationType: string
}

export function CompatibilityChecker({ gardenId, locationType }: Props) {
  const { user } = useAuth()
  const [selectedPlantId, setSelectedPlantId] = useState<string | null>(null)

  const plantsQuery = useQuery({
    queryKey: ['garden-plants', gardenId],
    queryFn: () => fetchGardenPlants(gardenId),
    enabled: Boolean(user && gardenId),
  })

  const compatibilityQuery = useQuery({
    queryKey: ['compatibility', selectedPlantId, locationType],
    queryFn: () => fetchPlantCompatibility(selectedPlantId!, locationType),
    enabled: Boolean(selectedPlantId),
  })

  const plants = plantsQuery.data ?? []

  if (plants.length === 0) {
    return null
  }

  return (
    <div className="compatibility-checker">
      <div className="plant-select-row">
        <label className="eyebrow">Check Compatibility</label>
        <select
          value={selectedPlantId || ''}
          onChange={(e) => setSelectedPlantId(e.target.value || null)}
        >
          <option value="">Select a plant...</option>
          {plants.map((plant) => (
            <option key={plant.id} value={plant.id}>
              {plant.common_name}
            </option>
          ))}
        </select>
      </div>

      {compatibilityQuery.isLoading && <p className="muted">Analyzing...</p>}

      {compatibilityQuery.data && (
        <div className={`compatibility-card ${compatibilityQuery.data.compatible ? 'compatible' : 'not-compatible'}`}>
          <div className="compat-header">
            <strong>
              {compatibilityQuery.data.compatible ? '✓ Compatible' : '⚠ May Struggle'}
            </strong>
            <span>{compatibilityQuery.data.confidence}% confidence</span>
          </div>

          {compatibilityQuery.data.issues.length > 0 && (
            <ul className="compat-issues">
              {compatibilityQuery.data.issues.map((issue, i) => (
                <li key={i}>{issue}</li>
              ))}
            </ul>
          )}

          {compatibilityQuery.data.recommendations.length > 0 && (
            <div className="compat-recs">
              {compatibilityQuery.data.recommendations.map((rec, i) => (
                <p key={i}>{rec}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}