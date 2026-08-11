import React, { useEffect, useRef, useState } from 'react'
import { listWorkspaces, type Workspace } from '../api/workspaces'
import { queryWorkspace, type Source } from '../api/rag'
import Button from '../components/primitives/Button'
import SourceCitation from '../components/primitives/SourceCitation'
import EmptyState from '../components/primitives/EmptyState'
import ErrorState from '../components/primitives/ErrorState'
import Spinner from '../components/primitives/Spinner'
import { motion, AnimatePresence } from 'framer-motion'

interface Entry {
  question: string
  answer: string
  sources: Source[]
  noContext: boolean
  ts: number
}

export default function Chat() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [workspaceId, setWorkspaceId] = useState<number | null>(null)
  const [question, setQuestion] = useState('')
  const [entries, setEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    listWorkspaces()
      .then((ws) => {
        setWorkspaces(ws)
        if (ws.length) setWorkspaceId(ws[0].id)
      })
      .catch(() => setError('Could not load workspaces.'))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [entries, loading])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!workspaceId || !question.trim() || loading) return
    const q = question.trim()
    setQuestion('')
    setLoading(true)
    setError(null)
    try {
      const res = await queryWorkspace(workspaceId, q, 5)
      setEntries((prev) => [
        ...prev,
        {
          question: q,
          answer: res.answer,
          sources: res.sources || [],
          noContext: res.sources.length === 0,
          ts: Date.now(),
        },
      ])
    } catch {
      setError('The question could not be answered right now. Check that documents are indexed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <p className="meta">Ask your knowledge</p>
      <h1 className="display" style={{ fontSize: 'var(--font-h1)' }}>
        Ask your knowledge.
      </h1>

      <form onSubmit={submit} className="surface-panel" style={{ marginTop: 32 }}>
        <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr 220px auto' }}>
          <input
            className="ui-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What did we decide about authentication?"
            aria-label="Question"
            autoFocus
          />
          <select className="ui-select" value={workspaceId ?? ''} onChange={(e) => setWorkspaceId(parseInt(e.target.value))}>
            {workspaces.map((w) => (
              <option key={w.id} value={w.id}>{w.name}</option>
            ))}
          </select>
          <Button type="submit" disabled={loading || !question.trim()}>
            Ask
          </Button>
        </div>
      </form>

      {error && <div style={{ marginTop: 24 }}><ErrorState message={error} /></div>}

      <div style={{ marginTop: 40 }}>
        {entries.length === 0 && !error && !loading && (
          <EmptyState
            title="Start a conversation"
            body="Ask a question and NeuroOS will answer from your indexed documents, citing its sources."
          />
        )}

        <AnimatePresence>
          {entries.map((entry) => (
            <motion.article
              key={entry.ts}
              className="chat-source"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
            >
              <div className="meta" style={{ marginBottom: 10 }}>Q</div>
              <h2 className="h3" style={{ marginBottom: 24 }}>{entry.question}</h2>

              <div className="meta" style={{ marginBottom: 10 }}>Answer</div>
              <div className="answer-block">{entry.answer}</div>

              {entry.noContext ? (
                <p className="small muted" style={{ marginTop: 20 }}>
                  No relevant context was found in this workspace for that question.
                </p>
              ) : (
                <>
                  <div className="meta" style={{ margin: '28px 0 12px' }}>Sources</div>
                  {entry.sources.map((s, i) => (
                    <SourceCitation key={`${entry.ts}-${i}`} source={s} index={i} />
                  ))}
                </>
              )}
            </motion.article>
          ))}
        </AnimatePresence>

        {loading && (
          <div style={{ padding: '16px 0' }}>
            <Spinner label="Retrieving and reasoning…" />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </section>
  )
}