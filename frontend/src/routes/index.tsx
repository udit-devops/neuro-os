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
import Settings from '../pages/Settings'
import {useAuth} from '../auth/AuthProvider'

function Protected({children}:{children:JSX.Element}){
  const auth = useAuth()
  if(!auth.token) return <Navigate to="/login" replace />
  return children
}

export default function AppRoutes(){
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login/>} />
        <Route path="/signup" element={<Signup/>} />
        <Route path="/" element={<Shell /> }>
          <Route index element={<Protected><Dashboard/></Protected>} />
          <Route path="workspaces" element={<Protected><Workspaces/></Protected>} />
          <Route path="workspaces/:workspaceId" element={<Protected><WorkspaceDetail/></Protected>} />
          <Route path="documents" element={<Protected><Documents/></Protected>} />
          <Route path="chat" element={<Protected><Chat/></Protected>} />
          <Route path="settings" element={<Protected><Settings/></Protected>} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
