import React, {useState} from 'react'
import client from '../api/client'
import {useNavigate} from 'react-router-dom'

export default function Signup(){
  const [email,setEmail] = useState('')
  const [password,setPassword] = useState('')
  const [name,setName] = useState('')
  const nav = useNavigate()

  async function submit(e:React.FormEvent){
    e.preventDefault()
    try{
      await client.post('/users', {email, password, full_name: name})
      nav('/login')
    }catch(err){
      alert('Signup failed')
    }
  }

  return (
    <div style={{maxWidth:560,margin:40}}>
      <h2 className="h1">Create account</h2>
      <form onSubmit={submit} style={{marginTop:16,display:'grid',gap:12}}>
        <label className="muted">Full name</label>
        <input className="ui-input" value={name} onChange={e=>setName(e.target.value)} />
        <label className="muted">Email</label>
        <input className="ui-input" value={email} onChange={e=>setEmail(e.target.value)} />
        <label className="muted">Password</label>
        <input className="ui-input" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <div style={{display:'flex',gap:12}}>
          <button className="btn btn-primary" type="submit">Create</button>
          <a href="/login" style={{color:'var(--muted)',textDecoration:'none',alignSelf:'center'}}>Sign in</a>
        </div>
      </form>
    </div>
  )
}
