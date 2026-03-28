'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Zap } from 'lucide-react'
import axios from 'axios'

interface Props {
  projectId?: number
}

const SUGGESTIONS = [
  'Create tasks for user authentication module',
  'Identify potential risks for this project',
  'Generate a project status report',
  'Show daily standup summary',
]

export default function AllInputBox({ projectId = 1 }: Props) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState<{ text: string; type: 'user' | 'agent' | 'error' | 'success' }[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  // Intent detection to route to correct FastAPI endpoint
  const detectIntent = (text: string) => {
    const t = text.toLowerCase()
    if (t.includes('risk') || t.includes('danger') || t.includes('issue')) return 'risk'
    if (t.includes('report') || t.includes('summary') || t.includes('standup')) return 'report'
    return 'task' // Default intent
  }

  const handleSubmit = async () => {
    if (!input.trim() || loading) return

    const userText = input.trim()
    const intent = detectIntent(userText)
    
    setInput('')
    setShowSuggestions(false)
    setLogs(l => [...l, { text: `> ${userText}`, type: 'user' }])
    setLoading(true)

    try {
      let response;
      const backendUrl = "http://localhost:8000";

      if (intent === 'risk') {
        setLogs(l => [...l, { text: `[AI PM Boss] Risk Detection Agent initializing...`, type: 'agent' }])
        response = await axios.post(`${backendUrl}/agents/risk-detector?project_id=${projectId}`)
        setLogs(l => [...l, { text: `✓ Analysis: ${response.data.risks || response.data.message}`, type: 'success' }])
      } 
      else if (intent === 'report') {
        setLogs(l => [...l, { text: `[AI PM Boss] Standup Agent gathering data...`, type: 'agent' }])
        response = await axios.get(`${backendUrl}/agents/standup/${projectId}`)
        setLogs(l => [...l, { text: `✓ ${response.data.report}`, type: 'success' }])
      }
      else {
        setLogs(l => [...l, { text: `[AI PM Boss] Task Creator Agent decomposing requirements...`, type: 'agent' }])
        response = await axios.post(`${backendUrl}/agents/task-creator`, {
          command: userText,
          project_id: projectId
        })
        setLogs(l => [...l, { text: `✓ Successfully created ${response.data.count} tasks. Refreshing board...`, type: 'success' }])
        // Trigger board refresh
        setTimeout(() => window.location.reload(), 2000)
      }

    } catch (err: any) {
      console.error("Agent Error:", err)
      setLogs(l => [...l, { text: `✗ Error: ${err.response?.data?.detail || "Backend unreachable"}`, type: 'error' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="rounded-lg overflow-hidden border border-gray-800 shadow-2xl"
      style={{ background: 'rgba(10, 15, 20, 0.95)' }}
    >
      {/* Terminal Header */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-800 bg-black/50">
        <Zap size={14} className="text-[#00ffb4]" />
        <span className="text-[10px] font-bold tracking-[0.2em] text-[#00ffb4] font-mono">
          AI-PM-SYSTEM v3.0
        </span>
        <div className="ml-auto flex gap-1.5">
          <div className="w-2 h-2 rounded-full bg-red-500/50" />
          <div className="w-2 h-2 rounded-full bg-yellow-500/50" />
          <div className="w-2 h-2 rounded-full bg-green-500/50" />
        </div>
      </div>

      {/* Terminal Logs View */}
      <div className="h-48 overflow-y-auto px-4 py-3 font-mono text-[11px] leading-relaxed scrollbar-hide bg-black/20">
        {logs.length === 0 && (
          <div className="text-gray-600 italic">Waiting for command...</div>
        )}
        {logs.map((log, i) => (
          <div
            key={i}
            className={`mb-1 whitespace-pre-wrap ${
              log.type === 'user' ? 'text-white' : 
              log.type === 'error' ? 'text-red-400' : 
              log.type === 'success' ? 'text-[#00ffb4]' : 'text-blue-400'
            }`}
          >
            {log.text}
          </div>
        ))}
        {loading && (
          <div className="text-[#00ffb4] animate-pulse">_ Processing request...</div>
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Command Input Area */}
      <div className="p-4 bg-black/40 border-t border-gray-800 relative">
        <div className="flex items-center gap-3">
          <span className="text-[#00ffb4] font-mono text-sm font-bold">$</span>
          <input
            ref={inputRef}
            className="flex-1 bg-transparent border-none outline-none text-sm text-white font-mono placeholder:text-gray-700"
            placeholder="Type your command here..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !input.trim()}
            className="group flex items-center gap-2 px-4 py-1.5 rounded bg-[#00ffb4] text-black text-[10px] font-black uppercase tracking-tighter hover:scale-105 active:scale-95 transition-all disabled:opacity-30 disabled:grayscale"
          >
            {loading ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
            {loading ? 'Exec' : 'Run'}
          </button>
        </div>

        {/* Floating Suggestions */}
        {showSuggestions && !input && (
          <div className="absolute left-4 right-4 bottom-full mb-2 rounded-md border border-gray-800 bg-[#0a0f14] overflow-hidden">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                onMouseDown={() => setInput(s)}
                className="w-full text-left px-3 py-2 text-[10px] text-gray-500 font-mono hover:bg-[#00ffb4]/10 hover:text-[#00ffb4] transition-colors border-b border-gray-900 last:border-none"
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}