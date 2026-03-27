# backend/workers/tasks.pyimport os
from workers.celery_app import celery_app
from agents.task_creator import TaskCreatorAgent
from agents.delay_predictor import DelayPredictorAgent
from agents.report_generator import ReportGeneratorAgent
from agents.standup_bot import StandupBotAgent
from database import SessionLocal
from models.task import Task
from models.project import Project
from models.sprint import Sprint


@celery_app.task(name="workers.tasks.create_tasks_from_requirement")
def create_tasks_from_requirement(requirement: str, project_name: str, project_id: int):
    try:
        print(f"[Worker] Creating tasks for project: {project_name}")
        agent = TaskCreatorAgent()
        result = agent.create_tasks(
            requirement=requirement,
            project_name=project_name,
        )
        if result.get("success") and project_id:
            db = SessionLocal()
            for task_data in result.get("tasks", []):
                new_task = Task(
                    title=task_data.get("title"),
                    description=task_data.get("description"),
                    status="todo",
                    priority=task_data.get("priority", "medium"),
                    project_id=project_id,
                )
                db.add(new_task)
            db.commit()
            db.close()
            print(f"[Worker] Saved {len(result.get('tasks', []))} tasks to database")
        return result
    except Exception as e:
        print(f"[Worker] Error creating tasks: {str(e)}")
        return {"success": False, "error": str(e)}


@celery_app.task(name="workers.tasks.check_sprint_delays")
def check_sprint_delays():
    try:
        print("[Worker] Checking sprint delays...")
        db = SessionLocal()
        sprints = db.query(Sprint).filter(Sprint.status == "active").all()
        agent = DelayPredictorAgent()
        alerts = []
        for sprint in sprints:
            total_tasks = db.query(Task).filter(Task.project_id == sprint.project_id).count()
            completed_tasks = db.query(Task).filter(
                Task.project_id == sprint.project_id,
                Task.status == "done"
            ).count()
            in_progress_tasks = db.query(Task).filter(
                Task.project_id == sprint.project_id,
                Task.status == "in_progress"
            ).count()
            blocked_tasks = db.query(Task).filter(
                Task.project_id == sprint.project_id,
                Task.status == "blocked"
            ).count()
            result = agent.predict_delay(
                sprint_name=sprint.name,
                start_date=sprint.start_date.strftime("%Y-%m-%d"),
                end_date=sprint.end_date.strftime("%Y-%m-%d"),
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                in_progress_tasks=in_progress_tasks,
                blocked_tasks=blocked_tasks,
                team_size=4,
                velocity_last_sprint=10,
                current_velocity=completed_tasks,
                blockers=[],
            )
            alert_message = agent.get_alert_message(result)
            alerts.append({
                "sprint": sprint.name,
                "alert": alert_message,
                "risk_level": result.get("prediction", {}).get("risk_level", "green"),
            })
            print(f"[Worker] Sprint {sprint.name}: {alert_message}")
        db.close()
        return {"success": True, "alerts": alerts}
    except Exception as e:
        print(f"[Worker] Error checking delays: {str(e)}")
        return {"success": False, "error": str(e)}


@celery_app.task(name="workers.tasks.run_daily_standup")
def run_daily_standup():
    try:
        print("[Worker] Running daily standup...")
        db = SessionLocal()
        projects = db.query(Project).filter(Project.status == "active").all()
        agent = StandupBotAgent()
        results = []
        for project in projects:
            tasks = db.query(Task).filter(Task.project_id == project.id).all()
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.status == "done"])
            completion_percentage = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0
            result = agent.generate_standup_summary(
                project_name=project.name,
                sprint_name="Current Sprint",
                developer_updates=[],
                sprint_days_remaining=5,
                overall_completion_percentage=completion_percentage,
            )
            results.append({
                "project": project.name,
                "summary": result.get("summary", ""),
            })
            print(f"[Worker] Standup generated for project: {project.name}")
        db.close()
        return {"success": True, "results": results}
    except Exception as e:
        print(f"[Worker] Error running standup: {str(e)}")
        return {"success": False, "error": str(e)}


@celery_app.task(name="workers.tasks.generate_weekly_reports")
def generate_weekly_reports():
    try:
        print("[Worker] Generating weekly reports...")
        db = SessionLocal()
        projects = db.query(Project).filter(Project.status == "active").all()
        agent = ReportGeneratorAgent()
        results = []
        for project in projects:
            completed_tasks = db.query(Task).filter(
                Task.project_id == project.id,
                Task.status == "done"
            ).all()
            in_progress_tasks = db.query(Task).filter(
                Task.project_id == project.id,
                Task.status == "in_progress"
            ).all()
            blocked_tasks = db.query(Task).filter(
                Task.project_id == project.id,
                Task.status == "blocked"
            ).all()
            upcoming_tasks = db.query(Task).filter(
                Task.project_id == project.id,
                Task.status == "todo"
            ).all()
            result = agent.generate_weekly_report(
                project_name=project.name,
                sprint_name="Current Sprint",
                week_number=1,
                team_members=[],
                completed_tasks=[{"title": t.title, "priority": t.priority} for t in completed_tasks],
                in_progress_tasks=[{"title": t.title, "priority": t.priority, "assignee": str(t.assignee_id)} for t in in_progress_tasks],
                blocked_tasks=[{"title": t.title, "blocked_reason": "Under investigation"} for t in blocked_tasks],
                upcoming_tasks=[{"title": t.title, "priority": t.priority} for t in upcoming_tasks],
                sprint_velocity=len(completed_tasks),
                target_velocity=20,
                blockers=[],
                notes="",
            )
            results.append({
                "project": project.name,
                "report": result.get("report", ""),
            })
            print(f"[Worker] Report generated for project: {project.name}")
        db.close()
        return {"success": True, "results": results}
    except Exception as e:
        print(f"[Worker] Error generating reports: {str(e)}")
        return {"success": False, "error": str(e)}