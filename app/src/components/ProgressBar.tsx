export function ProgressBar({ percent, label }: { percent: number; label?: string }) {
  return (
    <div className="progress" role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
      <span style={{ width: `${Math.max(0, Math.min(100, percent))}%` }} />
    </div>
  )
}
