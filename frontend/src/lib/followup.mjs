/**
 * Suivi annuel : proposé seulement si le dossier a un exercice antérieur à
 * l'exercice du rapport (sinon rien à suivre). Le serveur accepte quand même
 * la génération et le dit dans le rapport.
 * Exécution des tests : node --test src/lib/followup.test.mjs
 */
export function hasPreviousExercise(history, year) {
  return (history || []).some(h => Number(h.year) < Number(year))
}
