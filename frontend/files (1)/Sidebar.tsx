'use client'
// components/Sidebar.tsx
// Fixed left sidebar with navigation and system status

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, FolderKanban, CheckSquare,
  FileText, Zap, Settings, Bot, Activity
} from 'lucide-react'

const NAV = [
  { href: '/',          icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/projects',  icon: FolderKanban,    label: 'Projects'  },
  { href: '/tasks',     icon: CheckSquare,     label: 'Tasks'     },
  { href: '/reports',   icon: FileText,        label: 'Reports'   },
  { href: '/agents',    icon: Bot,             label: 'Agents'    },
]

const AGENTS_STATUS = [
  { name: 'TaskCreator',    active: true  },
  { name: 'PRMapper',       active: true  },
  { name: 'DelayPredictor', active: false },
  { name: 'ReportGen',      active: true  },
  { name: 'StandupBot',     active: true  },
]

export default function Sidebar() {
  const path = usePathname()

  return (
    <aside
      style={{ background: 'var(--surface)', borderRight: '1px solid var(--border)' }}
      className="fixed left-0 top-0 bottom-0 w-56 flex flex-col z-20"
    >
      {/* Logo */}
      <div className="px-5 py-5 border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center gap-2">
          <div
            className="w-7 h-7 rounded flex items-center justify-center"
            style={{ background: 'rgba(0,229,255,0.1)', border: '1px solid rgba(0,229,255,0.3)' }}
          >
            <Zap size={14} color="var(--accent)" />
          </div>
          <div>
            <div
              className="text-sm font-bold tracking-wide"
              style={{ fontFamily: 'Syne, sans-serif', color: 'var(--accent)' }}
            >
              AI PM BOSS
            </div>
            <div className="text-xs" style={{ color: 'var(--text-dim)', fontFamily: 'JetBrains Mono, monospace' }}>
              v1.0 · online
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ href, icon: Icon, label }) => {
          const active = path === href
          return (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-all duration-150"
              style={{
                color: active ? 'var(--accent)' : 'var(--text-dim)',
                background: active ? 'rgba(0,229,255,0.08)' : 'transparent',
                borderLeft: active ? '2px solid var(--accent)' : '2px solid transparent',
                fontWeight: active ? 500 : 400,
              }}
            >
              <Icon size={15} />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Agent Status */}
      <div className="px-4 py-4 border-t" style={{ borderColor: 'var(--border)' }}>
        <div
          className="text-xs mb-3 flex items-center gap-2"
          style={{ color: 'var(--text-dim)', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.08em' }}
        >
          <Activity size={11} />
          AGENTS
        </div>
        {AGENTS_STATUS.map(a => (
          <div key={a.name} className="flex items-center justify-between py-1">
            <span className="text-xs" style={{ color: 'var(--text-dim)', fontFamily: 'JetBrains Mono, monospace' }}>
              {a.name}
            </span>
            <span
              className="text-xs"
              style={{
                color: a.active ? 'var(--green)' : 'var(--muted)',
                fontFamily: 'JetBrains Mono, monospace',
              }}
            >
              {a.active ? '● RUN' : '○ OFF'}
            </span>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t" style={{ borderColor: 'var(--border)' }}>
        <div className="flex items-center justify-between">
          <div className="text-xs" style={{ color: 'var(--text-dim)' }}>
            <span className="font-medium" style={{ color: 'var(--text)' }}>Sofi Faiz Ahmed</span>
            <br />Team Lead · PM
          </div>
          <button className="p-1.5 rounded" style={{ color: 'var(--muted)' }}>
            <Settings size={14} />
          </button>
        </div>
      </div>
    </aside>
  )
}
