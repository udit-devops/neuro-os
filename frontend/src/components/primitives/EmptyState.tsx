import React from 'react'

export default function EmptyState({
  title,
  body,
  action,
}: {
  title: string
  body?: string
  action?: React.ReactNode
}) {
  return (
    <div className="state-block">
      <div>
        <div className="h3" style={{ marginBottom: 8 }}>{title}</div>
        {body && <p className="small muted" style={{ margin: 0 }}>{body}</p>}
      </div>
      {action}
    </div>
  )
}