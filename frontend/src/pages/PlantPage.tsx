import { useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { AuthRequired } from '../components/AuthRequired'
import { ChatPanel } from '../components/ChatPanel'
import { CompletionBars } from '../components/CompletionBars'
import { FileUploadButton } from '../components/FileUploadButton'
import { IssueBreakdown } from '../components/IssueBreakdown'
import { TaskChecklist } from '../components/TaskChecklist'
import { TrendChart } from '../components/TrendChart'
import { useAuth } from '../context/AuthContext'
import { analyzePlant, askPlantChat, completeTask, fetchPlantAnalytics, fetchPlantDetails, fetchPlantLogs, fetchPlantTasks, previewPlantAnalysis } from '../services/api'

export function PlantPage() {
  const { plantId = '' } = useParams()
  const { user, loading } = useAuth()
  const queryClient = useQueryClient()
  const [analysisFile, setAnalysisFile] = useState<File | null>(null)
  const [observations, setObservations] = useState('')
  const [previewData, setPreviewData] = useState<{ health_score: number; summary: string; issues: string[]; is_urgent: boolean } | null>(null)
  const [isPreviewLoading, setIsPreviewLoading] = useState(false)

  const detailsQuery = useQuery({ queryKey: ['plant', plantId], queryFn: () => fetchPlantDetails(plantId), enabled: Boolean(plantId && user) })
  const logsQuery = useQuery({ queryKey: ['plant-logs', plantId], queryFn: () => fetchPlantLogs(plantId), enabled: Boolean(plantId && user) })
  const tasksQuery = useQuery({ queryKey: ['plant-tasks', plantId], queryFn: () => fetchPlantTasks(plantId), enabled: Boolean(plantId && user) })
  const analyticsQuery = useQuery({ queryKey: ['plant-analytics', plantId], queryFn: () => fetchPlantAnalytics(plantId), enabled: Boolean(plantId && user) })

  const previewMutation = useMutation({
    mutationFn: async () => {
      if (!analysisFile) throw new Error('Select a photo first')
      setIsPreviewLoading(true)
      const result = await previewPlantAnalysis(plantId, analysisFile, observations)
      return result
    },
    onSuccess: (data) => {
      setPreviewData(data)
      setIsPreviewLoading(false)
    },
    onError: () => {
      setIsPreviewLoading(false)
    },
  })

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
      setPreviewData(null)
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

  const handleFileSelect = (file: File | null) => {
    setAnalysisFile(file)
    setPreviewData(null)
  }

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
    <div className="grid-layout plant-layout">
      <section className="panel spotlight">
        <div className="spotlight-content">
          <div className="panel-intro">
            <p className="eyebrow">Plant Details</p>
            <h2>{plant.common_name}</h2>
            <p className="muted">{plant.species_name}</p>
          </div>
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

      <section className="panel page-panel-full">
        <div className="section-head">
          <div>
            <p className="eyebrow">Photo Analysis</p>
            <h3>Upload today's plant photo</h3>
          </div>
        </div>
        <div className="panel-content-split">
          <div className="panel-intro">
            <p className="section-copy">A single check-in photo can update health history, surface emerging issues, and create a more complete diary entry for this plant.</p>
            <p className="section-copy">Use the preview first when you want a quick read before committing the analysis to the timeline.</p>
          </div>
          <div className="form-panel">
            <FileUploadButton
              onFileSelect={handleFileSelect}
              selectedFile={analysisFile}
              label="Upload plant photo"
            />
            <div className="field-group">
              <label className="field-label" htmlFor="plant-observations">Observations</label>
              <textarea 
                id="plant-observations"
                value={observations} 
                onChange={(event) => setObservations(event.target.value)} 
                placeholder="Optional notes: yellow edges, drooping, dry soil, new growth..." 
                rows={3} 
              />
            </div>

            {analysisFile && (
              <div className="upload-actions">
                <button 
                  onClick={() => previewMutation.mutate()} 
                  disabled={isPreviewLoading || previewMutation.isPending}
                  className="secondary"
                >
                  {isPreviewLoading ? 'Analyzing...' : 'Preview Analysis'}
                </button>
                <button 
                  onClick={() => analyzeMutation.mutate()} 
                  disabled={!analysisFile || analyzeMutation.isPending}
                >
                  {analyzeMutation.isPending ? 'Saving...' : 'Save to Diary'}
                </button>
              </div>
            )}

            {analyzeMutation.isError ? <p className="status-text error">{(analyzeMutation.error as Error).message}</p> : null}
          </div>
        </div>

        {/* Analysis Preview */}
        {isPreviewLoading && (
          <div className="analysis-loading">
            <div className="spinner"></div>
            <span>Analyzing your plant photo...</span>
          </div>
        )}

        {previewData && !analyzeMutation.isSuccess && (
          <div className="analysis-preview">
            <div className={`health-badge ${previewData.is_urgent ? 'danger' : previewData.health_score < 7 ? 'warning' : ''}`}>
              Health Score: {previewData.health_score}/10
            </div>
            <h4>AI Summary</h4>
            <p>{previewData.summary}</p>
            {previewData.issues.length > 0 && previewData.issues[0] !== 'none' && (
              <div className="detected-issues">
                <small>Detected: {previewData.issues.join(', ')}</small>
              </div>
            )}
          </div>
        )}
      </section>

      <section className="panel page-panel-full">
        <div className="section-head">
          <div>
            <p className="eyebrow">Plant Diary</p>
            <h3>Recent timeline</h3>
          </div>
        </div>
        <p className="section-copy">Each photo, summary, and recommendation becomes part of a visible care record you can review over time.</p>
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
