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
    <div style={{maxWidth:480,margin:40}}>
      <h2>Sign in</h2>
      <form onSubmit={submit}>
        <label>Email</label>
        <input value={email} onChange={e=>setEmail(e.target.value)} />
        <label>Password</label>
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button disabled={loading} type="submit">Sign in</button>
      </form>
    </div>
  )
}
