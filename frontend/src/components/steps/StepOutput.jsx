import { useState } from 'react'
import PreviewPanel from '../PreviewPanel'

const THEMES = [
  { id: 'corporate_blue', name: 'Corporate Blue', desc: 'Professionnel, sobre — finance & industrie', colors: ['#1B3A6B', '#2E86C1', '#F39C12'] },
  { id: 'green_nature', name: 'Green Nature', desc: 'Verdoyant, impact-first — rapports RSE', colors: ['#1A5C38', '#27AE60', '#F1C40F'] },
  { id: 'dark_premium', name: 'Dark Premium', desc: 'Elegant, haut de gamme — investisseurs', colors: ['#0D1117', '#58A6FF', '#F7C948'] },
  { id: 'minimal_white', name: 'Minimal White', desc: 'Epure, moderne — focus sur les donnees', colors: ['#212121', '#1E88E5', '#FF6F00'] },
  { id: 'sunset_terracotta', name: 'Terracotta Sunset', desc: 'Chaleureux, organique — marques engagees', colors: ['#9A3412', '#E76F51', '#F4A261'] },
  { id: 'ocean_deep', name: 'Ocean Profond', desc: 'Teal & cyan — maritime, energie, eau', colors: ['#0F4C5C', '#277DA1', '#00BFA6'] },
  { id: 'royal_purple', name: 'Royal Violet', desc: 'Violet & or — prestige, luxe, culture', colors: ['#2B1055', '#5E35B1', '#FFD54F'] },
]

const PRES_TYPES = [
  { id: 'executive_summary', name: 'Synthese Executive', desc: 'Vue dirigeant condensee' },
  { id: 'investor_deck', name: 'Investor Deck', desc: 'Pour les investisseurs ESG' },
  { id: 'detailed_report', name: 'Rapport Detaille', desc: 'Analyse complete tous piliers' },
  { id: 'stakeholder_brief', name: 'Parties Prenantes', desc: 'Communication externe' },
  { id: 'annual_report', name: 'Rapport Annuel', desc: 'Rapport annuel RSE officiel' },
]

const REPORT_TYPES = [
  { id: 'full_report', name: 'Rapport ESG Complet', desc: 'Analyse detaillee tous piliers' },
  { id: 'white_paper', name: 'Livre Blanc RSE', desc: 'Document de reference strategique' },
  { id: 'executive_summary_pdf', name: 'Synthese PDF', desc: 'Resume executif condense' },
]

function Swatch({ colors }) {
  return (
    <div style={{ display: 'flex', gap: 4, marginTop: 8 }}>
      {colors.map(c => (
        <div key={c} style={{ width: 18, height: 18, borderRadius: 4, background: c, border: '1px solid rgba(0,0,0,0.1)' }} />
      ))}
    </div>
  )
}

function OptionCard({ item, selected, onClick, type }) {
  return (
    <button className={`option-card ${selected ? 'selected' : ''}`} onClick={onClick} type="button">
      <div className="option-name">{item.name}</div>
      <div className="option-desc">{item.desc}</div>
      {type === 'theme' && <Swatch colors={item.colors} />}
      {selected && <div className="option-check">✓</div>}
    </button>
  )
}

