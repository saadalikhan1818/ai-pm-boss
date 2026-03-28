'use client'
// app/projects/page.tsx — Projects list page

import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import { MOCK_PROJECTS, Project, projectsApi } from '@/lib/api'
import { Plus, Search, Folder, Trash2, ExternalLink, Calendar } from 'lucide-react'

const STATUS_STYLE: Record<string, { label: string; cls: string }> = {
  active:    { label: 'Active',    cls: 'badge-progress' },
  completed: { label: 'Completed', cls: 'badge-done'     },
  delayed:   { label: 'Delayed',   cls: 'badge-delayed'  },
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>(MOCK_PROJECTS)
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', description: '' })
  const [loading, setLoading] = useState(false)

  const filtered = projects.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.description.toLowerCase().includes(search.toLowerCase())
  )

  const handleCreate = async () => {
    if (!form.name.trim()) return
    setLoading(true)
    try {
      const res = await projectsApi.create({ ...form, status: 'active' })
      setProjects(prev => [...prev, res.data])
    } catch {
      // demo fallback
      setProjects(prev => [...prev, {
        id: Date.now(), name: form.name, description: form.description,
        status: 'active', created_at: new Date().toISOString(), task_count: 0, completion: 0,
      }])
    }
    setForm({ name: '', description: '' })
    setShowModal(false)
    setLoading(false)
  }

  const handleDelete = async (id: number) => {
    try { await projectsApi.delete(id) } catch {}
    setProjects(p => p.filter(x => x.id !== id))
  }
  const handleDeploy = async () => {
  try {
    const res = await axios.post("http://localhost:8000/projects", {
      name: projectName,
      description: description
    });
    
    if (res.data.status === "success") {
      // Use the project_id returned by the backend
      window.location.href = `/tasks?projectId=${res.data.project_id}`;
    }
  } catch (err) {
    console.error("Connection to backend failed. Is main.py running?");
  }
};

  return (
    <div className="flex min-h-screen grid-bg" style={{ background: 'var(--bg)' }}>
      <Sidebar />
      <main className="ml-56 flex-1 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold" style={{ fontFamily: 'Syne, sans-serif' }}>Projects</h1>
            <p className="text-sm mt-0.5" style={{ color: 'var(--text-dim)' }}>{projects.length} total projects</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all"
            style={{ background: 'rgba(0,229,255,0.12)', color: 'var(--accent)', border: '1px solid rgba(0,229,255,0.25)' }}
          >
            <Plus size={14} />
            New Project
          </button>
        </div>

        {/* Search */}
        <div
          className="flex items-center gap-2 px-3 py-2 rounded-lg mb-6"
          style={{ background: 'var(--surface)', border: '1px solid var(--border)', maxWidth: 360 }}
        >
          <Search size={14} color="var(--muted)" />
          <input
            className="bg-transparent outline-none text-sm flex-1"
            style={{ color: 'var(--text)' }}
            placeholder="Search projects..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {/* Grid */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
          {filtered.map((p, i) => {
            const s = STATUS_STYLE[p.status]
            return (
              <div
                key={p.id}
                className="card p-5 group"
                style={{ animation: `slideUp 0.35s ease-out ${i * 50}ms forwards`, opacity: 0 }}
              >
                {/* Top row */}
                <div className="flex items-start justify-between mb-3">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                    style={{ background: 'rgba(0,229,255,0.08)', border: '1px solid rgba(0,229,255,0.15)' }}
                  >
                    <Folder size={15} color="var(--accent)" />
                  </div>
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button style={{ color: 'var(--muted)' }}><ExternalLink size={13} /></button>
                    <button onClick={() => handleDelete(p.id)} style={{ color: 'var(--red)' }}><Trash2 size={13} /></button>
                  </div>
                </div>

                <h3 className="text-sm font-semibold mb-1" style={{ fontFamily: 'Syne, sans-serif' }}>{p.name}</h3>
                <p className="text-xs mb-4" style={{ color: 'var(--text-dim)' }}>{p.description}</p>

                {/* Completion bar */}
                <div className="mb-3">
                  <div className="flex justify-between text-xs mb-1.5" style={{ color: 'var(--text-dim)' }}>
                    <span>Progress</span>
                    <span style={{ fontFamily: 'JetBrains Mono, monospace', color: 'var(--accent)' }}>
                      {p.completion ?? 0}%
                    </span>
                  </div>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${p.completion ?? 0}%`,
                        background: p.status === 'delayed' ? 'var(--red)' : p.status === 'completed' ? 'var(--green)' : 'var(--accent)',
                      }}
                    />
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between">
                  <span className={`badge ${s.cls}`}>{s.label}</span>
                  <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--muted)' }}>
                    <Calendar size={10} />
                    <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                      {new Date(p.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </main>

      {/* New project modal */}
      {showModal && (
        <div
          className="fixed inset-0 flex items-center justify-center z-50"
          style={{ background: 'rgba(8,11,16,0.85)' }}
          onClick={e => e.target === e.currentTarget && setShowModal(false)}
        >
          <div
            className="w-96 rounded-xl p-6"
            style={{ background: 'var(--surface)', border: '1px solid rgba(0,229,255,0.2)' }}
          >
            <h2 className="text-base font-bold mb-4" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--accent)' }}>
              New Project
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs mb-1 block" style={{ color: 'var(--text-dim)' }}>Project name</label>
                <input
                  className="w-full px-3 py-2 rounded-lg text-sm outline-none"
                  style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text)' }}
                  placeholder="e.g. Payment Module"
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs mb-1 block" style={{ color: 'var(--text-dim)' }}>Description</label>
                <textarea
                  className="w-full px-3 py-2 rounded-lg text-sm outline-none resize-none"
                  style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text)' }}
                  rows={3}
                  placeholder="What does this project do?"
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                />
              </div>
              <div className="flex gap-2 pt-1">
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2 rounded-lg text-sm"
                  style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-dim)' }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreate}
                  disabled={loading || !form.name.trim()}
                  className="flex-1 py-2 rounded-lg text-sm font-semibold"
                  style={{ background: 'rgba(0,229,255,0.15)', color: 'var(--accent)', border: '1px solid rgba(0,229,255,0.25)' }}
                >
                  {loading ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
