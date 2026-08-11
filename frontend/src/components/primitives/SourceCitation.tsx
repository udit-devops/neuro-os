import { motion } from 'framer-motion'
import type { Source } from '../../api/rag'

export default function SourceCitation({ source, index }: { source: Source; index: number }) {
  return (
    <motion.article
      className="chat-source"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.3, ease: 'easeOut' }}
    >
      <div className="chat-source-head">
        <div className="meta">
          [{index + 1}] {source.title}
        </div>
        <span className="pill">{source.chunk_index} · {Math.round(source.score * 100)}%</span>
      </div>
      <p className="doc-meta" style={{ margin: '0 0 8px' }}>
        Document {source.document_id}
        <span className="doc-meta-sep">/</span>
      </p>
      <p className="chat-source-content">
        {source.content.length > 220 ? `${source.content.slice(0, 220)}…` : source.content}
      </p>
    </motion.article>
  )
}