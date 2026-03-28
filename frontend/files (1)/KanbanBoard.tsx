'use client'
// components/KanbanBoard.tsx
// Kanban board with To Do / In Progress / Done columns

import { useState } from 'react'
import { Task } from '@/lib/api'
import TaskCard from './TaskCard'
import { Plus } from 'lucide-react'

interface Props {
  tasks: Task[]
  onTaskUpdate?: (id: number, status: Task['status']) => void
}

const COLUMNS: { id: Task['status']; label: string; color: string; accent: string }[] = [
  { id: 'todo',        label: 'To Do',       color: 'var(--muted)',  accent: 'var(--border)'  },
  { id: 'in_progress', label: 'In Progress', color: 'var(--accent)', accent: 'rgba(0,229,255,0.12)' },
  { id: 'done',        label: 'Done',        color: 'var(--green)',  accent: 'rgba(0,255,136,0.08)' },
]

export default function KanbanBoard({ tasks, onTaskUpdate }: Props) {
  const [localTasks, setLocalTasks] = useState(tasks)

  const handleUpdate = (id: number, status: Task['status']) => {
    setLocalTasks(prev => prev.map(t => t.id === id ? { ...t, status } : t))
    onTaskUpdate?.(id, status)
  }

  return (
    <div className="grid grid-cols-3 gap-4 h-full">
      {COLUMNS.map(col => {
        const colTasks = localTasks.filter(t => t.status === col.id)
        return (
          <div
            key={col.id}
            className="kanban-col flex flex-col"
            style={{ background: col.accent }}
          >
            {/* Column header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold" style={{ color: col.color, fontFamily: 'Syne, sans-serif' }}>
                  {col.label}
                </span>
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{ background: `${col.color}18`, color: col.color, fontFamily: 'JetBrains Mono, monospace' }}
                >
                  {colTasks.length}
                </span>
              </div>
              <button style={{ color: 'var(--muted)' }}>
                <Plus size={14} />
              </button>
            </div>

            {/* Divider */}
            <div
              className="h-px mb-4"
              style={{ background: `linear-gradient(90deg, ${col.color}40, transparent)` }}
            />

            {/* Tasks */}
            <div className="flex-1 overflow-y-auto pr-0.5">
              {colTasks.length === 0 ? (
                <div
                  className="flex items-center justify-center h-20 rounded-lg border border-dashed text-sm"
                  style={{ borderColor: 'var(--border)', color: 'var(--muted)' }}
                >
                  No tasks here
                </div>
              ) : (
                colTasks.map(task => (
                  <TaskCard key={task.id} task={task} onUpdate={handleUpdate} />
                ))
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
