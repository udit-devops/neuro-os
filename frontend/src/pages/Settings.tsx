import React, { useEffect, useState } from 'react'
import { listWorkspaces, type Workspace } from '../api/workspaces'
import { listDocuments, type Document } from '../api/documents'
import Spinner from '../components/primitives/Spinner'

export default function Settings() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [docs, setDocs] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      try {
        const ws = await listWorkspaces()
        setWorkspaces(ws)
        let all: Document[] = []
        await Promise.all(
          ws.map(async (w) => {
            all = all.concat(await listDocuments(w.id))
          })
        )
        setDocs(all)
      } catch {
        /* noop */
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const chunks = docs.reduce((sum, d) => sum + d.chunk_count, 0)
  const completed = docs.filter((d) => d.processing_status === 'COMPLETED').length
  const failed = docs.filter((d) => d.processing_status === 'FAILED').length

  return (
    <section>
      <p className="meta">Settings</p>
      <h1 className="h1">System overview</h1>

      {loading ? (
        <div style={{ padding: '40px 0' }}>
          <Spinner label="Loading…" />
        </div>
      ) : (
        <>
          <div className="grid-stats">
            <div className="stat-card">
              <div className="meta">Workspaces</div>
              <div className="stat-value">{workspaces.length}</div>
            </div>
            <div className="stat-card">
              <div className="meta">Documents</div>
              <div className="stat-value">{docs.length}</div>
            </div>
            <div className="stat-card">
              <div className="meta">Indexed chunks</div>
              <div className="stat-value">{chunks}</div>
            </div>
            <div className="stat-card">
              <div className="meta">Indexed documents</div>
              <div className="stat-value">{completed}</div>
            </div>
          </div>

          {failed > 0 && (
            <p className="small" style={{ color: 'var(--warn)', marginTop: 16 }}>
              {failed} document{failed === 1 ? '' : 's'} failed processing.
            </p>
          )}

          <hr className="divider" />

          <div>
            <div className="meta" style={{ marginBottom: 8 }}>Workspaces</div>
            {workspaces.map((w) => (
              <div key={w.id} className="doc-row">
                <div className="doc-main">
                  <div className="doc-title">{w.name}</div>
                  <div className="doc-meta">
                    <span className="mono">id {w.id}</span>
                    <span className="doc-meta-sep">/</span>
                    <span>{w.document_count} documents</span>
                    <span className="doc-meta-sep">/</span>
                    <span>
                      {w.description || 'no description'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  )
}