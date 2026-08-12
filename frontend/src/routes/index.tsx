import React from 'react'
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import Shell from '../components/Shell'
import Login from '../pages/Login'
import Signup from '../pages/Signup'
import Dashboard from '../pages/Dashboard'
import Workspaces from '../pages/Workspaces'
import WorkspaceDetail from '../pages/WorkspaceDetail'
import Chat from '../pages/Chat'
import Documents from '../pages/Documents'
import Search from '../pages/Search'
import Settings from '../pages/Settings'
import {useAuth} from '../auth/AuthProvider'

function Protected({children}:{children:React.ReactNode}){
  const {token} = useAuth()
  if(!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function AppRoutes(){
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login/>} />
        <Route path="/signup" element={<Signup/>} />
        <Route path="/" element={<Protected><Shell /></Protected>}>
          <Route index element={<Dashboard/>} />
          <Route path="workspaces" element={<Workspaces/>} />
          <Route path="workspaces/:workspaceId" element={<WorkspaceDetail/>} />
          <Route path="documents" element={<Documents/>} />
          <Route path="search" element={<Search/>} />
          <Route path="chat" element={<Chat/>} />
          <Route path="settings" element={<Settings/>} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
