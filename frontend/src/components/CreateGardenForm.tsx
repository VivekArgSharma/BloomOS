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
      <div>
        <p className="eyebrow">New Garden</p>
        <h3>Start a new growing zone</h3>
      </div>
      <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Balcony herbs" />
      <div className="inline-fields">
        <select value={locationType} onChange={(event) => setLocationType(event.target.value)}>
          <option value="balcony">Balcony</option>
          <option value="indoor">Indoor</option>
          <option value="terrace">Terrace</option>
          <option value="outdoor">Outdoor</option>
        </select>
        <input value={city} onChange={(event) => setCity(event.target.value)} placeholder="City" />
      </div>
      <button type="submit">Create garden</button>
    </form>
  )
}
