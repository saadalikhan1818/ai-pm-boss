import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class StandupBotAgent:

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=0.3,
        )

        self.system_prompt = (
            "You are an expert AI Scrum Master who runs daily standup meetings. "
            "Your job is to collect each developer's update and produce a clean standup summary. "
            "Rules: "
            "Keep the summary concise and scannable. "
            "Highlight blockers clearly so the team can act on them immediately. "
            "Identify if any developer needs help based on their update. "
            "Always use plain text with no markdown symbols like hashtags or asterisks. "
            "Use capital letters for section headings. "
            "Keep the tone friendly, energetic and professional. "
            "Always end with a motivational one liner for the team."
        )

    def generate_standup_summary(
        self,
        project_name: str,
        sprint_name: str,
        developer_updates: List[Dict],
        sprint_days_remaining: int,
        overall_completion_percentage: float
    ) -> Dict:
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            day_name = datetime.now().strftime("%A")

            updates_text = ""
            for update in developer_updates:
                updates_text += (
                    f"Developer: {update.get('name')} ({update.get('role', 'Developer')})\n"
                    f"  Yesterday: {update.get('yesterday', 'No update provided')}\n"
                    f"  Today: {update.get('today', 'No update provided')}\n"
                    f"  Blockers: {update.get('blockers', 'None')}\n"
                    f"  Mood: {update.get('mood', 'neutral')}\n\n"
                )

            user_message = (
                f"Generate a daily standup summary for the team:\n\n"
                f"PROJECT: {project_name}\n"
                f"SPRINT: {sprint_name}\n"
                f"DATE: {today} ({day_name})\n"
                f"SPRINT DAYS REMAINING: {sprint_days_remaining}\n"
                f"OVERALL SPRINT COMPLETION: {overall_completion_percentage}%\n\n"
                f"DEVELOPER UPDATES:\n{updates_text}"
                f"Write the standup summary with these sections:\n"
                f"1. GOOD MORNING GREETING with date\n"
                f"2. SPRINT HEALTH snapshot in one line\n"
                f"3. INDIVIDUAL UPDATES for each developer\n"
                f"4. BLOCKERS AND WHO NEEDS HELP\n"
                f"5. FOCUS FOR TODAY as a team\n"
                f"6. MOTIVATIONAL CLOSING LINE\n"
            )

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_message),
            ]

            print(f"[StandupBotAgent] Generating standup for: {project_name} | {today}")
            response = self.llm(messages)

            summary_text = response.content.strip()

            blockers_found = [
                update.get("name")
                for update in developer_updates
                if update.get("blockers") and update.get("blockers").lower() != "none"
            ]

            needs_help = [
                update.get("name")
                for update in developer_updates
                if update.get("mood") in ["stressed", "stuck", "overwhelmed"]
            ]

            print(
                f"[StandupBotAgent] Standup generated | "
                f"{len(developer_updates)} developers | "
                f"{len(blockers_found)} blockers found"
            )

            return {
                "success": True,
                "project_name": project_name,
                "sprint_name": sprint_name,
                "date": today,
                "day": day_name,
                "summary": summary_text,
                "stats": {
                    "total_developers": len(developer_updates),
                    "developers_with_blockers": blockers_found,
                    "developers_needing_help": needs_help,
                    "sprint_days_remaining": sprint_days_remaining,
                    "overall_completion_percentage": overall_completion_percentage,
                }
            }

        except Exception as e:
            print(f"[StandupBotAgent] Error: {str(e)}")
            return {
                "success": False,
                "project_name": project_name,
                "summary": None,
                "error": str(e),
            }

    def generate_async_standup(
        self,
        project_name: str,
        sprint_name: str,
        developer_updates: List[Dict]
    ) -> Dict:
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            updates_text = ""
            for update in developer_updates:
                updates_text += (
                    f"Developer: {update.get('name')}\n"
                    f"  Update: {update.get('update', 'No update provided')}\n\n"
                )

            user_message = (
                f"Generate a short async standup digest from these updates:\n\n"
                f"PROJECT: {project_name}\n"
                f"SPRINT: {sprint_name}\n"
                f"DATE: {today}\n\n"
                f"UPDATES:\n{updates_text}"
                f"Write a brief async digest with:\n"
                f"1. TEAM DIGEST SUMMARY in 2 sentences\n"
                f"2. KEY HIGHLIGHTS as bullet points in plain text\n"
                f"3. ACTION ITEMS if any\n"
                f"Keep it under 150 words total."
            )

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_message),
            ]

            print(f"[StandupBotAgent] Generating async standup digest for: {project_name}")
            response = self.llm(messages)

            return {
                "success": True,
                "project_name": project_name,
                "sprint_name": sprint_name,
                "date": today,
                "type": "async_digest",
                "summary": response.content.strip(),
            }

        except Exception as e:
            print(f"[StandupBotAgent] Error generating async standup: {str(e)}")
            return {
                "success": False,
                "summary": None,
                "error": str(e),
            }

    def generate_end_of_day_summary(
        self,
        project_name: str,
        sprint_name: str,
        tasks_completed_today: List[Dict],
        tasks_started_today: List[Dict],
        blockers_raised_today: List[str],
        prs_merged_today: int,
        commits_today: int
    ) -> Dict:
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            completed_text = ""
            for task in tasks_completed_today:
                completed_text += f"  - {task.get('title')} (by {task.get('assignee', 'Unknown')})\n"

            started_text = ""
            for task in tasks_started_today:
                started_text += f"  - {task.get('title')} (by {task.get('assignee', 'Unknown')})\n"

            blockers_text = ""
            if blockers_raised_today:
                for i, blocker in enumerate(blockers_raised_today):
                    blockers_text += f"  {i + 1}. {blocker}\n"
            else:
                blockers_text = "  None\n"

            user_message = (
                f"Generate an end of day summary for the team:\n\n"
                f"PROJECT: {project_name}\n"
                f"SPRINT: {sprint_name}\n"
                f"DATE: {today}\n\n"
                f"TODAY'S ACTIVITY:\n"
                f"  PRs Merged: {prs_merged_today}\n"
                f"  Commits Made: {commits_today}\n\n"
                f"TASKS COMPLETED TODAY:\n{completed_text if completed_text else '  None'}\n"
                f"TASKS STARTED TODAY:\n{started_text if started_text else '  None'}\n"
                f"BLOCKERS RAISED TODAY:\n{blockers_text}\n"
                f"Write an end of day summary with:\n"
                f"1. END OF DAY RECAP\n"
                f"2. WHAT GOT DONE\n"
                f"3. WHAT IS IN FLIGHT\n"
                f"4. BLOCKERS TO RESOLVE TOMORROW\n"
                f"5. CLOSING NOTE\n"
                f"Keep it concise and positive. Under 200 words."
            )

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_message),
            ]

            print(f"[StandupBotAgent] Generating end of day summary for: {project_name}")
            response = self.llm(messages)

            return {
                "success": True,
                "project_name": project_name,
                "sprint_name": sprint_name,
                "date": today,
                "type": "end_of_day",
                "summary": response.content.strip(),
                "stats": {
                    "tasks_completed_today": len(tasks_completed_today),
                    "tasks_started_today": len(tasks_started_today),
                    "blockers_raised": len(blockers_raised_today),
                    "prs_merged": prs_merged_today,
                    "commits": commits_today,
                }
            }

        except Exception as e:
            print(f"[StandupBotAgent] Error: {str(e)}")
            return {
                "success": False,
                "project_name": project_name,
                "summary": None,
                "error": str(e),
            }


