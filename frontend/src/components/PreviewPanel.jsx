const THEME_STYLES = {
  corporate_blue: { primary: '#1B3A6B', secondary: '#2E86C1', accent: '#F39C12', bg: '#f0f4fa', env: '#27AE60', social: '#2E86C1', gov: '#8E44AD' },
  green_nature:   { primary: '#1A5C38', secondary: '#27AE60', accent: '#F1C40F', bg: '#f0faf4', env: '#27AE60', social: '#2980B9', gov: '#8E44AD' },
  dark_premium:   { primary: '#0D1117', secondary: '#58A6FF', accent: '#F7C948', bg: '#161b22', env: '#3FB950', social: '#58A6FF', gov: '#BC8CFF' },
  minimal_white:  { primary: '#212121', secondary: '#1E88E5', accent: '#FF6F00', bg: '#f9f9f9', env: '#43A047', social: '#1E88E5', gov: '#7B1FA2' },
  sunset_terracotta: { primary: '#9A3412', secondary: '#E76F51', accent: '#F4A261', bg: '#FDF6F0', env: '#2A9D8F', social: '#E76F51', gov: '#6D597A' },
  ocean_deep:     { primary: '#0F4C5C', secondary: '#277DA1', accent: '#00BFA6', bg: '#F0FAFB', env: '#43AA8B', social: '#277DA1', gov: '#577590' },
  royal_purple:   { primary: '#2B1055', secondary: '#7E9BF5', accent: '#FFD54F', bg: '#241047', env: '#2E9E62', social: '#7E9BF5', gov: '#C08CF5' },
}

const DARK_THEMES = ['dark_premium', 'royal_purple']

const RATING_COLOR = { AAA: '#00875a', AA: '#27AE60', A: '#2ECC71', BBB: '#F39C12', BB: '#E67E22', B: '#E74C3C', CCC: '#922B21' }

const PRES_LABELS = {
  executive_summary: 'Synthèse Exécutive',
  investor_deck: 'Investor Deck',
  detailed_report: 'Rapport Détaillé',
  stakeholder_brief: 'Parties Prenantes',
  annual_report: 'Rapport Annuel RSE',
}

const REPORT_LABELS = {
  full_report: 'Rapport ESG Complet',
  white_paper: 'Livre Blanc RSE',
  executive_summary_pdf: 'Synthèse Exécutive PDF',
}

function ScoreBar({ label, value, color }) {
  const pct = Math.min(100, Math.max(0, value || 0))
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: 12, fontWeight: 600 }}>{label}</span>
        <span style={{ fontSize: 12, fontWeight: 700, color }}>{pct.toFixed(1)}/100</span>
      </div>
      <div style={{ background: '#e0e7ef', borderRadius: 99, height: 8, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, background: color, height: '100%', borderRadius: 99, transition: 'width 0.5s' }} />
      </div>
    </div>
  )
}

function KpiGrid({ items }) {
  const filled = items.filter(i => i.value !== null && i.value !== '' && i.value !== undefined)
  if (!filled.length) return <p style={{ fontSize: 12, color: '#8a9bb0', fontStyle: 'italic' }}>Aucune donnée saisie</p>
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 8 }}>
      {filled.map(({ label, value, unit }) => (
        <div key={label} style={{ background: 'rgba(0,0,0,0.04)', borderRadius: 8, padding: '8px 12px' }}>
          <div style={{ fontSize: 10, color: '#8a9bb0', textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</div>
          <div style={{ fontSize: 15, fontWeight: 700, marginTop: 2 }}>
            {typeof value === 'boolean' ? (value ? 'Oui' : 'Non') : `${Number(value).toLocaleString('fr')}${unit ? ' ' + unit : ''}`}
          </div>
        </div>
      ))}
    </div>
  )
}

