import { FormField, NumberInput, SelectInput, SectionTitle } from '../FormField'

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

export default function StepCompany({ form, updateSection }) {
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
