import { useState } from 'react'
import { FormField, NumberInput, SelectInput, SectionTitle } from '../FormField'

function ImportPanel({ onImport }) {
  const [status, setStatus] = useState(null)
  const [busy, setBusy] = useState(false)

  const handleFile = async (e) => {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file || !onImport) return
    setBusy(true); setStatus(null)
    const r = await onImport(file)
    setBusy(false)
    if (r) {
      setStatus({
        ok: true,
        msg: `✅ ${r.matched} champ(s) importé(s)`
          + (r.unmatched?.length ? ` — ${r.unmatched.length} ignoré(s) : ${r.unmatched.slice(0, 3).join(', ')}${r.unmatched.length > 3 ? '…' : ''}` : ''),
      })
    }
  }

  return (
    <div className="import-panel">
      <div className="import-head">
        <span className="import-title">📥 Importer depuis un fichier</span>
        <span className="import-sub">CSV ou Excel — remplit le formulaire automatiquement</span>
      </div>
      <div className="import-actions">
        <a className="import-tpl" href="/api/import/template" download>⬇ Télécharger le modèle</a>
        <label className={`import-btn ${busy ? 'busy' : ''}`}>
          <input type="file" accept=".csv,.xlsx,.xlsm,text/csv" onChange={handleFile} disabled={busy} />
          {busy ? '⏳ Import…' : '📂 Choisir un fichier CSV / Excel'}
        </label>
      </div>
      {status && <div className={`import-status ${status.ok ? 'ok' : 'err'}`}>{status.msg}</div>}
      <style>{`
        .import-panel {
          border: 1px solid var(--glass-border-lit); border-radius: var(--radius);
          background: rgba(34,211,238,0.06); padding: 18px 20px; margin-bottom: 22px;
          backdrop-filter: blur(8px);
        }
        .import-head { display: flex; flex-direction: column; gap: 2px; margin-bottom: 14px; }
        .import-title { font-weight: 700; color: var(--neon); font-size: 15px; }
        .import-sub { font-size: 12px; color: var(--muted); }
        .import-actions { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
        .import-tpl {
          font-size: 13px; color: var(--text-dim); text-decoration: none;
          padding: 10px 18px; border: 1px solid var(--glass-border); border-radius: var(--radius-pill);
          transition: background var(--fast), border-color var(--fast);
        }
        .import-tpl:hover { background: rgba(124,92,246,0.14); border-color: var(--glass-border-lit); }
        .import-btn {
          display: inline-flex; align-items: center; gap: 8px; cursor: pointer;
          font-size: 13px; font-weight: 600; color: #04121a;
          background: linear-gradient(135deg, var(--neon), var(--neon-blue));
          padding: 10px 20px; border-radius: var(--radius-pill);
          box-shadow: 0 0 16px rgba(34,211,238,0.35); transition: transform var(--fast) var(--ease);
        }
        .import-btn:hover { transform: translateY(-1px); }
        .import-btn.busy { opacity: 0.7; cursor: wait; }
        .import-btn input { display: none; }
        .import-status { margin-top: 12px; font-size: 13px; padding: 8px 14px; border-radius: 10px; }
        .import-status.ok { background: rgba(52,211,153,0.12); color: #6ee7b7; border: 1px solid rgba(52,211,153,0.3); }
        .import-status.err { background: rgba(244,63,94,0.12); color: #fda4af; border: 1px solid rgba(244,63,94,0.3); }
      `}</style>
    </div>
  )
}

const SECTORS = [
  'Agroalimentaire', 'Automobile', 'BTP & Construction', 'Chimie', 'Commerce de détail',
  'Distribution', 'Énergie', 'Finance & Assurance', 'Immobilier', 'Industrie',
  'Logistique & Transport', 'Numérique & Tech', 'Pharmaceutique', 'Services aux entreprises',
  'Télécommunications', 'Tourisme & Hôtellerie', 'Autre',
]

const COUNTRIES = [
  'France', 'Belgique', 'Suisse', 'Luxembourg', 'Canada', 'Maroc', 'Tunisie',
  'Allemagne', 'Espagne', 'Italie', 'Royaume-Uni', 'Autre',
]

const YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
const TARGET_YEARS = [2027, 2028, 2030, 2035, 2040, 2050]

