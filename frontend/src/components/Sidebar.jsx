function MiniGauge({ score, color }) {
  const r = 14
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - Math.min(100, Math.max(0, score || 0)) / 100)
  return (
    <svg width="34" height="34" viewBox="0 0 34 34" style={{ flexShrink: 0 }}>
      <circle cx="17" cy="17" r={r} fill="none" strokeWidth="3"
        style={{ stroke: 'var(--nav-active)' }} />
      <circle cx="17" cy="17" r={r} fill="none" strokeWidth="3"
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round" transform="rotate(-90 17 17)"
        style={{ stroke: color, transition: 'stroke-dashoffset 0.6s ease' }}
      />
      <text x="17" y="21" textAnchor="middle" fontSize="9" fontWeight="700" style={{ fill: color }}>
        {score ? score.toFixed(0) : '—'}
      </text>
    </svg>
  )
}

const STEP_SCORE_MAP = [null, 'environmental_score', 'social_score', 'governance_score', 'total_esg_score']
// Couleurs prises aux jetons de piliers (index.css), jamais recopiées en dur.
const STEP_COLORS = [null, 'var(--env-on-nav)', 'var(--social-on-nav)', 'var(--gov-on-nav)', 'var(--brand-mark)']

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
                  {i < current ? '✓' : i}
                </span>
              )}
              <div className="sidebar-text-wrap">
                <span className="sidebar-text">{step.label}</span>
                {score !== null && (
                  <span className="sidebar-score">{score.toFixed(1)}/100</span>
                )}
              </div>
              {i === current && <span className="sidebar-indicator" />}
            </button>
          )
        })}
      </nav>
      <style>{`
        .sidebar {
          width: 224px;
          background: var(--nav);
          border-right: 1px solid var(--nav-border);
          flex-shrink: 0;
          padding: 18px 0;
          display: flex;
          flex-direction: column;
        }
        .sidebar-label {
          font-size: 10px; font-weight: 700;
          text-transform: uppercase; letter-spacing: 1.2px;
          color: var(--text-on-nav-dim); padding: 0 20px 12px;
        }
        .sidebar-nav { display: flex; flex-direction: column; gap: 2px; padding: 0 10px; flex: 1; }
        .sidebar-item {
          display: flex; align-items: center; gap: 11px;
          padding: 9px 10px; border: 1px solid transparent; background: transparent;
          border-radius: var(--radius-sm); cursor: pointer; font-size: 13.5px;
          font-weight: 500; color: var(--text-on-nav-dim);
          transition: background var(--fast), color var(--fast);
          text-align: left; position: relative;
        }
        .sidebar-item:hover { background: var(--nav-raised); color: var(--text-on-nav); }
        .sidebar-item.active {
          background: var(--nav-active); color: var(--text-on-nav); font-weight: 650;
        }
        .sidebar-item.done { color: var(--text-on-nav); }
        .sidebar-icon {
          width: 26px; height: 26px; display: flex; align-items: center;
          justify-content: center; border-radius: var(--radius-pill);
          background: var(--nav-raised); color: var(--text-on-nav-dim);
          font-size: 12px; font-weight: 650; flex-shrink: 0;
          border: 1px solid var(--nav-border);
        }
        .icon-done { background: var(--brand); color: #fff; border-color: transparent; }
        .sidebar-item.active .sidebar-icon {
          background: var(--brand); color: #fff; border-color: transparent;
        }
        .sidebar-text-wrap { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
        .sidebar-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .sidebar-score { font-size: 11px; font-weight: 600; color: var(--text-on-nav-dim); }
        .sidebar-indicator {
          position: absolute; left: 0; top: 50%; transform: translateY(-50%);
          width: 3px; height: 20px;
          background: var(--brand-mark); border-radius: 0 2px 2px 0;
        }
        @media (max-width: 960px) {
          .sidebar { width: 62px; }
          .sidebar-text-wrap, .sidebar-label, .sidebar-indicator { display: none; }
          .sidebar-item { justify-content: center; }
        }
      `}</style>
    </aside>
  )
}
