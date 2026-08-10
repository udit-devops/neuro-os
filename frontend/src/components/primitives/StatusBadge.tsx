import React from 'react'

export default function StatusBadge({status}:{status:string}){
  const cls = `status status-${status?.toLowerCase()}`
  return <span className={cls}>{status}</span>
}
