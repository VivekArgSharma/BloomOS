import { useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { AuthRequired } from '../components/AuthRequired'
import { ChatPanel } from '../components/ChatPanel'
import { CompletionBars } from '../components/CompletionBars'
import { IssueBreakdown } from '../components/IssueBreakdown'
import { TaskChecklist } from '../components/TaskChecklist'
import { TrendChart } from '../components/TrendChart'
import { useAuth } from '../context/AuthContext'
import { analyzePlant, askPlantChat, completeTask, fetchPlantAnalytics, fetchPlantDetails, fetchPlantLogs, fetchPlantTasks } from '../services/api'

export function PlantPage() {
  const { plantId = '' } = useParams()
  const { user, loading } = useAuth()
  const queryClient = useQueryClient()
  const [analysisFile, setAnalysisFile] = useState<File | null>(null)
  const [observations, setObservations] = useState('')

  const detailsQuery = useQuery({ queryKey: ['plant', plantId], queryFn: () => fetchPlantDetails(plantId), enabled: Boolean(plantId && user) })
  const logsQuery = useQuery({ queryKey: ['plant-logs', plantId], queryFn: () => fetchPlantLogs(plantId), enabled: Boolean(plantId && user) })
  const tasksQuery = useQuery({ queryKey: ['plant-tasks', plantId], queryFn: () => fetchPlantTasks(plantId), enabled: Boolean(plantId && user) })
  const analyticsQuery = useQuery({ queryKey: ['plant-analytics', plantId], queryFn: () => fetchPlantAnalytics(plantId), enabled: Boolean(plantId && user) })

  const analyzeMutation = useMutation({
    mutationFn: () => {
      if (!analysisFile) {
        throw new Error('Please choose a photo first.')
      }
      return analyzePlant(plantId, { file: analysisFile, observations })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plant', plantId] })
      queryClient.invalidateQueries({ queryKey: ['plant-logs', plantId] })
      queryClient.invalidateQueries({ queryKey: ['plant-tasks', plantId] })
      queryClient.invalidateQueries({ queryKey: ['plant-analytics', plantId] })
      setAnalysisFile(null)
      setObservations('')
    },
  })

  const taskMutation = useMutation({
    mutationFn: (taskId: string) => completeTask(plantId, taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plant-tasks', plantId] })
      queryClient.invalidateQueries({ queryKey: ['plant-analytics', plantId] })
    },
  })

  const plant = detailsQuery.data?.plant
  const logs = logsQuery.data ?? []
  const plan = tasksQuery.data ?? detailsQuery.data?.plan
  const analytics = analyticsQuery.data

  if (loading) {
    return <section className="panel"><p>Loading account...</p></section>
  }

  if (!user) {
    return <AuthRequired message="Sign in to upload progress photos, run Gemini analysis, and save your plant history." />
  }

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

      {analytics ? (
        <section className="panel analytics-panel">
          <div className="section-head">
            <div>
              <p className="eyebrow">Plant Analytics</p>
              <h3>Performance snapshot</h3>
            </div>
          </div>
          <div className="metric-row compact analytics-metrics">
            <article>
              <strong>{analytics.average_health}/10</strong>
              <span>Average health</span>
            </article>
            <article>
              <strong>{analytics.task_completion_rate}%</strong>
              <span>Task completion</span>
            </article>
            <article>
              <strong>{analytics.streak_days}d</strong>
              <span>Consistency streak</span>
            </article>
          </div>
          <p className="insight-note">{analytics.insight}</p>
        </section>
      ) : null}

      {analytics ? <TrendChart title="Health trend" subtitle={`${analytics.health_delta >= 0 ? '+' : ''}${analytics.health_delta} change this week`} points={analytics.health_history} max={10} /> : null}

      {analytics ? <CompletionBars points={analytics.completion_history} /> : null}

      {analytics ? <IssueBreakdown items={analytics.issue_breakdown} /> : null}

      {plan ? <TaskChecklist tasks={plan.tasks} onComplete={async (taskId) => taskMutation.mutateAsync(taskId)} /> : null}

      <section className="panel">
        <div className="section-head">
          <div>
            <p className="eyebrow">Photo Analysis</p>
            <h3>Upload today's plant photo</h3>
          </div>
        </div>
        <div className="form-panel">
          <input type="file" accept="image/*" onChange={(event) => setAnalysisFile(event.target.files?.[0] ?? null)} />
          <textarea value={observations} onChange={(event) => setObservations(event.target.value)} placeholder="Optional notes: yellow edges, drooping, dry soil, new growth..." rows={4} />
          <button onClick={() => analyzeMutation.mutate()} disabled={!analysisFile || analyzeMutation.isPending}>
            {analyzeMutation.isPending ? 'Analyzing photo...' : 'Analyze uploaded photo'}
          </button>
          {analyzeMutation.isError ? <p className="status-text">{(analyzeMutation.error as Error).message}</p> : null}
          {analysisFile ? <p className="status-text">Selected: {analysisFile.name}</p> : null}
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
          {logs.length === 0 ? <p className="muted">No logs yet. Upload a photo to start the diary.</p> : null}
          {logs.map((log) => (
            <article key={log.id} className="timeline-card">
              <strong>{new Date(log.created_at).toLocaleDateString()}</strong>
              <img src={log.photo_url} alt={`${plant.common_name} log`} className="timeline-photo" />
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
