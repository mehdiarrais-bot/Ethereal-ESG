/**
 * Années proposées par l'étape Entreprise (DETTE § 25 : la liste s'arrêtait
 * à 2025, l'exercice 2026 n'était pas sélectionnable). Bornes du modèle :
 * exercice 2000-2035, horizon 2025-2050 (backend/models.py, CompanyInfo).
 * Tests : node --test src/lib/years.test.mjs
 */
const FIRST_YEAR = 2020
const MAX_REPORTING_YEAR = 2035
const HORIZONS = [2027, 2028, 2030, 2035, 2040, 2050]

export function reportingYears(today = new Date()) {
  const last = Math.min(today.getFullYear(), MAX_REPORTING_YEAR)
  const out = []
  for (let y = FIRST_YEAR; y <= last; y++) out.push(y)
  return out
}

/** Horizons postérieurs à l'exercice : un horizon passé n'a pas de sens. */
export function targetYears(reportingYear) {
  return HORIZONS.filter(y => y > Number(reportingYear))
}
