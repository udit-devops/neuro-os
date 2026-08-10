import React, {useEffect, useState, useRef} from 'react'
import {useParams} from 'react-router-dom'
import {getWorkspace} from '../api/workspaces'
import {listDocuments, uploadDocument, getDocument} from '../api/documents'
import DocumentRow from '../components/DocumentRow'

export default function WorkspaceDetail(){
  const {"*": rest, workspaceId} = useParams() as any
  const id = parseInt(useParams().workspaceId || '')
  const [workspace,setWorkspace] = useState<any>(null)
  const [docs,setDocs] = useState<any[]>([])
  const [file,setFile] = useState<File | null>(null)
  const [uploadProgress,setUploadProgress] = useState<number | null>(null)
  const pollingRef = useRef<Record<number, number>>({})

  useEffect(()=>{
    if(!id) return
    getWorkspace(id).then(setWorkspace).catch(()=>{})
    listDocuments(id).then(setDocs).catch(()=>setDocs([]))
  },[id])

  async function handleUpload(e:React.FormEvent){
    e.preventDefault()
    if(!file || !id) return
    setUploadProgress(0)
    try{
      const newDoc = await uploadDocument(id,file,undefined,(p)=>{
        setUploadProgress(p)
      } as any)
      setDocs(prev=>[newDoc,...prev])
      // start polling this document until completed/failed
      pollDocumentStatus(id, newDoc.id)
    }catch(err){
      alert('Upload failed')
    }finally{
      setFile(null)
      setUploadProgress(null)
    }
  }

  function pollDocumentStatus(workspaceId:number, documentId:number){
    // avoid duplicate polling
    if(pollingRef.current[documentId]) return
    const interval = window.setInterval(async ()=>{
      try{
        const doc = await getDocument(workspaceId, documentId)
        setDocs(prev => prev.map(d => d.id === doc.id ? doc : d))
        if(doc.processing_status === 'COMPLETED' || doc.processing_status === 'FAILED'){
          clearInterval(interval)
          delete pollingRef.current[documentId]
        }
      }catch(e){
        // stop polling on error
        clearInterval(interval)
        delete pollingRef.current[documentId]
      }
    }, 2000)
    pollingRef.current[documentId] = interval
  }

  return (
    <div style={{padding:32}}>
      <h2>{workspace?.name ?? 'Workspace'}</h2>
      <section style={{marginTop:20}}>
        <form onSubmit={handleUpload}>
          <input type="file" onChange={e=>setFile(e.target.files?.[0] ?? null)} />
          <button type="submit">Upload</button>
        </form>
        {uploadProgress !== null && (
          <div style={{marginTop:8,width:320}}>
            <div style={{height:8,background:'#222',borderRadius:6,overflow:'hidden'}}>
              <div style={{width:`${uploadProgress}%`,height:'100%',background:'var(--accent)'}} />
            </div>
            <div style={{color:'var(--muted)',fontSize:12,marginTop:6}}>{uploadProgress}%</div>
          </div>
        )}
      </section>
      <section style={{marginTop:24}}>
        <h3>Documents</h3>
        <div>
          {docs.map(d=> <DocumentRow key={d.id} doc={d} />)}
        </div>
      </section>
    </div>
  )
}
