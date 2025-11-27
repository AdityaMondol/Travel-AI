
import { Link, useLocation } from 'react-router-dom'
import { Home, Zap, Workflow, MessageSquare, BarChart3, Settings } from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { icon: Home, label: 'Dashboard', path: '/' },
  { icon: Zap, label: 'Agents', path: '/agents' },
  { icon: Workflow, label: 'Workflows', path: '/workflows' },
  { icon: MessageSquare, label: 'Chat', path: '/chat' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
]

const bottomItems = [
  { icon: Settings, label: 'Settings', path: '/settings' },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 border-r border-neutral-200 bg-white flex flex-col">
      <div className="p-6 border-b border-neutral-200">
        <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-4">Navigation</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                'flex items-center gap-3 px-4 py-2.5 rounded-sm text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-neutral-100 text-neutral-900 border-r-2 border-neutral-900'
                  : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'
              )}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-neutral-200 px-3 py-4 space-y-1">
        <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider px-4 mb-3">Account</p>
        {bottomItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                'flex items-center gap-3 px-4 py-2.5 rounded-sm text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-neutral-100 text-neutral-900'
                  : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50'
              )}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </div>
    </aside>
  )
}
