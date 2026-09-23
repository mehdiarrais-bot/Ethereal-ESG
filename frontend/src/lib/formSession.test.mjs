/**
 * Session de saisie (DETTE.md § 7). Exécution : npm test
 */
import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { sessionAfter, mayDiscard, NO_DOSSIER } from './formSession.mjs'

describe('sessionAfter', () => {
  test('les données exemple détachent le dossier ouvert', () => {
    // Le scénario destructeur : un dossier est ouvert, on charge la démo.
    const s = sessionAfter('demo')
    assert.equal(s.clientId, null, 'Enregistrer ne doit plus viser le dossier réel')
    assert.deepEqual(s, NO_DOSSIER)
  })

  test('« Nouveau » détache aussi le dossier', () => {
    assert.deepEqual(sessionAfter('reset'), NO_DOSSIER)
  })

  test('le chargement ouvre le dossier et son historique', () => {
    const s = sessionAfter('load', { id: 'a'.repeat(32), score_history: [{ year: 2024 }],
                                     completed_actions: [{ title: 'x', year: 2024 }] })
    assert.equal(s.clientId, 'a'.repeat(32))
    assert.equal(s.history.length, 1)
    assert.equal(s.actions.length, 1)
  })

  test('action inconnue : échec bruyant', () => {
    assert.throws(() => sessionAfter('import'))
  })
})

describe('mayDiscard', () => {
  test('sans modification, aucune question', () => {
    let asked = false
    assert.equal(mayDiscard(false, () => { asked = true; return false }), true)
    assert.equal(asked, false)
  })

  test('avec modifications, la réponse de l’utilisateur décide', () => {
    assert.equal(mayDiscard(true, () => true), true)
    assert.equal(mayDiscard(true, () => false), false)
  })
})
