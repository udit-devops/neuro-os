import React, {useEffect, useState} from 'react'
import {listWorkspaces} from '../api/workspaces'
import {listDocuments} from '../api/documents'

export default function Documents(){
  const [workspaces,setWorkspaces] = useState<any[]>([])
  const [workspaceId,setWorkspaceId] = useState<number | null>(null)
  const [docs,setDocs] = useState<any[]>([])

  useEffect(()=>{
    listWorkspaces().then(ws=>{
      setWorkspaces(ws)
      if(ws.length) setWorkspaceId(ws[0].id)
    }).catch(()=>{})
  },[])

  useEffect(()=>{
    if(!workspaceId) return
    listDocuments(workspaceId).then(setDocs).catch(()=>setDocs([]))
  },[workspaceId])

  return (
    <div style={{padding:32}}>
      <h2>Documents</h2>
      <div style={{marginTop:12,display:'flex',gap:12,alignItems:'center'}}>
        <select value={workspaceId ?? ''} onChange={e=>setWorkspaceId(parseInt(e.target.value))}>
          {workspaces.map(w=> <option key={w.id} value={w.id}>{w.name}</option>)}
        </select>
      </div>
      <div style={{marginTop:20}}>
        {docs.map(d=> (
          <div key={d.id} style={{padding:12,background:'var(--surface)',borderRadius:8,marginBottom:8}}>
            <div style={{display:'flex',justifyContent:'space-between'}}>
              <div>
                <div style={{fontWeight:700}}>{d.title}</div>
                <div style={{color:'var(--muted)'}}>{d.original_filename} · {Math.round(d.file_size/1024)} KB</div>
              </div>
              <div style={{alignSelf:'center'}}>
                <span className={`status status-${d.processing_status?.toLowerCase()}`}>{d.processing_status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
