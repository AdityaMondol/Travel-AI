import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  icon: LucideIcon
  label: string
  value: string | number
  change?: {
    value: number
    direction: 'up' | 'down'
  }
}

export default function StatCard({
  icon: Icon,
  label,
  value,
  change,
}: StatCardProps) {
  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div className="w-10 h-10 bg-neutral-100 rounded-sm flex items-center justify-center text-neutral-600">
          <Icon size={20} />
        </div>
        {change && (
          <span className={`text-xs font-semibold ${
            change.direction === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {change.direction === 'up' ? '+' : '-'}{Math.abs(change.value)}%
          </span>
        )}
      </div>
      <p className="text-3xl font-bold text-neutral-900 mb-1">{value}</p>
      <p className="text-muted">{label}</p>
    </div>
  )
}
