import { FormField, NumberInput, BoolToggle, SectionTitle } from '../FormField'

export default function StepGovernance({ form, updateSection }) {
  const { governance: gov } = form
  const set = (field) => (val) => updateSection('governance', { [field]: val })

  return (
    <div className="card">
      <div className="card-title">⚖️ Données de Gouvernance</div>

      <div className="form-section">
        <SectionTitle icon="🏛️">Conseil d'Administration</SectionTitle>
        <div className="form-grid">
          <FormField label="Nombre de membres du CA">
            <NumberInput value={gov.board_members} onChange={set('board_members')} placeholder="Ex: 12" min={0} step={1} />
          </FormField>
          <FormField label="Part des femmes au CA (%)" hint="Seuil légal de 40 % (art. L225-18-1 du Code de commerce) pour les sociétés d'au moins 250 salariés permanents et 50 M€ de CA ou de bilan, trois exercices consécutifs">
            <NumberInput value={gov.female_board_percent} onChange={set('female_board_percent')} placeholder="Ex: 38" min={0} max={100} />
          </FormField>
          <FormField label="Part des administrateurs indépendants (%)" hint="Recommandation AFEP-MEDEF : >50%">
            <NumberInput value={gov.independent_board_percent} onChange={set('independent_board_percent')} placeholder="Ex: 55" min={0} max={100} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="🛡️">Éthique & Conformité</SectionTitle>
        <div className="form-grid">
          <FormField label="Violations du code d'éthique (nombre)">
            <NumberInput value={gov.ethics_violations} onChange={set('ethics_violations')} placeholder="Ex: 0" min={0} step={1} />
          </FormField>
          <FormField label="Cas de corruption identifiés">
            <NumberInput value={gov.corruption_cases} onChange={set('corruption_cases')} placeholder="Ex: 0" min={0} step={1} />
          </FormField>
          <FormField label="Violations de données / cyberattaques">
            <NumberInput value={gov.data_breaches} onChange={set('data_breaches')} placeholder="Ex: 0" min={0} step={1} />
          </FormField>
        </div>
      </div>

      <div className="form-section">
        <SectionTitle icon="♻️">Engagement RSE</SectionTitle>
        <div className="form-grid">
          <FormField label="Budget RSE annuel (€)">
            <NumberInput value={gov.csr_budget_eur} onChange={set('csr_budget_eur')} placeholder="Ex: 500000" min={0} />
          </FormField>
        </div>
        <div className="form-grid" style={{ marginTop: 16 }}>
          <FormField label="Audit ESG indépendant conduit" hint="Auditeur tiers certifié">
            <BoolToggle value={gov.esg_audit_conducted} onChange={set('esg_audit_conducted')} />
          </FormField>
          <FormField label="Comité de durabilité au niveau du CA" hint="Comité dédié aux enjeux ESG">
            <BoolToggle value={gov.sustainability_committee} onChange={set('sustainability_committee')} />
          </FormField>
          <FormField label="Société cotée" hint="Active la référence AFEP-MEDEF (code des sociétés cotées)">
            <BoolToggle value={gov.listed_company} onChange={set('listed_company')} />
          </FormField>
          <FormField label="Société contrôlée" hint="Un actionnaire de contrôle : seuil AFEP-MEDEF d'un tiers">
            <BoolToggle value={gov.controlled_company} onChange={set('controlled_company')} />
          </FormField>
        </div>
      </div>
    </div>
  )
}
