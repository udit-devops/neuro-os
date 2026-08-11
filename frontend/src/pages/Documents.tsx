import React, { useEffect, useState } from 'react'
import { listWorkspaces, type Workspace } from '../api/workspaces'
import { listDocuments, type Document } from '../api/documents'
import DocumentRow from '../components/DocumentRow'
import EmptyState from '../components/primitives/EmptyState'
import ErrorState from '../components/primitives/ErrorState'
import Spinner from '../components/primitives/Spinner'

export default function Documents() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [workspaceId, setWorkspaceId] = useState<number | null>(null)
  const [workspaceNames, setWorkspaceNames] = useState<Record<number, string>>({})
  const [docs, setDocs] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      try {
        const ws = await listWorkspaces()
        setWorkspaces(ws)
        setWorkspaceNames(Object.fromEntries(ws.map((w) => [w.id, w.name])))
        if (ws.length) setWorkspaceId(ws[0].id)
      } catch {
        setError('Could not load workspaces.')
      }
    })()
  }, [])

  useEffect(() => {
    if (workspaceId === null) {
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    listDocuments(workspaceId)
      .then((d) => setDocs(d))
      .catch(() => setError('Could not load documents.'))
      .finally(() => setLoading(false))
  }, [workspaceId])

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 40 }}>
        <div>
          <p className="meta">Documents</p>
          <h1 className="h1">All indexed files</h1>
        </div>
        {workspaces.length > 1 && (
          <label>
            <span className="ui-label">Workspace</span>
            <select className="ui-select" value={workspaceId ?? ''} onChange={(e) => setWorkspaceId(parseInt(e.target.value))}>
              {workspaces.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
          </label>
        )}
      </div>

      {error && <ErrorState message={error} onRetry={() => workspaceId && listDocuments(workspaceId).then(setDocs)} />}

      {loading ? (
        <Spinner label="Loading documents…" />
      ) : docs.length === 0 ? (
        <EmptyState
          title="No documents in this workspace"
          body="Upload a document from the workspace page to begin indexing."
        />
      ) : (
        docs.map((doc) => (
          <DocumentRow key={doc.id} doc={doc} workspaceName={workspaceNames[doc.workspace_id]} />
        ))
      )}
    </section>
  )
}