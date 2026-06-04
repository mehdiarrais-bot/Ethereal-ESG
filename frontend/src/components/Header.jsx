export default function Header() {
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
        <div className="header-badges">
          <span className="badge badge-env">🌍 Environnement</span>
          <span className="badge badge-soc">👥 Social</span>
          <span className="badge badge-gov">⚖️ Gouvernance</span>
        </div>
      </div>
      <style>{`
        .header {
          background: linear-gradient(135deg, #1B3A6B 0%, #2E86C1 100%);
          color: white;
          padding: 0;
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
          padding: 14px 32px;
          max-width: 1600px;
          margin: 0 auto;
          width: 100%;
        }
        .header-brand { display: flex; align-items: center; gap: 16px; }
        .header-logo {
          width: 48px;
          height: 48px;
          background: #F39C12;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          font-weight: 900;
          color: #1B3A6B;
          letter-spacing: -1px;
        }
        .header-title { font-size: 20px; font-weight: 800; line-height: 1.2; }
        .header-sub { font-size: 12px; opacity: 0.75; margin-top: 2px; }
        .header-badges { display: flex; gap: 10px; }
        .badge {
          padding: 5px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          backdrop-filter: blur(4px);
        }
        .badge-env { background: rgba(39,174,96,0.25); border: 1px solid rgba(39,174,96,0.4); }
        .badge-soc { background: rgba(46,134,193,0.25); border: 1px solid rgba(46,134,193,0.4); }
        .badge-gov { background: rgba(142,68,173,0.25); border: 1px solid rgba(142,68,173,0.4); }
        @media (max-width: 768px) {
          .header-badges { display: none; }
        }
      `}</style>
    </header>
  )
}
