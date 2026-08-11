import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { listWorkspaces, type Workspace } from '../api/workspaces'
import { listDocuments, type Document } from '../api/documents'
import EmptyState from '../components/primitives/EmptyState'
import Button from '../components/primitives/Button'
import Spinner from '../components/primitives/Spinner'

export default function Dashboard() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [docCount, setDocCount] = useState(0)
  const [processed, setProcessed] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const ws = await listWorkspaces()
        if (cancelled) return
        setWorkspaces(ws)
        let docs = 0
        let done = 0
        await Promise.all(
          ws.map(async (w) => {
            const list: Document[] = await listDocuments(w.id)
            docs += list.length
            done += list.filter((d) => d.processing_status === 'COMPLETED').length
          })
        )
        if (!cancelled) {
          setDocCount(docs)
          setProcessed(done)
        }
      } catch {
        /* noop */
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section>
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <p className="meta">
          NeuroOS / Second Brain
        </p>
        <h1 className="display">
          Your knowledge.
          <br />
          <span className="accent-text">Connected.</span>
        </h1>
        <p className="lead" style={{ marginTop: 16 }}>
          Upload documents into workspaces, let NeuroOS index them, then ask questions
          about everything you know — answered with sources.
        </p>

        <div className="grid-stats">
          <div className="stat-card">
            <div className="meta">Workspaces</div>
            <div className="stat-value">{workspaces.length}</div>
          </div>
          <div className="stat-card">
            <div className="meta">Documents</div>
            <div className="stat-value">{docCount}</div>
          </div>
          <div className="stat-card">
            <div className="meta">Indexed</div>
            <div className="stat-value">
              {processed}
              <span className="small faint" style={{ marginLeft: 6 }}>
                / {docCount || 0}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      <hr className="divider" />

      {loading ? (
        <div style={{ padding: '48px 0' }}>
          <Spinner label="Loading your knowledge…" />
        </div>
      ) : workspaces.length === 0 ? (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <h2 className="h2" style={{ marginBottom: 20 }}>Get started</h2>
          <EmptyState
            title="Create your first workspace"
            body="A workspace is a container for documents. Create one to start building your knowledge base."
            action={
              <Link to="/workspaces">
                <Button variant="primary">Create workspace</Button>
              </Link>
            }
          />
        </motion.div>
      ) : (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 20 }}>
            <h2 className="h2">Workspaces</h2>
            <Link to="/workspaces" className="small muted" style={{ textDecoration: 'none' }}>
              View all →
            </Link>
          </div>
          <div className="grid-workspaces">
            {workspaces.slice(0, 4).map((w) => (
              <motion.div key={w.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                <Link to={`/workspaces/${w.id}`} className="workspace-card">
                  <div className="meta" style={{ marginBottom: 10 }}>Workspace</div>
                  <div className="workspace-name">{w.name}</div>
                  <div className="small muted" style={{ marginTop: 12 }}>
                    {w.document_count} documents
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </section>
  )
}