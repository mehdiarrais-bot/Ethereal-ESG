import { useEffect, useRef, useState } from 'react'
import { useDesigns } from '../hooks/useDesigns'
import { usePreview } from '../hooks/usePreview'

const SLOT_LABELS = {
  cover: 'Couverture',
  company: "L'entreprise",
  environment: 'Environnement',
  social: 'Social / équipes',
  governance: 'Gouvernance',
}

const MAX_SIDE = 1600      // px : largeur utile maximale d'une photo pleine page
const JPEG_QUALITY = 0.82

// Réduit la photo dans le navigateur avant envoi (~300 Ko au lieu de
// plusieurs Mo) : le backend plafonne chaque photo à 1,5 Mo.
function downscale(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      const scale = Math.min(1, MAX_SIDE / Math.max(img.width, img.height))
      const canvas = document.createElement('canvas')
      canvas.width = Math.round(img.width * scale)
      canvas.height = Math.round(img.height * scale)
      canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)
      URL.revokeObjectURL(url)
      resolve(canvas.toDataURL('image/jpeg', JPEG_QUALITY))
    }
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('Image illisible')) }
    img.src = url
  })
}

// Pastilles de palette lues dans les jetons du gabarit (/api/designs) :
// aucune couleur de livrable n'est recopiée dans le frontend.
const SWATCHES = ['paper', 'primary', 'accent', 'env', 'social', 'gov']

// Largeur de rendu demandée au serveur, par paliers : un redimensionnement de
// fenêtre ne relance pas un rendu à chaque pixel, et le cache reste utile.
const WIDTH_STEP = 160
const MIN_PAGE_PX = 320
const MAX_PAGE_PX = 1600

function usePageWidth(ref) {
  const [px, setPx] = useState(0)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const measure = () => {
      const cs = getComputedStyle(el)
      const inner = el.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)
      if (inner <= 0) { setPx(0); return }                 // pas encore disposé : aucun rendu
      const pageCss = inner / 2                             // deux pages côte à côte
      const real = pageCss * (window.devicePixelRatio || 1)
      const stepped = Math.ceil(real / WIDTH_STEP) * WIDTH_STEP
      setPx(Math.max(MIN_PAGE_PX, Math.min(MAX_PAGE_PX, stepped)))
    }
    measure()
    const ro = new ResizeObserver(measure)
    ro.observe(el)
    return () => ro.disconnect()
  }, [ref])
  return px
}

function DesignStage({ design, form }) {
  // Conteneur stable (hors du bloc remonté à chaque gabarit) : l'observateur
  // de taille reste attaché au bon élément.
  const stageRef = useRef(null)
  const pageWidth = usePageWidth(stageRef)
  const { url, loading, unavailable } = usePreview(design.id, form, pageWidth)
  const [liveShown, setLiveShown] = useState(false)
  useEffect(() => { setLiveShown(false) }, [url])
  const status = unavailable ? 'Aperçu générique (rendu indisponible sur cette installation)'
    : !form?.company?.name ? "Aperçu générique — saisissez le nom de l'entreprise pour voir vos données"
    : loading ? 'Rendu avec vos données…'
    : url ? 'Aperçu avec vos données : couverture et « ESG en un coup d’œil »' : ''
  return (
    <div className="design-stage" aria-live="polite" ref={stageRef}>
      {/* key : chaque gabarit remonte le bloc, ce qui rejoue l'animation d'entrée */}
      <div key={design.id} className="design-stage-inner">
        <div className="design-stage-frame">
          <img className="design-stage-thumb" src={`/designs/${design.id}.webp`}
            alt={`Aperçu du gabarit ${design.label.fr}`} />
          {url && (
            <img className={`design-stage-live ${liveShown ? 'shown' : ''}`} src={url}
              alt={`Couverture et page « coup d’œil » au gabarit ${design.label.fr}, avec vos données`}
              onLoad={() => setLiveShown(true)} />
          )}
          {loading && <div className="design-stage-spinner" aria-hidden="true" />}
        </div>
        <div className="design-stage-caption">
          <div>
            <div className="design-stage-name">{design.label.fr}</div>
            <div className="design-stage-tagline">{design.tagline.fr}</div>
          </div>
          <div className="design-stage-status">{status}</div>
        </div>
      </div>
    </div>
  )
}

export function DesignPicker({ value, onChange, form }) {
  const { designs, error } = useDesigns()
  const listRef = useRef(null)
  if (error) return <p className="design-error">Gabarits indisponibles : le serveur ne répond pas.</p>
  if (!designs.length) return null
  const current = designs.find(d => d.id === value) || designs[0]

  // Flèches du clavier : parcourir les gabarits comme un groupe de boutons radio.
  const onKeyDown = (e) => {
    const step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key]
    if (!step) return
    e.preventDefault()
    const i = designs.findIndex(d => d.id === current.id)
    const next = designs[(i + step + designs.length) % designs.length]
    onChange(next.id)
    listRef.current?.querySelector(`[data-design="${next.id}"]`)?.focus()
  }

  return (
    <div className="design-chooser">
      <div className="design-list" role="radiogroup" aria-label="Gabarit du rapport"
        ref={listRef} onKeyDown={onKeyDown}>
        {designs.map(d => {
          const selected = d.id === current.id
          return (
            <button key={d.id} type="button" role="radio" aria-checked={selected}
              tabIndex={selected ? 0 : -1} data-design={d.id}
              className={`design-chip ${selected ? 'selected' : ''}`} onClick={() => onChange(d.id)}>
              <span className="design-chip-swatches" aria-hidden="true">
                {SWATCHES.map(k => <span key={k} style={{ background: d.colors[k] }} />)}
              </span>
              <span className="design-chip-text">
                <span className="design-chip-name">{d.label.fr}</span>
                <span className="design-chip-tagline">{d.tagline.fr}</span>
              </span>
            </button>
          )
        })}
      </div>
      <DesignStage design={current} form={form} />
    </div>
  )
}

export function PhotoSlots({ photos, onChange }) {
  const { photoSlots } = useDesigns()
  const [error, setError] = useState(null)
  const current = photos || {}

  const pick = (slot) => async (e) => {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    if (!/^image\/(png|jpeg)$/.test(file.type)) { setError('Format PNG ou JPEG attendu.'); return }
    try {
      const dataUrl = await downscale(file)
      setError(null)
      onChange({ ...current, [slot]: dataUrl })
    } catch (err) {
      setError(err.message)
    }
  }
  const remove = (slot) => () => {
    const next = { ...current }
    delete next[slot]
    onChange(Object.keys(next).length ? next : null)
  }

  return (
    <div>
      <div className="photo-grid">
        {photoSlots.map(slot => (
          <div key={slot} className="photo-slot">
            {current[slot] ? (
              <>
                <img src={current[slot]} alt={SLOT_LABELS[slot] || slot} />
                <button type="button" className="photo-remove" onClick={remove(slot)}>Retirer</button>
              </>
            ) : (
              <label className="photo-add">
                <input type="file" accept="image/png,image/jpeg" onChange={pick(slot)} />
                <span>+ Ajouter</span>
              </label>
            )}
            <div className="photo-label">{SLOT_LABELS[slot] || slot}</div>
          </div>
        ))}
      </div>
      {error && <p className="design-error">{error}</p>}
      <p className="photo-hint">
        Sans photo fournie, la couverture et le pilier environnemental sont illustrés par des
        paysages libres de droits (signalés dans la note méthodologique) ; les autres emplacements
        restent sans photo plutôt que d'afficher une image sans rapport avec le sujet.
      </p>
    </div>
  )
}
