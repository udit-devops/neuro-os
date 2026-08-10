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
    <div style={{maxWidth:480,margin:40}}>
      <h2>Create account</h2>
      <form onSubmit={submit}>
        <label>Full name</label>
        <input value={name} onChange={e=>setName(e.target.value)} />
        <label>Email</label>
        <input value={email} onChange={e=>setEmail(e.target.value)} />
        <label>Password</label>
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button type="submit">Create</button>
      </form>
    </div>
  )
}
