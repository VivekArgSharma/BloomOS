import { useState } from 'react'

import { useAuth } from '../context/AuthContext'
import { supabase } from '../services/supabase'

export function AuthPage() {
  const { user, signOut } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('Use your Supabase account to unlock the full backend, uploads, analytics, and Gemini flows.')

  async function handleSignIn() {
    if (!supabase) {
      setMessage('Supabase is not configured yet. Fill `frontend/.env` with your project URL and anon key.')
      return
    }
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    setMessage(error ? error.message : 'Signed in successfully.')
  }

  async function handleSignUp() {
    if (!supabase) {
      setMessage('Supabase is not configured yet. Fill `frontend/.env` with your project URL and anon key.')
      return
    }
    const { error } = await supabase.auth.signUp({ email, password })
    setMessage(error ? error.message : 'Account created. Check your email if confirmation is enabled.')
  }

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
      <div className="panel auth-card page-panel-full">
        <div className="panel-intro split">
          <div>
            <p className="eyebrow">Authentication</p>
            <h2>{user ? 'You are connected.' : 'Sign in to use the live PlantIQ backend.'}</h2>
          </div>
          <p className="section-copy">{user ? `Signed in as ${user.email}` : 'Supabase auth remains the ownership layer across gardens, plants, uploads, community posting, likes, and comments.'}</p>
        </div>
        {!user ? (
          <>
            <div className="field-group">
              <label className="field-label" htmlFor="auth-email">Email</label>
              <input id="auth-email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" />
            </div>
            <div className="field-group">
              <label className="field-label" htmlFor="auth-password">Password</label>
              <input id="auth-password" value={password} onChange={(event) => setPassword(event.target.value)} type="password" placeholder="Password" />
            </div>
            <div className="inline-fields auth-actions">
              <button onClick={handleSignIn}>Sign in</button>
              <button onClick={handleSignUp}>Create account</button>
            </div>
            <button onClick={handleMagicLink}>Send magic link</button>
          </>
        ) : (
          <button onClick={signOut}>Sign out</button>
        )}
        <p className="status-text">{message}</p>
      </div>
    </section>
  )
}
