# AI PM Boss — Frontend

> Next.js dashboard for the AI PM Boss autonomous project manager.
> Built for **Code Apex — "Hack the Upside Down"** · Quadra Elites

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Next.js 14 (App Router) | React framework |
| Tailwind CSS | Utility-first styling |
| Axios | HTTP client for backend API |
| Recharts | Sprint velocity & burndown charts |
| Lucide React | Icons |
| JetBrains Mono + Syne + DM Sans | Typography |

---

## Folder Structure

```
frontend/
├── app/
│   ├── globals.css          ← Design tokens, animations, base styles
│   ├── layout.tsx           ← Root HTML layout
│   ├── page.tsx             ← Dashboard (Mission Control)
│   ├── projects/page.tsx    ← Projects list + create/delete
│   ├── tasks/page.tsx       ← Task list with filters
│   ├── reports/page.tsx     ← AI-generated reports viewer
│   ├── agents/page.tsx      ← Agent monitor + manual trigger
│   └── not-found.tsx        ← 404 page
├── components/
│   ├── Sidebar.tsx          ← Fixed left navigation
│   ├── StatsGrid.tsx        ← 6-card metrics row
│   ├── KanbanBoard.tsx      ← 3-column To Do / In Progress / Done
│   ├── TaskCard.tsx         ← Individual task card (draggable)
│   ├── AIInputBox.tsx       ← AI command terminal input
│   └── RiskAlert.tsx        ← Delay/risk alert cards
├── lib/
│   └── api.ts               ← Axios client, types, mock data
├── .env.local               ← Backend URL config
├── tailwind.config.js
├── next.config.js
└── tsconfig.json
```

---

## Setup & Run

### 1. Install dependencies
```bash
cd frontend
npm install
```

### 2. Configure environment
```bash
# .env.local is already created — edit if backend runs on a different port
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start development server
```bash
npm run dev
```

Visit **http://localhost:3000**

---

## Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Mission Control | Stats, Kanban, charts, agent log |
| `/projects` | Projects | List, create, delete projects |
| `/tasks` | Tasks | Filterable task table with status updates |
| `/reports` | Reports | AI-generated weekly/standup/risk reports |
| `/agents` | Agents | Monitor and manually trigger AI agents |

---

## Connecting to Backend

All API calls in `lib/api.ts` point to `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000`).

When the backend is **offline**, all pages gracefully fall back to **mock data** so the UI always works for demo purposes.

---

## Design System

| Token | Value |
|-------|-------|
| Background | `#080b10` |
| Surface | `#0e1117` |
| Border | `#1a2030` |
| Accent (cyan) | `#00e5ff` |
| Green | `#00ff88` |
| Yellow | `#ffd60a` |
| Red | `#ff4060` |
| Purple | `#a855f7` |

---

## Git Branch

```bash
git checkout -b feature/dashboard-ui
git push origin feature/dashboard-ui
```

---

*AI PM Boss · Quadra Elites · Code Apex Hackathon*
