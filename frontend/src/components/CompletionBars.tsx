import type { CompletionPoint } from '../types'

type Props = {
  points: CompletionPoint[]
}

export function CompletionBars({ points }: Props) {
  return (
    <section className="panel analytics-panel page-panel-full">
      <div className="section-head">
        <div>
          <p className="eyebrow">Consistency</p>
          <h3>Task completion rhythm</h3>
        </div>
      </div>
      {points.length === 0 ? (
        <p className="muted">No completion history yet.</p>
      ) : (
        <div className="bar-list">
          {points.map((point) => (
            <div key={point.label} className="bar-row">
              <div className="bar-meta">
                <span>{point.label}</span>
                <strong>{point.rate}%</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${point.rate}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
