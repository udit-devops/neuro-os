import { statusLabel } from '../../lib/format'

export default function StatusBadge({ status }: { status: string }) {
  const cls = `status status-${status?.toLowerCase()}`
  return (
    <span className={cls}>
      <span className="status-dot" aria-hidden="true" />
      {statusLabel(status)}
    </span>
  )
}