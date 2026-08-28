/**
 * Couverture de la vue portefeuille (dette de test signalée en revue).
 * Exécution :  node --test src/lib/portfolioMath.test.mjs
 * Aucune dépendance ajoutée — test-runner natif de Node (>= 18).
 *
 * Ne couvre pas le rendu React (fetch, cartes DOM) : ça demanderait
 * jsdom + testing-library, un ajout d'outillage distinct non fait ici.
 * Ce fichier couvre la logique pure : statuts, score moyen, sparkline.
 */
import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { computeSparklinePoints, groupByStatus, averageScore } from './portfolioMath.mjs'

describe('groupByStatus', () => {
  test('compte les dossiers par statut', () => {
    const clients = [
      { status: 'prospect' }, { status: 'signed' },
      { status: 'signed' }, { status: 'delivered' },
    ]
    assert.deepEqual(groupByStatus(clients), { prospect: 1, signed: 2, delivered: 1 })
  })

  test('un dossier sans statut compte comme "prospect"', () => {
    assert.deepEqual(groupByStatus([{}, { status: undefined }]), { prospect: 2 })
  })

  test('liste vide ou absente -> objet vide', () => {
    assert.deepEqual(groupByStatus([]), {})
    assert.deepEqual(groupByStatus(null), {})
    assert.deepEqual(groupByStatus(undefined), {})
  })
})

describe('averageScore', () => {
  test('moyenne des dossiers scorés uniquement', () => {
    const clients = [{ last_score: 60 }, { last_score: 80 }, { last_score: null }]
    assert.equal(averageScore(clients), 70)
  })

  test('aucun dossier scoré -> null', () => {
    assert.equal(averageScore([{ last_score: null }]), null)
    assert.equal(averageScore([]), null)
    assert.equal(averageScore(null), null)
  })
})

describe('computeSparklinePoints — structure', () => {
  test('moins de 2 points -> null (rendu "—")', () => {
    assert.equal(computeSparklinePoints([]), null)
    assert.equal(computeSparklinePoints([{ year: 2025, total: 60 }]), null)
    assert.equal(computeSparklinePoints(null), null)
  })

  test('produit un point par exercice, dans l\'ordre, tracé "M...L..."', () => {
    const history = [{ year: 2023, total: 50 }, { year: 2024, total: 55 }, { year: 2025, total: 60 }]
    const pts = computeSparklinePoints(history)
    assert.equal(pts.xs.length, 3)
    assert.equal(pts.ys.length, 3)
    assert.ok(pts.path.startsWith('M'))
    assert.equal((pts.path.match(/L/g) || []).length, 2)
    // Abscisses strictement croissantes (ordre chronologique préservé)
    assert.ok(pts.xs[0] < pts.xs[1] && pts.xs[1] < pts.xs[2])
  })

  test('trajectoire montante -> up=true, descendante -> up=false', () => {
    const montante = computeSparklinePoints([{ total: 50 }, { total: 70 }])
    const descendante = computeSparklinePoints([{ total: 70 }, { total: 50 }])
    assert.equal(montante.up, true)
    assert.equal(descendante.up, false)
  })

  test('valeur absente traitée comme 0 (h.total || 0)', () => {
    const pts = computeSparklinePoints([{ total: null }, { total: 40 }])
    assert.ok(pts) // ne plante pas, produit bien 2 points
  })
})

describe('computeSparklinePoints — échelle verticale (anomalie signalée en revue)', () => {
  test('deux exercices identiques -> ligne plate, pas de division par zéro', () => {
    const pts = computeSparklinePoints([{ total: 60 }, { total: 60 }])
    assert.ok(Number.isFinite(pts.ys[0]) && Number.isFinite(pts.ys[1]))
    assert.equal(pts.ys[0], pts.ys[1])
  })

  test(
    'CONFIRMÉ : un écart réel de 2 points (55 -> 57 / 100) occupe plus de 40 % ' +
    'de la hauteur disponible du graphique — l\'échelle verticale se cale sur ' +
    'min/max ± 25 %, pas sur 0-100. Ce test verrouille le comportement actuel ' +
    'tel quel ; il ne dit pas si c\'est le comportement voulu.',
    () => {
      const pts = computeSparklinePoints([{ year: 2024, total: 55 }, { year: 2025, total: 57 }])
      const drawableHeight = pts.H - 2 * pts.P          // hauteur utile du tracé
      const verticalSwing = Math.abs(pts.ys[0] - pts.ys[1])
      const swingRatio = verticalSwing / drawableHeight
      const realMoveRatio = 2 / 100                     // le vrai déplacement : 2 points sur 100

      assert.ok(
        swingRatio > 0.4,
        `swing visuel = ${(swingRatio * 100).toFixed(0)}% de la hauteur pour un ` +
        `déplacement réel de ${(realMoveRatio * 100).toFixed(0)}% de l'échelle du score`
      )
      // Le rapport visuel/réel dépasse 10x : la distorsion est majeure, pas marginale.
      assert.ok(swingRatio / realMoveRatio > 10)
    }
  )

  test(
    'à titre de comparaison : sur une échelle fixe 0-100, le même écart ' +
    'de 2 points serait quasi invisible (< 3 % de la hauteur)',
    () => {
      const H = 36, P = 4
      const fixedScale = v => H - P - (v / 100) * (H - 2 * P)
      const swing = Math.abs(fixedScale(55) - fixedScale(57))
      const drawableHeight = H - 2 * P
      assert.ok(swing / drawableHeight < 0.03)
    }
  )
})
