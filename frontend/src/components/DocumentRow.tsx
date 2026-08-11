import React from 'react'
import StatusBadge from './primitives/StatusBadge'
import { formatBytes, formatDate } from '../lib/format'
import type { Document } from '../api/documents'
import Button from './primitives/Button'

export default function DocumentRow({
  doc,
  workspaceName,
  onDelete,
}: {
  doc: Document
  workspaceName?: string
  onDelete?: (doc: Document) => void
}) {
  return (
    <div className="doc-row">
      <div className="doc-main">
        <div className="doc-title">{doc.title}</div>
        <div className="doc-meta">
          <span className="mono">{doc.file_type ?? 'file'}</span>
          <span className="doc-meta-sep">/</span>
          <span>{formatBytes(doc.file_size)}</span>
          <span className="doc-meta-sep">/</span>
          <span>{doc.chunk_count} chunks</span>
          {workspaceName && (
            <>
              <span className="doc-meta-sep">/</span>
              <span>{workspaceName}</span>
            </>
          )}
          <span className="doc-meta-sep">/</span>
          <span>{formatDate(doc.created_at)}</span>
        </div>
        {doc.error_message && (
          <div className="small" style={{ color: 'var(--danger)', marginTop: 6 }}>
            {doc.error_message}
          </div>
        )}
      </div>
      <div className="doc-actions">
        <StatusBadge status={doc.processing_status} />
        {onDelete && (
          <Button variant="ghost" size="sm" onClick={() => onDelete(doc)} aria-label={`Delete ${doc.title}`}>
            Delete
          </Button>
        )}
      </div>
    </div>
  )
}