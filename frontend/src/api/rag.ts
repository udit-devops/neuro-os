import client from './client'
import type { Workspace } from './workspaces'

export interface Source {
  document_id: number
  title: string
  chunk_index: number
  content: string
  score: number
}

export interface RAGResponse {
  answer: string
  sources: Source[]
}

export async function queryWorkspace(
  workspaceId: number,
  question: string,
  top_k = 5
): Promise<RAGResponse> {
  const res = await client.post(`/workspaces/${workspaceId}/query`, { question, top_k })
  return res.data
}

export async function searchWorkspace(
  workspaceId: number,
  query: string,
  top_k = 8
): Promise<Source[]> {
  const res = await client.post(`/workspaces/${workspaceId}/search`, {
    question: query,
    top_k,
  })
  return res.data
}

export async function listWorkspacesForPicker(): Promise<Workspace[]> {
  const res = await client.get('/workspaces/')
  return res.data
}