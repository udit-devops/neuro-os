import React, {useEffect, useState} from 'react'
import {listWorkspaces} from '../api/workspaces'
import Card from '../components/primitives/Card'
import {Link} from 'react-router-dom'

export default function Workspaces(){
  const [items,setItems] = useState<any[]>([])
  useEffect(()=>{
    listWorkspaces().then(setItems).catch(()=>setItems([]))
  },[])

  return (
    <div style={{padding:32}}>
      <h2>Workspaces</h2>
      <div style={{display:'flex',gap:20,flexWrap:'wrap'}}>
        {items.map(w=> (
          <Link key={w.id} to={`/workspaces/${w.id}`} style={{textDecoration:'none'}}>
            <Card style={{width:260,padding:20}}>
              <div style={{fontSize:20,fontWeight:700}}>{w.name}</div>
              <div style={{color:'var(--muted)',marginTop:8}}>{w.document_count ?? 0} documents</div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
