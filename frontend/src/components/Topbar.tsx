import React from 'react'
import { Link } from 'react-router-dom'

export default function Topbar() {
  return (
    <header className="topbar">
      <Link to="/" className="brand" style={{ textDecoration: 'none' }}>
        NEURO<span className="accent-dot">OS</span>
      </Link>
      <div className="topbar-actions">
        <Link to="/search" className="search-pill">
          <span aria-hidden="true">⌕</span> Search
        </Link>
        <Link to="/settings" className="profile-pill">
          Local
        </Link>
      </div>
    </header>
  )
}