function ProgressBar({ progress, loading }) {
  if (!loading && progress === 0) return null
  const pct = Math.min(100, Math.round(progress))
  const done = pct === 100
  return (
    <div className="progress-wrap">
      <div className="progress-bar-bg">
        <div
          className={`progress-bar-fill ${done ? 'done' : ''}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="progress-label">
        {done ? '✓ Fichier pret — telechargement lance' : `Generation en cours... ${pct}%`}
      </span>
    </div>
  )
}

export default function StepOutput({ form, setForm, onDownload, loading, progress, downloadLink, onClearLink, scores }) {
  const set = (field) => (val) => setForm(f => ({ ...f, [field]: val }))
  const [showPreview, setShowPreview] = useState(false)
  const busy = loading

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div className="card">
        <div className="card-title">📊 Configuration des Livrables</div>

        <div className="output-section">
          <div className="output-section-title">🎨 Theme Esthetique</div>
          <div className="options-grid options-grid-4">
            {THEMES.map(t => (
              <OptionCard key={t.id} item={t} selected={form.aesthetic_theme === t.id}
                onClick={() => set('aesthetic_theme')(t.id)} type="theme" />
            ))}
          </div>
        </div>

        <div className="output-section">
          <div className="output-section-title">📽️ Type de Presentation PowerPoint</div>
          <div className="options-grid">
            {PRES_TYPES.map(p => (
              <OptionCard key={p.id} item={p} selected={form.presentation_type === p.id}
                onClick={() => set('presentation_type')(p.id)} />
            ))}
          </div>
        </div>

        <div className="output-section">
          <div className="output-section-title">📄 Type de Rapport (PDF & Word)</div>
          <div className="options-grid">
            {REPORT_TYPES.map(r => (
              <OptionCard key={r.id} item={r} selected={form.report_type === r.id}
                onClick={() => set('report_type')(r.id)} />
            ))}
          </div>
        </div>

        <div className="output-section">
          <div className="output-section-title">⚙️ Options</div>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
            <label className="checkbox-label">
              <input type="checkbox" checked={form.include_recommendations}
                onChange={e => set('include_recommendations')(e.target.checked)} />
              Inclure les recommandations
            </label>
            <label className="checkbox-label">
              <input type="checkbox" checked={form.include_benchmarks}
                onChange={e => set('include_benchmarks')(e.target.checked)} />
              Inclure les benchmarks sectoriels
            </label>
            <label className="checkbox-label">
              <input type="checkbox" checked={form.include_cover_image ?? true}
                onChange={e => set('include_cover_image')(e.target.checked)} />
              Illustration de couverture (générée localement)
            </label>
          </div>
        </div>

        <div className="generate-actions">
          {scores ? (
            <div className="score-preview-chip">
              ✅ Score : <strong>{scores.total_esg_score?.toFixed(1)}/100</strong> — Note <strong>{scores.rating}</strong>
            </div>
          ) : (
            <div className="score-preview-chip score-preview-pending">
              ⏳ Saisissez des donnees pour calculer le score
            </div>
          )}

          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
            <button className="btn btn-preview" onClick={() => setShowPreview(p => !p)} disabled={!scores}>
              {showPreview ? '✕ Fermer la preview' : '👁 Previsualiser'}
            </button>
            <button className="btn btn-pptx btn-lg" onClick={() => onDownload('pptx')} disabled={busy || !scores}>
              📑 PowerPoint
            </button>
            <button className="btn btn-pdf btn-lg" onClick={() => onDownload('pdf')} disabled={busy || !scores}>
              📄 Rapport PDF
            </button>
            <button className="btn btn-docx btn-lg" onClick={() => onDownload('docx')} disabled={busy || !scores}>
              📝 Word .docx
            </button>
          </div>

          <ProgressBar progress={progress} loading={loading} />

          {downloadLink && (
            <div className="manual-dl-banner">
              <span>✅ Fichier pret !</span>
              <a href={downloadLink.url} download={downloadLink.fname} className="manual-dl-link">
                ⬇ Cliquer ici pour telecharger : <strong>{downloadLink.fname}</strong>
              </a>
              <button onClick={onClearLink} className="manual-dl-close">✕</button>
            </div>
          )}
        </div>
      </div>

      {/* Preview HTML instantanée */}
      {showPreview && scores && (
        <div className="preview-card">
          <div className="preview-header">
            <span className="preview-title">👁 Previsualisation du livrable</span>
            <span className="preview-hint">Mise a jour en temps reel selon vos donnees</span>
          </div>
          <div style={{ padding: '20px', maxHeight: 700, overflowY: 'auto' }}>
            <PreviewPanel scores={scores} form={form} />
          </div>
          <div className="preview-footer">
            <button className="btn btn-pdf" onClick={() => onDownload('pdf')} disabled={busy}>
              📄 Telecharger PDF
            </button>
            <button className="btn btn-pptx" onClick={() => onDownload('pptx')} disabled={busy}>
              📑 Telecharger PowerPoint
            </button>
            <button className="btn btn-docx" onClick={() => onDownload('docx')} disabled={busy}>
              📝 Telecharger Word
            </button>
          </div>
        </div>
      )}

      <style>{`
        .output-section { margin-bottom: 24px; }
        .output-section-title {
          font-size: 12px; font-weight: 700; text-transform: uppercase;
          letter-spacing: 1px; color: var(--blue-secondary);
          margin-bottom: 12px; padding-bottom: 7px;
          border-bottom: 2px solid var(--border);
        }
        .options-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
          gap: 10px;
        }
        .options-grid-4 { grid-template-columns: repeat(4, 1fr); }
        .option-card {
          position: relative; padding: 13px 14px;
          border: 1px solid var(--glass-border); border-radius: 12px;
          background: rgba(8, 5, 22, 0.5); text-align: left; cursor: pointer;
          transition: border-color var(--fast), background var(--fast), transform var(--fast) var(--ease), box-shadow var(--fast);
          color: var(--text);
        }
        .option-card:hover { border-color: var(--glass-border-lit); background: rgba(124,92,246,0.12); transform: translateY(-2px); }
        .option-card.selected {
          border-color: var(--neon); background: rgba(34,211,238,0.1);
          box-shadow: var(--glow-neon);
        }
        .option-name { font-size: 13px; font-weight: 700; color: var(--text); }
        .option-desc { font-size: 11px; color: var(--muted); margin-top: 3px; }
        .option-check {
          position: absolute; top: 8px; right: 10px;
          width: 20px; height: 20px;
          background: linear-gradient(135deg, var(--neon), var(--neon-blue)); color: #04121a;
          border-radius: 50%; display: flex; align-items: center; justify-content: center;
          font-size: 11px; font-weight: 800;
        }
        .generate-actions {
          display: flex; gap: 16px; align-items: flex-start;
          padding-top: 20px; border-top: 1px solid var(--border);
          flex-wrap: wrap; flex-direction: column;
        }
        .generate-actions > div { width: 100%; }
        .score-preview-chip {
          background: rgba(52,211,153,0.12);
          border: 1px solid rgba(52,211,153,0.35);
          border-radius: 10px; padding: 8px 16px;
          font-size: 13px; color: #6ee7b7;
        }
        .score-preview-pending {
          background: rgba(34,211,238,0.1);
          border-color: rgba(34,211,238,0.35);
          color: var(--neon);
        }
        .checkbox-label {
          display: flex; align-items: center; gap: 8px;
          font-size: 13px; cursor: pointer; color: var(--text-dim);
        }
        .checkbox-label input[type=checkbox] {
          width: 16px; height: 16px;
          cursor: pointer; accent-color: var(--neon);
        }
        .btn-preview {
          background: var(--glass); color: var(--neon);
          border: 1px solid var(--glass-border-lit);
          padding: 10px 20px; border-radius: 10px;
          font-weight: 600; cursor: pointer; font-size: 14px;
          transition: background var(--fast), color var(--fast), box-shadow var(--fast), transform var(--fast) var(--ease);
        }
        .btn-preview:hover:not(:disabled) {
          background: rgba(34,211,238,0.15); box-shadow: var(--glow-neon); transform: translateY(-1px);
        }
        .btn-preview:disabled { opacity: 0.4; cursor: not-allowed; }

        /* Lien manuel */
        .manual-dl-banner {
          display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
          background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.4); border-radius: 12px;
          padding: 12px 16px; margin-top: 8px;
        }
        .manual-dl-banner span { color: #6ee7b7; font-weight: 700; font-size: 13px; }
        .manual-dl-link {
          color: var(--neon); font-size: 13px; font-weight: 600;
          text-decoration: underline; flex: 1;
        }
        .manual-dl-close {
          background: none; border: none; color: var(--muted);
          font-size: 16px; cursor: pointer; padding: 0 4px;
        }

        /* Barre de progression */
        .progress-wrap {
          width: 100%; display: flex; flex-direction: column; gap: 6px;
          padding: 12px 0 4px;
        }
        .progress-bar-bg {
          width: 100%; height: 8px; background: rgba(140,120,255,0.18); border-radius: 99px; overflow: hidden;
        }
        .progress-bar-fill {
          height: 100%; background: linear-gradient(90deg, var(--violet), var(--neon));
          border-radius: 99px; transition: width 0.3s var(--ease); box-shadow: var(--glow-neon);
        }
        .progress-bar-fill.done { background: linear-gradient(90deg, #059669, var(--env)); }
        .progress-label {
          font-size: 12px; color: var(--neon); font-weight: 600;
        }

        /* Zone preview */
        .preview-card {
          background: var(--glass-strong); border-radius: 16px;
          border: 1px solid var(--glass-border-lit);
          overflow: hidden; box-shadow: var(--shadow), var(--glow-neon);
          backdrop-filter: blur(16px);
          animation: fadeUp var(--med) var(--ease) both;
        }
        .preview-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 20px; background: rgba(34,211,238,0.08);
          border-bottom: 1px solid var(--glass-border);
        }
        .preview-title { font-weight: 700; color: var(--neon); font-size: 14px; }
        .preview-hint { font-size: 12px; color: var(--muted); }
        .preview-footer {
          display: flex; gap: 10px; padding: 14px 20px;
          border-top: 1px solid var(--glass-border); background: rgba(8,5,22,0.4);
          flex-wrap: wrap;
        }

        @media (max-width: 900px) {
          .options-grid-4 { grid-template-columns: repeat(2, 1fr); }
        }
      `}</style>
    </div>
  )
}
