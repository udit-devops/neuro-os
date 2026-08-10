import React from 'react'

export default function Topbar(){
  return (
    <header className="topbar">
      <div className="brand">NEUROOS</div>
      <div className="topbar-actions">
        <div className="search-pill">Search</div>
        <div className="profile-pill">Profile</div>
      </div>
    </header>
  )
}
