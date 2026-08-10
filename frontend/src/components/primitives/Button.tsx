import React from 'react'

export default function Button({children,onClick,variant='primary'}:{children:React.ReactNode,onClick?:()=>void,variant?:'primary'|'ghost'}){
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>{children}</button>
  )
}
