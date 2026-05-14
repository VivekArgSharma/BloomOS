import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { ChatPanel } from '../components/ChatPanel'
import { TaskChecklist } from '../components/TaskChecklist'
import { analyzePlant, askPlantChat, completeTask, fetchPlantDetails, fetchPlantLogs, fetchPlantTasks } from '../services/api'

export function PlantPage() {
  const { plantId = '' } = useParams()
  const queryClient = useQueryClient()
  const detailsQuery = useQuery({ queryKey: ['plant', plantId], queryFn: () => fetchPlantDetails(plantId), enabled: Boolean(plantId) })
  const logsQuery = useQuery({ queryKey: ['plant-logs', plantId], queryFn: () => fetchPlantLogs(plantId), enabled: Boolean(plantId) })
  const tasksQuery = useQuery({ queryKey: ['plant-tasks', plantId], queryFn: () => fetchPlantTasks(plantId), enabled: Boolean(plantId) })

  const analyzeMutation = useMutation({
    mutationFn: (observations: string) => analyzePlant(plantId, observations),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plant', plantId] })
      queryClient.invalidateQueries({ queryKey: ['plant-logs', plantId] })
      queryClient.invalidateQueries({ queryKey: ['plant-tasks', plantId] })
    },
  })

  const taskMutation = useMutation({
    mutationFn: (taskId: string) => completeTask(plantId, taskId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['plant-tasks', plantId] }),
  })

  const plant = detailsQuery.data?.plant
  const logs = logsQuery.data ?? []
  const plan = tasksQuery.data ?? detailsQuery.data?.plan

  if (!plant) {
    return <section className="panel"><p>Loading plant...</p></section>
  }

  return (
    <div className="grid-layout">
      <section className="panel spotlight">
        <p className="eyebrow">Plant Details</p>
        <h2>{plant.common_name}</h2>
        <p className="muted">{plant.species_name}</p>
        <div className="metric-row compact">
          <article>
            <strong>{plant.current_health_score}/10</strong>
            <span>Health</span>
          </article>
          <article>
            <strong>{plant.care_profile.water_interval_days}d</strong>
            <span>Water cycle</span>
          </article>
          <article>
            <strong>{plant.recovery_mode ? 'On' : 'Off'}</strong>
            <span>Recovery mode</span>
          </article>
        </div>
      </section>

      {plan ? <TaskChecklist tasks={plan.tasks} onComplete={async (taskId) => taskMutation.mutateAsync(taskId)} /> : null}

      <section className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Photo Analysis</p>
            <h3>Simulate today's check-in</h3>
          </div>
        </div>
        <div className="inline-fields">
          <button onClick={() => analyzeMutation.mutate('Leaves look healthy and upright.')}>Analyze healthy photo</button>
          <button onClick={() => analyzeMutation.mutate('Some yellow edges and slight droop today.')}>Analyze stressed photo</button>
        </div>
      </section>

      <section className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Plant Diary</p>
            <h3>Recent timeline</h3>
          </div>
        </div>
        <div className="timeline-list">
          {logs.length === 0 ? <p className="muted">No logs yet. Run a photo analysis to start the diary.</p> : null}
          {logs.map((log) => (
            <article key={log.id} className="timeline-card">
              <strong>{new Date(log.created_at).toLocaleDateString()}</strong>
              <p>{log.analysis.diary_entry}</p>
              <small>{log.analysis.recommended_action}</small>
            </article>
          ))}
        </div>
      </section>

      <ChatPanel onAsk={(question) => askPlantChat(plantId, question)} />
    </div>
  )
}
