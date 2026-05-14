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
    <section className="panel" id="chat-anchor">
      <div className="section-head">
        <div>
          <p className="eyebrow">RAG Chat</p>
          <h3>Ask with context</h3>
        </div>
      </div>
      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} />
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
