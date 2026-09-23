import { useEffect, useState } from 'react'

// Gabarits éditoriaux des livrables, servis par le backend (report_designs.py,
// source unique) : le frontend n'embarque aucune palette de livrable.
let cache = null
let pending = null

function load() {
  if (cache) return Promise.resolve(cache)
  if (!pending) {
    pending = fetch('/api/designs')
      .then(r => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(data => { cache = data; return data })
      .catch(err => { pending = null; throw err })
  }
  return pending
}

export function useDesigns() {
  const [data, setData] = useState(cache)
  const [error, setError] = useState(null)
  useEffect(() => {
    if (cache) return
    let alive = true
    load().then(d => alive && setData(d)).catch(e => alive && setError(e))
    return () => { alive = false }
  }, [])
  return { designs: data?.designs || [], photoSlots: data?.photo_slots || [], error }
}
