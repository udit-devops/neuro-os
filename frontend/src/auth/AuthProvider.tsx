import React, {createContext, useContext, useEffect, useState} from 'react'
import client, {setToken} from '../api/client'

type User = {
  id:number
  email:string
  full_name:string
}

type AuthContext = {
  user: User | null
  token: string | null
  login: (email:string,password:string)=>Promise<void>
  logout: ()=>void
}

const ctx = createContext<AuthContext | undefined>(undefined)

export function useAuth(){
  const c = useContext(ctx)
  if(!c) throw new Error('useAuth must be used within AuthProvider')
  return c
}

export function AuthProvider({children}:{children:React.ReactNode}){
  const [user,setUser] = useState<User | null>(null)
  const [token,setTok] = useState<string | null>(()=>localStorage.getItem('token'))

  useEffect(()=>{
    setToken(token)
    if(token){
      // optionally fetch user
      client.get('/users/me').then(r=>setUser(r.data)).catch(()=>{setUser(null)})
    }else{
      setUser(null)
    }
  },[token])

  async function login(email:string,password:string){
    const form = new FormData()
    form.append('username',email)
    form.append('password',password)
    const res = await client.post('/users/login', form)
    const data = res.data
    setTok(data.access_token)
    localStorage.setItem('token',data.access_token)
    setUser((await client.get('/users/me')).data)
  }

  function logout(){
    setTok(null)
    localStorage.removeItem('token')
    setUser(null)
    setToken(null)
  }

  return <ctx.Provider value={{user,token,login,logout}}>{children}</ctx.Provider>
}
