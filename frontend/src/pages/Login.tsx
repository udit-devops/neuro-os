import React, {useState} from 'react'
import {useNavigate} from 'react-router-dom'
import {useAuth} from '../auth/AuthProvider'

export default function Login(){
  const [email,setEmail] = useState('')
  const [password,setPassword] = useState('')
  const [loading,setLoading] = useState(false)
  const auth = useAuth()
  const nav = useNavigate()

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setLoading(true)
    try{
      await auth.login(email,password)
      nav('/')
    }catch(err){
      alert('Login failed')
    }finally{setLoading(false)}
  }

  return (
    <div style={{maxWidth:560,margin:40}}>
      <h2 className="h1">Sign in</h2>
      <form onSubmit={submit} style={{marginTop:16,display:'grid',gap:12}}>
        <label className="muted">Email</label>
        <input className="ui-input" value={email} onChange={e=>setEmail(e.target.value)} aria-label="email" />
        <label className="muted">Password</label>
        <input className="ui-input" type="password" value={password} onChange={e=>setPassword(e.target.value)} aria-label="password" />
        <div style={{display:'flex',gap:12,alignItems:'center'}}>
          <button className="btn btn-primary" disabled={loading} type="submit">Sign in</button>
          <a href="/signup" style={{color:'var(--muted)',textDecoration:'none'}}>Create account</a>
        </div>
      </form>
    </div>
  )
}
