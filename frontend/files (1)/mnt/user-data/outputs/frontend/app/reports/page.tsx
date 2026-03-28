'use client'
// app/reports/page.tsx — AI-generated reports viewer

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import AIInputBox from '@/components/AIInputBox'
import { FileText, Download, Clock, Zap, ChevronRight, RefreshCw } from 'lucide-react'

interface Report {
  id: number
  title: string
  project: string
  type: 'weekly' | 'standup' | 'risk' | 'sprint'
  content: string
  generated_at: string
  agent: string
}

const MOCK_REPORTS: Report[] = [
  {
    id: 1,
    title: 'Weekly Sprint Report — AI PM Boss Core',
    project: 'AI PM Boss Core',
    type: 'weekly',
    agent: 'ReportGenerator',
    generated_at: '2024-06-10 06:28:00',
    content: `## Sprint 4 Summary

**Period:** June 3 – June 10, 2024
**Team:** Quadra Elites (8 members)
**Sprint Health:** 🟡 Moderate (68%)

### Completed This Week
- ✅ LangChain agent framework setup (Riya S.)
- ✅ Task Creator Agent v1 (Sofi F.)
- ✅ Kanban board component (Sofi F.)
- ✅ JWT authentication system (Dev M.)

### In Progress
- 🔄 PR Mapper Agent — 70% done (Arjun K.)
- 🔄 Delay Prediction model — 55% done (Dev M.)
- 🔄 StatsGrid component (Riya S.)

### Risks Identified
- ⚠️ Jira Integration sprint at 30% — delay likely
- ⚠️ Redis + Celery setup blocked on Docker config

### Next Sprint Goals
1. Complete PR Mapper + Delay Predictor agents
2. Connect GitHub webhooks
3. Deploy to staging environment

**Velocity:** Planned 24 pts · Actual 16 pts (67% efficiency)`,
  },
  {
    id: 2,
    title: 'Daily Standup Summary',
    project: 'All Projects',
    type: 'standup',
    agent: 'StandupBot',
    generated_at: '2024-06-10 09:00:00',
    content: `## Standup — June 10, 2024

**Sofi Faiz Ahmed (PM/Lead)**
- ✅ Yesterday: Reviewed PRD, created 6 tasks via AI
- 🔄 Today: Frontend dashboard polish
- 🚧 Blockers: None

**Riya S. (Backend)**
- ✅ Yesterday: LangChain setup complete, agents running
- 🔄 Today: StatsGrid component + API integration
- 🚧 Blockers: Redis Docker config unclear

**Arjun K. (Backend)**
- ✅ Yesterday: PR Mapper 70% done
- 🔄 Today: Finishing mapper + GitHub webhook
- 🚧 Blockers: GitHub API rate limits in dev

**Dev M. (ML)**
- ✅ Yesterday: Delay prediction model trained (72% accuracy)
- 🔄 Today: Integrating model into agent endpoint
- 🚧 Blockers: None`,
  },
  {
    id: 3,
    title: 'Risk Assessment — Jira Integration',
    project: 'Jira Integration',
    type: 'risk',
    agent: 'DelayPredictor',
    generated_at: '2024-06-10 06:40:03',
    content: `## Risk Report: Jira Integration Sprint

**Risk Level: 🔴 CRITICAL**
**Confidence: 89%**

### Prediction
Sprint is at **30% completion** with **2 days remaining**.
At current velocity (15 pts/day), only **38%** of planned work will be completed.

### Root Cause Analysis
1. **Jira REST API complexity** underestimated — took 3x planned time
2. **OAuth token refresh** logic not accounted for in estimates
3. **Team bandwidth** reduced (1 dev on sick leave)

### Recommended Actions
- [ ] Scope down: defer webhook sync to Sprint 5
- [ ] Reassign Arjun K. to unblock API token issue
- [ ] Escalate to PM for sprint goal adjustment

### Impact if Unaddressed
- Sprint 5 delayed by 3–5 days
- CEO dashboard feature delayed by 1 week`,
  },
]

const TYPE_COLORS = {
  weekly:  { color: 'var(--accent)',  label: 'Weekly'  },
  standup: { color: 'var(--green)',   label: 'Standup' },
  risk:    { color: 'var(--red)',     label: 'Risk'    },
  sprint:  { color: 'var(--purple)', label: 'Sprint'  },
}

