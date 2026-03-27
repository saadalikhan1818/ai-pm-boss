# backend/agents/report_generator.py
import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class ReportGeneratorAgent:

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=0.4,
        )

        self.system_prompt = (
            "You are an expert AI Project Manager who writes clear and professional project reports. "
            "Your reports are concise, data-driven, and actionable. "
            "Rules: "
            "Always use the data provided, do not make up numbers. "
            "Keep the tone professional but easy to read. "
            "Highlight risks and blockers clearly. "
            "Always end with clear next steps. "
            "Format the report in clean plain text with clear sections. "
            "Do not use markdown symbols like hashtags or asterisks. "
            "Use capital letters for section headings instead."
        )

    def generate_weekly_report(
        self,
        project_name: str,
        sprint_name: str,
        week_number: int,
        team_members: List[Dict],
        completed_tasks: List[Dict],
        in_progress_tasks: List[Dict],
        blocked_tasks: List[Dict],
        upcoming_tasks: List[Dict],
        sprint_velocity: int,
        target_velocity: int,
        blockers: List[str] = None,
        notes: str = ""
    ) -> Dict:
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            team_text = ""
            for member in team_members:
                team_text += (
                    f"  Name: {member.get('name')} | "
                    f"Role: {member.get('role')} | "
                    f"Tasks Done: {member.get('tasks_completed', 0)} | "
                    f"Tasks In Progress: {member.get('tasks_in_progress', 0)}\n"
                )

            completed_text = ""
            for task in completed_tasks:
                completed_text += f"  - {task.get('title')} (Priority: {task.get('priority', 'medium')})\n"

            in_progress_text = ""
            for task in in_progress_tasks:
                in_progress_text += (
                    f"  - {task.get('title')} "
                    f"(Assignee: {task.get('assignee', 'Unassigned')} | "
                    f"Priority: {task.get('priority', 'medium')})\n"
                )

            blocked_text = ""
            for task in blocked_tasks:
                blocked_text += (
                    f"  - {task.get('title')} "
                    f"(Reason: {task.get('blocked_reason', 'Unknown')})\n"
                )

            upcoming_text = ""
            for task in upcoming_tasks:
                upcoming_text += f"  - {task.get('title')} (Priority: {task.get('priority', 'medium')})\n"

            blockers_text = ""
            if blockers:
                for i, blocker in enumerate(blockers):
                    blockers_text += f"  {i + 1}. {blocker}\n"
            else:
                blockers_text = "  None reported\n"

            velocity_health = round((sprint_velocity / target_velocity) * 100, 1) if target_velocity > 0 else 0

            user_message = (
                f"Generate a professional weekly project status report using this data:\n\n"
                f"PROJECT: {project_name}\n"
                f"SPRINT: {sprint_name}\n"
                f"WEEK NUMBER: {week_number}\n"
                f"REPORT DATE: {today}\n\n"
                f"TEAM MEMBERS:\n{team_text}\n"
                f"VELOCITY:\n"
                f"  Current Sprint Velocity: {sprint_velocity} tasks completed\n"
                f"  Target Velocity: {target_velocity} tasks\n"
                f"  Velocity Health: {velocity_health}%\n\n"
                f"COMPLETED TASKS THIS WEEK:\n{completed_text}\n"
                f"IN PROGRESS TASKS:\n{in_progress_text}\n"
                f"BLOCKED TASKS:\n{blocked_text}\n"
                f"UPCOMING TASKS:\n{upcoming_text}\n"
                f"ACTIVE BLOCKERS:\n{blockers_text}\n"
                f"ADDITIONAL NOTES:\n  {notes if notes else 'None'}\n\n"
                f"Write a complete weekly report with these sections:\n"
                f"1. EXECUTIVE SUMMARY\n"
                f"2. TEAM PERFORMANCE\n"
                f"3. SPRINT PROGRESS\n"
                f"4. COMPLETED THIS WEEK\n"
                f"5. IN PROGRESS\n"
                f"6. BLOCKERS AND RISKS\n"
                f"7. NEXT WEEK PLAN\n"
                f"8. RECOMMENDATIONS\n"
            )

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_message),
            ]

            print(f"[ReportGeneratorAgent] Generating weekly report for: {project_name} - Week {week_number}")
            response = self.llm(messages)

            report_text = response.content.strip()

            print(f"[ReportGeneratorAgent] Report generated successfully | {len(report_text)} characters")

            return {
                "success": True,
                "project_name": project_name,
                "sprint_name": sprint_name,
                "week_number": week_number,
                "generated_on": today,
                "report": report_text,
                "stats": {
                    "total_completed": len(completed_tasks),
                    "total_in_progress": len(in_progress_tasks),
                    "total_blocked": len(blocked_tasks),
                    "total_upcoming": len(upcoming_tasks),
                    "velocity_health_percentage": velocity_health,
                }
            }

        except Exception as e:
            print(f"[ReportGeneratorAgent] Error: {str(e)}")
            return {
                "success": False,
                "project_name": project_name,
                "report": None,
                "error": str(e),
            }

    def generate_ceo_summary(
        self,
        projects: List[Dict],
        overall_stats: Dict
    ) -> Dict:
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            projects_text = ""
            for project in projects:
                projects_text += (
                    f"  Project: {project.get('name')}\n"
                    f"  Status: {project.get('status')}\n"
                    f"  Completion: {project.get('completion_percentage', 0)}%\n"
                    f"  Team Size: {project.get('team_size', 0)}\n"
                    f"  Risk Level: {project.get('risk_level', 'green')}\n"
                    f"  Deadline: {project.get('deadline', 'Not set')}\n\n"
                )

            user_message = (
                f"Generate a concise CEO-level project portfolio summary for {today}:\n\n"
                f"OVERALL STATS:\n"
                f"  Total Projects: {overall_stats.get('total_projects', 0)}\n"
                f"  On Track: {overall_stats.get('on_track', 0)}\n"
                f"  At Risk: {overall_stats.get('at_risk', 0)}\n"
                f"  Delayed: {overall_stats.get('delayed', 0)}\n"
                f"  Total Developers: {overall_stats.get('total_developers', 0)}\n"
                f"  Tasks Completed This Week: {overall_stats.get('tasks_completed_this_week', 0)}\n\n"
                f"PROJECT DETAILS:\n{projects_text}"
                f"Write a short CEO summary with these sections:\n"
                f"1. PORTFOLIO HEALTH\n"
                f"2. KEY ACHIEVEMENTS\n"
                f"3. PROJECTS NEEDING ATTENTION\n"
                f"4. STRATEGIC RECOMMENDATIONS\n"
                f"Keep it under 300 words. Executive audience only."
            )

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_message),
            ]

            print(f"[ReportGeneratorAgent] Generating CEO summary for {len(projects)} projects")
            response = self.llm(messages)

            return {
                "success": True,
                "generated_on": today,
                "type": "ceo_summary",
                "report": response.content.strip(),
                "projects_covered": len(projects),
            }

        except Exception as e:
            print(f"[ReportGeneratorAgent] Error generating CEO summary: {str(e)}")
            return {
                "success": False,
                "report": None,
                "error": str(e),
            }

    def generate_developer_report(
        self,
        developer_name: str,
        tasks_completed: List[Dict],
        tasks_in_progress: List[Dict],
        hours_logged: int,
        sprint_name: str
    ) -> Dict:
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            completed_text = ""
            for task in tasks_completed:
                completed_text += f"  - {task.get('title')} (Priority: {task.get('priority', 'medium')})\n"

            in_progress_text = ""
            for task in tasks_in_progress:
                in_progress_text += f"  - {task.get('title')} (Priority: {task.get('priority', 'medium')})\n"

            user_message = (
                f"Generate a brief individual developer performance report:\n\n"
                f"Developer: {developer_name}\n"
                f"Sprint: {sprint_name}\n"
                f"Date: {today}\n"
                f"Hours Logged: {hours_logged}\n\n"
                f"Tasks Completed:\n{completed_text}\n"
                f"Tasks In Progress:\n{in_progress_text}\n"
                f"Write a short performance summary with:\n"
                f"1. PERFORMANCE SUMMARY\n"
                f"2. ACHIEVEMENTS\n"
                f"3. CURRENT FOCUS\n"
                f"4. SUGGESTIONS\n"
                f"Keep it under 150 words. Be encouraging but honest."
            )

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_message),
            ]

            print(f"[ReportGeneratorAgent] Generating report for developer: {developer_name}")
            response = self.llm(messages)

            return {
                "success": True,
                "developer_name": developer_name,
                "sprint_name": sprint_name,
                "generated_on": today,
                "report": response.content.strip(),
                "stats": {
                    "tasks_completed": len(tasks_completed),
                    "tasks_in_progress": len(tasks_in_progress),
                    "hours_logged": hours_logged,
                }
            }

        except Exception as e:
            print(f"[ReportGeneratorAgent] Error: {str(e)}")
            return {
                "success": False,
                "developer_name": developer_name,
                "report": None,
                "error": str(e),
            }


