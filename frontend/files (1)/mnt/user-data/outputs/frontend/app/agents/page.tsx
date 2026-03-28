'use client'
// app/agents/page.tsx — AI Agents monitor and control panel

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import { MOCK_AGENTS, agentsApi } from '@/lib/api'
import { Play, Square, RotateCcw, Zap, CheckCircle2, AlertTriangle, Info, XCircle, Bot, Activity } from 'lucide-react'

interface AgentConfig {
  id: string
  name: string
  description: string
  endpoint: string
  status: 'running' | 'idle' | 'error'
  lastRun: string
  runCount: number
  color: string
}

const AGENTS: AgentConfig[] = [
  {
    id: 'task_creator',
    name: 'Task Creator Agent',
    description: 'Reads PRD or Slack input and auto-creates Jira-style tasks with priority and assignee.',
    endpoint: '/agents/create-tasks',
    status: 'running',
    lastRun: '2 min ago',
    runCount: 34,
    color: 'var(--accent)',
  },
  {
    id: 'pr_mapper',
    name: 'PR Mapper Agent',
    description: 'Links GitHub pull requests to their matching tasks. Updates task status on merge.',
    endpoint: '/agents/pr-mapper',
    status: 'running',
    lastRun: '5 min ago',
    runCount: 28,
    color: 'var(--purple)',
  },
  {
    id: 'delay_predictor',
    name: 'Delay Predictor Agent',
    description: 'Analyzes sprint velocity and task completion to predict delays 1–2 weeks early.',
    endpoint: '/agents/predict-delay',
    status: 'error',
    lastRun: '15 min ago',
    runCount: 12,
    color: 'var(--red)',
  },
  {
    id: 'report_generator',
    name: 'Report Generator',
    description: 'Generates weekly sprint reports and sends them to Slack #pm-channel automatically.',
    endpoint: '/agents/generate-report',
    status: 'idle',
    lastRun: '1 hr ago',
    runCount: 8,
    color: 'var(--green)',
  },
  {
    id: 'standup_bot',
    name: 'Standup Bot',
    description: 'Collects updates from developers and posts daily standup summaries to Slack.',
    endpoint: '/agents/standup',
    status: 'running',
    lastRun: '3 hr ago',
    runCount: 21,
    color: 'var(--yellow)',
  },
]

const STATUS_STYLE = {
  running: { color: 'var(--green)',  label: 'RUNNING', dot: true  },
  idle:    { color: 'var(--muted)',  label: 'IDLE',    dot: false },
  error:   { color: 'var(--red)',    label: 'ERROR',   dot: false },
}

const LOG_ICON: Record<string, React.ReactNode> = {
  success: <CheckCircle2 size={12} color="var(--green)"  />,
  warning: <AlertTriangle size={12} color="var(--yellow)" />,
  error:   <XCircle size={12}      color="var(--red)"    />,
  info:    <Info size={12}         color="var(--accent)" />,
}

