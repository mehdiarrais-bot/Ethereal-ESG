import { useState } from 'react'
import PreviewPanel from '../PreviewPanel'
import { DesignPicker, PhotoSlots } from '../DesignPicker'

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

// Palette déterministe depuis le nom du client (même logique que le backend :
// primaire sombre + accent vif, teintes dérivées d'un hash du nom).
function autoBrand(name) {
  let h = 0
  for (const ch of (name || 'esg')) h = (h * 31 + ch.charCodeAt(0)) >>> 0
  const hue = h % 360
  const accentHue = (hue + 35 + ((h >> 8) % 50)) % 360
  const hsl = (hh, s, l) => {
    const a = s * Math.min(l, 1 - l)
    const f = n => {
      const k = (n + hh / 30) % 12
      const c = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
      return Math.round(255 * c).toString(16).padStart(2, '0')
    }
    return `#${f(0)}${f(8)}${f(4)}`
  }
  return { primary: hsl(hue, 0.42, 0.20), accent: hsl(accentHue, 0.72, 0.55) }
}

function OptionCard({ item, selected, onClick }) {
  return (
    <button className={`option-card ${selected ? 'selected' : ''}`} onClick={onClick} type="button">
      <div className="option-name">{item.name}</div>
      <div className="option-desc">{item.desc}</div>
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

export default function StepOutput({ form, setForm, onDownload, loading, progress, downloadLink, onClearLink, scores, clientId, clientActions, onToggleAction }) {
  const set = (field) => (val) => setForm(f => ({ ...f, [field]: val }))
  const [showPreview, setShowPreview] = useState(false)
  const busy = loading

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div className="card">
        <div className="card-title">📊 Configuration des Livrables</div>

        <div className="output-section">
          <div className="output-section-title">🎨 Gabarit du rapport</div>
          <DesignPicker value={form.aesthetic_theme} onChange={set('aesthetic_theme')} />
        </div>

        <div className="output-section">
          <div className="output-section-title">🖼️ Photos de l'entreprise (facultatif)</div>
          <PhotoSlots photos={form.report_photos} onChange={set('report_photos')} />
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
          <div className="output-section-title">🎯 Couleurs du client</div>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
            <label className="checkbox-label">
              <input type="checkbox" checked={!!form.custom_colors}
                onChange={e => set('custom_colors')(e.target.checked
                  ? autoBrand(form.company?.name || 'client')
                  : null)} />
              Décliner le thème aux couleurs du client
            </label>
            {form.custom_colors && (
              <>
                <label className="color-pick">
                  Primaire
                  <input type="color" value={form.custom_colors.primary}
                    onChange={e => set('custom_colors')({ ...form.custom_colors, primary: e.target.value })} />
                </label>
                <label className="color-pick">
                  Accent
                  <input type="color" value={form.custom_colors.accent}
                    onChange={e => set('custom_colors')({ ...form.custom_colors, accent: e.target.value })} />
                </label>
                <button type="button" className="btn btn-preview"
                  title="Palette déterministe générée depuis le nom du client"
                  onClick={() => set('custom_colors')(autoBrand(form.company?.name || 'client'))}>
                  🎲 Depuis le nom
                </button>
              </>
            )}
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 6 }}>
            Chaque client obtient une identité visuelle distincte (couvertures, titres, graphiques).
            Les couleurs des piliers E/S/G restent standard pour la lisibilité.
          </div>
        </div>

        <div className="output-section">
          <div className="output-section-title">💬 Vos analyses (encarts « L\u2019analyse du consultant »)</div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 10 }}>
            Facultatif — vos commentaires d\u2019expert, affichés dans des encarts dédiés des livrables.
            C\u2019est ce qui distingue votre diagnostic d\u2019un rapport automatique.
          </div>
          <div className="notes-grid">
            {[['global', 'Synthèse globale'], ['env', 'Environnement'], ['social', 'Social'], ['gov', 'Gouvernance']].map(([k, label]) => (
              <label key={k} className="note-field">
                {label}
                <textarea
                  rows={2}
                  maxLength={1000}
                  value={form.consultant_notes?.[k] || ''}
                  onChange={e => set('consultant_notes')({ ...(form.consultant_notes || {}), [k]: e.target.value })}
                  placeholder={k === 'global'
                    ? 'Ex: La priorité 2026 est la fiabilisation du reporting énergie avant l\u2019audit\u2026'
                    : 'Votre lecture de ce pilier\u2026'}
                />
              </label>
            ))}
          </div>
        </div>

        {clientId && scores?.recommendations?.length > 0 && (
          <div className="output-section">
            <div className="output-section-title">✅ Suivi du plan d\u2019action</div>
            <div style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 8 }}>
              Cochez les actions réalisées : elles apparaîtront comme « acquis » dans les
              prochains livrables (encart vert + mention en synthèse). Sauvegarde immédiate.
            </div>
            <div className="actions-track">
              {[...new Set([...(scores.recommendations || []), ...(clientActions || []).map(a => a.title)])].map(title => {
                const done = (clientActions || []).some(a => a.title === title)
                return (
                  <label key={title} className={`action-check ${done ? 'done' : ''}`}>
                    <input type="checkbox" checked={done} onChange={() => onToggleAction(title)} />
                    {title}
                  </label>
                )
              })}
            </div>
          </div>
        )}

        <div className="output-section">
          <div className="output-section-title">📐 Référentiel visé</div>
          <div className="lang-toggle">
            <button type="button" className={`lang-btn ${(form.reporting_framework || 'csrd') === 'csrd' ? 'active' : ''}`}
              onClick={() => set('reporting_framework')('csrd')}
              title="Exigences complètes CSRD / ESRS — entreprises soumises ou en préparation">
              CSRD / ESRS
            </button>
            <button type="button" className={`lang-btn ${form.reporting_framework === 'vsme' ? 'active' : ''}`}
              onClick={() => set('reporting_framework')('vsme')}
              title="Norme volontaire PME (EFRAG) — Scope 3, assurance tierce et Taxonomie sortent du périmètre évalué">
              VSME (PME)
            </button>
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 6 }}>
            En VSME, trois exigences (Scope 3, assurance tierce, Taxonomie) sont marquées
            « hors périmètre » plutôt que non conformes. Leur rattachement exact aux modules
            de la norme reste à valider contre le texte EFRAG.
          </div>
        </div>

        <div className="output-section">
          <div className="output-section-title">🌍 Langue des livrables</div>
          <div className="lang-toggle">
            <button type="button" className={`lang-btn ${(form.language || 'fr') === 'fr' ? 'active' : ''}`}
              onClick={() => set('language')('fr')}>🇫🇷 Français</button>
            <button type="button" className={`lang-btn ${form.language === 'en' ? 'active' : ''}`}
              onClick={() => set('language')('en')}>🇬🇧 English</button>
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
            <button className="btn btn-pdf" onClick={() => onDownload('onepager')} disabled={busy || !scores}
                    title="Synthèse une page (PDF) : score, benchmark, risques/opportunités, top-3 actions">
              📃 Synthèse 1 page
            </button>
            <button className="btn btn-docx" onClick={() => onDownload('proposal')} disabled={busy || !scores}
                    title="Lettre de mission commerciale basée sur le pré-diagnostic (écarts, maturité, phases)">
              🖋 Lettre de mission
            </button>
            <button className="btn btn-preview" onClick={() => onDownload('questionnaire')} disabled={busy}
                    title="Fichier HTML autonome à envoyer au client : il le remplit hors ligne et vous renvoie un CSV réimportable">
              📋 Questionnaire client
            </button>
            <button className="btn btn-pptx" onClick={() => onDownload('pack')} disabled={busy || !scores}
                    title="Tous les livrables de la mission en un zip : PPTX, PDF, Word, synthèse 1 page, lettre de mission">
              📦 Pack complet
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
        .output-section { margin-bottom: 28px; }
        .output-section-title {
          display: inline-flex; align-items: center;
          font-size: 12px; font-weight: 700; text-transform: uppercase;
          letter-spacing: 1px; color: var(--brand);
          margin-bottom: 16px; padding: 7px 16px;
          background: var(--brand-soft);
          border: 1px solid var(--brand-soft-border);
          border-radius: var(--radius-pill);
        }
        .options-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
          gap: 14px;
        }
        .design-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
        .design-card {
          position: relative; padding: 0; overflow: hidden; text-align: left; cursor: pointer;
          border: 1px solid var(--border); border-radius: var(--radius);
          background: var(--bg-surface); color: var(--text);
          transition: border-color var(--fast), background var(--fast);
        }
        .design-card img { display: block; width: 100%; aspect-ratio: 610 / 424; object-fit: cover; background: var(--bg-inset); }
        .design-card:hover { border-color: var(--brand); }
        .design-card.selected { border-color: var(--brand); box-shadow: 0 0 0 2px var(--brand-ring); background: var(--brand-soft); }
        .design-meta { padding: 10px 14px 12px; border-top: 1px solid var(--border); }
        .design-error { font-size: 12px; color: var(--danger); margin-top: 8px; }
        .photo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
        .photo-slot { display: flex; flex-direction: column; gap: 6px; position: relative; }
        .photo-slot img, .photo-add {
          width: 100%; aspect-ratio: 4 / 3; border-radius: var(--radius-sm);
          object-fit: cover; border: 1px solid var(--border);
        }
        .photo-add {
          display: flex; align-items: center; justify-content: center; cursor: pointer;
          border: 2px dashed var(--border); color: var(--brand-hover); font-size: 13px;
          background: var(--bg-subtle); transition: border-color var(--fast);
        }
        .photo-add:hover { border-color: var(--brand-hover); }
        .photo-add input[type=file] { display: none; }
        .photo-remove {
          position: absolute; top: 6px; right: 6px; font-size: 11px; cursor: pointer;
          background: var(--bg-surface); color: var(--danger);
          border: 1px solid var(--danger); border-radius: var(--radius-sm); padding: 3px 7px;
        }
        .photo-label { font-size: 12px; color: var(--text-dim); font-weight: 600; }
        .photo-hint { font-size: 12px; color: var(--muted); margin-top: 10px; line-height: 1.5; }
        .lang-toggle { display: inline-flex; gap: 0; border: 1px solid var(--border); border-radius: var(--radius-pill); overflow: hidden; }
        .lang-btn {
          padding: 10px 22px; border: none; background: var(--bg-surface);
          color: var(--text-dim); font-size: 14px; font-weight: 600; cursor: pointer;
          transition: background var(--fast), color var(--fast);
        }
        .lang-btn:first-child { border-right: 1px solid var(--border); }
        .lang-btn:hover { background: var(--bg-subtle); color: var(--text); }
        .lang-btn.active { background: linear-gradient(135deg, var(--brand), var(--brand-hover)); color: #fff; }
        .option-card {
          position: relative; padding: 16px 18px 15px;
          border: 1px solid var(--border); border-radius: var(--radius);
          background: var(--bg-surface); text-align: left; cursor: pointer;
          transition: border-color var(--fast), background var(--fast), transform var(--fast) var(--ease), box-shadow var(--fast);
          color: var(--text); min-height: 74px;
        }
        .option-card:hover { border-color: var(--brand); background: var(--bg-subtle);  }
        .option-card.selected {
          border-color: var(--brand); background: var(--brand-soft);
          box-shadow: none;
        }
        .option-name { font-size: 13.5px; font-weight: 700; color: var(--text); line-height: 1.3; padding-right: 24px; }
        .option-desc { font-size: 11.5px; color: var(--muted); margin-top: 5px; line-height: 1.45; }
        .option-check {
          position: absolute; top: 12px; right: 12px;
          width: 22px; height: 22px;
          background: var(--brand); color: #fff;
          border-radius: 50%; display: flex; align-items: center; justify-content: center;
          font-size: 12px; font-weight: 800;
          box-shadow: none;
        }
        .generate-actions {
          display: flex; gap: 16px; align-items: flex-start;
          padding-top: 22px; border-top: 1px solid var(--border);
          flex-wrap: wrap; flex-direction: column;
        }
        .generate-actions > div { width: 100%; }
        .score-preview-chip {
          display: inline-flex; align-items: center;
          background: var(--ok-soft);
          border: 1px solid var(--ok-border);
          border-radius: var(--radius-pill); padding: 9px 20px;
          font-size: 13px; color: var(--ok);
        }
        .score-preview-pending {
          background: var(--brand-soft);
          border-color: var(--brand-soft-border);
          color: var(--brand);
        }
        .actions-track { display: flex; flex-direction: column; gap: 6px; }
        .action-check {
          display: flex; align-items: center; gap: 9px;
          font-size: 12.5px; color: var(--text); cursor: pointer;
          padding: 7px 10px; border-radius: 8px;
          background: var(--bg-subtle); border: 1px solid var(--border);
        }
        .action-check.done { opacity: 0.75; }
        .action-check.done { text-decoration: line-through; border-color: var(--ok-border); }
        .notes-grid {
          display: grid; grid-template-columns: 1fr 1fr; gap: 10px 14px;
        }
        .note-field {
          display: flex; flex-direction: column; gap: 4px;
          font-size: 11.5px; font-weight: 700; color: var(--text);
        }
        .note-field textarea {
          background: var(--bg-subtle); border: 1px solid var(--border);
          border-radius: 8px; color: var(--text); font-size: 12px;
          padding: 8px 10px; resize: vertical; min-height: 46px;
          font-family: inherit; font-weight: 400;
        }
        .note-field textarea:focus { outline: none; border-color: var(--brand); }
        @media (max-width: 700px) { .notes-grid { grid-template-columns: 1fr; } }
        .color-pick {
          display: inline-flex; align-items: center; gap: 8px;
          font-size: 12px; color: var(--text); font-weight: 600;
        }
        .color-pick input[type=color] {
          width: 42px; height: 28px; border: 1px solid var(--border);
          border-radius: 6px; background: none; cursor: pointer; padding: 1px;
        }
        .checkbox-label {
          display: flex; align-items: center; gap: 8px;
          font-size: 13px; cursor: pointer; color: var(--text-dim);
        }
        .checkbox-label input[type=checkbox] {
          width: 16px; height: 16px;
          cursor: pointer; accent-color: var(--brand);
        }
        .btn-preview {
          background: var(--bg-subtle); color: var(--brand);
          border: 1px solid var(--brand);
          padding: 10px 20px; border-radius: 10px;
          font-weight: 600; cursor: pointer; font-size: 14px;
          transition: background var(--fast), color var(--fast), box-shadow var(--fast), transform var(--fast) var(--ease);
        }
        .btn-preview:hover:not(:disabled) {
          background: var(--brand-soft); box-shadow: none;
        }
        .btn-preview:disabled { opacity: 0.4; cursor: not-allowed; }

        /* Lien manuel */
        .manual-dl-banner {
          display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
          background: var(--ok-soft); border: 1px solid var(--ok-border); border-radius: 12px;
          padding: 12px 16px; margin-top: 8px;
        }
        .manual-dl-banner span { color: var(--ok); font-weight: 700; font-size: 13px; }
        .manual-dl-link {
          color: var(--brand); font-size: 13px; font-weight: 600;
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
          width: 100%; height: 8px; background: var(--bg-inset); border-radius: 99px; overflow: hidden;
        }
        .progress-bar-fill {
          height: 100%; background: linear-gradient(90deg, var(--brand), var(--brand));
          border-radius: 99px; transition: width 0.3s var(--ease); box-shadow: none;
        }
        .progress-bar-fill.done { background: var(--ok); }
        .progress-label {
          font-size: 12px; color: var(--brand); font-weight: 600;
        }

        /* Zone preview */
        .preview-card {
          background: var(--bg-surface); border-radius: 16px;
          border: 1px solid var(--brand);
          overflow: hidden; box-shadow: var(--shadow), none;
          backdrop-filter: blur(16px);
          animation: fadeUp var(--med) var(--ease) both;
        }
        .preview-header {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 20px; background: var(--brand-soft);
          border-bottom: 1px solid var(--border);
        }
        .preview-title { font-weight: 700; color: var(--brand); font-size: 14px; }
        .preview-hint { font-size: 12px; color: var(--muted); }
        .preview-footer {
          display: flex; gap: 10px; padding: 14px 20px;
          border-top: 1px solid var(--border); background: var(--bg-surface);
          flex-wrap: wrap;
        }

        @media (max-width: 900px) {
          .design-grid { grid-template-columns: repeat(2, 1fr); }
          .photo-grid { grid-template-columns: repeat(3, 1fr); }
        }
      `}</style>
    </div>
  )
}
