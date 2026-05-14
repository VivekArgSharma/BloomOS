type Point = {
  label: string
  score: number
}

type Props = {
  title: string
  subtitle: string
  points: Point[]
  max?: number
}

function buildPath(points: Point[], width: number, height: number, max: number) {
  if (points.length === 0) return ''
  return points
    .map((point, index) => {
      const x = points.length === 1 ? width / 2 : (index / (points.length - 1)) * width
      const y = height - (point.score / max) * height
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
}

export function TrendChart({ title, subtitle, points, max = 10 }: Props) {
  const width = 320
  const height = 120
  const path = buildPath(points, width, height, max)

  return (
    <section className="panel analytics-panel">
      <div className="section-head">
        <div>
          <p className="eyebrow">Analytics</p>
          <h3>{title}</h3>
        </div>
        <span className="pill">{subtitle}</span>
      </div>
      {points.length === 0 ? (
        <p className="muted">No chart data yet.</p>
      ) : (
        <div className="trend-wrap">
          <svg viewBox={`0 0 ${width} ${height}`} className="trend-svg" preserveAspectRatio="none" aria-hidden="true">
            {[0.25, 0.5, 0.75, 1].map((fraction) => (
              <line key={fraction} x1="0" y1={height - height * fraction} x2={width} y2={height - height * fraction} className="trend-grid" />
            ))}
            <path d={path} className="trend-path" />
            {points.map((point, index) => {
              const x = points.length === 1 ? width / 2 : (index / (points.length - 1)) * width
              const y = height - (point.score / max) * height
              return <circle key={`${point.label}-${index}`} cx={x} cy={y} r="4" className="trend-dot" />
            })}
          </svg>
          <div className="trend-labels">
            {points.map((point) => (
              <div key={point.label}>
                <span>{point.label}</span>
                <strong>{point.score}</strong>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
