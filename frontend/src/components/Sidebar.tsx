import React from 'react'

import {Link} from 'react-router-dom'

const items = [
  {to:'/','label':'Dashboard'},
  {to:'/workspaces','label':'Workspaces'},
  {to:'/documents','label':'Documents'},
  {to:'/chat','label':'Chat'},
  {to:'/search','label':'Search'},
  {to:'/settings','label':'Settings'},
]

export default function Sidebar(){
  return (
    <aside className="sidebar">
      <nav>
        {items.map(i => (
          <Link key={i.label} to={i.to} className="nav-item">{i.label}</Link>
        ))}
      </nav>
      <div style={{marginTop:20}}>
        <Link to="/chat" className="nav-item">AI Chat</Link>
      </div>
    </aside>
  )
}
