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
      `}</style>
    </div>
  )
}
