import { useState, useEffect, useCallback, useRef } from 'react'

/**
 * Panneau « Dossiers clients » — le cœur du workflow freelance :
 * sauvegarder un dossier, le recharger, suivre l'historique de scores
 * par exercice, supprimer. 100 % local (stockage backend sur disque).
 */
export default function ClientsPanel({ currentId, onSave, onLoad, onDelete, saving, dirty }) {
  const [open, setOpen] = useState(false)
  const [clients, setClients] = useState([])
  const [loading, setLoading] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const boxRef = useRef(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/clients')
      if (res.ok) setClients(await res.json())
    } catch {}
    setLoading(false)
  }, [])

  useEffect(() => { if (open) refresh() }, [open, refresh])

  useEffect(() => {
    const onClick = (e) => {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  const fmtDate = (iso) => {
    try {
      return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
    } catch { return '' }
  }

  return (
    <div className="clients-wrap" ref={boxRef}>
      <button className="hdr-btn clients-save" onClick={onSave} disabled={saving}
              title="Enregistrer le dossier client (données + historique de scores)">
        {saving ? '⏳' : '💾'} Enregistrer{dirty ? ' •' : ''}
      </button>
      <button className={`hdr-btn clients-toggle ${open ? 'on' : ''}`} onClick={() => setOpen(o => !o)}>
        📁 Dossiers
      </button>

      {open && (
        <div className="clients-pop">
          <div className="clients-pop-head">
            <strong>Dossiers clients</strong>
            <span className="clients-count">{clients.length}</span>
          </div>
          {loading && <div className="clients-empty">Chargement…</div>}
          {!loading && clients.length === 0 && (
            <div className="clients-empty">
              Aucun dossier. Remplissez le formulaire puis cliquez « 💾 Enregistrer ».
            </div>
          )}
          <div className="clients-list">
            {clients.map(c => (
              <div key={c.id} className={`client-row ${c.id === currentId ? 'active' : ''}`}>
                <button className="client-main" onClick={() => { onLoad(c.id); setOpen(false) }}>
                  <div className="client-name">{c.name}</div>
                  <div className="client-meta">
                    {c.sector} · {fmtDate(c.updated_at)}
                    {c.years?.length > 0 && <> · exercices : {c.years.join(', ')}</>}
                  </div>
                </button>
                {c.last_score != null && (
                  <div className="client-score" title={`Score ${c.last_score}/100`}>
                    {Math.round(c.last_score)}<small>·{c.last_rating}</small>
                  </div>
                )}
                {confirmDelete === c.id ? (
                  <button className="client-del confirm"
                          onClick={async () => { await onDelete(c.id); setConfirmDelete(null); refresh() }}>
                    Confirmer ?
                  </button>
                ) : (
                  <button className="client-del" title="Supprimer le dossier"
                          onClick={() => setConfirmDelete(c.id)}>✕</button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <style>{`
        .clients-wrap { position: relative; display: flex; gap: 8px; }
        .clients-save { background: linear-gradient(135deg, var(--violet), var(--neon-blue)); color: #fff; border: none; }
        .clients-save:disabled { opacity: 0.6; cursor: wait; }
        .clients-toggle.on { background: rgba(124,92,246,0.25); border-color: var(--violet); }
        .clients-pop {
          position: absolute; top: 44px; right: 0; width: 380px; max-height: 420px;
          overflow: auto; z-index: 300;
          background: rgba(18,10,40,0.97); border: 1px solid var(--glass-border-lit);
          border-radius: 14px; box-shadow: 0 18px 50px rgba(0,0,0,0.55);
          backdrop-filter: blur(18px);
        }
        .clients-pop-head {
          display: flex; align-items: center; justify-content: space-between;
          padding: 12px 16px; border-bottom: 1px solid var(--glass-border);
          font-size: 13px; color: var(--text);
        }
        .clients-count {
          background: rgba(124,92,246,0.3); border-radius: 10px; padding: 1px 9px;
          font-size: 11px; font-weight: 700;
        }
        .clients-empty { padding: 18px 16px; font-size: 12px; color: var(--muted); }
        .clients-list { padding: 6px; }
        .client-row {
          display: flex; align-items: center; gap: 8px;
          border-radius: 10px; padding: 4px 6px;
        }
        .client-row:hover { background: rgba(124,92,246,0.12); }
        .client-row.active { background: rgba(56,189,248,0.12); outline: 1px solid rgba(56,189,248,0.35); }
        .client-main {
          flex: 1; text-align: left; background: none; border: none; cursor: pointer;
          padding: 6px 4px; color: var(--text);
        }
        .client-name { font-size: 13px; font-weight: 700; }
        .client-meta { font-size: 10.5px; color: var(--muted); margin-top: 2px; }
        .client-score {
          font-size: 14px; font-weight: 800; color: #34d399; white-space: nowrap;
        }
        .client-score small { font-size: 10px; color: var(--muted); font-weight: 600; }
        .client-del {
          background: none; border: 1px solid transparent; color: var(--muted);
          border-radius: 8px; cursor: pointer; padding: 4px 8px; font-size: 12px;
        }
        .client-del:hover { color: #f87171; border-color: rgba(248,113,113,0.4); }
        .client-del.confirm { color: #fff; background: #dc2626; font-size: 10.5px; font-weight: 700; }
        @media (max-width: 560px) { .clients-pop { width: 300px; } }
      `}</style>
    </div>
  )
}
