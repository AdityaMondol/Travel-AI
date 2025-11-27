
import { useAuthStore } from '@/store/auth'
import { LogOut, Settings } from 'lucide-react'

export default function Header() {
  const { user, logout } = useAuthStore()

  return (
    <header className="border-b border-neutral-200 bg-white">
      <div className="flex items-center justify-between px-8 py-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-neutral-900 rounded-sm flex items-center justify-center">
            <span className="text-white text-xs font-bold">L</span>
          </div>
          <h1 className="text-lg font-semibold text-neutral-900">Leonore</h1>
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <>
              <div className="text-right">
                <p className="text-sm font-medium text-neutral-900">{user.username}</p>
                <p className="text-xs text-neutral-500">{user.role}</p>
              </div>
              <div className="w-8 h-8 bg-neutral-200 rounded-full flex items-center justify-center text-xs font-semibold text-neutral-700">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <button
                onClick={() => logout()}
                className="btn-ghost"
                title="Logout"
              >
                <LogOut size={18} />
              </button>
              <button className="btn-ghost" title="Settings">
                <Settings size={18} />
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
