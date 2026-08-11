import React, { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getWorkspace, type Workspace } from '../api/workspaces'
import { listDocuments, uploadDocument, getDocument, deleteDocument, type Document } from '../api/documents'
import DocumentRow from '../components/DocumentRow'
import Button from '../components/primitives/Button'
import EmptyState from '../components/primitives/EmptyState'
import ErrorState from '../components/primitives/ErrorState'
import Spinner from '../components/primitives/Spinner'

const POLL_MS = 2000

export default function WorkspaceDetail() {
  const params = useParams() as { workspaceId?: string }
  const id = params.workspaceId ? parseInt(params.workspaceId) : NaN
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [docs, setDocs] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const pollingRef = useRef<Record<number, number>>({})

  async function load() {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      setWorkspace(await getWorkspace(id))
      setDocs(await listDocuments(id))
    } catch {
      setError('Could not load this workspace.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  function pollDocumentStatus(workspaceId: number, documentId: number) {
    if (pollingRef.current[documentId]) return
    const interval = window.setInterval(async () => {
      try {
        const doc = await getDocument(workspaceId, documentId)
        setDocs((prev) => prev.map((d) => (d.id === doc.id ? doc : d)))
        if (doc.processing_status === 'COMPLETED' || doc.processing_status === 'FAILED') {
          clearInterval(interval)
          delete pollingRef.current[documentId]
        }
      } catch {
        clearInterval(interval)
        delete pollingRef.current[documentId]
      }
    }, POLL_MS)
    pollingRef.current[documentId] = interval
  }

  useEffect(() => {
    return () => {
      Object.values(pollingRef.current).forEach((interval) => clearInterval(interval))
      pollingRef.current = {}
    }
  }, [])

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault()
    if (!file || !id) return
    setUploadError(null)
    setUploadProgress(0)
    try {
      const newDoc = await uploadDocument(id, file, undefined, setUploadProgress)
      setDocs((prev) => [newDoc, ...prev])
      pollDocumentStatus(id, newDoc.id)
    } catch {
      setUploadError('Upload failed. Check the file type or size.')
    } finally {
      setFile(null)
      setUploadProgress(null)
    }
  }

  async function handleDelete(doc: Document) {
    if (!id) return
    try {
      await deleteDocument(id, doc.id)
      setDocs((prev) => prev.filter((d) => d.id !== doc.id))
    } catch {
      setError('Could not delete document.')
    }
  }

  if (loading) {
    return (
      <section style={{ paddingTop: 24 }}>
        <Spinner label="Loading workspace…" />
      </section>
    )
  }

  if (error || !workspace) {
    return <ErrorState message={error ?? 'Workspace not found.'} onRetry={load} />
  }

  return (
    <section>
      <p className="meta">Workspace / {String(workspace.id).padStart(3, '0')}</p>
      <h1 className="h1">{workspace.name}</h1>
      {workspace.description && <p className="lead" style={{ marginTop: 12 }}>{workspace.description}</p>}

      <div className="surface-panel" style={{ marginTop: 40 }}>
        <div className="meta" style={{ marginBottom: 16 }}>Ingest document</div>
        <form onSubmit={handleUpload}>
          <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr auto' }}>
            <input
              type="file"
              className="ui-input"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              accept=".pdf,.txt,.md,.docx,text/plain,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              aria-label="Choose document"
            />
            <Button type="submit" disabled={!file || uploadProgress !== null}>
              {uploadProgress !== null ? 'Uploading…' : 'Upload'}
            </Button>
          </div>
          {uploadProgress !== null && (
            <div style={{ marginTop: 14 }}>
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
              </div>
              <div className="mono small faint" style={{ marginTop: 6 }}>{uploadProgress}%</div>
            </div>
          )}
          {uploadError && (
            <p className="small" style={{ color: 'var(--danger)', margin: '10px 0 0' }}>{uploadError}</p>
          )}
        </form>
        <p className="small faint" style={{ margin: '10px 0 0' }}>
          PDF, TXT, Markdown, DOCX · unpacked and chunked before embedding
        </p>
      </div>

      <div style={{ marginTop: 48 }}>
        <div className="meta" style={{ marginBottom: 8 }}>Documents</div>
        {docs.length === 0 ? (
          <EmptyState
            title="No documents yet"
            body="Upload a document above to populate this workspace."
          />
        ) : (
          docs.map((doc) => <DocumentRow key={doc.id} doc={doc} onDelete={handleDelete} />)
        )}
      </div>
    </section>
  )
}