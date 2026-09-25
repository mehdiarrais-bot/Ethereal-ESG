import { scoreText, ratingText, gaugePercent } from '../lib/scoreText.mjs'

export default function MiniScorebar({ scores, loading }) {
  if (!scores && !loading) return null

  // Couleurs prises aux jetons de piliers (index.css), jamais recopiées en dur.
  const pillars = [
    { label: 'E', score: scores?.environmental_score, color: 'var(--env)' },
    { label: 'S', score: scores?.social_score, color: 'var(--social)' },
    { label: 'G', score: scores?.governance_score, color: 'var(--gov)' },
  ]

  return (
    <div className="mini-scorebar">
      {loading && !scores && (
        <span className="mini-calculating">Calcul…</span>
      )}
      {scores && (
        <>
          {pillars.map(({ label, score, color }) => (
            <div key={label} className="mini-pillar">
              <span className="mini-label">{label}</span>
              <div className="mini-bar-track">
                <div
                  className="mini-bar-fill"
                  style={{ width: `${gaugePercent(score)}%`, background: color }}
                />
              </div>
              <span className="mini-value" style={{ color }}>{scoreText(score)}</span>
            </div>
          ))}
          <div className="mini-total">
            <span className="mini-total-label">Score</span>
            <span className="mini-total-value">{scoreText(scores.total_esg_score, 1)}</span>
            <span className="mini-rating">{ratingText(scores.rating)}</span>
          </div>
        </>
      )}
      <style>{`
        .mini-scorebar {
          display: flex;
          align-items: center;
          gap: 16px;
          background: var(--bg-surface);
          border-top: 1px solid var(--border);
          padding: 9px 30px;
          font-size: 12px;
          flex-wrap: wrap;
        }
        .mini-calculating { color: var(--muted); font-size: 12px; }
        .mini-pillar { display: flex; align-items: center; gap: 7px; }
        .mini-label { font-weight: 700; width: 12px; color: var(--text-dim); }
        .mini-bar-track {
          width: 80px;
          height: 5px;
          background: var(--bg-inset);
          border-radius: var(--radius-pill);
          overflow: hidden;
        }
        .mini-bar-fill {
          height: 100%;
          border-radius: var(--radius-pill);
          transition: width 0.6s var(--ease);
        }
        .mini-value { font-weight: 650; width: 22px; text-align: right; }
        /* Rang secondaire assumé : le score reste lisible, il ne domine pas. */
        .mini-total {
          margin-left: auto;
          display: flex;
          align-items: baseline;
          gap: 7px;
          border-left: 1px solid var(--border);
          padding-left: 16px;
          color: var(--text-dim);
        }
        .mini-total-label { font-size: 11px; color: var(--muted); }
        .mini-total-value { font-size: 14px; font-weight: 650; color: var(--text); }
        .mini-rating {
          font-size: 11px;
          background: var(--bg-inset);
          color: var(--text-dim);
          padding: 2px 8px;
          border-radius: var(--radius-sm);
          font-weight: 700;
        }
        @media (max-width: 560px) {
          .mini-scorebar { padding: 8px 14px; gap: 10px; }
          .mini-bar-track { width: 46px; }
        }
      `}</style>
    </div>
  )
}