if __name__ == "__main__":
    agent = ReportGeneratorAgent()

    result = agent.generate_weekly_report(
        project_name="AI PM Boss",
        sprint_name="Sprint 3 - Core Agents",
        week_number=3,
        team_members=[
            {"name": "Sofi", "role": "Team Lead", "tasks_completed": 4, "tasks_in_progress": 2},
            {"name": "Ali", "role": "Backend Dev", "tasks_completed": 3, "tasks_in_progress": 1},
            {"name": "Sara", "role": "Frontend Dev", "tasks_completed": 2, "tasks_in_progress": 2},
            {"name": "Zain", "role": "AI Engineer", "tasks_completed": 5, "tasks_in_progress": 1},
        ],
        completed_tasks=[
            {"title": "Task Creator Agent", "priority": "high"},
            {"title": "PR Mapper Agent", "priority": "high"},
            {"title": "Database Models", "priority": "high"},
            {"title": "FastAPI Setup", "priority": "medium"},
        ],
        in_progress_tasks=[
            {"title": "Delay Predictor Agent", "assignee": "Zain", "priority": "high"},
            {"title": "Kanban Board UI", "assignee": "Sara", "priority": "medium"},
        ],
        blocked_tasks=[
            {"title": "Jira Integration", "blocked_reason": "Waiting for API credentials"},
        ],
        upcoming_tasks=[
            {"title": "Standup Bot", "priority": "medium"},
            {"title": "JWT Authentication", "priority": "high"},
        ],
        sprint_velocity=14,
        target_velocity=18,
        blockers=["Jira API credentials not received", "Redis not configured on staging"],
        notes="Hackathon demo is in 2 days, prioritize dashboard UI"
    )

    print(result.get("report"))