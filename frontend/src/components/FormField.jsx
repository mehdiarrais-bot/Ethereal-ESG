export function FormField({ label, hint, children }) {
  return (
    <div className="form-group">
      <label>{label}</label>
      {children}
      {hint && <span className="form-hint">{hint}</span>}
    </div>
  )
}

export function NumberInput({ value, onChange, placeholder, min, max, step = 'any' }) {
  const handleChange = (e) => {
    if (e.target.value === '') { onChange(''); return }
    const n = parseFloat(e.target.value)
    if (!isFinite(n)) return
    if (min !== undefined && n < min) return
    if (max !== undefined && n > max) return
    onChange(e.target.value)
  }
  return (
    <input
      type="number"
      value={value}
      onChange={handleChange}
      placeholder={placeholder || '—'}
      min={min}
      max={max}
      step={step}
    />
  )
}

export function SelectInput({ value, onChange, options }) {
  return (
    <select value={value} onChange={e => onChange(e.target.value)}>
      {options.map(([val, label]) => (
        <option key={val} value={val}>{label}</option>
      ))}
    </select>
  )
}

export function BoolToggle({ value, onChange, labelYes = 'Oui', labelNo = 'Non' }) {
  return (
    <div className="toggle-group">
      <button
        type="button"
        className={`toggle-btn ${value === true ? 'active' : ''}`}
        onClick={() => onChange(true)}
      >
        ✓ {labelYes}
      </button>
      <button
        type="button"
        className={`toggle-btn ${value === false ? 'active' : ''}`}
        onClick={() => onChange(false)}
      >
        ✗ {labelNo}
      </button>
      <button
        type="button"
        className={`toggle-btn ${value === null ? 'active' : ''}`}
        onClick={() => onChange(null)}
      >
        —
      </button>
    </div>
  )
}

export function SectionTitle({ icon, children }) {
  return (
    <div className="form-section-title">
      {icon && <span>{icon}</span>}
      {children}
    </div>
  )
}
