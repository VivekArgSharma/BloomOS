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
          <p className="eyebrow">BloomIQ Analysis</p>
          <h3>Ask with context</h3>
        </div>
      </div>
      <p className="section-copy">Ask about watering, symptoms, or recent diary changes.</p>
      <form className="chat-form" onSubmit={handleSubmit}>
        <div className="field-group">
          <label className="field-label" htmlFor="plant-question">Question</label>
          <textarea id="plant-question" value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} />
        </div>
        <button type="submit">Ask BloomIQ</button>
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
