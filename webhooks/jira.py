from fastapi import APIRouter, Request, HTTPException
from agents.task_creator import TaskCreatorAgent
from agents.delay_predictor import DelayPredictorAgent
from database import SessionLocal
from models.task import Task
from models.project import Project
import os

router = APIRouter()

JIRA_WEBHOOK_SECRET = os.getenv("JIRA_WEBHOOK_SECRET", "")


@router.post("/")
async def jira_webhook(request: Request):
    try:
        data = await request.json()
        event_type = data.get("webhookEvent", "")

        print(f"[Jira Webhook] Received event: {event_type}")

        if event_type == "jira:issue_created":
            await handle_issue_created(data)

        elif event_type == "jira:issue_updated":
            await handle_issue_updated(data)

        elif event_type == "jira:issue_deleted":
            await handle_issue_deleted(data)

        elif event_type == "sprint_started":
            await handle_sprint_started(data)

        elif event_type == "sprint_closed":
            await handle_sprint_closed(data)

        return {"success": True, "event": event_type}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Jira Webhook] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_issue_created(data: dict):
    try:
        issue = data.get("issue", {})
        fields = issue.get("fields", {})
        issue_key = issue.get("key", "")
        summary = fields.get("summary", "")
        description = fields.get("description", "") or ""
        priority = fields.get("priority", {}).get("name", "medium").lower()
        project_name = fields.get("project", {}).get("name", "Jira Project")

        print(f"[Jira Webhook] Issue created: {issue_key} - {summary}")

        db = SessionLocal()
        project = db.query(Project).filter(Project.name == project_name).first()

        if not project:
            project = Project(
                name=project_name,
                description="Imported from Jira",
                status="active",
            )
            db.add(project)
            db.commit()
            db.refresh(project)

        new_task = Task(
            title=summary,
            description=description,
            status="todo",
            priority=priority if priority in ["low", "medium", "high"] else "medium",
            project_id=project.id,
        )
        db.add(new_task)
        db.commit()
        db.close()

    except Exception as e:
        print(f"[Jira Webhook] Error handling issue created: {str(e)}")


async def handle_issue_updated(data: dict):
    try:
        issue = data.get("issue", {})
        fields = issue.get("fields", {})
        issue_key = issue.get("key", "")
        summary = fields.get("summary", "")
        changelog = data.get("changelog", {})
        changed_items = changelog.get("items", [])

        print(f"[Jira Webhook] Issue updated: {issue_key} - {summary}")

        status_map = {
            "to do": "todo",
            "in progress": "in_progress",
            "done": "done",
            "blocked": "blocked",
        }

        for item in changed_items:
            field = item.get("field", "")
            to_string = item.get("toString", "").lower()

            if field == "status":
                mapped_status = status_map.get(to_string, "todo")
                db = SessionLocal()
                task = db.query(Task).filter(Task.title == summary).first()
                if task:
                    task.status = mapped_status
                    db.commit()
                db.close()

    except Exception as e:
        print(f"[Jira Webhook] Error handling issue updated: {str(e)}")


async def handle_issue_deleted(data: dict):
    try:
        issue = data.get("issue", {})
        fields = issue.get("fields", {})
        summary = fields.get("summary", "")
        issue_key = issue.get("key", "")

        print(f"[Jira Webhook] Issue deleted: {issue_key} - {summary}")

        db = SessionLocal()
        task = db.query(Task).filter(Task.title == summary).first()
        if task:
            db.delete(task)
            db.commit()
        db.close()

    except Exception as e:
        print(f"[Jira Webhook] Error handling issue deleted: {str(e)}")


async def handle_sprint_started(data: dict):
    try:
        sprint = data.get("sprint", {})
        sprint_name = sprint.get("name", "")
        sprint_goal = sprint.get("goal", "") or ""

        print(f"[Jira Webhook] Sprint started: {sprint_name}")

        if sprint_goal:
            agent = TaskCreatorAgent()
            result = agent.create_tasks(
                requirement=sprint_goal,
                project_name=sprint_name,
            )
            print(f"[Jira Webhook] Created {result.get('total_tasks', 0)} tasks from sprint goal")

    except Exception as e:
        print(f"[Jira Webhook] Error handling sprint started: {str(e)}")


async def handle_sprint_closed(data: dict):
    try:
        sprint = data.get("sprint", {})
        sprint_name = sprint.get("name", "")

        print(f"[Jira Webhook] Sprint closed: {sprint_name}")

        db = SessionLocal()
        total_tasks = db.query(Task).count()
        completed_tasks = db.query(Task).filter(Task.status == "done").count()
        completion_rate = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0

        print(f"[Jira Webhook] Sprint {sprint_name} closed with {completion_rate}% completion rate")
        db.close()

    except Exception as e:
        print(f"[Jira Webhook] Error handling sprint closed: {str(e)}")