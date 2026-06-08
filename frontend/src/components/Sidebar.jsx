function MiniGauge({ score, color }) {
  const r = 14
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - Math.min(100, Math.max(0, score || 0)) / 100)
  return (
    <svg width="34" height="34" viewBox="0 0 34 34" style={{ flexShrink: 0 }}>
      <circle cx="17" cy="17" r={r} fill="none" stroke="#E8EFF8" strokeWidth="4" />
      <circle cx="17" cy="17" r={r} fill="none" stroke={color} strokeWidth="4"
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round" transform="rotate(-90 17 17)"
        style={{ transition: 'stroke-dashoffset 0.6s ease' }}
      />
      <text x="17" y="21" textAnchor="middle" fontSize="9" fontWeight="800" fill={color}>
        {score ? score.toFixed(0) : '—'}
      </text>
    </svg>
  )
}

const STEP_SCORE_MAP = [null, 'environmental_score', 'social_score', 'governance_score', 'total_esg_score']
const STEP_COLORS = [null, '#27AE60', '#2E86C1', '#8E44AD', '#F39C12']

export default function Sidebar({ steps, current, onChange, scores }) {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <div className="sidebar-label">Saisie des données</div>
        {steps.map((step, i) => {
          const scoreKey = STEP_SCORE_MAP[i]
          const score = scores && scoreKey ? scores[scoreKey] : null
          const color = STEP_COLORS[i]
          return (
            <button
              key={step.id}
              className={`sidebar-item ${i === current ? 'active' : ''} ${i < current ? 'done' : ''}`}
              onClick={() => onChange(i)}
            >
              {score !== null ? (
                <MiniGauge score={score} color={color} />
              ) : (
                <span className={`sidebar-icon ${i < current ? 'icon-done' : ''}`}>
                  {i < current ? '✓' : step.icon}
                </span>
              )}
              <div className="sidebar-text-wrap">
                <span className="sidebar-text">{step.label}</span>
                {score !== null && (
                  <span className="sidebar-score" style={{ color }}>{score.toFixed(1)}/100</span>
                )}
              </div>
              {i === current && <span className="sidebar-indicator" />}
            </button>
          )
        })}
      </nav>
      <style>{`
        .sidebar {
          width: 220px;
          background: white;
          border-right: 1px solid var(--border);
          flex-shrink: 0;
          padding: 20px 0;
          display: flex;
          flex-direction: column;
        }
        .sidebar-label {
          font-size: 10px; font-weight: 700;
          text-transform: uppercase; letter-spacing: 1.5px;
          color: #8a9bb0; padding: 0 16px 14px;
        }
        .sidebar-nav { display: flex; flex-direction: column; gap: 2px; padding: 0 8px; flex: 1; }
        .sidebar-item {
          display: flex; align-items: center; gap: 10px;
          padding: 10px 12px; border: none; background: transparent;
          border-radius: 10px; cursor: pointer; font-size: 13px;
          font-weight: 500; color: #5a6a7e; transition: all 0.15s;
          text-align: left; position: relative;
        }
        .sidebar-item:hover { background: var(--bg); color: var(--blue-primary); }
        .sidebar-item.active { background: rgba(27,58,107,0.08); color: var(--blue-primary); font-weight: 700; }
        .sidebar-item.done { color: var(--env); }
        .sidebar-icon {
          width: 34px; height: 34px; display: flex; align-items: center;
          justify-content: center; border-radius: 8px;
          background: var(--bg); font-size: 16px; flex-shrink: 0;
        }
        .icon-done { background: var(--env); color: white; font-size: 14px; }
        .sidebar-item.active .sidebar-icon { background: var(--blue-primary); font-size: 14px; }
        .sidebar-text-wrap { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
        .sidebar-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .sidebar-score { font-size: 11px; font-weight: 700; }
        .sidebar-indicator {
          position: absolute; right: 0; top: 50%; transform: translateY(-50%);
          width: 3px; height: 22px; background: var(--blue-primary); border-radius: 2px 0 0 2px;
        }
        @media (max-width: 960px) {
          .sidebar { width: 60px; }
          .sidebar-text-wrap, .sidebar-label, .sidebar-indicator { display: none; }
          .sidebar-item { justify-content: center; }
        }
      `}</style>
    </aside>
  )
}
