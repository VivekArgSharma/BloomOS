import { FormEvent, useState } from 'react'

type Props = {
  onSubmit: (payload: { name: string; location_type: string; city?: string }) => Promise<unknown>
}

export function CreateGardenForm({ onSubmit }: Props) {
  const [name, setName] = useState('')
  const [locationType, setLocationType] = useState('balcony')
  const [city, setCity] = useState('')

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim()) return
    await onSubmit({ name, location_type: locationType, city })
    setName('')
    setCity('')
  }

  return (
    <form className="panel form-panel" onSubmit={handleSubmit}>
      <div className="panel-intro split">
        <div>
          <p className="eyebrow">New Garden</p>
          <h3>Start a new growing zone</h3>
        </div>
        <p className="muted">Define the environment first so PlantIQ can tailor weather context, plant compatibility, and care pacing to the space.</p>
      </div>
      <div className="field-group">
        <label className="field-label" htmlFor="garden-name">Garden name</label>
        <input id="garden-name" value={name} onChange={(event) => setName(event.target.value)} placeholder="Balcony herbs" />
      </div>
      <div className="inline-fields">
        <div className="field-group">
          <label className="field-label" htmlFor="location-type">Location type</label>
          <select id="location-type" value={locationType} onChange={(event) => setLocationType(event.target.value)}>
            <option value="balcony">Balcony</option>
            <option value="indoor">Indoor</option>
            <option value="terrace">Terrace</option>
            <option value="outdoor">Outdoor</option>
          </select>
        </div>
        <div className="field-group">
          <label className="field-label" htmlFor="garden-city">City</label>
          <input id="garden-city" value={city} onChange={(event) => setCity(event.target.value)} placeholder="City" />
        </div>
      </div>
      <button type="submit">Create garden</button>
    </form>
  )
}
