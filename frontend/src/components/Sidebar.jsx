export default function Sidebar({ steps, current, onChange }) {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <div className="sidebar-label">Étapes de saisie</div>
        {steps.map((step, i) => (
          <button
            key={step.id}
            className={`sidebar-item ${i === current ? 'active' : ''} ${i < current ? 'done' : ''}`}
            onClick={() => onChange(i)}
          >
            <span className="sidebar-icon">{i < current ? '✓' : step.icon}</span>
            <span className="sidebar-text">{step.label}</span>
            {i === current && <span className="sidebar-indicator" />}
          </button>
        ))}
      </nav>
      <style>{`
        .sidebar {
          width: 220px;
          background: white;
          border-right: 1px solid var(--border);
          flex-shrink: 0;
          padding: 24px 0;
        }
        .sidebar-label {
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          color: #8a9bb0;
          padding: 0 20px 16px;
        }
        .sidebar-nav { display: flex; flex-direction: column; gap: 2px; padding: 0 8px; }
        .sidebar-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 14px;
          border: none;
          background: transparent;
          border-radius: 10px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          color: #5a6a7e;
          transition: all 0.15s;
          text-align: left;
          position: relative;
        }
        .sidebar-item:hover { background: var(--bg); color: var(--blue-primary); }
        .sidebar-item.active {
          background: rgba(27,58,107,0.08);
          color: var(--blue-primary);
          font-weight: 700;
        }
        .sidebar-item.done { color: var(--env); }
        .sidebar-item.done .sidebar-icon {
          background: var(--env);
          color: white;
        }
        .sidebar-icon {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 8px;
          background: var(--bg);
          font-size: 16px;
          flex-shrink: 0;
        }
        .sidebar-item.active .sidebar-icon {
          background: var(--blue-primary);
          font-size: 14px;
        }
        .sidebar-indicator {
          position: absolute;
          right: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 24px;
          background: var(--blue-primary);
          border-radius: 2px 0 0 2px;
        }
        @media (max-width: 900px) {
          .sidebar { width: 64px; }
          .sidebar-text, .sidebar-label, .sidebar-indicator { display: none; }
          .sidebar-item { justify-content: center; }
        }
      `}</style>
    </aside>
  )
}
