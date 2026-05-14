import { useState } from 'react'

import { supabase } from '../services/supabase'

export function AuthPage() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('Use Supabase credentials in `frontend/.env` to enable live auth. Until then, the app runs in demo mode.')

  async function handleMagicLink() {
    if (!supabase) {
      setMessage('Supabase is not configured yet. Fill `frontend/.env` with your project URL and anon key.')
      return
    }
    const { error } = await supabase.auth.signInWithOtp({ email })
    setMessage(error ? error.message : 'Magic link sent. Check your inbox.')
  }

  return (
    <section className="grid-layout single">
      <div className="panel auth-card">
        <p className="eyebrow">Authentication</p>
        <h2>Connect Supabase auth when you are ready.</h2>
        <p className="muted">This scaffold is already shaped for email/password or magic-link auth. Demo data still works before you connect the backend.</p>
        <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" />
        <button onClick={handleMagicLink}>Send magic link</button>
        <p className="status-text">{message}</p>
      </div>
    </section>
  )
}
