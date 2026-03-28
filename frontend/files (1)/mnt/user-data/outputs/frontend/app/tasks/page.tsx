"use client";

import { useState } from 'react';
import Sidebar from "../../components/Sidebar"; 
import KanbanBoard from "../../components/KanbanBoard";
import AllInputBox from "../../components/AllInputBox";
import RiskAlert from "../../components/RiskAlert";
import StatsGrid from "../../components/StatsGrid";
import { Plus } from 'lucide-react';

export default function TasksPage() {
  const [showModal, setShowModal] = useState(false);
  const projectId = 1; // Default project ID

  return (
    <div className="flex min-h-screen grid-bg" style={{ background: 'var(--bg)' }}>
      <Sidebar />
      
      <main className="ml-56 flex-1 p-6 space-y-6">
        {/* Header with StatsGrid Integration */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--text)' }}>
              Task Board
            </h1>
            <p className="text-sm mt-0.5" style={{ color: 'var(--text-dim)' }}>
              Autonomous AI PM Mode Active
            </p>
          </div>
          <div className="flex items-center gap-4">
             <StatsGrid />
             <button
                onClick={() => setShowModal(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold h-fit"
                style={{ background: 'rgba(0,229,255,0.12)', color: 'var(--accent)', border: '1px solid rgba(0,229,255,0.25)' }}
              >
                <Plus size={14} /> New Task
              </button>
          </div>
        </div>

        {/* AI Agent Monitoring Section */}
        <div className="grid grid-cols-1 md:grid-cols-1 gap-4">
          <RiskAlert projectId={projectId} />
        </div>

        {/* AI Command Center (The AllInputBox) */}
        <div className="p-4 rounded-xl border" style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}>
          <h3 className="text-xs font-mono mb-4 flex items-center gap-2" style={{ color: 'var(--accent)' }}>
            <span className="w-2 h-2 rounded-full bg-[#00ffb4] animate-pulse"></span>
            AI PM BOSS COMMAND • STANDBY
          </h3>
          <AllInputBox projectId={projectId} /> 
        </div>

        {/* The Main Board */}
        <section className="mt-4">
          <KanbanBoard projectId={projectId} />
        </section>
      </main>

      {/* Keep your existing Modal logic here if you still want manual task creation */}
      {showModal && (
        <div
          className="fixed inset-0 flex items-center justify-center z-50"
          style={{ background: 'rgba(8,11,16,0.85)' }}
          onClick={e => e.target === e.currentTarget && setShowModal(false)}
        >
          <div className="w-96 rounded-xl p-6" style={{ background: 'var(--surface)', border: '1px solid rgba(0,229,255,0.2)' }}>
            <h2 className="text-base font-bold mb-4" style={{ fontFamily: 'Syne, sans-serif', color: 'var(--accent)' }}>
              New Manual Task
            </h2>
            {/* ... rest of your modal form code ... */}
            <button onClick={() => setShowModal(false)} className="w-full py-2 mt-4 rounded-lg text-sm" style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-dim)' }}>
               Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}