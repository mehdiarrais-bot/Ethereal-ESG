/**
 * Logique pure du portefeuille — extraite de PortfolioView.jsx pour être
 * testable sans moteur de rendu (aucune dépendance à React/DOM).
 * Aucun comportement n'est modifié ici : c'est une extraction, pas une
 * correction. Voir portfolioMath.test.mjs pour la couverture, exécutée
 * avec le test-runner natif de Node (`node --test`), sans dépendance
 * ajoutée au projet.
 */

/**
 * Points SVG de la sparkline de trajectoire.
 *
 * ATTENTION — comportement actuel documenté, pas nécessairement voulu :
 * l'échelle verticale s'ajuste à la plage réelle des valeurs de `history`
 * (min/max avec une marge de 25 %), et non à une échelle fixe 0-100. Un
 * écart de quelques points peut donc occuper toute la hauteur disponible
 * et se lire visuellement comme une forte progression. Voir le test
 * `sparkline : un écart de 2 points occupe la quasi-totalité de la hauteur`
 * pour la démonstration chiffrée. Décision de correction laissée à part.
 */
export function computeSparklinePoints(history, { W = 140, H = 36, P = 4 } = {}) {
  if (!history || history.length < 2) return null
  const vals = history.map(h => h.total || 0)
  const lo = Math.min(...vals), hi = Math.max(...vals)
  const span = Math.max(hi - lo, 4)        // évite une courbe plate sur données identiques
  const pad = span * 0.25
  const min = lo - pad, max = hi + pad
  const xs = history.map((_, i) => P + (i * (W - 2 * P)) / (history.length - 1))
  const ys = vals.map(v => H - P - ((v - min) / (max - min)) * (H - 2 * P))
  const d = xs.map((x, i) => `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${ys[i].toFixed(1)}`).join(' ')
  const up = vals[vals.length - 1] >= vals[0]
  return { W, H, P, xs, ys, path: d, up, lastX: xs[xs.length - 1], lastY: ys[ys.length - 1] }
}

/** Regroupe les dossiers clients par statut CRM (prospect par défaut). */
export function groupByStatus(clients) {
  return (clients || []).reduce((acc, c) => {
    const k = c.status || 'prospect'
    acc[k] = (acc[k] || 0) + 1
    return acc
  }, {})
}

/** Score moyen des dossiers effectivement scorés (null si aucun). */
export function averageScore(clients) {
  const scored = (clients || []).filter(c => c.last_score != null)
  if (!scored.length) return null
  return scored.reduce((s, c) => s + c.last_score, 0) / scored.length
}
