export default function Spinner({ label }: { label?: string }) {
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>
      <span className="spinner" aria-hidden="true" />
      {label && <span className="small muted">{label}</span>}
    </div>
  )
}