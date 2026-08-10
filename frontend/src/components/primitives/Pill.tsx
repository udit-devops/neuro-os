import React from 'react'

export default function Pill({children,active}:{children:React.ReactNode,active?:boolean}){
  return <span className={`pill ${active? 'pill-active':''}`}>{children}</span>
}
