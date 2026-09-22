export default function Header({ onLoadDemo, onReset, scores, showResults, onToggleResults, clientsPanel }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-brand">
          <div className="header-logo">E</div>
          <div>
            <div className="header-title">Ethereal ESG</div>
            <div className="header-sub">Diagnostic &amp; reporting extra-financier — 100 % local</div>
          </div>
        </div>
        <div className="header-right">
          <div className="header-badges">
            <span className="badge badge-env">Environnement</span>
            <span className="badge badge-soc">Social</span>
            <span className="badge badge-gov">Gouvernance</span>
          </div>
          <div className="header-actions">
            {clientsPanel}
            {scores && (
              <button className="hdr-btn hdr-btn-score" onClick={onToggleResults}>
                {scores.total_esg_score?.toFixed(1)} · {scores.rating} {showResults ? '◀' : '▶'}
              </button>
            )}
            <button className="hdr-btn hdr-btn-demo" onClick={onLoadDemo}>
              Données exemple
            </button>
            <button className="hdr-btn hdr-btn-reset" onClick={onReset}>
              Réinitialiser
            </button>
          </div>
        </div>
      </div>
      <style>{`
        .header {
          background: var(--bg-surface);
          color: var(--text);
          border-bottom: 1px solid var(--border);
          position: sticky;
          top: 0;
          z-index: 100;
        }
        .header-inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 10px 24px;
          gap: 16px;
        }
        .header-brand { display: flex; align-items: center; gap: 11px; }
        .header-logo {
          width: 34px; height: 34px;
          background: var(--brand);
          border-radius: var(--radius-sm);
          display: flex; align-items: center; justify-content: center;
          font-size: 16px; font-weight: 700; color: #fff;
          flex-shrink: 0;
        }
        .header-title { font-size: 15px; font-weight: 650; line-height: 1.2; color: var(--text); }
        .header-sub { font-size: 11px; color: var(--muted); margin-top: 1px; }
        .header-right { display: flex; align-items: center; gap: 16px; }
        .header-badges { display: flex; gap: 6px; }
        .badge {
          padding: 4px 10px; border-radius: var(--radius-pill);
          font-size: 11px; font-weight: 600;
          display: inline-flex; align-items: center; gap: 6px;
        }
        .badge::before {
          content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor;
        }
        .badge-env { background: var(--env-soft); color: var(--env); }
        .badge-soc { background: var(--social-soft); color: var(--social); }
        .badge-gov { background: var(--gov-soft); color: var(--gov); }
        .header-actions { display: flex; gap: 7px; align-items: center; }
        .hdr-btn {
          padding: 7px 13px; border-radius: var(--radius-sm);
          border: 1px solid var(--border); font-size: 12.5px; font-weight: 600;
          cursor: pointer; transition: background var(--fast), border-color var(--fast), color var(--fast);
          color: var(--text-dim); background: var(--bg-surface);
          white-space: nowrap;
        }
        .hdr-btn:hover { background: var(--bg-subtle); border-color: var(--border-strong); color: var(--text); }
        .hdr-btn:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--brand-ring); }
        .hdr-btn-score {
          background: var(--brand-soft); color: var(--brand-hover);
          border-color: var(--brand-soft-border); font-weight: 700;
        }
        .hdr-btn-score:hover { background: var(--brand-soft-border); color: var(--brand-hover); }
        .hdr-btn-demo { background: var(--brand); color: #fff; border-color: transparent; }
        .hdr-btn-demo:hover { background: var(--brand-hover); color: #fff; }
        @media (max-width: 900px) {
          .header-badges { display: none; }
          .header-inner { padding: 10px 14px; }
        }
        @media (max-width: 560px) {
          .header-sub { display: none; }
          .hdr-btn-demo, .hdr-btn-reset { display: none; }
        }
      `}</style>
    </header>
  )
}
