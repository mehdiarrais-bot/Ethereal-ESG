import { useState, useEffect } from 'react'
import { computeSparklinePoints, groupByStatus, averageScore } from '../lib/portfolioMath.mjs'

// Couleurs de statut prises aux jetons (index.css), jamais recopiées en dur.
const STATUSES = {
  prospect: { label: 'Prospect', color: 'var(--social)' },
  signed: { label: 'Signé', color: 'var(--gov)' },
  delivered: { label: 'Livré', color: 'var(--ok)' },
  archived: { label: 'Archivé', color: 'var(--neutral)' },
}

/** Sparkline SVG de la trajectoire du score. Le calcul des points est dans
 * lib/portfolioMath.mjs (testé indépendamment du rendu). */
function Sparkline({ history }) {
  const pts = computeSparklinePoints(history)
  if (!pts) return <div className="spark-empty">—</div>
  const col = pts.up ? 'var(--ok)' : 'var(--danger)'
  return (
    <svg width={pts.W} height={pts.H} className="spark">
      <path d={pts.path} fill="none" strokeWidth="2" strokeLinecap="round" style={{ stroke: col }} />
      <circle cx={pts.lastX} cy={pts.lastY} r="3" style={{ fill: col }} />
    </svg>
  )
}

/**
 * Vue portefeuille — le cockpit du consultant : tous les clients,
 * statut de mission, dernier score et trajectoire, en un écran.
 */
export default function PortfolioView({ onClose, onLoad }) {
  const [clients, setClients] = useState(null)

  useEffect(() => {
    fetch('/api/clients').then(r => r.json()).then(setClients).catch(() => setClients([]))
  }, [])

  const byStatus = groupByStatus(clients)
  const avg = averageScore(clients)

  return (
    <div className="pf-overlay" onClick={e => { if (e.target === e.currentTarget) onClose() }}>
      <div className="pf-panel">
        <div className="pf-head">
          <div>
            <div className="pf-title">Portefeuille clients</div>
            <div className="pf-sub">
              {(clients || []).length} dossier{(clients || []).length > 1 ? 's' : ''}
              {Object.entries(byStatus).map(([k, n]) => (
                <span key={k} className="pf-chip" style={{ color: STATUSES[k]?.color }}>
                  {n} {STATUSES[k]?.label?.toLowerCase()}
                </span>
              ))}
              {avg != null && <span className="pf-chip">score moyen {avg.toFixed(0)}/100</span>}
            </div>
          </div>
          <button className="pf-close" onClick={onClose}>✕</button>
        </div>

        {clients === null && <div className="pf-empty">Chargement…</div>}
        {clients?.length === 0 && (
          <div className="pf-empty">
            Aucun dossier client. Remplissez le formulaire puis « Enregistrer ».
          </div>
        )}

        <div className="pf-grid">
          {(clients || []).map(c => {
            const st = STATUSES[c.status || 'prospect']
            return (
              <button key={c.id} className="pf-card" onClick={() => { onLoad(c.id); onClose() }}>
                <div className="pf-card-head">
                  <span className="pf-name">{c.name}</span>
                  <span className="pf-status" style={{ color: st.color, borderColor: st.color }}>
                    {st.label}
                  </span>
                </div>
                <div className="pf-meta">{c.sector}</div>
                <div className="pf-body">
                  <div className="pf-score">
                    {c.last_score != null ? (
                      <>
                        <span className="pf-score-num">{Math.round(c.last_score)}</span>
                        <span className="pf-score-sub">/100 · {c.last_rating}</span>
                      </>
                    ) : <span className="pf-score-sub">non scoré</span>}
                  </div>
                  <Sparkline history={c.history} />
                </div>
                <div className="pf-years">
                  {c.years?.length ? `Exercices : ${c.years.join(' · ')}` : 'Aucun exercice'}
                </div>
              </button>
            )
          })}
        </div>
      </div>

      <style>{`
        .pf-overlay {
          position: fixed; inset: 0; z-index: 500;
          background: var(--scrim);
          display: flex; align-items: flex-start; justify-content: center;
          padding: 40px 20px; overflow: auto;
        }
        .pf-panel {
          width: min(1100px, 100%);
          background: var(--bg-surface); border: 1px solid var(--border);
          border-radius: var(--radius-lg); box-shadow: var(--shadow-lg);
          padding: 22px 26px 26px;
        }
        .pf-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 18px; }
        .pf-title { font-size: 18px; font-weight: 650; color: var(--text); }
        .pf-sub { font-size: 12px; color: var(--muted); margin-top: 5px; display: flex; gap: 10px; flex-wrap: wrap; }
        .pf-chip { font-weight: 650; color: var(--text-dim); }
        .pf-close {
          background: var(--bg-surface); border: 1px solid var(--border);
          color: var(--text-dim); border-radius: var(--radius-sm); padding: 6px 12px; cursor: pointer;
        }
        .pf-close:hover { background: var(--bg-subtle); border-color: var(--border-strong); color: var(--text); }
        .pf-empty { padding: 30px 6px; color: var(--muted); font-size: 13px; }
        .pf-grid {
          display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 14px;
        }
        .pf-card {
          text-align: left; background: var(--bg-surface);
          border: 1px solid var(--border); border-radius: var(--radius);
          padding: 14px 16px; cursor: pointer; color: var(--text);
          transition: border-color var(--fast), box-shadow var(--fast);
        }
        .pf-card:hover { border-color: var(--brand-soft-border); box-shadow: var(--shadow); }
        .pf-card-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
        .pf-name { font-size: 14px; font-weight: 650; }
        .pf-status {
          font-size: 10px; font-weight: 700; border: 1px solid;
          border-radius: var(--radius-pill); padding: 2px 9px; white-space: nowrap;
        }
        .pf-meta { font-size: 11px; color: var(--muted); margin-top: 3px; }
        .pf-body { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
        /* Rang secondaire : la trajectoire prime sur le chiffre. */
        .pf-score-num { font-size: 22px; font-weight: 650; color: var(--text); }
        .pf-score-sub { font-size: 11px; color: var(--muted); margin-left: 4px; }
        .spark-empty { color: var(--muted); font-size: 12px; }
        .pf-years { font-size: 10.5px; color: var(--muted); margin-top: 10px; }
      `}</style>
    </div>
  )
}
