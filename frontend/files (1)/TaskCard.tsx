'use client'
// components/TaskCard.tsx
// A single task card for the Kanban board

import { Task } from '@/lib/api'
import { MoreHorizontal, User, Flag } from 'lucide-react'

interface Props {
  task: Task
  onUpdate?: (id: number, status: Task['status']) => void
}

const PRIORITY_COLORS: Record<string, string> = {
  high:   'var(--red)',
  medium: 'var(--yellow)',
  low:    'var(--green)',
}

export default function TaskCard({ task, onUpdate }: Props) {
  const priColor = PRIORITY_COLORS[task.priority] || 'var(--muted)'

  return (
    <div
      className="card p-3 mb-3 cursor-grab active:cursor-grabbing group"
      draggable
    >
      {/* Priority flag + overflow menu */}
      <div className="flex items-center justify-between mb-2">
        <span className={`badge badge-${task.priority}`}>
          <Flag size={9} />
          {task.priority}
        </span>
        <button
          className="opacity-0 group-hover:opacity-100 transition-opacity"
          style={{ color: 'var(--text-dim)' }}
        >
          <MoreHorizontal size={14} />
        </button>
      </div>

      {/* Title */}
      <p className="text-sm font-medium mb-3 leading-snug" style={{ color: 'var(--text)' }}>
        {task.title}
      </p>

      {/* Footer: assignee + ID */}
      <div className="flex items-center justify-between">
        {task.assignee_name ? (
          <div className="flex items-center gap-1.5">
            <div
              className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold"
              style={{ background: `${priColor}20`, color: priColor, border: `1px solid ${priColor}40` }}
            >
              {task.assignee_name.charAt(0)}
            </div>
            <span className="text-xs" style={{ color: 'var(--text-dim)' }}>
              {task.assignee_name}
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-1" style={{ color: 'var(--muted)' }}>
            <User size={11} />
            <span className="text-xs">Unassigned</span>
          </div>
        )}

        <span
          className="text-xs"
          style={{ color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}
        >
          #{task.id.toString().padStart(3, '0')}
        </span>
      </div>

      {/* Move buttons */}
      {onUpdate && (
        <div className="mt-3 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {task.status !== 'todo' && (
            <button
              onClick={() => onUpdate(task.id, task.status === 'done' ? 'in_progress' : 'todo')}
              className="text-xs px-2 py-0.5 rounded"
              style={{ background: 'var(--border)', color: 'var(--text-dim)' }}
            >
              ← Back
            </button>
          )}
          {task.status !== 'done' && (
            <button
              onClick={() => onUpdate(task.id, task.status === 'todo' ? 'in_progress' : 'done')}
              className="text-xs px-2 py-0.5 rounded"
              style={{ background: 'rgba(0,229,255,0.1)', color: 'var(--accent)' }}
            >
              Forward →
            </button>
          )}
        </div>
      )}
    </div>
  )
}
