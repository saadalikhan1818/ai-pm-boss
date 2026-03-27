# backend/agents/delay_predictor.py
import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class RiskFactor(BaseModel):
    factor: str = Field(description="Name of the risk factor")
    severity: str = Field(description="Severity level: low, medium, high, critical")
    impact: str = Field(description="Description of how this factor impacts the sprint")


class DelayPrediction(BaseModel):
    delay_likelihood: float = Field(description="Probability of delay between 0.0 and 1.0")
    predicted_delay_days: int = Field(description="Estimated number of days the sprint will be delayed")
    risk_level: str = Field(description="Overall risk level: green, yellow, orange, red")
    risk_factors: List[RiskFactor] = Field(description="List of identified risk factors")
    recommendations: List[str] = Field(description="List of actionable recommendations to prevent delay")
    summary: str = Field(description="Short summary of the sprint health in 2 to 3 sentences")


class DelayPredictorAgent:

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=0.2,
        )

        self.system_prompt = (
            "You are an expert AI Scrum Master and project risk analyst. "
            "Your job is to analyze sprint data and predict whether a sprint will be delayed. "
            "Rules: "
            "Analyze task completion rates, blockers, and team velocity carefully. "
            "delay_likelihood must be a float between 0.0 and 1.0. "
            "predicted_delay_days must be a realistic integer, 0 if no delay expected. "
            "risk_level must be exactly one of: green, yellow, orange, red. "
            "green means on track, yellow means slight risk, orange means at risk, red means critical. "
            "recommendations must be specific and actionable, not generic advice. "
            "Always return valid JSON only, no extra text or explanation."
        )

    def predict_delay(
        self,
        sprint_name: str,
        start_date: str,
        end_date: str,
        total_tasks: int,
        completed_tasks: int,
        in_progress_tasks: int,
        blocked_tasks: int,
        team_size: int,
        velocity_last_sprint: int,
        current_velocity: int,
        blockers: List[str] = None
    ) -> Dict:
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            today_dt = datetime.now()

            total_days = (end - start).days
            days_elapsed = (today_dt - start).days
            days_remaining = (end - today_dt).days

            todo_tasks = total_tasks - completed_tasks - in_progress_tasks - blocked_tasks

            completion_percentage = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0
            time_elapsed_percentage = round((days_elapsed / total_days) * 100, 1) if total_days > 0 else 0

            blockers_text = ""
            if blockers:
                for i, blocker in enumerate(blockers):
                    blockers_text += f"  {i + 1}. {blocker}\n"
            else:
                blockers_text = "  None reported\n"

            user_message = (
                f"Analyze this sprint and predict delay risk:\n\n"
                f"Sprint Name: {sprint_name}\n"
                f"Today Date: {today}\n"
                f"Sprint Start: {start_date}\n"
                f"Sprint End: {end_date}\n"
                f"Total Sprint Days: {total_days}\n"
                f"Days Elapsed: {days_elapsed}\n"
                f"Days Remaining: {days_remaining}\n"
                f"Time Elapsed: {time_elapsed_percentage}%\n\n"
                f"Task Breakdown:\n"
                f"  Total Tasks: {total_tasks}\n"
                f"  Completed: {completed_tasks}\n"
                f"  In Progress: {in_progress_tasks}\n"
                f"  Blocked: {blocked_tasks}\n"
                f"  Todo: {todo_tasks}\n"
                f"  Completion: {completion_percentage}%\n\n"
                f"Team Info:\n"
                f"  Team Size: {team_size} developers\n"
                f"  Velocity Last Sprint: {velocity_last_sprint} tasks\n"
                f"  Current Sprint Velocity: {current_velocity} tasks completed so far\n\n"
                f"Active Blockers:\n{blockers_text}\n"
                f"Return a JSON object with these exact fields:\n"
                f"delay_likelihood, predicted_delay_days, risk_level, risk_factors, recommendations, summary\n"
                f"Each item in risk_factors must have: factor, severity, impact\n"
                f"Return only valid JSON, nothing else."
            )

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_message),
            ]

            print(f"[DelayPredictorAgent] Analyzing sprint: {sprint_name}")
            response = self.llm(messages)

            clean_response = response.content.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("\n", 1)[1]
                clean_response = clean_response.rsplit("```", 1)[0]

            prediction_data = json.loads(clean_response)

            print(
                f"[DelayPredictorAgent] Risk Level: {prediction_data.get('risk_level')} | "
                f"Delay Likelihood: {prediction_data.get('delay_likelihood')} | "
                f"Predicted Delay: {prediction_data.get('predicted_delay_days')} days"
            )

            return {
                "success": True,
                "sprint_name": sprint_name,
                "analyzed_on": today,
                "sprint_stats": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "completion_percentage": completion_percentage,
                    "days_remaining": days_remaining,
                    "time_elapsed_percentage": time_elapsed_percentage,
                },
                "prediction": prediction_data,
            }

        except Exception as e:
            print(f"[DelayPredictorAgent] Error: {str(e)}")
            return {
                "success": False,
                "sprint_name": sprint_name,
                "prediction": None,
                "error": str(e),
            }

    def analyze_multiple_sprints(self, sprints: List[Dict]) -> List[Dict]:
        results = []

        for sprint in sprints:
            result = self.predict_delay(
                sprint_name=sprint.get("name", "Unknown Sprint"),
                start_date=sprint.get("start_date"),
                end_date=sprint.get("end_date"),
                total_tasks=sprint.get("total_tasks", 0),
                completed_tasks=sprint.get("completed_tasks", 0),
                in_progress_tasks=sprint.get("in_progress_tasks", 0),
                blocked_tasks=sprint.get("blocked_tasks", 0),
                team_size=sprint.get("team_size", 1),
                velocity_last_sprint=sprint.get("velocity_last_sprint", 0),
                current_velocity=sprint.get("current_velocity", 0),
                blockers=sprint.get("blockers", [])
            )
            results.append(result)

        critical = [
            r for r in results
            if r.get("prediction", {}).get("risk_level") in ["orange", "red"]
        ]

        print(f"[DelayPredictorAgent] Analyzed {len(results)} sprints | {len(critical)} at risk")
        return results

    def get_alert_message(self, prediction_result: Dict) -> str:
        if not prediction_result.get("success"):
            return "Could not analyze sprint risk."

        prediction = prediction_result.get("prediction", {})
        risk_level = prediction.get("risk_level", "green")
        sprint_name = prediction_result.get("sprint_name", "Sprint")
        delay_days = prediction.get("predicted_delay_days", 0)
        likelihood = prediction.get("delay_likelihood", 0)

        if risk_level == "green":
            return f"Sprint {sprint_name} is on track. No delays expected."
        elif risk_level == "yellow":
            return (
                f"Warning: Sprint {sprint_name} has slight risk. "
                f"Delay likelihood: {round(likelihood * 100)}%."
            )
        elif risk_level == "orange":
            return (
                f"Alert: Sprint {sprint_name} is at risk of {delay_days} day delay. "
                f"Immediate attention needed. Delay likelihood: {round(likelihood * 100)}%."
            )
        elif risk_level == "red":
            return (
                f"Critical: Sprint {sprint_name} will likely be delayed by {delay_days} days. "
                f"Escalate to manager now. Delay likelihood: {round(likelihood * 100)}%."
            )
        return "Unable to determine sprint risk level."


if __name__ == "__main__":
    agent = DelayPredictorAgent()

    result = agent.predict_delay(
        sprint_name="Sprint 4 - Auth Module",
        start_date="2024-01-15",
        end_date="2024-01-29",
        total_tasks=20,
        completed_tasks=6,
        in_progress_tasks=4,
        blocked_tasks=3,
        team_size=4,
        velocity_last_sprint=18,
        current_velocity=6,
        blockers=[
            "API keys for third party service not received",
            "Developer sick for 2 days",
            "Database migration failed twice"
        ]
    )

    print(json.dumps(result, indent=2))
    print("\nAlert Message:")
    print(agent.get_alert_message(result))