export default function StepCompany({ form, updateSection, onImport }) {
  const { company } = form
  const set = (field) => (val) => updateSection('company', { [field]: val })

  const handleLogoUpload = (e) => {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    if (!['image/png', 'image/jpeg'].includes(file.type)) {
      alert('Format non supporté : utilisez un PNG ou un JPEG.')
      return
    }
    if (file.size > 1_400_000) {
      alert('Logo trop volumineux (max 1,4 Mo). Réduisez la taille de l\'image.')
      return
    }
    const reader = new FileReader()
    reader.onload = () => set('logo_base64')(reader.result)
    reader.readAsDataURL(file)
  }

  return (
    <div className="card">
      <div className="card-title">🏢 Informations sur l'Entreprise</div>

      <ImportPanel onImport={onImport} />

      <div className="form-section">
        <SectionTitle icon="📋">Identité</SectionTitle>
        <div className="form-grid">
          <FormField label="Nom de l'entreprise *">
            <input
              type="text"
              value={company.name}
              onChange={e => set('name')(e.target.value)}
              placeholder="Ex: Acme Industries SA"
              maxLength={200}
            />
          </FormField>

          <FormField label="Secteur d'activité *">
            <SelectInput
              value={company.sector}
              onChange={set('sector')}
              options={SECTORS.map(s => [s, s])}
            />
          </FormField>

          <FormField label="Pays">
            <SelectInput
              value={company.country}
              onChange={set('country')}
              options={COUNTRIES.map(c => [c, c])}
            />
          </FormField>

          <FormField label="Année de reporting">
            <SelectInput
              value={company.reporting_year}
              onChange={(v) => updateSection('company', { reporting_year: parseInt(v) })}
              options={YEARS.map(y => [y, y.toString()])}
            />
          </FormField>

          <FormField label="Horizon des objectifs" hint="Année cible pour la trajectoire ESG (CSRD/SBTi)">
            <SelectInput
              value={company.target_year || 2030}
              onChange={(v) => updateSection('company', { target_year: parseInt(v) })}
              options={TARGET_YEARS.map(y => [y, y.toString()])}
            />
          </FormField>

          <FormField label="Chiffre d'affaires (€)" hint="Utilisé pour calculer les intensités carbone et énergie">
            <NumberInput
              value={company.revenue_eur}
              onChange={set('revenue_eur')}
              placeholder="Ex: 50000000"
              min={0}
            />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="🎤">Présentation & Identité visuelle</SectionTitle>
        <div className="form-grid">
          <FormField label="Nom du présentateur" hint="Apparaît sur la couverture des livrables">
            <input
              type="text"
              value={company.presenter_name || ''}
              onChange={e => set('presenter_name')(e.target.value)}
              placeholder="Ex: Marie Dupont"
              maxLength={100}
            />
          </FormField>

          <FormField label="Fonction du présentateur">
            <input
              type="text"
              value={company.presenter_title || ''}
              onChange={e => set('presenter_title')(e.target.value)}
              placeholder="Ex: Directrice RSE"
              maxLength={100}
            />
          </FormField>

          <FormField
            label="Initiatives internes"
            hint="Projets/actions réels, séparés par des virgules — cités dans les textes du rapport"
          >
            <input
              type="text"
              value={company.key_initiatives || ''}
              onChange={e => set('key_initiatives')(e.target.value)}
              placeholder="Ex: programme Cap Climat 2027, panneaux solaires site de Lyon"
              maxLength={600}
            />
          </FormField>

          <FormField label="Logo de l'entreprise" hint="PNG ou JPEG, max 1,4 Mo — intégré aux couvertures">
            {company.logo_base64 ? (
              <div className="logo-preview">
                <img src={company.logo_base64} alt="Logo" />
                <button type="button" className="logo-remove" onClick={() => set('logo_base64')(null)}>
                  ✕ Retirer
                </button>
              </div>
            ) : (
              <label className="logo-upload">
                <input type="file" accept="image/png,image/jpeg" onChange={handleLogoUpload} />
                📁 Choisir un fichier…
              </label>
            )}
          </FormField>
        </div>
      </div>

      <div className="tip-box">
        <strong>💡 Conseil :</strong> Les champs marqués * sont obligatoires. Les autres données ESG
        sont facultatives mais améliorent la précision du score et la qualité des livrables générés.
      </div>
      <style>{`
        .tip-box {
          background: rgba(46,134,193,0.08);
          border-left: 4px solid var(--blue-secondary);
          border-radius: 0 8px 8px 0;
          padding: 14px 18px;
          font-size: 13px;
          color: var(--blue-primary);
          margin-top: 12px;
        }
        .logo-upload {
          display: inline-flex; align-items: center; gap: 8px;
          padding: 9px 16px; border: 2px dashed var(--border);
          border-radius: 8px; cursor: pointer; font-size: 13px;
          color: var(--blue-secondary); background: rgba(46,134,193,0.04);
          transition: all 0.15s;
        }
        .logo-upload:hover { border-color: var(--blue-secondary); }
        .logo-upload input[type=file] { display: none; }
        .logo-preview {
          display: flex; align-items: center; gap: 12px;
        }
        .logo-preview img {
          height: 44px; max-width: 140px; object-fit: contain;
          border: 1px solid var(--border); border-radius: 6px;
          background: white; padding: 4px;
        }
        .logo-remove {
          background: none; border: 1px solid #E74C3C; color: #E74C3C;
          border-radius: 6px; padding: 5px 10px; font-size: 12px;
          cursor: pointer;
        }
        .logo-remove:hover { background: rgba(231,76,60,0.08); }
      `}</style>
    </div>
  )
}
