/**
 * Scores absents (DETTE § 11) : l'interface affiche « — », jamais 0.
 * Exécution :  node --test src/lib/scoreText.test.mjs
 */
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { scoreText, ratingText, gaugePercent, NON_NOTE } from './scoreText.mjs'

test('un score absent s\'affiche « — »', () => {
  assert.equal(scoreText(null), NON_NOTE)
  assert.equal(scoreText(undefined, 1), NON_NOTE)
})

test('un score présent garde ses décimales', () => {
  assert.equal(scoreText(69.54, 1), '69.5')
  assert.equal(scoreText(0), '0')          // un vrai zéro reste un zéro
})

test('une note absente s\'affiche « — »', () => {
  assert.equal(ratingText(null), NON_NOTE)
  assert.equal(ratingText('A'), 'A')
})

test('jauge : piste vide pour un score absent, bornée sinon', () => {
  assert.equal(gaugePercent(null), 0)
  assert.equal(gaugePercent(130), 100)
  assert.equal(gaugePercent(42), 42)
})