export default function AgentsPage() {
  const [agents, setAgents] = useState(AGENTS)
  const [logs] = useState(MOCK_AGENTS)
  const [running, setRunning] = useState<string | null>(null)
  const [triggerLog, setTriggerLog] = useState<string[]>([])

  const triggerAgent = async (agent: AgentConfig) => {
    setRunning(agent.id)
    setTriggerLog(l => [...l, `[${new Date().toLocaleTimeString()}] Triggering ${agent.name}...`])

    try {
      if (agent.id === 'task_creator')    await agentsApi.createTasks('Manual trigger', 1)
      if (agent.id === 'delay_predictor') await agentsApi.predictDelay(1)
      if (agent.id === 'report_generator')await agentsApi.generateReport(1)
      if (agent.id === 'standup_bot')     await agentsApi.standup(1)
      setTriggerLog(l => [...l, `[${new Date().toLocaleTimeString()}] ✓ ${agent.name} completed successfully.`])
      setAgents(a => a.map(x => x.id === agent.id ? { ...x, status: 'running', lastRun: 'just now', runCount: x.runCount + 1 } : x))
    } catch {
      setTriggerLog(l => [...l, `[${new Date().toLocaleTimeString()}] ✗ Backend offline — demo mode.`])
      setTriggerLog(l => [...l, `[${new Date().toLocaleTimeString()}] ✓ ${agent.name} demo run complete.`])
    } finally {
      setRunning(null)
    }
  }

  const resetAgent = (id: string) => {
    setAgents(a => a.map(x => x.id === id ? { ...x, status: 'idle' } : x))
  }

  return (
    <div className="flex min-h-screen grid-bg" style={{ background: 'var(--bg)' }}>
      <Sidebar />
      <main className="ml-56 flex-1 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold" style={{ fontFamily: 'Syne, sans-serif' }}>AI Agents</h1>
            <p className="text-sm mt-0.5" style={{ color: 'var(--text-dim)' }}>
              {agents.filter(a => a.status === 'running').length} running · {agents.filter(a => a.status === 'error').length} errors
            </p>
          </div>
          <div
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs"
            style={{ background: 'rgba(0,255,136,0.07)', border: '1px solid rgba(0,255,136,0.2)', color: 'var(--green)', fontFamily: 'JetBrains Mono, monospace' }}
          >
            <Activity size={12} />
            Orchestrator: LangChain
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Agent cards — 2 cols */}
          <div className="col-span-2 space-y-4">
            {agents.map((agent, i) => {
              const ss = STATUS_STYLE[agent.status]
              const isRunning = running === agent.id
              return (
                <div
                  key={agent.id}
                  className="card p-5 relative overflow-hidden"
                  style={{ animation: `slideUp 0.3s ease-out ${i * 60}ms forwards`, opacity: 0 }}
                >
                  {/* Color bar */}
                  <div className="absolute left-0 top-0 bottom-0 w-0.5" style={{ background: agent.color }} />

                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{ background: `${agent.color}12`, border: `1px solid ${agent.color}25` }}
                    >
                      <Bot size={18} color={agent.color} />
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* Name + status */}
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-sm font-semibold" style={{ fontFamily: 'Syne, sans-serif' }}>
                          {agent.name}
                        </span>
                        <span
                          className="flex items-center gap-1.5 text-xs"
                          style={{ color: ss.color, fontFamily: 'JetBrains Mono, monospace' }}
                        >
                          {ss.dot ? (
                            <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ background: 'var(--green)', boxShadow: '0 0 6px var(--green)' }} />
                          ) : (
                            <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ background: ss.color }} />
                          )}
                          {ss.label}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-xs mb-3" style={{ color: 'var(--text-dim)' }}>{agent.description}</p>

                      {/* Meta */}
                      <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>
                        <span>Last run: {agent.lastRun}</span>
                        <span>Total runs: {agent.runCount}</span>
                        <span style={{ color: 'rgba(255,255,255,0.2)' }}>·</span>
                        <span style={{ color: 'var(--text-dim)' }}>{agent.endpoint}</span>
                      </div>
                    </div>

                    {/* Controls */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {agent.status === 'error' && (
                        <button
                          onClick={() => resetAgent(agent.id)}
                          className="p-2 rounded-lg"
                          style={{ background: 'rgba(255,64,96,0.1)', color: 'var(--red)', border: '1px solid rgba(255,64,96,0.2)' }}
                          title="Reset agent"
                        >
                          <RotateCcw size={13} />
                        </button>
                      )}
                      <button
                        onClick={() => triggerAgent(agent)}
                        disabled={isRunning}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
                        style={{
                          background: isRunning ? 'var(--border)' : `${agent.color}15`,
                          color: isRunning ? 'var(--muted)' : agent.color,
                          border: `1px solid ${isRunning ? 'var(--border)' : `${agent.color}30`}`,
                          cursor: isRunning ? 'not-allowed' : 'pointer',
                          fontFamily: 'JetBrains Mono, monospace',
                        }}
                      >
                        {isRunning ? (
                          <><RotateCcw size={11} className="animate-spin" /> Running...</>
                        ) : (
                          <><Play size={11} /> Run</>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Right panel */}
          <div className="space-y-4">
            {/* Trigger log */}
            {triggerLog.length > 0 && (
              <div className="card p-4">
                <div className="text-xs font-semibold mb-3 flex items-center gap-2" style={{ fontFamily: 'Syne, sans-serif' }}>
                  <Zap size={12} color="var(--accent)" />
                  <span style={{ color: 'var(--accent)' }}>Live Output</span>
                </div>
                <div className="terminal-log">
                  {triggerLog.map((line, i) => (
                    <div key={i} style={{ color: line.includes('✓') ? 'var(--green)' : line.includes('✗') ? 'var(--red)' : 'var(--accent)' }}>
                      {line}
                    </div>
                  ))}
                  {running && <div className="cursor" style={{ color: 'var(--accent)' }}></div>}
                </div>
              </div>
            )}

            {/* Activity feed */}
            <div className="card p-4">
              <div className="text-xs font-semibold mb-3 flex items-center gap-2" style={{ fontFamily: 'Syne, sans-serif' }}>
                <Activity size={12} color="var(--text-dim)" />
                <span>Activity Feed</span>
              </div>
              <div className="space-y-3">
                {logs.map((log, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <div className="flex-shrink-0 mt-0.5">{LOG_ICON[log.type]}</div>
                    <div>
                      <div className="text-xs font-medium mb-0.5" style={{ color: 'var(--text-dim)', fontFamily: 'JetBrains Mono, monospace' }}>
                        [{log.agent}]
                      </div>
                      <div className="text-xs" style={{ color: 'var(--text-dim)' }}>{log.message}</div>
                      <div className="text-xs mt-0.5" style={{ color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>
                        {log.timestamp}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Stats */}
            <div className="card p-4">
              <div className="text-xs font-semibold mb-3" style={{ fontFamily: 'Syne, sans-serif' }}>
                Agent Stats
              </div>
              <div className="space-y-3">
                {[
                  { label: 'Total tasks auto-created', value: '34', color: 'var(--accent)' },
                  { label: 'PRs auto-linked',          value: '28', color: 'var(--purple)' },
                  { label: 'Delays predicted',         value: '5',  color: 'var(--red)' },
                  { label: 'Reports generated',        value: '8',  color: 'var(--green)' },
                  { label: 'Standups sent',            value: '21', color: 'var(--yellow)' },
                ].map(s => (
                  <div key={s.label} className="flex items-center justify-between">
                    <span className="text-xs" style={{ color: 'var(--text-dim)' }}>{s.label}</span>
                    <span className="text-sm font-bold" style={{ color: s.color, fontFamily: 'Syne, sans-serif' }}>{s.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
