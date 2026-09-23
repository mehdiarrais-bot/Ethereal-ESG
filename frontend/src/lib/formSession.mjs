/**
 * Session de saisie : quel dossier client est « ouvert » et quand demander
 * confirmation avant d'écraser le formulaire. Logique pure, testée par
 * formSession.test.mjs (node --test).
 *
 * Défaut corrigé (DETTE.md § 7, audit du 2026-09-24) : « Données exemple »
 * remplaçait le formulaire mais gardait l'identifiant du dossier ouvert ;
 * « Enregistrer » écrasait alors le dossier réel avec la démonstration.
 * Règle : tout remplacement du formulaire qui n'est pas le chargement d'un
 * dossier DÉTACHE la session de tout dossier.
 */

export const NO_DOSSIER = Object.freeze({ clientId: null, history: [], actions: [] })

/** Session après un remplacement du formulaire. `dossier` : réponse de
 *  GET /api/clients/{id}, pour l'action « load » uniquement. */
export function sessionAfter(action, dossier) {
  if (action === 'load') {
    return {
      clientId: dossier.id,
      history: dossier.score_history || [],
      actions: dossier.completed_actions || [],
    }
  }
  if (action === 'demo' || action === 'reset') return NO_DOSSIER
  throw new Error(`Action de session inconnue : ${action}`)
}

export const DISCARD_MESSAGE =
  'Les modifications non enregistrées de ce dossier seront perdues. Continuer ?'

/** Faut-il confirmer avant de remplacer le formulaire ? `confirm` est
 *  injecté (window.confirm dans l'interface) pour rester testable. */
export function mayDiscard(dirty, confirm) {
  return !dirty || Boolean(confirm(DISCARD_MESSAGE))
}
