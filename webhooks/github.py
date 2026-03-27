# backend/webhooks/github.py
from fastapi import APIRouter, Request, HTTPException
from agents.task_creator import TaskCreatorAgent
from agents.pr_mapper import PRMapperAgent
from database import SessionLocal
from models.task import Task
import hmac
import hashlib
import os

router = APIRouter()

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_github_signature(payload: bytes, signature: str) -> bool:
    try:
        mac = hmac.new(
            GITHUB_WEBHOOK_SECRET.encode(),
            msg=payload,
            digestmod=hashlib.sha256
        )
        expected_signature = f"sha256={mac.hexdigest()}"
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        return False


@router.post("/")
async def github_webhook(request: Request):
    try:
        payload = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")

        if GITHUB_WEBHOOK_SECRET and not verify_github_signature(payload, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        event_type = request.headers.get("X-GitHub-Event", "")
        data = await request.json()

        print(f"[GitHub Webhook] Received event: {event_type}")

        if event_type == "pull_request":
            await handle_pull_request(data)

        elif event_type == "push":
            await handle_push(data)

        elif event_type == "issues":
            await handle_issues(data)

        return {"success": True, "event": event_type}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[GitHub Webhook] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_pull_request(data: dict):
    try:
        action = data.get("action")
        pr = data.get("pull_request", {})
        pr_title = pr.get("title", "")
        pr_body = pr.get("body", "") or ""
        pr_state = pr.get("state", "open")
        pr_number = pr.get("number")
        merged = pr.get("merged", False)

        print(f"[GitHub Webhook] PR {action}: #{pr_number} - {pr_title}")

        if action in ["opened", "closed", "reopened", "synchronize"]:
            db = SessionLocal()
            tasks = db.query(Task).all()
            tasks_list = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                }
                for task in tasks
            ]

            if tasks_list:
                agent = PRMapperAgent()
                result = agent.map_pr_to_task(
                    pr_title=pr_title,
                    pr_description=pr_body,
                    pr_state=pr_state,
                    tasks=tasks_list,
                )

                mapping = result.get("mapping", {})
                if mapping and mapping.get("confidence", 0) >= 0.7:
                    task_id = mapping.get("task_id")
                    if task_id:
                        task = db.query(Task).filter(Task.id == int(task_id)).first()
                        if task:
                            if merged:
                                task.status = "done"
                            elif action == "opened":
                                task.status = "in_progress"
                            db.commit()
                            print(f"[GitHub Webhook] Updated task {task_id} status to {task.status}")

            db.close()

    except Exception as e:
        print(f"[GitHub Webhook] Error handling PR: {str(e)}")


async def handle_push(data: dict):
    try:
        commits = data.get("commits", [])
        branch = data.get("ref", "").replace("refs/heads/", "")
        pusher = data.get("pusher", {}).get("name", "Unknown")

        print(f"[GitHub Webhook] Push to {branch} by {pusher} with {len(commits)} commits")

        for commit in commits:
            message = commit.get("message", "")
            print(f"[GitHub Webhook] Commit: {message}")

    except Exception as e:
        print(f"[GitHub Webhook] Error handling push: {str(e)}")


async def handle_issues(data: dict):
    try:
        action = data.get("action")
        issue = data.get("issue", {})
        issue_title = issue.get("title", "")
        issue_body = issue.get("body", "") or ""

        print(f"[GitHub Webhook] Issue {action}: {issue_title}")

        if action == "opened":
            agent = TaskCreatorAgent()
            result = agent.create_tasks(
                requirement=f"{issue_title}\n\n{issue_body}",
                project_name="GitHub Issues",
            )
            print(f"[GitHub Webhook] Created {result.get('total_tasks', 0)} tasks from issue")

    except Exception as e:
        print(f"[GitHub Webhook] Error handling issue: {str(e)}")