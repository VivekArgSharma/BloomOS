import { Link } from 'react-router-dom'

export function AuthRequired({ message }: { message: string }) {
  return (
    <section className="panel auth-required">
      <p className="eyebrow">Sign In Required</p>
      <h3>Connect your Supabase account</h3>
      <p className="muted">{message}</p>
      <Link to="/auth" className="button-link">Sign in</Link>
    </section>
  )
}
