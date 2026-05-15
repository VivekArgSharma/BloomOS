import { FormEvent, useState } from 'react'

import type { ChatResponse } from '../types'

type Props = {
  onAsk: (question: string) => Promise<ChatResponse>
}

export function ChatPanel({ onAsk }: Props) {
  const [question, setQuestion] = useState('Should I water today?')
  const [response, setResponse] = useState<ChatResponse | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const next = await onAsk(question)
    setResponse(next)
  }

  return (
    <section className="panel page-panel-full" id="chat-anchor">
      <div className="section-head">
        <div>
          <p className="eyebrow">RAG Chat</p>
          <h3>Ask with context</h3>
        </div>
      </div>
      <p className="section-copy">Ask about watering cadence, symptom patterns, or the latest diary changes and let the answer stay grounded in this plant's own history.</p>
      <form className="chat-form" onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="plant-question">Question</label>
          <textarea id="plant-question" value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} />
        </div>
        <button type="submit">Ask PlantIQ</button>
      </form>
      {response ? (
        <div className="chat-response">
          <p>{response.answer}</p>
          <ul>
            {response.grounding.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  )
}
