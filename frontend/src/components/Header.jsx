export default function Header({ onLoadDemo, onReset, scores, showResults, onToggleResults, clientsPanel }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-brand">
          <div className="header-logo">Eth</div>
          <div>
            <div className="header-title">Ethereal ESG</div>
            <div className="header-sub">Diagnostic & reporting extra-financier — 100 % local</div>
          </div>
        </div>
        <div className="header-right">
          <div className="header-badges">
            <span className="badge badge-env">🌍 Environnement</span>
            <span className="badge badge-soc">👥 Social</span>
            <span className="badge badge-gov">⚖️ Gouvernance</span>
          </div>
          <div className="header-actions">
            {clientsPanel}
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
          background: linear-gradient(135deg, rgba(20,10,45,0.85) 0%, rgba(10,6,30,0.9) 100%);
          color: var(--text);
          border-bottom: 1px solid var(--glass-border);
          position: sticky;
          top: 0;
          z-index: 100;
          box-shadow: 0 4px 30px rgba(5,2,25,0.6);
          backdrop-filter: blur(18px) saturate(150%);
          -webkit-backdrop-filter: blur(18px) saturate(150%);
        }
        /* Neon underline */
        .header::after {
          content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 1px;
          background: linear-gradient(90deg, transparent, var(--violet), var(--neon), transparent);
          opacity: 0.8;
        }
        .header-inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 32px;
        }
        .header-brand { display: flex; align-items: center; gap: 14px; }
        .header-logo {
          width: 48px; height: 48px;
          background: linear-gradient(135deg, var(--violet), var(--neon-blue));
          border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          font-size: 15px; font-weight: 900; color: #fff; letter-spacing: -0.5px;
          box-shadow: var(--glow-violet);
          animation: glowPulse 3.5s ease-in-out infinite;
        }
        .header-title {
          font-size: 18px; font-weight: 800; line-height: 1.2;
          background: linear-gradient(90deg, #fff, var(--violet-soft));
          -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
        }
        .header-sub { font-size: 11px; color: var(--muted); margin-top: 2px; }
        .header-right { display: flex; align-items: center; gap: 20px; }
        .header-badges { display: flex; gap: 8px; }
        .badge {
          padding: 4px 11px; border-radius: 20px;
          font-size: 11px; font-weight: 600; color: var(--text);
          backdrop-filter: blur(6px);
        }
        .badge-env { background: rgba(52,211,153,0.14); border: 1px solid rgba(52,211,153,0.4); }
        .badge-soc { background: rgba(56,189,248,0.14); border: 1px solid rgba(56,189,248,0.4); }
        .badge-gov { background: rgba(192,132,252,0.14); border: 1px solid rgba(192,132,252,0.4); }
        .header-actions { display: flex; gap: 8px; }
        .hdr-btn {
          padding: 8px 16px; border-radius: 999px;
          border: 1px solid var(--glass-border); font-size: 12px; font-weight: 600;
          cursor: pointer; transition: transform var(--fast) var(--ease), box-shadow var(--fast), background var(--fast);
          color: var(--text); background: var(--glass);
          white-space: nowrap;
        }
        .hdr-btn:hover { transform: translateY(-1px); }
        .hdr-btn-score { background: rgba(52,211,153,0.16); color: #fff; border: 1px solid rgba(52,211,153,0.5); font-size: 13px; font-weight: 700; }
        .hdr-btn-score:hover { box-shadow: 0 0 16px rgba(52,211,153,0.45); }
        .hdr-btn-demo { background: linear-gradient(135deg, var(--neon), var(--neon-blue)); color: #04121a; border: none; }
        .hdr-btn-demo:hover { box-shadow: var(--glow-neon); }
        .hdr-btn-reset:hover { background: rgba(124,92,246,0.2); border-color: var(--glass-border-lit); }
        @media (max-width: 900px) {
          .header-badges { display: none; }
          .header-inner { padding: 10px 16px; }
        }
        @media (max-width: 560px) {
          .header-sub { display: none; }
          .hdr-btn-demo, .hdr-btn-reset { display: none; }
        }
      `}</style>
    </header>
  )
}
