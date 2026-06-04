function ScoreGauge({ label, score, color }) {
  const pct = Math.min(100, Math.max(0, score))
  const r = 44
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - pct / 100)

  return (
    <div className="gauge-wrap">
      <svg width="110" height="110" viewBox="0 0 110 110">
        <circle cx="55" cy="55" r={r} fill="none" stroke="#E8EFF8" strokeWidth="10" />
        <circle
          cx="55" cy="55" r={r} fill="none"
          stroke={color} strokeWidth="10"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 55 55)"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
        <text x="55" y="52" textAnchor="middle" fontSize="20" fontWeight="800" fill={color}>
          {score.toFixed(0)}
        </text>
        <text x="55" y="67" textAnchor="middle" fontSize="10" fill="#8a9bb0">
          /100
        </text>
      </svg>
      <div className="gauge-label">{label}</div>
    </div>
  )
}

function RatingBadge({ rating }) {
  const colors = {
    AAA: '#27AE60', AA: '#2ECC71', A: '#82E0AA',
    BBB: '#F39C12', BB: '#E67E22', B: '#E74C3C', CCC: '#C0392B',
  }
  return (
    <div className="rating-badge" style={{ background: colors[rating] || '#95A5A6' }}>
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

export default function ResultsPanel({ scores, onDownloadPptx, onDownloadPdf, loading, inline }) {
  if (!scores) return null

  return (
    <div className={`results-panel ${inline ? 'results-inline' : 'results-sidebar'}`}>
      <div className="results-header">
        <span>📊 Résultats ESG</span>
        <RatingBadge rating={scores.rating} />
      </div>

      <div className="gauges-row">
        <ScoreGauge label="Environnement" score={scores.environmental_score} color="#27AE60" />
        <ScoreGauge label="Social" score={scores.social_score} color="#2E86C1" />
        <ScoreGauge label="Gouvernance" score={scores.governance_score} color="#8E44AD" />
        <ScoreGauge label="Global" score={scores.total_esg_score} color="#F39C12" />
      </div>

      {scores.strengths?.length > 0 && (
        <div className="result-section">
          <div className="result-section-title">✅ Points Forts</div>
          <ListItems items={scores.strengths} icon="✓" color="#27AE60" />
        </div>
      )}

      {scores.weaknesses?.length > 0 && (
        <div className="result-section">
          <div className="result-section-title">⚠️ Axes d'Amélioration</div>
          <ListItems items={scores.weaknesses} icon="→" color="#E67E22" />
        </div>
      )}

      {scores.recommendations?.length > 0 && (
        <div className="result-section">
          <div className="result-section-title">💡 Recommandations</div>
          <ListItems items={scores.recommendations.slice(0, 4)} icon="•" color="#2E86C1" />
        </div>
      )}

      <div className="download-actions">
        <button
          className="btn btn-pptx"
          onClick={onDownloadPptx}
          disabled={loading}
          style={{ flex: 1 }}
        >
          {loading ? '⏳' : '📑'} PowerPoint
        </button>
        <button
          className="btn btn-pdf"
          onClick={onDownloadPdf}
          disabled={loading}
          style={{ flex: 1 }}
        >
          {loading ? '⏳' : '📄'} Rapport PDF
        </button>
      </div>

      <style>{`
        .results-panel {
          background: white;
          border-left: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          gap: 20px;
          overflow-y: auto;
        }
        .results-sidebar {
          width: 340px;
          flex-shrink: 0;
          padding: 24px 20px;
        }
        .results-inline {
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 24px;
          border-left: 4px solid var(--accent);
        }
        .results-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 18px;
          font-weight: 800;
          color: var(--blue-primary);
        }
        .rating-badge {
          padding: 6px 16px;
          border-radius: 8px;
          color: white;
          text-align: center;
        }
        .rating-label { font-size: 10px; font-weight: 600; opacity: 0.85; text-transform: uppercase; }
        .rating-value { font-size: 22px; font-weight: 900; line-height: 1.2; }
        .gauges-row {
          display: flex;
          gap: 8px;
          justify-content: space-around;
          flex-wrap: wrap;
        }
        .gauge-wrap { display: flex; flex-direction: column; align-items: center; gap: 4px; }
        .gauge-label { font-size: 11px; font-weight: 600; color: #5a6a7e; text-align: center; }
        .result-section { display: flex; flex-direction: column; gap: 8px; }
        .result-section-title {
          font-size: 13px;
          font-weight: 700;
          color: var(--blue-primary);
        }
        .result-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .result-list li {
          padding: 8px 12px;
          background: var(--bg);
          border-radius: 6px;
          font-size: 12px;
          color: var(--text);
          display: flex;
          align-items: flex-start;
          gap: 8px;
          line-height: 1.4;
        }
        .result-icon { flex-shrink: 0; font-size: 12px; margin-top: 1px; }
        .download-actions {
          display: flex;
          gap: 10px;
          padding-top: 4px;
          border-top: 1px solid var(--border);
          margin-top: 4px;
        }
      `}</style>
    </div>
  )
}
