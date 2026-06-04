import { useState } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import StepCompany from './components/steps/StepCompany'
import StepEnvironmental from './components/steps/StepEnvironmental'
import StepSocial from './components/steps/StepSocial'
import StepGovernance from './components/steps/StepGovernance'
import StepOutput from './components/steps/StepOutput'
import ResultsPanel from './components/ResultsPanel'
import './App.css'

const STEPS = [
  { id: 'company', label: 'Entreprise', icon: '🏢' },
  { id: 'environmental', label: 'Environnement', icon: '🌍' },
  { id: 'social', label: 'Social', icon: '👥' },
  { id: 'governance', label: 'Gouvernance', icon: '⚖️' },
  { id: 'output', label: 'Livrables', icon: '📊' },
]

const DEFAULT_FORM = {
  company: {
    name: '',
    sector: 'Industrie',
    country: 'France',
    revenue_eur: '',
    reporting_year: 2024,
  },
  environmental: {
    co2_emissions_tonnes: '',
    energy_consumption_mwh: '',
    renewable_energy_percent: '',
    water_consumption_m3: '',
    waste_generated_tonnes: '',
    waste_recycled_percent: '',
    biodiversity_initiatives: '',
    scope1_emissions: '',
    scope2_emissions: '',
    scope3_emissions: '',
  },
  social: {
    total_employees: '',
    female_employees_percent: '',
    employee_turnover_percent: '',
    training_hours_per_employee: '',
    work_accidents: '',
    accident_frequency_rate: '',
    community_investment_eur: '',
    local_suppliers_percent: '',
    customer_satisfaction_score: '',
    disabled_employees_percent: '',
  },
  governance: {
    board_members: '',
    female_board_percent: '',
    independent_board_percent: '',
    ethics_violations: '',
    corruption_cases: '',
    data_breaches: '',
    csr_budget_eur: '',
    esg_audit_conducted: null,
    sustainability_committee: null,
  },
  presentation_type: 'executive_summary',
  aesthetic_theme: 'corporate_blue',
  report_type: 'full_report',
  language: 'fr',
  include_recommendations: true,
  include_benchmarks: true,
}

function cleanNumeric(obj) {
  if (typeof obj !== 'object' || obj === null) return obj
  const result = {}
  for (const [k, v] of Object.entries(obj)) {
    if (v === '' || v === undefined) result[k] = null
    else if (typeof v === 'object' && !Array.isArray(v)) result[k] = cleanNumeric(v)
    else result[k] = v
  }
  return result
}

export default function App() {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(DEFAULT_FORM)
  const [scores, setScores] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const updateSection = (section, data) => {
    setForm(f => ({ ...f, [section]: { ...f[section], ...data } }))
  }

  const buildPayload = () => {
    const clean = cleanNumeric(form)
    return {
      company: clean.company,
      environmental: clean.environmental,
      social: clean.social,
      governance: clean.governance,
      presentation_type: form.presentation_type,
      aesthetic_theme: form.aesthetic_theme,
      report_type: form.report_type,
      language: form.language,
      include_recommendations: form.include_recommendations,
      include_benchmarks: form.include_benchmarks,
    }
  }

  const handleCalculate = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPayload()),
      })
      if (!res.ok) throw new Error('Erreur calcul')
      const data = await res.json()
      setScores(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (type) => {
    setLoading(true)
    setError(null)
    try {
      const endpoint = type === 'pptx' ? '/api/generate/pptx' : '/api/generate/pdf'
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPayload()),
      })
      if (!res.ok) throw new Error('Erreur génération')
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const cd = res.headers.get('content-disposition') || ''
      const fname = cd.match(/filename="(.+)"/)?.[1] || `rapport.${type}`
      a.download = fname
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const stepProps = { form, updateSection, setForm }

  const stepComponents = [
    <StepCompany {...stepProps} />,
    <StepEnvironmental {...stepProps} />,
    <StepSocial {...stepProps} />,
    <StepGovernance {...stepProps} />,
    <StepOutput
      {...stepProps}
      onCalculate={handleCalculate}
      onDownload={handleDownload}
      loading={loading}
      scores={scores}
    />,
  ]

  return (
    <div className="app-layout">
      <Header />
      <div className="app-body">
        <Sidebar steps={STEPS} current={step} onChange={setStep} />
        <main className="main-content">
          {error && (
            <div className="error-banner">
              ⚠️ {error}
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}
          <div className="step-wrapper">
            {stepComponents[step]}
          </div>
          <div className="step-nav">
            <button
              className="btn btn-ghost"
              onClick={() => setStep(s => Math.max(0, s - 1))}
              disabled={step === 0}
            >
              ← Précédent
            </button>
            <div className="step-dots">
              {STEPS.map((_, i) => (
                <button
                  key={i}
                  className={`dot ${i === step ? 'active' : i < step ? 'done' : ''}`}
                  onClick={() => setStep(i)}
                />
              ))}
            </div>
            {step < STEPS.length - 1 ? (
              <button
                className="btn btn-primary"
                onClick={() => setStep(s => Math.min(STEPS.length - 1, s + 1))}
              >
                Suivant →
              </button>
            ) : (
              <button
                className="btn btn-success"
                onClick={handleCalculate}
                disabled={loading}
              >
                {loading ? '⏳ Calcul...' : '🚀 Calculer & Générer'}
              </button>
            )}
          </div>
        </main>
        {scores && (
          <ResultsPanel
            scores={scores}
            onDownloadPptx={() => handleDownload('pptx')}
            onDownloadPdf={() => handleDownload('pdf')}
            loading={loading}
          />
        )}
      </div>
    </div>
  )
}
