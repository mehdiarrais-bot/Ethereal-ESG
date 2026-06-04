import { FormField, NumberInput, SectionTitle } from '../FormField'

export default function StepSocial({ form, updateSection }) {
  const { social } = form
  const set = (field) => (val) => updateSection('social', { [field]: val })

  return (
    <div className="card">
      <div className="card-title">👥 Données Sociales</div>

      <div className="form-section">
        <SectionTitle icon="🧑‍🤝‍🧑">Ressources Humaines</SectionTitle>
        <div className="form-grid">
          <FormField label="Effectif total (ETP)">
            <NumberInput value={social.total_employees} onChange={set('total_employees')} placeholder="Ex: 1250" min={0} step={1} />
          </FormField>
          <FormField label="Part des femmes dans l'effectif (%)" hint="0 à 100%">
            <NumberInput value={social.female_employees_percent} onChange={set('female_employees_percent')} placeholder="Ex: 42" min={0} max={100} />
          </FormField>
          <FormField label="Taux de turnover (%)" hint="Départs volontaires / effectif">
            <NumberInput value={social.employee_turnover_percent} onChange={set('employee_turnover_percent')} placeholder="Ex: 12" min={0} max={100} />
          </FormField>
          <FormField label="Salariés en situation de handicap (%)" hint="DOETH — objectif légal : 6%">
            <NumberInput value={social.disabled_employees_percent} onChange={set('disabled_employees_percent')} placeholder="Ex: 4.2" min={0} max={100} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="📚">Formation & Développement</SectionTitle>
        <div className="form-grid">
          <FormField label="Heures de formation / employé / an" hint="Objectif recommandé : 20h minimum">
            <NumberInput value={social.training_hours_per_employee} onChange={set('training_hours_per_employee')} placeholder="Ex: 28" min={0} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="🦺">Santé & Sécurité</SectionTitle>
        <div className="form-grid">
          <FormField label="Nombre d'accidents de travail">
            <NumberInput value={social.work_accidents} onChange={set('work_accidents')} placeholder="Ex: 8" min={0} step={1} />
          </FormField>
          <FormField label="Taux de fréquence des accidents (TF)" hint="Accidents × 1 000 000 / heures travaillées">
            <NumberInput value={social.accident_frequency_rate} onChange={set('accident_frequency_rate')} placeholder="Ex: 4.2" min={0} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="🤝">Engagement Local & Clients</SectionTitle>
        <div className="form-grid">
          <FormField label="Investissement dans la communauté (€)" hint="Dons, mécénat, fondations">
            <NumberInput value={social.community_investment_eur} onChange={set('community_investment_eur')} placeholder="Ex: 250000" min={0} />
          </FormField>
          <FormField label="Part des fournisseurs locaux (%)" hint="Fournisseurs dans un rayon défini">
            <NumberInput value={social.local_suppliers_percent} onChange={set('local_suppliers_percent')} placeholder="Ex: 55" min={0} max={100} />
          </FormField>
          <FormField label="Score de satisfaction client (/10)" hint="NPS ou CSAT converti sur 10">
            <NumberInput value={social.customer_satisfaction_score} onChange={set('customer_satisfaction_score')} placeholder="Ex: 7.8" min={0} max={10} />
          </FormField>
        </div>
      </div>
    </div>
  )
}
