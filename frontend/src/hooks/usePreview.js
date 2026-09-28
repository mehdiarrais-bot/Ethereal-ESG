import { useEffect, useRef, useState } from 'react'
import { buildPayload } from './useESGScore'

// Aperçu vivant d'un gabarit : couverture + « coup d'œil » rendues par le
// backend (POST /api/preview) avec les données du dossier en cours.
const DEBOUNCE_MS = 450          // la saisie se calme avant de relancer un rendu
const CACHE_SIZE = 12            // rendus gardés (gabarit × état du dossier)

const cache = new Map()          // clé -> URL d'objet (image PNG)

function remember(key, url) {
  cache.set(key, url)
  if (cache.size > CACHE_SIZE) {
    const [oldKey, oldUrl] = cache.entries().next().value
    URL.revokeObjectURL(oldUrl)
    cache.delete(oldKey)
  }
}

/**
 * { url, loading, unavailable } pour le gabarit `design`, le formulaire `form`
 * et `pageWidth` : largeur d'une page en pixels RÉELS (taille affichée × densité
 * de l'écran). Sans elle, un écran à 150-200 % étire l'image : elle est floue.
 */
export function usePreview(design, form, pageWidth) {
  const [state, setState] = useState({ url: null, loading: false, unavailable: false })
  const abortRef = useRef(null)

  const payload = form?.company?.name ? { ...buildPayload(form), aesthetic_theme: design } : null
  const body = payload ? JSON.stringify(payload) : null
  const key = body && pageWidth ? `${pageWidth}|${body}` : null

  useEffect(() => {
    if (!key) { setState({ url: null, loading: false, unavailable: false }); return }
    if (cache.has(key)) { setState({ url: cache.get(key), loading: false, unavailable: false }); return }
    setState(s => ({ ...s, url: null, loading: true }))
    const timer = setTimeout(async () => {
      abortRef.current?.abort()
      const ctrl = new AbortController()
      abortRef.current = ctrl
      try {
        const res = await fetch(`/api/preview?width=${pageWidth}`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body, signal: ctrl.signal,
        })
        if (!res.ok) {                       // 503 : installation sans rendu d'aperçu
          setState({ url: null, loading: false, unavailable: res.status === 503 })
          return
        }
        const url = URL.createObjectURL(await res.blob())
        remember(key, url)
        setState({ url, loading: false, unavailable: false })
      } catch (e) {
        if (e.name !== 'AbortError') setState({ url: null, loading: false, unavailable: false })
      }
    }, DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [key])  // eslint-disable-line react-hooks/exhaustive-deps -- key contient body et pageWidth

  useEffect(() => () => abortRef.current?.abort(), [])
  return state
}
