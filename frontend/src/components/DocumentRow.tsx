import React from 'react'
import StatusBadge from './primitives/StatusBadge'

export default function DocumentRow({doc}:{doc:any}){
  return (
    <div className="doc-row">
      <div className="doc-main">
        <div className="doc-title">{doc.title}</div>
        <div className="doc-meta">{doc.original_filename} · {Math.round(doc.file_size/1024)} KB</div>
      </div>
      <div className="doc-status">
        <StatusBadge status={doc.processing_status} />
      </div>
    </div>
  )
}
