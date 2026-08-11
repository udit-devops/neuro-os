import client from './client'
import type { AxiosProgressEvent } from 'axios'

export type ProcessingStatus = 'UPLOADED' | 'PROCESSING' | 'COMPLETED' | 'FAILED'

export interface Document {
  id: number
  title: string
  original_filename: string
  file_path: string
  file_size: number
  file_type: string | null
  workspace_id: number
  processing_status: ProcessingStatus
  error_message: string | null
  processing_started_at: string | null
  processing_completed_at: string | null
  chunk_count: number
  created_at: string
  updated_at: string
}

export async function listDocuments(workspaceId: number): Promise<Document[]> {
  const res = await client.get(`/workspaces/${workspaceId}/documents`)
  return res.data
}

export async function uploadDocument(
  workspaceId: number,
  file: File,
  title?: string,
  onProgress?: (p: number) => void
): Promise<Document> {
  const fd = new FormData()
  fd.append('file', file)
  if (title) fd.append('title', title)
  const res = await client.post(`/workspaces/${workspaceId}/documents/upload`, fd, {
    onUploadProgress: (ev: AxiosProgressEvent) => {
      if (onProgress && ev.total) {
        onProgress(Math.round((ev.loaded / ev.total) * 100))
      }
    },
  })
  return res.data
}

export async function getDocument(workspaceId: number, documentId: number): Promise<Document> {
  const res = await client.get(`/workspaces/${workspaceId}/documents/${documentId}`)
  return res.data
}

export async function deleteDocument(workspaceId: number, documentId: number): Promise<{ message: string }> {
  const res = await client.delete(`/workspaces/${workspaceId}/documents/${documentId}`)
  return res.data
}