export default function MiniScorebar({ scores, loading }) {
  if (!scores && !loading) return null

  const pillars = [
    { label: 'E', score: scores?.environmental_score, color: '#27AE60' },
    { label: 'S', score: scores?.social_score, color: '#2E86C1' },
    { label: 'G', score: scores?.governance_score, color: '#8E44AD' },
  ]

  return (
    <div className="mini-scorebar">
      {loading && !scores && (
        <span className="mini-calculating">⏳ Calcul…</span>
      )}
      {scores && (
        <>
          {pillars.map(({ label, score, color }) => (
            <div key={label} className="mini-pillar">
              <span className="mini-label">{label}</span>
              <div className="mini-bar-track">
                <div
                  className="mini-bar-fill"
                  style={{ width: `${score}%`, background: color }}
                />
              </div>
              <span className="mini-value" style={{ color }}>{score?.toFixed(0)}</span>
            </div>
          ))}
          <div className="mini-total">
            <span>{scores.total_esg_score?.toFixed(1)}</span>
            <span className="mini-rating">{scores.rating}</span>
          </div>
        </>
      )}
      <style>{`
        .mini-scorebar {
          display: flex;
          align-items: center;
          gap: 16px;
          background: white;
          border-top: 1px solid var(--border);
          padding: 10px 32px;
          font-size: 12px;
        }
        .mini-calculating { color: #8a9bb0; font-size: 12px; }
        .mini-pillar { display: flex; align-items: center; gap: 6px; }
        .mini-label { font-weight: 800; width: 14px; color: var(--text); }
        .mini-bar-track {
          width: 80px;
          height: 6px;
          background: #E8EFF8;
          border-radius: 3px;
          overflow: hidden;
        }
        .mini-bar-fill {
          height: 100%;
          border-radius: 3px;
          transition: width 0.5s ease;
        }
        .mini-value { font-weight: 700; width: 24px; text-align: right; }
        .mini-total {
          margin-left: 12px;
          display: flex;
          align-items: center;
          gap: 8px;
          border-left: 1px solid var(--border);
          padding-left: 16px;
          font-size: 18px;
          font-weight: 800;
          color: var(--blue-primary);
        }
        .mini-rating {
          font-size: 12px;
          background: var(--accent);
          color: white;
          padding: 2px 8px;
          border-radius: 4px;
          font-weight: 700;
        }
      `}</style>
    </div>
  )
}
