import React, {useEffect, useState} from 'react'
import {listWorkspaces} from '../api/workspaces'
import {queryWorkspace} from '../api/rag'

export default function Chat(){
  const [workspaces,setWorkspaces] = useState<any[]>([])
  const [workspaceId,setWorkspaceId] = useState<number | null>(null)
  const [question,setQuestion] = useState('')
  const [loading,setLoading] = useState(false)
  const [answer,setAnswer] = useState<string | null>(null)
  const [sources,setSources] = useState<any[]>([])

  useEffect(()=>{
    listWorkspaces().then(ws=>{
      setWorkspaces(ws)
      if(ws.length) setWorkspaceId(ws[0].id)
    }).catch(()=>{})
  },[])

  async function submit(e:React.FormEvent){
    e.preventDefault()
    if(!workspaceId || !question) return
    setLoading(true)
    try{
      const res = await queryWorkspace(workspaceId, question, 5)
      setAnswer(res.answer)
      setSources(res.sources || [])
    }catch(err){
      alert('Query failed')
    }finally{setLoading(false)}
  }

  return (
    <div style={{padding:32}}>
      <h2>Ask your knowledge</h2>
      <form onSubmit={submit} style={{marginTop:12}}>
        <div style={{display:'flex',gap:12,alignItems:'center'}}>
          <select value={workspaceId ?? ''} onChange={e=>setWorkspaceId(parseInt(e.target.value))}>
            {workspaces.map(w=> <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
          <input style={{flex:1}} value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask a question..." />
          <button disabled={loading} type="submit">Ask</button>
        </div>
      </form>

      {loading && <div style={{marginTop:12,color:'var(--muted)'}}>Thinking…</div>}

      {answer && (
        <article style={{marginTop:24,background:'var(--surface)',padding:20,borderRadius:10}}>
          <h3>Answer</h3>
          <div style={{whiteSpace:'pre-wrap',marginTop:8}}>{answer}</div>
          <h4 style={{marginTop:12}}>Sources</h4>
          <ul>
            {sources.map((s:any,idx:number)=> (
              <li key={idx}>{s.title} — Chunk {s.chunk_index} — score {Math.round(s.score*100)/100}</li>
            ))}
          </ul>
        </article>
      )}
    </div>
  )
}
