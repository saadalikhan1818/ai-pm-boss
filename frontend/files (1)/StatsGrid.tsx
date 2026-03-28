'use client'
// components/StatsGrid.tsx
// Top row of metric cards shown on the dashboard

import { TrendingUp, AlertTriangle, CheckCircle2, Users, Zap, Clock } from 'lucide-react'

interface StatCard {
  label: string
  value: string
  sub: string
  color: string
  icon: React.ReactNode
  trend?: string
  trendUp?: boolean
}

const STATS: StatCard[] = [
  {
    label: 'Active Projects',
    value: '4',
    sub: '3 on track · 1 delayed',
    color: 'var(--accent)',
    icon: <Zap size={16} />,
    trend: '+1 this week',
    trendUp: true,
  },
  {
    label: 'Open Tasks',
    value: '23',
    sub: '8 in progress · 15 todo',
    color: 'var(--yellow)',
    icon: <Clock size={16} />,
    trend: '−3 since yesterday',
    trendUp: false,
  },
  {
    label: 'Completed',
    value: '47',
    sub: 'Tasks closed this sprint',
    color: 'var(--green)',
    icon: <CheckCircle2 size={16} />,
    trend: '+12 this week',
    trendUp: true,
  },
  {
    label: 'Risk Alerts',
    value: '2',
    sub: '1 critical · 1 warning',
    color: 'var(--red)',
    icon: <AlertTriangle size={16} />,
  },
  {
    label: 'Team Members',
    value: '8',
    sub: '6 active · 2 idle',
    color: 'var(--purple)',
    icon: <Users size={16} />,
  },
  {
    label: 'AI Tasks Created',
    value: '34',
    sub: 'Auto-generated this week',
    color: 'var(--accent)',
    icon: <TrendingUp size={16} />,
    trend: '+8 vs last week',
    trendUp: true,
  },
]

export default function StatsGrid() {
  return (
    <div className="grid grid-cols-3 gap-4 lg:grid-cols-6">
      {STATS.map((s, i) => (
        <div
          key={i}
          className="card p-4 relative overflow-hidden"
          style={{ animationDelay: `${i * 60}ms`, animation: 'slideUp 0.4s ease-out forwards', opacity: 0 }}
        >
          {/* Accent bar */}
          <div
            className="absolute top-0 left-0 right-0 h-0.5"
            style={{ background: `linear-gradient(90deg, ${s.color}, transparent)` }}
          />

          {/* Icon */}
          <div
            className="w-7 h-7 rounded flex items-center justify-center mb-3"
            style={{ background: `${s.color}18`, color: s.color, border: `1px solid ${s.color}30` }}
          >
            {s.icon}
          </div>

          {/* Value */}
          <div
            className="text-2xl font-bold mb-0.5"
            style={{ fontFamily: 'Syne, sans-serif', color: s.color }}
          >
            {s.value}
          </div>

          {/* Label */}
          <div className="text-xs font-medium mb-1" style={{ color: 'var(--text)' }}>
            {s.label}
          </div>

          {/* Sub */}
          <div className="text-xs" style={{ color: 'var(--text-dim)' }}>
            {s.sub}
          </div>

          {/* Trend */}
          {s.trend && (
            <div
              className="text-xs mt-2 font-mono"
              style={{ color: s.trendUp ? 'var(--green)' : 'var(--red)', fontFamily: 'JetBrains Mono, monospace' }}
            >
              {s.trendUp ? '↑' : '↓'} {s.trend}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