export default function PreviewPanel({ scores, form }) {
  if (!scores || !form) return null
  const t = THEME_STYLES[form.aesthetic_theme] || THEME_STYLES.corporate_blue
  const isDark = DARK_THEMES.includes(form.aesthetic_theme)
  const textColor = isDark ? '#e6edf3' : '#1a2332'
  const cardBg = isDark ? '#1c2128' : '#ffffff'
  const borderColor = isDark ? '#30363d' : '#e2e8f0'

  const envData = form.environmental || {}
  const socData = form.social || {}
  const govData = form.governance || {}

  const envKpis = [
    { label: 'CO₂ (tonnes)', value: envData.co2_emissions_tonnes },
    { label: 'Énergie (MWh)', value: envData.energy_consumption_mwh },
    { label: '% Renouvelable', value: envData.renewable_energy_percent, unit: '%' },
    { label: 'Eau (m³)', value: envData.water_consumption_m3 },
    { label: 'Déchets (t)', value: envData.waste_generated_tonnes },
    { label: 'Scope 1', value: envData.scope1_emissions },
    { label: 'Scope 2', value: envData.scope2_emissions },
    { label: 'Scope 3', value: envData.scope3_emissions },
  ]
  const socKpis = [
    { label: 'Employés', value: socData.total_employees },
    { label: '% Femmes', value: socData.female_employees_percent, unit: '%' },
    { label: 'Turnover', value: socData.employee_turnover_percent, unit: '%' },
    { label: 'Formation (h)', value: socData.training_hours_per_employee, unit: 'h' },
    { label: 'Accidents', value: socData.work_accidents },
    { label: 'Satisfaction', value: socData.customer_satisfaction_score, unit: '/10' },
  ]
  const govKpis = [
    { label: 'Membres CA', value: govData.board_members },
    { label: '% Femmes CA', value: govData.female_board_percent, unit: '%' },
    { label: '% Indépendants', value: govData.independent_board_percent, unit: '%' },
    { label: 'Audit ESG', value: govData.esg_audit_conducted },
    { label: 'Comité RSE', value: govData.sustainability_committee },
    { label: 'Budget RSE (€)', value: govData.csr_budget_eur },
  ]

  const section = (title, color, children) => (
    <div style={{ marginBottom: 20 }}>
      <div style={{
        fontSize: 11, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1,
        color, borderBottom: `2px solid ${color}`, paddingBottom: 6, marginBottom: 12
      }}>{title}</div>
      {children}
    </div>
  )

  return (
    <div style={{
      background: t.bg, borderRadius: 16, overflow: 'hidden',
      border: `2px solid ${t.secondary}`, fontFamily: 'system-ui, sans-serif',
      color: textColor,
    }}>
      {/* En-tête */}
      <div style={{ background: t.primary, color: 'white', padding: '24px 28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
            {form.company?.logo_base64 && (
              <img src={form.company.logo_base64} alt="Logo"
                style={{ height: 48, maxWidth: 120, objectFit: 'contain', background: 'white', borderRadius: 8, padding: 4 }} />
            )}
            <div>
            <div style={{ fontSize: 22, fontWeight: 900, letterSpacing: -0.5 }}>
              {form.company?.name || 'Entreprise'}
            </div>
            <div style={{ fontSize: 13, opacity: 0.75, marginTop: 4 }}>
              {form.company?.sector} · {form.company?.country} · {form.company?.reporting_year}
            </div>
            <div style={{ fontSize: 11, opacity: 0.6, marginTop: 6, textTransform: 'uppercase', letterSpacing: 1 }}>
              {PRES_LABELS[form.presentation_type]} · {REPORT_LABELS[form.report_type]}
            </div>
            {form.company?.presenter_name && (
              <div style={{ fontSize: 12, opacity: 0.8, marginTop: 6, fontStyle: 'italic' }}>
                Présenté par {form.company.presenter_name}
                {form.company.presenter_title ? ` — ${form.company.presenter_title}` : ''}
              </div>
            )}
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              background: RATING_COLOR[scores.rating] || '#888',
              color: 'white', borderRadius: 12, padding: '8px 20px',
              fontWeight: 900, fontSize: 28, letterSpacing: 2
            }}>{scores.rating}</div>
            <div style={{ fontSize: 11, opacity: 0.7, marginTop: 4 }}>Score ESG global</div>
            <div style={{ fontSize: 20, fontWeight: 800, marginTop: 2 }}>{scores.total_esg_score?.toFixed(1)}/100</div>
          </div>
        </div>
      </div>

      {/* Corps */}
      <div style={{ padding: '24px 28px', background: cardBg }}>

        {/* Scores E/S/G */}
        {section('Scores par pilier', t.secondary,
          <div>
            <ScoreBar label="🌍 Environnement (40%)" value={scores.environmental_score} color={t.env} />
            <ScoreBar label="👥 Social (35%)" value={scores.social_score} color={t.social} />
            <ScoreBar label="⚖️ Gouvernance (25%)" value={scores.governance_score} color={t.gov} />
          </div>
        )}

        {/* KPIs Environnement */}
        {section('Données Environnementales', t.env, <KpiGrid items={envKpis} />)}

        {/* KPIs Social */}
        {section('Données Sociales', t.social, <KpiGrid items={socKpis} />)}

        {/* KPIs Gouvernance */}
        {section('Données de Gouvernance', t.gov, <KpiGrid items={govKpis} />)}

        {/* Forces / Faiblesses */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', color: '#27AE60', marginBottom: 8 }}>✅ Points forts</div>
            {scores.strengths?.length ? scores.strengths.map((s, i) => (
              <div key={i} style={{ fontSize: 12, padding: '6px 10px', background: 'rgba(39,174,96,0.08)', borderRadius: 6, marginBottom: 4, borderLeft: '3px solid #27AE60' }}>{s}</div>
            )) : <div style={{ fontSize: 12, color: '#8a9bb0', fontStyle: 'italic' }}>Aucun point fort identifié</div>}
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', color: '#E67E22', marginBottom: 8 }}>⚠️ Axes d'amélioration</div>
            {scores.weaknesses?.length ? scores.weaknesses.map((w, i) => (
              <div key={i} style={{ fontSize: 12, padding: '6px 10px', background: 'rgba(230,126,34,0.08)', borderRadius: 6, marginBottom: 4, borderLeft: '3px solid #E67E22' }}>{w}</div>
            )) : <div style={{ fontSize: 12, color: '#8a9bb0', fontStyle: 'italic' }}>Aucun axe identifié</div>}
          </div>
        </div>

        {/* Recommandations */}
        {scores.recommendations?.length > 0 && section('Recommandations prioritaires', t.accent,
          <div>
            {scores.recommendations.slice(0, 5).map((r, i) => (
              <div key={i} style={{ fontSize: 12, padding: '6px 10px', background: `rgba(0,0,0,0.04)`, borderRadius: 6, marginBottom: 4, display: 'flex', gap: 8 }}>
                <span style={{ color: t.accent, fontWeight: 700 }}>{i + 1}.</span> {r}
              </div>
            ))}
          </div>
        )}

        <div style={{ fontSize: 10, color: '#8a9bb0', textAlign: 'center', marginTop: 16, borderTop: `1px solid ${borderColor}`, paddingTop: 12 }}>
          Prévisualisation — le document final contiendra graphiques, mise en page et contenus rédigés
        </div>
      </div>
    </div>
  )
}
