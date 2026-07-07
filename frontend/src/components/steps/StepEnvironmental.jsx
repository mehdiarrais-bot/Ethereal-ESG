import { FormField, NumberInput, SectionTitle } from '../FormField'

export default function StepEnvironmental({ form, updateSection }) {
  const { environmental: env } = form
  const tax = form.taxonomy || {}
  const set = (field) => (val) => updateSection('environmental', { [field]: val })
  const setTax = (field) => (val) => updateSection('taxonomy', { [field]: val })

  return (
    <div className="card">
      <div className="card-title">🌍 Données Environnementales</div>

      <div className="form-section">
        <SectionTitle icon="☁️">Émissions de Gaz à Effet de Serre</SectionTitle>
        <div className="form-grid">
          <FormField label="Émissions CO₂ totales (t CO₂e)" hint="Toutes sources confondues">
            <NumberInput value={env.co2_emissions_tonnes} onChange={set('co2_emissions_tonnes')} placeholder="Ex: 5200" min={0} />
          </FormField>
          <FormField label="Scope 1 — Émissions directes (t CO₂e)" hint="Combustion, procédés, émissions fugitives">
            <NumberInput value={env.scope1_emissions} onChange={set('scope1_emissions')} placeholder="Ex: 1800" min={0} />
          </FormField>
          <FormField label="Scope 2 — Énergie indirecte (t CO₂e)" hint="Électricité, vapeur, chaleur achetée">
            <NumberInput value={env.scope2_emissions} onChange={set('scope2_emissions')} placeholder="Ex: 1200" min={0} />
          </FormField>
          <FormField label="Scope 3 — Autres émissions indirectes (t CO₂e)" hint="Chaîne de valeur amont/aval">
            <NumberInput value={env.scope3_emissions} onChange={set('scope3_emissions')} placeholder="Ex: 2200" min={0} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="⚡">Énergie</SectionTitle>
        <div className="form-grid">
          <FormField label="Consommation totale d'énergie (MWh)">
            <NumberInput value={env.energy_consumption_mwh} onChange={set('energy_consumption_mwh')} placeholder="Ex: 12500" min={0} />
          </FormField>
          <FormField label="Part d'énergie renouvelable (%)" hint="0 à 100%">
            <NumberInput value={env.renewable_energy_percent} onChange={set('renewable_energy_percent')} placeholder="Ex: 35" min={0} max={100} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="💧">Eau & Déchets</SectionTitle>
        <div className="form-grid">
          <FormField label="Consommation d'eau (m³)">
            <NumberInput value={env.water_consumption_m3} onChange={set('water_consumption_m3')} placeholder="Ex: 48000" min={0} />
          </FormField>
          <FormField label="Déchets générés (t)">
            <NumberInput value={env.waste_generated_tonnes} onChange={set('waste_generated_tonnes')} placeholder="Ex: 320" min={0} />
          </FormField>
          <FormField label="Taux de recyclage des déchets (%)" hint="0 à 100%">
            <NumberInput value={env.waste_recycled_percent} onChange={set('waste_recycled_percent')} placeholder="Ex: 68" min={0} max={100} />
          </FormField>
          <FormField label="Initiatives biodiversité (nombre)">
            <NumberInput value={env.biodiversity_initiatives} onChange={set('biodiversity_initiatives')} placeholder="Ex: 3" min={0} step={1} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="🇪🇺">Taxonomie UE — Activités durables</SectionTitle>
        <div className="form-grid">
          <FormField label="CA aligné Taxonomie (%)" hint="Part du chiffre d'affaires issu d'activités durables">
            <NumberInput value={tax.turnover_aligned_percent} onChange={setTax('turnover_aligned_percent')} placeholder="Ex: 38" min={0} max={100} />
          </FormField>
          <FormField label="CapEx aligné Taxonomie (%)" hint="Investissements verts (prospectif)">
            <NumberInput value={tax.capex_aligned_percent} onChange={setTax('capex_aligned_percent')} placeholder="Ex: 52" min={0} max={100} />
          </FormField>
          <FormField label="OpEx aligné Taxonomie (%)" hint="Dépenses opérationnelles durables">
            <NumberInput value={tax.opex_aligned_percent} onChange={setTax('opex_aligned_percent')} placeholder="Ex: 29" min={0} max={100} />
          </FormField>
        </div>
      </div>
    </div>
  )
}
