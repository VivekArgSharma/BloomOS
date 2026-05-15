import type { IssueCount } from '../types'

type Props = {
  items: IssueCount[]
}

export function IssueBreakdown({ items }: Props) {
  const topCount = items[0]?.count ?? 1

  return (
    <section className="panel analytics-panel page-panel-full">
      <div className="section-head">
        <div>
          <p className="eyebrow">Signals</p>
          <h3>Observed patterns</h3>
        </div>
      </div>
      {items.length === 0 ? (
        <p className="muted">No recurring issues tracked yet.</p>
      ) : (
        <div className="bar-list compact-bars">
          {items.map((item) => (
            <div key={item.issue} className="bar-row">
              <div className="bar-meta">
                <span>{item.issue}</span>
                <strong>{item.count}</strong>
              </div>
              <div className="bar-track faint">
                <div className="bar-fill warm" style={{ width: `${(item.count / topCount) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
