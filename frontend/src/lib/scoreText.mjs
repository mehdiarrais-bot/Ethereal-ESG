/**
 * Affichage d'un score ou d'une note : « — » quand le backend n'en calcule
 * pas (pilier sans indicateur noté, moins de deux piliers pour le global).
 * Jamais 0 ni 50 à la place d'une absence — même règle que le backend
 * (esg_calculator.score_label).
 */
export const NON_NOTE = '—'

export function scoreText(value, digits = 0) {
  return value == null ? NON_NOTE : value.toFixed(digits)
}

export function ratingText(rating) {
  return rating || NON_NOTE
}

/** Largeur d'une jauge en %, bornée ; 0 pour un score absent (piste vide). */
export function gaugePercent(value) {
  return value == null ? 0 : Math.min(100, Math.max(0, value))
}
