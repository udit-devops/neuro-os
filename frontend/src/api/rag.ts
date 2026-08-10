import client from './client'

export async function queryWorkspace(workspaceId:number, question:string, top_k=5){
  const res = await client.post(`/workspaces/${workspaceId}/query`, {question, top_k})
  return res.data
}
