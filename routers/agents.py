# backend/routers/agents.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.task import Task
from models.project import Project
from models.sprint import Sprint
from agents.task_creator import TaskCreatorAgent
from agents.pr_mapper import PRMapperAgent
from agents.delay_predictor import DelayPredictorAgent
from agents.report_generator import ReportGeneratorAgent
from agents.standup_bot import StandupBotAgent
from pydantic import BaseModel

router = APIRouter()


class TaskCreatorRequest(BaseModel):
    requirement: str
    project_name: str
    project_id: Optional[int] = None


class PRMapperRequest(BaseModel):
    pr_title: str
    pr_description: str
    pr_state: str
    project_id: int


class DelayPredictorRequest(BaseModel):
    sprint_id: int
    sprint_name: str
    start_date: str
    end_date: str
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    team_size: int
    velocity_last_sprint: int
    current_velocity: int
    blockers: Optional[List[str]] = []


class ReportRequest(BaseModel):
    project_id: int
    project_name: str
    sprint_name: str
    week_number: int
    sprint_velocity: int
    target_velocity: int
    blockers: Optional[List[str]] = []
    notes: Optional[str] = ""


class StandupRequest(BaseModel):
    project_name: str
    sprint_name: str
    sprint_days_remaining: int
    overall_completion_percentage: float
    developer_updates: List[dict]


@router.post("/create-tasks")
def create_tasks(request: TaskCreatorRequest, db: Session = Depends(get_db)):
    try:
        print(f"[Agents Router] Triggering Task Creator Agent for: {request.project_name}")
        agent = TaskCreatorAgent()
        result = agent.create_tasks(
            requirement=request.requirement,
            project_name=request.project_name,
        )
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Agent failed"))
        if request.project_id:
            for task_data in result.get("tasks", []):
                new_task = Task(
                    title=task_data.get("title"),
                    description=task_data.get("description"),
                    status="todo",
                    priority=task_data.get("priority", "medium"),
                    project_id=request.project_id,
                )
                db.add(new_task)
            db.commit()
            print(f"[Agents Router] Saved {len(result.get('tasks', []))} tasks to database")
        return {
            "success": True,
            "message": f"Created {result.get('total_tasks')} tasks successfully",
            "data": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/map-pr")
def map_pr(request: PRMapperRequest, db: Session = Depends(get_db)):
    try:
        print(f"[Agents Router] Triggering PR Mapper Agent for PR: {request.pr_title}")
        tasks = db.query(Task).filter(Task.project_id == request.project_id).all()
        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found for this project")
        tasks_list = [
            {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
            }
            for task in tasks
        ]
        agent = PRMapperAgent()
        result = agent.map_pr_to_task(
            pr_title=request.pr_title,
            pr_description=request.pr_description,
            pr_state=request.pr_state,
            tasks=tasks_list,
        )
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Agent failed"))
        mapping = result.get("mapping", {})
        if mapping.get("confidence", 0) >= 0.7 and mapping.get("task_id"):
            task = db.query(Task).filter(Task.id == int(mapping.get("task_id"))).first()
            if task:
                task.status = mapping.get("status_update", "in_progress")
                db.commit()
                print(f"[Agents Router] Updated task {task.id} status to {task.status}")
        return {
            "success": True,
            "message": "PR mapped successfully",
            "data": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-delay")
def predict_delay(request: DelayPredictorRequest):
    try:
        print(f"[Agents Router] Triggering Delay Predictor for sprint: {request.sprint_name}")
        agent = DelayPredictorAgent()
        result = agent.predict_delay(
            sprint_name=request.sprint_name,
            start_date=request.start_date,
            end_date=request.end_date,
            total_tasks=request.total_tasks,
            completed_tasks=request.completed_tasks,
            in_progress_tasks=request.in_progress_tasks,
            blocked_tasks=request.blocked_tasks,
            team_size=request.team_size,
            velocity_last_sprint=request.velocity_last_sprint,
            current_velocity=request.current_velocity,
            blockers=request.blockers,
        )
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Agent failed"))
        alert_message = agent.get_alert_message(result)
        return {
            "success": True,
            "message": alert_message,
            "data": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-report")
def generate_report(request: ReportRequest, db: Session = Depends(get_db)):
    try:
        print(f"[Agents Router] Triggering Report Generator for: {request.project_name}")
        completed_tasks = db.query(Task).filter(
            Task.project_id == request.project_id,
            Task.status == "done"
        ).all()
        in_progress_tasks = db.query(Task).filter(
            Task.project_id == request.project_id,
            Task.status == "in_progress"
        ).all()
        blocked_tasks = db.query(Task).filter(
            Task.project_id == request.project_id,
            Task.status == "blocked"
        ).all()
        upcoming_tasks = db.query(Task).filter(
            Task.project_id == request.project_id,
            Task.status == "todo"
        ).all()
        completed_list = [{"title": t.title, "priority": t.priority} for t in completed_tasks]
        in_progress_list = [{"title": t.title, "priority": t.priority, "assignee": str(t.assignee_id)} for t in in_progress_tasks]
        blocked_list = [{"title": t.title, "blocked_reason": "Under investigation"} for t in blocked_tasks]
        upcoming_list = [{"title": t.title, "priority": t.priority} for t in upcoming_tasks]
        agent = ReportGeneratorAgent()
        result = agent.generate_weekly_report(
            project_name=request.project_name,
            sprint_name=request.sprint_name,
            week_number=request.week_number,
            team_members=[],
            completed_tasks=completed_list,
            in_progress_tasks=in_progress_list,
            blocked_tasks=blocked_list,
            upcoming_tasks=upcoming_list,
            sprint_velocity=request.sprint_velocity,
            target_velocity=request.target_velocity,
            blockers=request.blockers,
            notes=request.notes,
        )
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Agent failed"))
        return {
            "success": True,
            "message": "Report generated successfully",
            "data": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/standup")
def run_standup(request: StandupRequest):
    try:
        print(f"[Agents Router] Triggering Standup Bot for: {request.project_name}")
        agent = StandupBotAgent()
        result = agent.generate_standup_summary(
            project_name=request.project_name,
            sprint_name=request.sprint_name,
            developer_updates=request.developer_updates,
            sprint_days_remaining=request.sprint_days_remaining,
            overall_completion_percentage=request.overall_completion_percentage,
        )
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Agent failed"))
        return {
            "success": True,
            "message": "Standup summary generated successfully",
            "data": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))