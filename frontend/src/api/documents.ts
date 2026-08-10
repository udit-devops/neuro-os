import client from './client'

export async function listDocuments(workspaceId:number){
  const res = await client.get(`/workspaces/${workspaceId}/documents`)
  return res.data
}

export async function uploadDocument(workspaceId:number,file:File,title?:string,onProgress?: (p:number)=>void){
  const fd = new FormData()
  fd.append('file', file)
  if(title) fd.append('title', title)
  const res = await client.post(`/workspaces/${workspaceId}/documents/upload`, fd, {
    headers: {'Content-Type':'multipart/form-data'},
    onUploadProgress: (ev: ProgressEvent) => {
      if(onProgress && ev.total) {
        onProgress(Math.round((ev.loaded / ev.total) * 100))
      }
    }
  })
  return res.data
}

export async function getDocument(workspaceId:number, documentId:number){
  const res = await client.get(`/workspaces/${workspaceId}/documents/${documentId}`)
  return res.data
}
