import React from 'react'

export default function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}) {
  return (
    <div className="state-block" style={{ borderColor: 'rgba(255,107,107,0.4)' }}>
      <div>
        <div className="h3" style={{ color: 'var(--danger)', marginBottom: 8 }}>Something went wrong</div>
        <p className="small muted" style={{ margin: 0 }}>{message}</p>
      </div>
      {onRetry && (
        <button className="btn btn-ghost" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}