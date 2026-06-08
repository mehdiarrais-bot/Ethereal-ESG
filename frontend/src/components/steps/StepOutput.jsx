const THEMES = [
  {
    id: 'corporate_blue',
    name: 'Corporate Blue',
    desc: 'Professionnel, sobre — finance & industrie',
    colors: ['#1B3A6B', '#2E86C1', '#F39C12'],
  },
  {
    id: 'green_nature',
    name: 'Green Nature',
    desc: 'Verdoyant, impact-first — rapports RSE',
    colors: ['#1A5C38', '#27AE60', '#F1C40F'],
  },
  {
    id: 'dark_premium',
    name: 'Dark Premium',
    desc: 'Élégant, haut de gamme — investisseurs',
    colors: ['#0D1117', '#58A6FF', '#F7C948'],
  },
  {
    id: 'minimal_white',
    name: 'Minimal White',
    desc: 'Épuré, moderne — focus sur les données',
    colors: ['#212121', '#1E88E5', '#FF6F00'],
  },
]

const PRES_TYPES = [
  { id: 'executive_summary', name: 'Synthèse Exécutive', desc: 'Vue dirigeant condensée' },
  { id: 'investor_deck', name: 'Investor Deck', desc: 'Pour les investisseurs ESG' },
  { id: 'detailed_report', name: 'Rapport Détaillé', desc: 'Analyse complète tous piliers' },
  { id: 'stakeholder_brief', name: 'Parties Prenantes', desc: 'Communication externe' },
  { id: 'annual_report', name: 'Rapport Annuel', desc: 'Rapport annuel RSE officiel' },
]

const REPORT_TYPES = [
  { id: 'full_report', name: 'Rapport ESG Complet', desc: 'Analyse détaillée tous piliers' },
  { id: 'white_paper', name: 'Livre Blanc RSE', desc: 'Document de référence stratégique' },
  { id: 'executive_summary_pdf', name: 'Synthèse PDF', desc: 'Résumé exécutif condensé' },
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

export default function StepOutput({ form, setForm, onDownload, loading, scores }) {
  const set = (field) => (val) => setForm(f => ({ ...f, [field]: val }))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div className="card">
        <div className="card-title">📊 Configuration des Livrables</div>

        <div className="output-section">
          <div className="output-section-title">🎨 Thème Esthétique</div>
          <div className="options-grid options-grid-4">
            {THEMES.map(t => (
              <OptionCard key={t.id} item={t} selected={form.aesthetic_theme === t.id}
                onClick={() => set('aesthetic_theme')(t.id)} type="theme" />
            ))}
          </div>
        </div>

        <div className="output-section">
          <div className="output-section-title">📽️ Type de Présentation PowerPoint</div>
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
              <input type="checkbox" checked={form.language === 'fr'}
                onChange={e => set('language')(e.target.checked ? 'fr' : 'en')} />
              Rapport en français
            </label>
          </div>
        </div>

        <div className="generate-actions">
          {scores ? (
            <div className="score-preview-chip">
              ✅ Score calculé : <strong>{scores.total_esg_score?.toFixed(1)}/100</strong> — Note <strong>{scores.rating}</strong>
            </div>
          ) : (
            <div className="score-preview-chip score-preview-pending">
              ⏳ Saisissez des données pour calculer le score
            </div>
          )}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <button className="btn btn-pptx btn-lg" onClick={() => onDownload('pptx')} disabled={loading || !scores}>
              {loading ? '⏳' : '📑'} PowerPoint
            </button>
            <button className="btn btn-pdf btn-lg" onClick={() => onDownload('pdf')} disabled={loading || !scores}>
              {loading ? '⏳' : '📄'} Rapport PDF
            </button>
            <button className="btn btn-docx btn-lg" onClick={() => onDownload('docx')} disabled={loading || !scores}>
              {loading ? '⏳' : '📝'} Word .docx
            </button>
          </div>
        </div>
      </div>

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
          border: 2px solid var(--border); border-radius: 10px;
          background: white; text-align: left; cursor: pointer;
          transition: all 0.15s;
        }
        .option-card:hover { border-color: var(--blue-secondary); background: rgba(46,134,193,0.04); }
        .option-card.selected { border-color: var(--blue-primary); background: rgba(27,58,107,0.06); }
        .option-name { font-size: 13px; font-weight: 700; color: var(--text); }
        .option-desc { font-size: 11px; color: #8a9bb0; margin-top: 3px; }
        .option-check {
          position: absolute; top: 8px; right: 10px;
          width: 20px; height: 20px; background: var(--blue-primary); color: white;
          border-radius: 50%; display: flex; align-items: center; justify-content: center;
          font-size: 11px; font-weight: 700;
        }
        .generate-actions {
          display: flex; gap: 16px; align-items: center;
          padding-top: 20px; border-top: 1px solid var(--border);
          flex-wrap: wrap;
        }
        .score-preview-chip {
          background: rgba(39,174,96,0.1);
          border: 1px solid rgba(39,174,96,0.3);
          border-radius: 8px; padding: 8px 16px;
          font-size: 13px; color: #1A5C38;
        }
        .score-preview-pending {
          background: rgba(243,156,18,0.1);
          border-color: rgba(243,156,18,0.3);
          color: #7D5A00;
        }
        .checkbox-label {
          display: flex; align-items: center; gap: 8px;
          font-size: 13px; cursor: pointer; color: var(--text);
        }
        .checkbox-label input[type=checkbox] {
          width: 16px; height: 16px;
          cursor: pointer; accent-color: var(--blue-primary);
        }
        @media (max-width: 900px) {
          .options-grid-4 { grid-template-columns: repeat(2, 1fr); }
        }
      `}</style>
    </div>
  )
}
