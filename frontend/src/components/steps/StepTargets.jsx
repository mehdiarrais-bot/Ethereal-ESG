import { FormField, NumberInput, SelectInput, SectionTitle } from '../FormField'

// Objectifs DÉCLARÉS par l'entreprise (étape B, DETTE § 0bis). Les livrables
// les citent comme tels, sans en évaluer l'alignement. Une cible incomplète
// (réduction, année de référence et année cible) n'est pas citée.
const SCOPES = [['', '— Non précisé —'], ['1-2', 'Scopes 1 et 2'], ['1-2-3', 'Scopes 1, 2 et 3']]

function range(from, to) {
  const out = []
  for (let y = from; y <= to; y++) out.push(y)
  return out
}

const toYear = (v) => (v === '' ? '' : parseInt(v))

export default function StepTargets({ form, updateSection }) {
  const { targets, company } = form
  const set = (field) => (val) => updateSection('targets', { [field]: val })
  const year = company.reporting_year
  // Référence : jusqu'à l'exercice du rapport ; cible : au-delà de la référence.
  const baseYears = range(2015, year)
  const firstTarget = Math.max(year, targets.climate_base_year || year) + 1
  const targetYears = range(firstTarget, 2060)

  return (
    <div className="card">
      <div className="card-title">🎯 Objectifs & engagements</div>

      <div className="form-section">
        <SectionTitle icon="🌡️">Trajectoire climat</SectionTitle>
        <div className="form-grid">
          <FormField label="Réduction visée des émissions (%)" hint="Par rapport à l'année de référence">
            <NumberInput value={targets.climate_reduction_percent} onChange={set('climate_reduction_percent')}
              placeholder="Ex: 42" min={0} max={100} />
          </FormField>
          <FormField label="Périmètre de la cible">
            <SelectInput value={targets.climate_scopes} onChange={set('climate_scopes')} options={SCOPES} />
          </FormField>
          <FormField label="Année de référence" hint="Si c'est l'exercice du rapport, la cible est aussi chiffrée en tonnes">
            <SelectInput value={targets.climate_base_year} onChange={(v) => {
              const base = toYear(v)
              // Une année cible qui ne suit plus la référence serait refusée par le serveur.
              const keep = base === '' || targets.climate_target_year === '' || targets.climate_target_year > base
              updateSection('targets', keep ? { climate_base_year: base }
                : { climate_base_year: base, climate_target_year: '' })
            }}
              options={[['', '—'], ...baseYears.map(y => [y, y.toString()])]} />
          </FormField>
          <FormField label="Année cible">
            <SelectInput value={targets.climate_target_year} onChange={(v) => set('climate_target_year')(toYear(v))}
              options={[['', '—'], ...targetYears.map(y => [y, y.toString()])]} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="📈">Cibles par indicateur — horizon {company.target_year}</SectionTitle>
        <div className="form-grid">
          <FormField label="Part d'énergie renouvelable visée (%)">
            <NumberInput value={targets.renewable_target_percent} onChange={set('renewable_target_percent')}
              placeholder="Ex: 60" min={0} max={100} />
          </FormField>
          <FormField label="Part de femmes dans l'effectif visée (%)">
            <NumberInput value={targets.female_employees_target_percent} onChange={set('female_employees_target_percent')}
              placeholder="Ex: 40" min={0} max={100} />
          </FormField>
          <FormField label="Heures de formation par salarié visées">
            <NumberInput value={targets.training_hours_target} onChange={set('training_hours_target')}
              placeholder="Ex: 30" min={0} />
          </FormField>
          <FormField label="Taux de fréquence des accidents visé" hint="Accidents avec arrêt par million d'heures travaillées">
            <NumberInput value={targets.accident_rate_target} onChange={set('accident_rate_target')}
              placeholder="Ex: 5" min={0} />
          </FormField>
        </div>
      </div>

      <div className="tip-box">
        <strong>💡 Conseil :</strong> Renseigner uniquement une cible que l'entreprise a effectivement
        fixée. Le rapport la cite comme déclarée par l'entreprise ; il n'en évalue pas l'alignement sur
        une trajectoire de référence. Une cible incomplète n'est pas reprise.
      </div>
    </div>
  )
}
