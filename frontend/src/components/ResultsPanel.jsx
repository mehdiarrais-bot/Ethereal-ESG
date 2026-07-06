function ScoreGauge({ label, score, color }) {
  const pct = Math.min(100, Math.max(0, score))
  const r = 44
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - pct / 100)

  return (
    <div className="gauge-wrap">
      <svg width="110" height="110" viewBox="0 0 110 110">
        <circle cx="55" cy="55" r={r} fill="none" stroke="rgba(140,120,255,0.18)" strokeWidth="10" />
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
        <text x="55" y="67" textAnchor="middle" fontSize="10" fill="var(--muted)">
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

export default function ResultsPanel({ scores, onDownloadPptx, onDownloadPdf, onDownloadDocx, loading, progress, inline }) {
  if (!scores) return null

  return (
    <div className={`results-panel ${inline ? 'results-inline' : 'results-sidebar'}`}>
      <div className="results-header">
        <span>📊 Résultats ESG</span>
        <RatingBadge rating={scores.rating} />
      </div>

      <div className="gauges-row">
        <ScoreGauge label="Environnement" score={scores.environmental_score} color="#34d399" />
        <ScoreGauge label="Social" score={scores.social_score} color="#38bdf8" />
        <ScoreGauge label="Gouvernance" score={scores.governance_score} color="#c084fc" />
        <ScoreGauge label="Global" score={scores.total_esg_score} color="#22d3ee" />
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
        <button className="btn btn-pptx" onClick={onDownloadPptx} disabled={loading} style={{ flex: 1 }}>
          📑 PowerPoint
        </button>
        <button className="btn btn-pdf" onClick={onDownloadPdf} disabled={loading} style={{ flex: 1 }}>
          📄 PDF
        </button>
        <button className="btn btn-docx" onClick={onDownloadDocx} disabled={loading} style={{ flex: 1 }}>
          📝 Word
        </button>
      </div>
      {loading && progress > 0 && (
        <div className="rp-progress-wrap">
          <div className="rp-progress-bg">
            <div className="rp-progress-fill" style={{ width: `${Math.min(100, progress)}%`, background: progress === 100 ? '#27AE60' : undefined }} />
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
          padding: 20px 16px;
          overflow-y: auto;
          max-height: 100%;
          border-left: 1px solid var(--glass-border);
          background: rgba(8, 5, 22, 0.4);
          backdrop-filter: blur(14px);
          -webkit-backdrop-filter: blur(14px);
        }
        .results-inline {
          border: 1px solid var(--glass-border);
          border-radius: var(--radius);
          padding: 24px;
          border-left: 3px solid var(--neon);
          background: var(--glass-strong);
          backdrop-filter: blur(16px);
        }
        .results-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 18px;
          font-weight: 800;
          color: var(--text);
        }
        .rating-badge {
          padding: 6px 16px;
          border-radius: 8px;
          color: white;
          text-align: center;
        }
        .rating-label { font-size: 10px; font-weight: 600; opacity: 0.9; text-transform: uppercase; color: #04121a; }
        .rating-value { font-size: 22px; font-weight: 900; line-height: 1.2; color: #04121a; }
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
          font-size: 13px;
          font-weight: 700;
          color: var(--text);
        }
        .result-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .result-list li {
          padding: 8px 12px;
          background: rgba(124,92,246,0.08);
          border-radius: 8px;
          font-size: 12px;
          color: var(--text-dim);
          display: flex;
          align-items: flex-start;
          gap: 8px;
          line-height: 1.4;
        }
        .result-icon { flex-shrink: 0; font-size: 12px; margin-top: 1px; }
        .download-actions {
          display: flex;
          gap: 10px;
          padding-top: 12px;
          border-top: 1px solid var(--glass-border);
          margin-top: 4px;
        }
        .rp-progress-wrap {
          display: flex; flex-direction: column; gap: 5px;
        }
        .rp-progress-bg {
          width: 100%; height: 6px; background: rgba(140,120,255,0.18); border-radius: 99px; overflow: hidden;
        }
        .rp-progress-fill {
          height: 100%; background: linear-gradient(90deg, var(--violet), var(--neon));
          border-radius: 99px; transition: width 0.3s var(--ease); box-shadow: var(--glow-neon);
        }
        .rp-progress-label {
          font-size: 11px; color: var(--neon); font-weight: 600;
        }
        @media (max-width: 960px) {
          .results-sidebar { display: none; }
        }
      `}</style>
    </div>
  )
}
