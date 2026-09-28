import { test } from 'node:test'
import assert from 'node:assert/strict'
import { hasPreviousExercise } from './followup.mjs'

test("sans exercice antérieur, pas de suivi", () => {
  assert.equal(hasPreviousExercise([], 2025), false)
  assert.equal(hasPreviousExercise(undefined, 2025), false)
  assert.equal(hasPreviousExercise([{ year: 2025 }], 2025), false)   // le même exercice ne compte pas
})

test("un exercice antérieur suffit", () => {
  assert.equal(hasPreviousExercise([{ year: 2024 }, { year: 2025 }], 2025), true)
  assert.equal(hasPreviousExercise([{ year: '2023' }], '2025'), true)
})
