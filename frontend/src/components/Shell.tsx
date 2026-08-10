import React from 'react'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import {Outlet} from 'react-router-dom'

export default function Shell(){
  return (
    <div className="app-shell">
      <Topbar />
      <div className="shell-body">
        <Sidebar />
        <main className="shell-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