if __name__ == "__main__":
    agent = StandupBotAgent()

    result = agent.generate_standup_summary(
        project_name="AI PM Boss",
        sprint_name="Sprint 3 - Core Agents",
        developer_updates=[
            {
                "name": "Sofi",
                "role": "Team Lead",
                "yesterday": "Reviewed all agent code and merged 2 PRs",
                "today": "Will finish the dashboard UI and test end to end flow",
                "blockers": "None",
                "mood": "energetic"
            },
            {
                "name": "Ali",
                "role": "Backend Developer",
                "yesterday": "Completed FastAPI routes for tasks and projects",
                "today": "Working on JWT authentication module",
                "blockers": "Need clarification on token expiry time",
                "mood": "neutral"
            },
            {
                "name": "Sara",
                "role": "Frontend Developer",
                "yesterday": "Built Kanban board component",
                "today": "Will connect Kanban to live backend API",
                "blockers": "None",
                "mood": "energetic"
            },
            {
                "name": "Zain",
                "role": "AI Engineer",
                "yesterday": "Finished delay predictor agent",
                "today": "Starting standup bot and report generator testing",
                "blockers": "LangChain version conflict with pydantic",
                "mood": "stuck"
            },
        ],
        sprint_days_remaining=2,
        overall_completion_percentage=68.5
    )

    print(result.get("summary"))
    print("\nStats:")
    print(json.dumps(result.get("stats"), indent=2))

