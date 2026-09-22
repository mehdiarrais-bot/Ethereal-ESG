function ScoreGauge({ label, score, color }) {
  const pct = Math.min(100, Math.max(0, score))
  const r = 44
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - pct / 100)

  return (
    <div className="gauge-wrap">
      <svg width="110" height="110" viewBox="0 0 110 110">
        <circle cx="55" cy="55" r={r} fill="none" strokeWidth="10" style={{ stroke: 'var(--bg-inset)' }} />
        <circle
          cx="55" cy="55" r={r} fill="none"
          strokeWidth="10"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 55 55)"
          style={{ stroke: color, transition: 'stroke-dashoffset 0.8s ease' }}
        />
        <text x="55" y="52" textAnchor="middle" fontSize="20" fontWeight="700" style={{ fill: color }}>
          {score.toFixed(0)}
        </text>
        <text x="55" y="67" textAnchor="middle" fontSize="10" style={{ fill: 'var(--muted)' }}>
          /100
        </text>
      </svg>
      <div className="gauge-label">{label}</div>
    </div>
  )
}

function RatingBadge({ rating }) {
  return (
    <div className="rating-badge">
      <div className="rating-label">Note ESG</div>
      <div className="rating-value">{rating}</div>
    </div>
  )
}

function ListItems({ items, icon, color }) {
  return (
    <ul className="result-list">
      {items.map((item, i) => (
        <li key={i} style={{ borderLeft: `3px solid ${color}` }}>
          <span className="result-icon">{icon}</span>
          {item}
        </li>
      ))}
    </ul>
  )
}

export default function ResultsPanel({ scores, onDownloadPptx, onDownloadPdf, onDownloadDocx, loading, progress, inline }) {
  if (!scores) return null

  return (
    <div className={`results-panel ${inline ? 'results-inline' : 'results-sidebar'}`}>
      <div className="results-header">
        <span>Résultats ESG</span>
        <RatingBadge rating={scores.rating} />
      </div>

      <div className="gauges-row">
        <ScoreGauge label="Environnement" score={scores.environmental_score} color="var(--env)" />
        <ScoreGauge label="Social" score={scores.social_score} color="var(--social)" />
        <ScoreGauge label="Gouvernance" score={scores.governance_score} color="var(--gov)" />
        <ScoreGauge label="Global" score={scores.total_esg_score} color="var(--brand)" />
      </div>

      {scores.strengths?.length > 0 && (
        <div className="result-section">
          <div className="result-section-title">Points forts</div>
          <ListItems items={scores.strengths} icon="✓" color="var(--ok)" />
        </div>
      )}

      {scores.weaknesses?.length > 0 && (
        <div className="result-section">
          <div className="result-section-title">Axes d'amélioration</div>
          <ListItems items={scores.weaknesses} icon="→" color="var(--warn)" />
        </div>
      )}

      {scores.recommendations?.length > 0 && (
        <div className="result-section">
          <div className="result-section-title">Recommandations</div>
          <ListItems items={scores.recommendations.slice(0, 4)} icon="•" color="var(--social)" />
        </div>
      )}

      <div className="download-actions">
        <button className="btn btn-pptx" onClick={onDownloadPptx} disabled={loading} style={{ flex: 1 }}>
          PowerPoint
        </button>
        <button className="btn btn-pdf" onClick={onDownloadPdf} disabled={loading} style={{ flex: 1 }}>
          PDF
        </button>
        <button className="btn btn-docx" onClick={onDownloadDocx} disabled={loading} style={{ flex: 1 }}>
          Word
        </button>
      </div>
      {loading && progress > 0 && (
        <div className="rp-progress-wrap">
          <div className="rp-progress-bg">
            <div className="rp-progress-fill" style={{ width: `${Math.min(100, progress)}%`, background: progress === 100 ? 'var(--ok)' : undefined }} />
          </div>
          <span className="rp-progress-label">
            {progress === 100 ? '✓ Pret' : `Generation... ${Math.round(progress)}%`}
          </span>
        </div>
      )}

      <style>{`
        .results-panel {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .results-sidebar {
          width: 320px;
          flex-shrink: 0;
          padding: 20px 18px;
          overflow-y: auto;
          max-height: 100%;
          border-left: 1px solid var(--border);
          background: var(--bg-surface);
        }
        .results-inline {
          border: 1px solid var(--border);
          border-radius: var(--radius-lg);
          padding: 22px 24px;
          background: var(--bg-surface);
          box-shadow: var(--shadow);
        }
        .results-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 16px;
          font-weight: 650;
          color: var(--text);
        }
        /* Rang secondaire assume : la note informe, elle ne domine plus. */
        .rating-badge {
          padding: 5px 12px;
          border-radius: var(--radius-sm);
          background: var(--bg-inset);
          text-align: center;
        }
        .rating-label { font-size: 9.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); }
        .rating-value { font-size: 15px; font-weight: 700; line-height: 1.2; color: var(--text); }
        .gauges-row {
          display: flex;
          gap: 8px;
          justify-content: space-around;
          flex-wrap: wrap;
        }
        .gauge-wrap { display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .gauge-label { font-size: 11px; font-weight: 600; color: var(--text-dim); text-align: center; }
        .result-section { display: flex; flex-direction: column; gap: 8px; }
        .result-section-title {
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.6px;
          color: var(--text-dim);
        }
        .result-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .result-list li {
          padding: 9px 12px;
          background: var(--bg-subtle);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          font-size: 12px;
          color: var(--text-dim);
          display: flex;
          align-items: flex-start;
          gap: 8px;
          line-height: 1.45;
        }
        .result-icon { flex-shrink: 0; font-size: 12px; margin-top: 1px; }
        .download-actions {
          display: flex;
          gap: 8px;
          padding-top: 12px;
          border-top: 1px solid var(--border);
          margin-top: 4px;
        }
        .rp-progress-wrap {
          display: flex; flex-direction: column; gap: 5px;
        }
        .rp-progress-bg {
          width: 100%; height: 6px; background: var(--bg-inset);
          border-radius: var(--radius-pill); overflow: hidden;
        }
        .rp-progress-fill {
          height: 100%; background: var(--brand);
          border-radius: var(--radius-pill); transition: width 0.3s var(--ease);
        }
        .rp-progress-label {
          font-size: 11px; color: var(--text-dim); font-weight: 600;
        }
        @media (max-width: 960px) {
          .results-sidebar { display: none; }
        }
      `}</style>
    </div>
  )
}
