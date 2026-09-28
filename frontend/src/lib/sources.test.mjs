/**
 * Garde-fou (DETTE § 25) : une séquence \uXXXX écrite dans du texte JSX
 * s'affiche telle quelle (« L\u2019analyse » apparaissait dans l'interface).
 * Les composants écrivent le caractère lui-même.
 */
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const SRC = join(dirname(fileURLToPath(import.meta.url)), '..')

function jsxFiles(dir) {
  return readdirSync(dir).flatMap(f => {
    const p = join(dir, f)
    return statSync(p).isDirectory() ? jsxFiles(p) : p.endsWith('.jsx') ? [p] : []
  })
}

test('aucun échappement \\uXXXX dans les composants', () => {
  const fautes = jsxFiles(SRC).flatMap(f =>
    readFileSync(f, 'utf8').split('\n')
      .map((l, i) => [i + 1, l])
      .filter(([, l]) => /\\u[0-9a-fA-F]{4}/.test(l))
      .map(([n]) => `${f}:${n}`))
  assert.deepEqual(fautes, [])
})