export default function ReportsPage() {
  const [selected, setSelected] = useState<Report>(MOCK_REPORTS[0])
  const [generating, setGenerating] = useState(false)

  const handleGenerate = async () => {
    setGenerating(true)
    await new Promise(r => setTimeout(r, 2000))
    setGenerating(false)
  }

  return (
    <div className="flex min-h-screen grid-bg" style={{ background: 'var(--bg)' }}>
      <Sidebar />
      <main className="ml-56 flex-1 flex">
        {/* Report list */}
        <aside className="w-72 flex-shrink-0 border-r p-4" style={{ borderColor: 'var(--border)' }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold" style={{ fontFamily: 'Syne, sans-serif' }}>Reports</h2>
            <button
              onClick={handleGenerate}
              className="p-1.5 rounded"
              style={{ background: 'rgba(0,229,255,0.08)', color: 'var(--accent)', border: '1px solid rgba(0,229,255,0.15)' }}
            >
              <RefreshCw size={13} className={generating ? 'animate-spin' : ''} />
            </button>
          </div>

          <div className="space-y-2">
            {MOCK_REPORTS.map(r => {
              const tc = TYPE_COLORS[r.type]
              const isActive = selected.id === r.id
              return (
                <button
                  key={r.id}
                  onClick={() => setSelected(r)}
                  className="w-full text-left p-3 rounded-lg transition-all"
                  style={{
                    background: isActive ? 'rgba(0,229,255,0.07)' : 'transparent',
                    border: `1px solid ${isActive ? 'rgba(0,229,255,0.2)' : 'transparent'}`,
                  }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <FileText size={12} color={tc.color} />
                    <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: `${tc.color}18`, color: tc.color, fontFamily: 'JetBrains Mono, monospace' }}>
                      {tc.label}
                    </span>
                  </div>
                  <p className="text-xs font-medium mb-1 leading-snug" style={{ color: 'var(--text)' }}>
                    {r.title}
                  </p>
                  <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>
                    <Clock size={9} />
                    {r.generated_at.split(' ')[1]}
                    <span className="ml-1">· {r.agent}</span>
                  </div>
                </button>
              )
            })}
          </div>

          {/* Generate new */}
          <div className="mt-4 pt-4 border-t" style={{ borderColor: 'var(--border)' }}>
            <p className="text-xs mb-2" style={{ color: 'var(--text-dim)' }}>Generate new report via AI:</p>
            <AIInputBox projectId={1} />
          </div>
        </aside>

        {/* Report content */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span
                  className="text-xs px-2 py-0.5 rounded"
                  style={{
                    background: `${TYPE_COLORS[selected.type].color}18`,
                    color: TYPE_COLORS[selected.type].color,
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                >
                  {TYPE_COLORS[selected.type].label}
                </span>
                <span className="text-xs" style={{ color: 'var(--text-dim)' }}>
                  Generated by {selected.agent}
                </span>
              </div>
              <h1 className="text-lg font-bold" style={{ fontFamily: 'Syne, sans-serif' }}>{selected.title}</h1>
            </div>
            <button
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs"
              style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-dim)' }}
            >
              <Download size={12} />
              Export
            </button>
          </div>

          {/* Rendered markdown-ish content */}
          <div className="card p-6">
            <div
              className="text-sm leading-relaxed whitespace-pre-wrap"
              style={{ color: 'var(--text)', fontFamily: 'DM Sans, sans-serif' }}
              dangerouslySetInnerHTML={{
                __html: selected.content
                  .replace(/^## (.+)$/gm, '<h2 style="font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:var(--accent);margin:20px 0 10px">$1</h2>')
                  .replace(/^### (.+)$/gm, '<h3 style="font-family:Syne,sans-serif;font-size:13px;font-weight:600;color:var(--text);margin:16px 0 8px">$1</h3>')
                  .replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--text);font-weight:600">$1</strong>')
                  .replace(/^- (.+)$/gm, '<div style="padding:2px 0;padding-left:12px;border-left:2px solid var(--border);margin-bottom:4px;color:var(--text-dim)">$1</div>')
                  .replace(/✅/g, '<span style="color:var(--green)">✅</span>')
                  .replace(/🔄/g, '<span style="color:var(--accent)">🔄</span>')
                  .replace(/⚠️/g, '<span style="color:var(--yellow)">⚠️</span>')
                  .replace(/🔴/g, '<span style="color:var(--red)">🔴</span>')
                  .replace(/🟡/g, '<span style="color:var(--yellow)">🟡</span>')
                  .replace(/\n/g, '<br/>')
              }}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
