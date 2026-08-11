import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { listWorkspaces, createWorkspace, deleteWorkspace, type Workspace } from '../api/workspaces'
import Button from '../components/primitives/Button'
import Input from '../components/primitives/Input'
import Modal from '../components/primitives/Modal'
import EmptyState from '../components/primitives/EmptyState'
import ErrorState from '../components/primitives/ErrorState'
import Spinner from '../components/primitives/Spinner'

export default function Workspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState<Workspace | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setWorkspaces(await listWorkspaces())
    } catch {
      setError('Could not load workspaces.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    setCreating(true)
    try {
      const created = await createWorkspace({ name: name.trim(), description: description.trim() || undefined })
      setWorkspaces((prev) => [created, ...prev])
      setModalOpen(false)
      setName('')
      setDescription('')
    } catch {
      setError('Could not create workspace.')
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete() {
    if (!confirmDelete) return
    try {
      await deleteWorkspace(confirmDelete.id)
      setWorkspaces((prev) => prev.filter((w) => w.id !== confirmDelete.id))
    } catch {
      setError('Could not delete workspace.')
    } finally {
      setConfirmDelete(null)
    }
  }

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 40 }}>
        <div>
          <p className="meta">Workspaces</p>
          <h1 className="h1">Your knowledge bases</h1>
        </div>
        <Button onClick={() => setModalOpen(true)}>+ New workspace</Button>
      </div>

      {error && <ErrorState message={error} onRetry={load} />}

      {loading ? (
        <div style={{ padding: '40px 0' }}>
          <Spinner label="Loading…" />
        </div>
      ) : workspaces.length === 0 && !error ? (
        <EmptyState
          title="No workspaces yet"
          body="Workspaces group related documents. Create one to start building your second brain."
          action={<Button onClick={() => setModalOpen(true)}>Create workspace</Button>}
        />
      ) : (
        <div className="grid-workspaces">
          {workspaces.map((w, i) => (
            <motion.div
              key={w.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
            >
              <motion.div whileHover={{ y: -5, scale: 1.01 }} transition={{ type: 'spring', stiffness: 280, damping: 22 }}>
                <Link to={`/workspaces/${w.id}`} className="workspace-card">
                  <div className="meta" style={{ marginBottom: 12 }}>
                    Workspace · {String(w.id).padStart(3, '0')}
                  </div>
                  <div className="workspace-name">{w.name}</div>
                  {w.description && (
                    <p className="small muted" style={{ margin: '10px 0 0' }}>
                      {w.description}
                    </p>
                  )}
                  <div className="small muted" style={{ marginTop: 16 }}>
                    {w.document_count} documents
                  </div>
                </Link>
              </motion.div>
            </motion.div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} title="New workspace" onClose={() => setModalOpen(false)}>
        <form onSubmit={handleCreate} style={{ display: 'grid', gap: 16 }}>
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Research" autoFocus required />
          <div>
            <label className="ui-label">Description</label>
            <textarea
              className="ui-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What lives in this workspace?"
              rows={3}
            />
          </div>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
            <Button variant="ghost" type="button" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={creating || !name.trim()}>
              {creating ? 'Creating…' : 'Create'}
            </Button>
          </div>
        </form>
      </Modal>

      <Modal open={!!confirmDelete} title="Delete workspace" onClose={() => setConfirmDelete(null)}>
        <p className="small muted" style={{ margin: '0 0 20px' }}>
          Delete <strong style={{ color: 'var(--text)' }}>{confirmDelete?.name}</strong>? Its documents and
          indexed chunks will be removed. This cannot be undone.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <Button variant="ghost" onClick={() => setConfirmDelete(null)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete
          </Button>
        </div>
      </Modal>
    </section>
  )
}