'use client'
// app/page.tsx — Dashboard home page

import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import StatsGrid from '@/components/StatsGrid'
import KanbanBoard from '@/components/KanbanBoard'
import AIInputBox from '@/components/AIInputBox'
import RiskAlert from '@/components/RiskAlert'
import { MOCK_TASKS, MOCK_PROJECTS, MOCK_AGENTS, AgentLog } from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { RefreshCw, ExternalLink } from 'lucide-react'

const VELOCITY_DATA = [
  { sprint: 'S1', planned: 20, actual: 18 },
  { sprint: 'S2', planned: 22, actual: 21 },
  { sprint: 'S3', planned: 25, actual: 19 },
  { sprint: 'S4', planned: 24, actual: 16 },
]

const BURNDOWN = [
  { day: 'D1', remaining: 24 },
  { day: 'D2', remaining: 22 },
  { day: 'D3', remaining: 19 },
  { day: 'D4', remaining: 17 },
  { day: 'D5', remaining: 15 },
  { day: 'D6', remaining: 14 },
  { day: 'D7', remaining: 10 },
]

const LOG_COLORS = {
  success: 'var(--green)',
  warning: 'var(--yellow)',
  error:   'var(--red)',
  info:    'var(--accent)',
}

export default function Dashboard() {
  const [time, setTime] = useState('')
  const [logs] = useState<AgentLog[]>(MOCK_AGENTS)

  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('en-US', { hour12: false }))
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="flex min-h-screen grid-bg" style={{ background: 'var(--bg)' }}>
      <Sidebar />

      {/* Main content */}
      <main className="ml-56 flex-1 p-6 overflow-y-auto">
        {/* Top bar */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1
              className="text-xl font-bold"
              style={{ fontFamily: 'Syne, sans-serif', color: 'var(--text)' }}
            >
              Mission Control
            </h1>
            <p className="text-sm mt-0.5" style={{ color: 'var(--text-dim)' }}>
              Code Apex · Quadra Elites · Sprint 4
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span
              className="text-sm tabular-nums"
              style={{ color: 'var(--accent)', fontFamily: 'JetBrains Mono, monospace' }}
            >
              {time}
            </span>
            <button
              className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs"
              style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-dim)' }}
            >
              <RefreshCw size={12} />
              Sync
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="mb-6">
          <StatsGrid />
        </div>

        {/* AI Input */}
        <div className="mb-6">
          <AIInputBox projectId={1} />
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-3 gap-6 mb-6">
          {/* Kanban — spans 2 cols */}
          <div className="col-span-2">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--text)' }}>
                Sprint Board — AI PM Boss Core
              </span>
              <span className="text-xs" style={{ color: 'var(--text-dim)', fontFamily: 'JetBrains Mono, monospace' }}>
                6 tasks
              </span>
            </div>
            <KanbanBoard tasks={MOCK_TASKS.filter(t => t.project_id === 1)} />
          </div>

          {/* Risk alerts */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--text)' }}>
                Risk Alerts
              </span>
              <span
                className="text-xs px-2 py-0.5 rounded"
                style={{ background: 'rgba(255,64,96,0.1)', color: 'var(--red)', fontFamily: 'JetBrains Mono, monospace' }}
              >
                2 active
              </span>
            </div>
            <RiskAlert />
          </div>
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Velocity chart */}
          <div className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-semibold" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--text)' }}>
                Sprint Velocity
              </span>
              <div className="flex items-center gap-3 text-xs" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                <span style={{ color: 'var(--accent)' }}>■ Planned</span>
                <span style={{ color: 'var(--green)' }}>■ Actual</span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={150}>
              <BarChart data={VELOCITY_DATA} barGap={4}>
                <XAxis dataKey="sprint" tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }}
                  labelStyle={{ color: 'var(--text)' }}
                  itemStyle={{ color: 'var(--accent)' }}
                />
                <Bar dataKey="planned" fill="rgba(0,229,255,0.25)" radius={[3,3,0,0]} />
                <Bar dataKey="actual"  fill="var(--green)"           radius={[3,3,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Burndown chart */}
          <div className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-semibold" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--text)' }}>
                Sprint Burndown
              </span>
              <span className="text-xs" style={{ color: 'var(--text-dim)', fontFamily: 'JetBrains Mono, monospace' }}>
                10 tasks remaining
              </span>
            </div>
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={BURNDOWN}>
                <XAxis dataKey="day" tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'JetBrains Mono' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 12 }}
                  labelStyle={{ color: 'var(--text)' }}
                  itemStyle={{ color: 'var(--accent)' }}
                />
                <Line type="monotone" dataKey="remaining" stroke="var(--accent)" strokeWidth={2} dot={{ fill: 'var(--accent)', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Agent Activity Log */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-semibold" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--text)' }}>
              Agent Activity Log
            </span>
            <button className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-dim)' }}>
              View all <ExternalLink size={11} />
            </button>
          </div>
          <div className="space-y-2">
            {logs.map((log, i) => (
              <div key={i} className="flex items-start gap-3 py-1.5 border-b" style={{ borderColor: 'var(--border)' }}>
                <span
                  className="text-xs flex-shrink-0 tabular-nums"
                  style={{ color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace', minWidth: 64 }}
                >
                  {log.timestamp}
                </span>
                <span
                  className="text-xs flex-shrink-0"
                  style={{ color: LOG_COLORS[log.type], fontFamily: 'JetBrains Mono, monospace', minWidth: 110 }}
                >
                  [{log.agent}]
                </span>
                <span className="text-xs" style={{ color: 'var(--text-dim)' }}>
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
