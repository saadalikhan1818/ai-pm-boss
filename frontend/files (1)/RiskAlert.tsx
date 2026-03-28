'use client'
// components/RiskAlert.tsx
// Displays AI-predicted sprint risk alerts with severity levels

import { AlertTriangle, X, ChevronRight, Clock } from 'lucide-react'
import { useState } from 'react'

interface Alert {
  id: number
  project: string
  message: string
  severity: 'critical' | 'warning' | 'info'
  time: string
  progress: number
}

const MOCK_ALERTS: Alert[] = [
  {
    id: 1,
    project: 'Jira Integration',
    message: 'Sprint at 30% completion with 2 days left. Delay very likely.',
    severity: 'critical',
    time: '10 min ago',
    progress: 30,
  },
  {
    id: 2,
    project: 'AI PM Boss Core',
    message: 'PR Mapper Agent task overdue by 1 day. Sprint health at 68%.',
    severity: 'warning',
    time: '1 hr ago',
    progress: 68,
  },
]

const COLORS = {
  critical: { text: 'var(--red)',    bg: 'rgba(255,64,96,0.08)',  border: 'rgba(255,64,96,0.2)'  },
  warning:  { text: 'var(--yellow)', bg: 'rgba(255,214,10,0.06)', border: 'rgba(255,214,10,0.2)' },
  info:     { text: 'var(--accent)', bg: 'rgba(0,229,255,0.06)',  border: 'rgba(0,229,255,0.2)'  },
}

export default function RiskAlert() {
  const [alerts, setAlerts] = useState(MOCK_ALERTS)

  const dismiss = (id: number) => setAlerts(a => a.filter(x => x.id !== id))

  if (alerts.length === 0) {
    return (
      <div
        className="card p-5 flex items-center gap-3"
        style={{ borderColor: 'rgba(0,255,136,0.2)', background: 'rgba(0,255,136,0.04)' }}
      >
        <div className="w-2 h-2 rounded-full" style={{ background: 'var(--green)' }} />
        <span className="text-sm" style={{ color: 'var(--green)' }}>All clear — no active risk alerts</span>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {alerts.map(alert => {
        const c = COLORS[alert.severity]
        return (
          <div
            key={alert.id}
            className="rounded-lg p-4 relative"
            style={{ background: c.bg, border: `1px solid ${c.border}` }}
          >
            <div className="flex items-start gap-3">
              {/* Pulse dot */}
              <div className="mt-0.5 flex-shrink-0">
                {alert.severity === 'critical' ? (
                  <div className="risk-pulse" />
                ) : (
                  <AlertTriangle size={14} color={c.text} />
                )}
              </div>

              <div className="flex-1 min-w-0">
                {/* Header */}
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className="text-sm font-semibold"
                    style={{ color: c.text, fontFamily: 'Syne, sans-serif' }}
                  >
                    {alert.project}
                  </span>
                  <span
                    className="text-xs uppercase tracking-wider px-1.5 py-0.5 rounded"
                    style={{ background: `${c.text}20`, color: c.text, fontFamily: 'JetBrains Mono, monospace' }}
                  >
                    {alert.severity}
                  </span>
                </div>

                {/* Message */}
                <p className="text-xs mb-2" style={{ color: 'var(--text-dim)' }}>
                  {alert.message}
                </p>

                {/* Progress */}
                <div className="flex items-center gap-3">
                  <div className="progress-track flex-1">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${alert.progress}%`,
                        background: c.text,
                      }}
                    />
                  </div>
                  <span
                    className="text-xs flex-shrink-0"
                    style={{ color: c.text, fontFamily: 'JetBrains Mono, monospace' }}
                  >
                    {alert.progress}%
                  </span>
                </div>

                {/* Footer */}
                <div className="flex items-center gap-1 mt-2" style={{ color: 'var(--muted)' }}>
                  <Clock size={11} />
                  <span className="text-xs" style={{ fontFamily: 'JetBrains Mono, monospace' }}>{alert.time}</span>
                  <button
                    className="ml-auto flex items-center gap-1 text-xs"
                    style={{ color: c.text }}
                  >
                    View sprint <ChevronRight size={11} />
                  </button>
                </div>
              </div>

              {/* Dismiss */}
              <button
                onClick={() => dismiss(alert.id)}
                className="flex-shrink-0 p-0.5 rounded"
                style={{ color: 'var(--muted)' }}
              >
                <X size={13} />
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
