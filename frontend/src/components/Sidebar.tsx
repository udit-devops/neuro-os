import React from 'react'
import { NavLink } from 'react-router-dom'

const items = [
  { to: '/', label: 'Dashboard', index: '01' },
  { to: '/workspaces', label: 'Workspaces', index: '02' },
  { to: '/documents', label: 'Documents', index: '03' },
  { to: '/search', label: 'Search', index: '04' },
  { to: '/chat', label: 'AI Chat', index: '05' },
  { to: '/settings', label: 'Settings', index: '06' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav" aria-label="Primary">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <span>{item.label}</span>
            <span className="nav-index">{item.index}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}