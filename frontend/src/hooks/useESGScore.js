import { useState, useEffect, useRef } from 'react'

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

export function useESGScore(form) {
  const [scores, setScores] = useState(null)
  const [loading, setLoading] = useState(false)
  const timerRef = useRef(null)

  const buildPayload = (f) => ({
    company: cleanNumeric(f.company),
    environmental: cleanNumeric(f.environmental),
    social: cleanNumeric(f.social),
    governance: cleanNumeric(f.governance),
    presentation_type: f.presentation_type,
    aesthetic_theme: f.aesthetic_theme,
    report_type: f.report_type,
    language: f.language,
    include_recommendations: f.include_recommendations,
    include_benchmarks: f.include_benchmarks,
    include_cover_image: f.include_cover_image ?? true,
  })

  useEffect(() => {
    if (!form.company?.name) return
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        // Le calcul de score n'utilise pas le logo : on l'exclut pour ne pas
        // renvoyer ~2 Mo de base64 à chaque frappe.
        const p = buildPayload(form)
        p.company = { ...p.company, logo_base64: null }
        const res = await fetch('/api/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(p),
        })
        if (res.ok) setScores(await res.json())
      } catch {}
      setLoading(false)
    }, 800)
    return () => clearTimeout(timerRef.current)
  }, [form])

  const calculate = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPayload(form)),
      })
      if (res.ok) setScores(await res.json())
    } catch (e) {
      throw e
    } finally {
      setLoading(false)
    }
  }

  return { scores, loading, calculate, buildPayload }
}
