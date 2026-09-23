import { useState } from 'react'
import { useDesigns } from '../hooks/useDesigns'

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

export function DesignPicker({ value, onChange }) {
  const { designs, error } = useDesigns()
  if (error) return <p className="design-error">Gabarits indisponibles : le serveur ne répond pas.</p>
  return (
    <div className="design-grid">
      {designs.map(d => (
        <button key={d.id} type="button" onClick={() => onChange(d.id)}
          className={`design-card ${value === d.id ? 'selected' : ''}`}>
          <img src={`/designs/${d.id}.jpg`} alt={`Aperçu du gabarit ${d.label.fr}`} loading="lazy" />
          <div className="design-meta">
            <div className="option-name">{d.label.fr}</div>
            <div className="option-desc">{d.tagline.fr}</div>
          </div>
          {value === d.id && <div className="option-check">✓</div>}
        </button>
      ))}
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
        Sans photo fournie, le rapport utilise des images d'illustration libres de droits
        (paysages, végétal, architecture), signalées comme telles dans la note méthodologique.
      </p>
    </div>
  )
}
