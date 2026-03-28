// lib/api.ts
// Central API client for all backend communication

import axios from 'axios'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Axios instance with base config
export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// ─── Types ───────────────────────────────────────────────────────────────────

export type ProjectStatus = 'active' | 'completed' | 'delayed'
export type TaskStatus    = 'todo' | 'in_progress' | 'done'
export type Priority      = 'low' | 'medium' | 'high'
export type UserRole      = 'developer' | 'pm' | 'ceo'

export interface Project {
  id: number
  name: string
  description: string
  status: ProjectStatus
  created_at: string
  task_count?: number
  completion?: number
}

export interface Task {
  id: number
  title: string
  description: string
  status: TaskStatus
  priority: Priority
  project_id: number
  assignee_id?: number
  assignee_name?: string
  created_at: string
}

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  created_at: string
}

export interface Sprint {
  id: number
  name: string
  project_id: number
  start_date: string
  end_date: string
  status: string
  velocity?: number
  health?: number
}

export interface AgentLog {
  timestamp: string
  agent: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
}

// ─── Projects API ─────────────────────────────────────────────────────────────

export const projectsApi = {
  list: ()                        => api.get<Project[]>('/projects'),
  get:  (id: number)              => api.get<Project>(`/projects/${id}`),
  create: (data: Partial<Project>) => api.post<Project>('/projects', data),
  delete: (id: number)            => api.delete(`/projects/${id}`),
}

// ─── Tasks API ────────────────────────────────────────────────────────────────

export const tasksApi = {
  byProject: (projectId: number)  => api.get<Task[]>(`/tasks/project/${projectId}`),
  all:       ()                    => api.get<Task[]>('/tasks'),
  create:    (data: Partial<Task>) => api.post<Task>('/tasks', data),
  update:    (id: number, data: Partial<Task>) => api.patch<Task>(`/tasks/${id}`, data),
  delete:    (id: number)          => api.delete(`/tasks/${id}`),
}

// ─── Users API ────────────────────────────────────────────────────────────────

export const usersApi = {
  list: ()                       => api.get<User[]>('/users'),
  get:  (id: number)             => api.get<User>(`/users/${id}`),
  create: (data: Partial<User>)  => api.post<User>('/users', data),
}

// ─── AI Agents API ───────────────────────────────────────────────────────────

export const agentsApi = {
  createTasks: (input: string, projectId: number) =>
    api.post('/agents/create-tasks', { input, project_id: projectId }),

  predictDelay: (projectId: number) =>
    api.post('/agents/predict-delay', { project_id: projectId }),

  generateReport: (projectId: number) =>
    api.post('/agents/generate-report', { project_id: projectId }),

  standup: (projectId: number) =>
    api.post('/agents/standup', { project_id: projectId }),
}

// ─── Mocked fallback data (used when backend is offline) ─────────────────────

export const MOCK_PROJECTS: Project[] = [
  { id: 1, name: 'AI PM Boss Core', description: 'Main agent orchestration engine', status: 'active',    created_at: '2024-06-01', task_count: 14, completion: 65 },
  { id: 2, name: 'Dashboard UI',    description: 'Next.js frontend + real-time views', status: 'active', created_at: '2024-06-05', task_count: 9,  completion: 40 },
  { id: 3, name: 'Jira Integration',description: 'Two-way Jira REST sync',           status: 'delayed',  created_at: '2024-05-28', task_count: 7,  completion: 30 },
  { id: 4, name: 'Auth System',     description: 'JWT + OAuth2 user auth',            status: 'completed',created_at: '2024-05-20', task_count: 6,  completion: 100 },
]

export const MOCK_TASKS: Task[] = [
  { id: 1, title: 'Setup LangChain agent framework',  description: '', status: 'done',        priority: 'high',   project_id: 1, assignee_name: 'Riya S.', created_at: '2024-06-01' },
  { id: 2, title: 'Task Creator Agent logic',          description: '', status: 'done',        priority: 'high',   project_id: 1, assignee_name: 'Sofi F.', created_at: '2024-06-02' },
  { id: 3, title: 'PR Mapper Agent',                   description: '', status: 'in_progress', priority: 'high',   project_id: 1, assignee_name: 'Arjun K.', created_at: '2024-06-03' },
  { id: 4, title: 'Delay Prediction model',            description: '', status: 'in_progress', priority: 'medium', project_id: 1, assignee_name: 'Dev M.',  created_at: '2024-06-04' },
  { id: 5, title: 'Report Generator Agent',            description: '', status: 'todo',        priority: 'medium', project_id: 1, assignee_name: undefined,  created_at: '2024-06-05' },
  { id: 6, title: 'Standup bot integration',           description: '', status: 'todo',        priority: 'low',    project_id: 1, assignee_name: undefined,  created_at: '2024-06-06' },
  { id: 7, title: 'Kanban board component',            description: '', status: 'done',        priority: 'high',   project_id: 2, assignee_name: 'Sofi F.', created_at: '2024-06-05' },
  { id: 8, title: 'StatsGrid component',               description: '', status: 'in_progress', priority: 'medium', project_id: 2, assignee_name: 'Riya S.', created_at: '2024-06-06' },
  { id: 9, title: 'AIInputBox component',              description: '', status: 'todo',        priority: 'high',   project_id: 2, assignee_name: undefined,  created_at: '2024-06-07' },
  { id:10, title: 'Jira API token auth',               description: '', status: 'in_progress', priority: 'high',   project_id: 3, assignee_name: 'Arjun K.', created_at: '2024-06-05' },
]

export const MOCK_AGENTS: AgentLog[] = [
  { timestamp: '06:42:11', agent: 'TaskCreator',     message: 'PRD parsed — 6 tasks generated for sprint #4',           type: 'success' },
  { timestamp: '06:40:03', agent: 'DelayPredictor',  message: 'WARN: Jira Integration sprint at 30% — delay likely',    type: 'warning' },
  { timestamp: '06:35:55', agent: 'PRMapper',        message: 'PR #47 linked → TASK-103 (PR Mapper Agent)',              type: 'info'    },
  { timestamp: '06:30:22', agent: 'StandupBot',      message: 'Daily standup sent to #dev-team (Slack)',                 type: 'success' },
  { timestamp: '06:28:00', agent: 'ReportGenerator', message: 'Weekly report drafted for AI PM Boss Core',               type: 'success' },
  { timestamp: '06:15:44', agent: 'DelayPredictor',  message: 'ERROR: Jira webhook timeout — retrying in 60s',          type: 'error'   },
  { timestamp: '06:10:11', agent: 'PRMapper',        message: 'PR #46 linked → TASK-098 (Setup LangChain framework)',    type: 'info'    },
  { timestamp: '05:55:00', agent: 'TaskCreator',     message: 'Slack message parsed: "Add OAuth2 to /users endpoint"',  type: 'info'    },
]
