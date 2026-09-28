import { test } from 'node:test'
import assert from 'node:assert/strict'
import { reportingYears, targetYears } from './years.mjs'

test("l'exercice de l'année en cours est proposé", () => {
  const ys = reportingYears(new Date('2026-09-28'))
  assert.equal(ys[0], 2020)
  assert.equal(ys.at(-1), 2026)
})

test('jamais au-delà de la borne du modèle', () => {
  assert.equal(reportingYears(new Date('2040-01-01')).at(-1), 2035)
})

test("l'horizon suit l'exercice", () => {
  assert.deepEqual(targetYears(2026), [2027, 2028, 2030, 2035, 2040, 2050])
  assert.deepEqual(targetYears(2030), [2035, 2040, 2050])
})
