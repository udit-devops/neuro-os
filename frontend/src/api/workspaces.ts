import client from './client'

export async function listWorkspaces(){
  const res = await client.get('/workspaces')
  return res.data
}

export async function getWorkspace(id:number){
  const res = await client.get(`/workspaces/${id}`)
  return res.data
}

export async function createWorkspace(data:{name:string}){
  const res = await client.post('/workspaces', data)
  return res.data
}
