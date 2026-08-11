import client from './client'

export interface Workspace {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
  owner_id: number
  document_count: number
}

export async function listWorkspaces(): Promise<Workspace[]> {
  const res = await client.get('/workspaces')
  return res.data
}

export async function getWorkspace(id: number): Promise<Workspace> {
  const res = await client.get(`/workspaces/${id}`)
  return res.data
}

export async function createWorkspace(data: { name: string; description?: string }): Promise<Workspace> {
  const res = await client.post('/workspaces', data)
  return res.data
}

export async function deleteWorkspace(id: number): Promise<{ message: string }> {
  const res = await client.delete(`/workspaces/${id}`)
  return res.data
}