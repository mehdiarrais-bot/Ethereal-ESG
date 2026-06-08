export default function Header({ onLoadDemo, onReset, scores, showResults, onToggleResults }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-brand">
          <div className="header-logo">ESG</div>
          <div>
            <div className="header-title">Plateforme ESG / RSE</div>
            <div className="header-sub">Génération automatique de rapports & présentations</div>
          </div>
        </div>
        <div className="header-right">
          <div className="header-badges">
            <span className="badge badge-env">🌍 Environnement</span>
            <span className="badge badge-soc">👥 Social</span>
            <span className="badge badge-gov">⚖️ Gouvernance</span>
          </div>
          <div className="header-actions">
            {scores && (
              <button className="hdr-btn hdr-btn-score" onClick={onToggleResults}>
                📊 {scores.total_esg_score?.toFixed(1)} · {scores.rating} {showResults ? '◀' : '▶'}
              </button>
            )}
            <button className="hdr-btn hdr-btn-demo" onClick={onLoadDemo}>
              🎯 Données exemple
            </button>
            <button className="hdr-btn hdr-btn-reset" onClick={onReset}>
              ↺ Réinitialiser
            </button>
          </div>
        </div>
      </div>
      <style>{`
        .header {
          background: linear-gradient(135deg, #1B3A6B 0%, #2E86C1 100%);
          color: white;
          border-bottom: 3px solid #F39C12;
          position: sticky;
          top: 0;
          z-index: 100;
          box-shadow: 0 2px 20px rgba(27,58,107,0.25);
        }
        .header-inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 32px;
        }
        .header-brand { display: flex; align-items: center; gap: 14px; }
        .header-logo {
          width: 46px; height: 46px;
          background: #F39C12; border-radius: 10px;
          display: flex; align-items: center; justify-content: center;
          font-size: 16px; font-weight: 900; color: #1B3A6B; letter-spacing: -1px;
        }
        .header-title { font-size: 18px; font-weight: 800; line-height: 1.2; }
        .header-sub { font-size: 11px; opacity: 0.75; margin-top: 2px; }
        .header-right { display: flex; align-items: center; gap: 20px; }
        .header-badges { display: flex; gap: 8px; }
        .badge {
          padding: 4px 10px; border-radius: 20px;
          font-size: 11px; font-weight: 600;
        }
        .badge-env { background: rgba(39,174,96,0.25); border: 1px solid rgba(39,174,96,0.4); }
        .badge-soc { background: rgba(46,134,193,0.25); border: 1px solid rgba(46,134,193,0.4); }
        .badge-gov { background: rgba(142,68,173,0.25); border: 1px solid rgba(142,68,173,0.4); }
        .header-actions { display: flex; gap: 8px; }
        .hdr-btn {
          padding: 7px 14px; border-radius: 7px;
          border: none; font-size: 12px; font-weight: 600;
          cursor: pointer; transition: all 0.15s;
        }
        .hdr-btn-score { background: rgba(39,174,96,0.25); color: #fff; border: 1px solid rgba(39,174,96,0.5); font-size: 13px; font-weight: 700; }
        .hdr-btn-score:hover { background: rgba(39,174,96,0.4); }
        .hdr-btn-demo { background: #F39C12; color: #1B3A6B; }
        .hdr-btn-demo:hover { background: #e08e0b; }
        .hdr-btn-reset { background: rgba(255,255,255,0.15); color: white; border: 1px solid rgba(255,255,255,0.3); }
        .hdr-btn-reset:hover { background: rgba(255,255,255,0.25); }
        @media (max-width: 900px) {
          .header-badges { display: none; }
          .header-actions { display: none; }
        }
      `}</style>
    </header>
  )
}
