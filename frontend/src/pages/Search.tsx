import React, { useEffect, useState } from 'react'
import { listWorkspaces, type Workspace } from '../api/workspaces'
import { searchWorkspace, type Source } from '../api/rag'
import Button from '../components/primitives/Button'
import EmptyState from '../components/primitives/EmptyState'
import ErrorState from '../components/primitives/ErrorState'
import Spinner from '../components/primitives/Spinner'
import { motion } from 'framer-motion'

export default function Search() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [workspaceId, setWorkspaceId] = useState<number | null>(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Source[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listWorkspaces()
      .then((ws) => {
        setWorkspaces(ws)
        if (ws.length) setWorkspaceId(ws[0].id)
      })
      .catch(() => setError('Could not load workspaces.'))
  }, [])

  async function run(e?: React.FormEvent) {
    e?.preventDefault()
    if (!query.trim()) return
    if (workspaceId === null) return
    setLoading(true)
    setSearched(false)
    setError(null)
    try {
      const res = await searchWorkspace(workspaceId, query.trim())
      setResults(res)
      setSearched(true)
    } catch {
      setError('Search failed. The index may still be empty.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <p className="meta">Semantic search</p>
      <h1 className="display" style={{ fontSize: 'var(--font-h1)' }}>Search your knowledge</h1>

      <form onSubmit={run} className="surface-panel" style={{ marginTop: 32 }}>
        <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr 200px auto' }}>
          <input
            className="ui-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything across your documents…"
            aria-label="Search query"
          />
          <select className="ui-select" value={workspaceId ?? ''} onChange={(e) => setWorkspaceId(parseInt(e.target.value))}>
            {workspaces.map((w) => (
              <option key={w.id} value={w.id}>{w.name}</option>
            ))}
          </select>
          <Button type="submit" disabled={loading || !query.trim()}>
            Search
          </Button>
        </div>
      </form>

      {loading && (
        <div style={{ padding: '40px 0' }}>
          <Spinner label="Embedding and matching…" />
        </div>
      )}

      {error && <div style={{ marginTop: 24 }}><ErrorState message={error} onRetry={() => run()} /></div>}

      {searched && !loading && !error && (
        <div style={{ marginTop: 32 }}>
          <div className="meta" style={{ marginBottom: 16 }}>
            {results.length} result{results.length === 1 ? '' : 's'} for “{query.trim()}”
          </div>
          {results.length === 0 ? (
            <EmptyState
              title="No matches"
              body="Nothing semantically similar was found. Upload and index documents first, then try again."
            />
          ) : (
            results.map((r, i) => (
              <motion.article
                key={`${r.document_id}-${r.chunk_index}`}
                className="search-result"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="chat-source-head">
                  <div className="meta">[{i + 1}] {r.title}</div>
                  <span className="pill">chunk {r.chunk_index} · {Math.round(r.score * 100)}%</span>
                </div>
                <p className="chat-source-content" style={{ margin: 0 }}>
                  {r.content.length > 320 ? `${r.content.slice(0, 320)}…` : r.content}
                </p>
              </motion.article>
            ))
          )}
        </div>
      )}
    </section>
  )
}