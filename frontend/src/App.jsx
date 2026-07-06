import { useState, useCallback, useEffect } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import StepCompany from './components/steps/StepCompany'
import StepEnvironmental from './components/steps/StepEnvironmental'
import StepSocial from './components/steps/StepSocial'
import StepGovernance from './components/steps/StepGovernance'
import StepOutput from './components/steps/StepOutput'
import ResultsPanel from './components/ResultsPanel'
import MiniScorebar from './components/MiniScorebar'
import { useESGScore } from './hooks/useESGScore'
import { DEMO_DATA } from './demoData'
import './App.css'

const STEPS = [
  { id: 'company', label: 'Entreprise', icon: '🏢' },
  { id: 'environmental', label: 'Environnement', icon: '🌍' },
  { id: 'social', label: 'Social', icon: '👥' },
  { id: 'governance', label: 'Gouvernance', icon: '⚖️' },
  { id: 'output', label: 'Livrables', icon: '📊' },
]

const EMPTY_FORM = {
  company: { name: '', sector: 'Industrie', country: 'France', revenue_eur: '', reporting_year: 2024,
    presenter_name: '', presenter_title: '', logo_base64: null },
  environmental: {
    co2_emissions_tonnes: '', energy_consumption_mwh: '', renewable_energy_percent: '',
    water_consumption_m3: '', waste_generated_tonnes: '', waste_recycled_percent: '',
    biodiversity_initiatives: '', scope1_emissions: '', scope2_emissions: '', scope3_emissions: '',
  },
  social: {
    total_employees: '', female_employees_percent: '', employee_turnover_percent: '',
    training_hours_per_employee: '', work_accidents: '', accident_frequency_rate: '',
    community_investment_eur: '', local_suppliers_percent: '', customer_satisfaction_score: '',
    disabled_employees_percent: '',
  },
  governance: {
    board_members: '', female_board_percent: '', independent_board_percent: '',
    ethics_violations: '', corruption_cases: '', data_breaches: '', csr_budget_eur: '',
    esg_audit_conducted: null, sustainability_committee: null,
  },
  presentation_type: 'executive_summary',
  aesthetic_theme: 'corporate_blue',
  report_type: 'full_report',
  language: 'fr',
  include_recommendations: true,
  include_benchmarks: true,
  include_cover_image: true,
}

export default function App() {
  const [step, setStep] = useState(0)
  const [form, setForm] = useState(EMPTY_FORM)
  const [downloadLoading, setDownloadLoading] = useState(false)
  const [downloadProgress, setDownloadProgress] = useState(0)
  const [downloadLink, setDownloadLink] = useState(null)
  const [error, setError] = useState(null)
  const [showResults, setShowResults] = useState(true)

  const { scores, loading: scoreLoading, buildPayload } = useESGScore(form)

  useEffect(() => {
    fetch('/api/warmup').catch(() => {})
  }, [])

  const updateSection = useCallback((section, data) => {
    setForm(f => ({ ...f, [section]: { ...f[section], ...data } }))
  }, [])

  const loadDemo = () => {
    setForm(DEMO_DATA)
    setError(null)
  }

  const resetForm = () => {
    setForm(EMPTY_FORM)
    setError(null)
  }

  const startProgress = () => {
    setDownloadProgress(5)
    const start = Date.now()
    const tick = () => {
      const elapsed = Date.now() - start
      // Progression rapide au début, ralentit vers 90%
      const target = Math.min(90, 5 + 85 * (1 - Math.exp(-elapsed / 12000)))
      setDownloadProgress(Math.round(target))
      if (target < 90) setTimeout(tick, 250)
    }
    setTimeout(tick, 250)
  }

  const handleDownload = async (type) => {
    setDownloadLoading(true)
    setDownloadProgress(0)
    setDownloadLink(null)
    setError(null)
    startProgress()
    try {
      const endpoints = { pptx: '/api/generate/pptx', pdf: '/api/generate/pdf', docx: '/api/generate/docx' }
      const res = await fetch(endpoints[type], {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPayload(form)),
      })
      if (!res.ok) {
        let msg = `Erreur serveur ${res.status}`
        try {
          const j = await res.json()
          if (Array.isArray(j.detail)) msg = j.detail.map(d => d.msg || JSON.stringify(d)).join(' ; ')
          else if (j.detail) msg = j.detail
        } catch {}
        throw new Error(msg)
      }
      setDownloadProgress(95)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const cd = res.headers.get('content-disposition') || ''
      const fname = cd.match(/filename="(.+)"/)?.[1] || `rapport.${type}`

      // Tentative auto-download
      const a = document.createElement('a')
      a.href = url
      a.download = fname
      a.style.display = 'none'
      document.body.appendChild(a)
      a.click()
      setTimeout(() => document.body.removeChild(a), 100)

      // Lien manuel visible en fallback (si navigateur bloque le download)
      setDownloadLink({ url, fname })
      setDownloadProgress(100)
      setTimeout(() => setDownloadProgress(0), 2000)
    } catch (e) {
      setError(e.message)
      setDownloadProgress(0)
    } finally {
      setDownloadLoading(false)
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
      onDownload={handleDownload}
      loading={downloadLoading}
      progress={downloadProgress}
      downloadLink={downloadLink}
      onClearLink={() => setDownloadLink(null)}
      scores={scores}
    />,
  ]

  return (
    <div className="app-layout">
      <Header onLoadDemo={loadDemo} onReset={resetForm} scores={scores} showResults={showResults} onToggleResults={() => setShowResults(r => !r)} />
      <div className="app-body">
        <Sidebar steps={STEPS} current={step} onChange={setStep} scores={scores} />
        <div className="main-column">
          <main className="main-content">
            {error && (
              <div className="error-banner">
                ⚠️ {error}
                <button onClick={() => setError(null)}>✕</button>
              </div>
            )}
            <div className="step-wrapper" key={step}>
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
                  className="btn btn-ghost"
                  onClick={() => setShowResults(r => !r)}
                >
                  {showResults ? '◀ Masquer panneau' : '▶ Afficher résultats'}
                </button>
              )}
            </div>
          </main>
          <MiniScorebar scores={scores} loading={scoreLoading} />
        </div>
        {showResults && scores && (
          <ResultsPanel
            scores={scores}
            onDownloadPptx={() => handleDownload('pptx')}
            onDownloadPdf={() => handleDownload('pdf')}
            onDownloadDocx={() => handleDownload('docx')}
            loading={downloadLoading}
          progress={downloadProgress}
          />
        )}
      </div>
    </div>
  )
}
