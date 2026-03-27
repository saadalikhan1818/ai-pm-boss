# backend/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.task import Task
from schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter()


@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    try:
        new_task = Task(
            title=task.title,
            description=task.description,
            status="todo",
            priority=task.priority,
            project_id=task.project_id,
            assignee_id=task.assignee_id,
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        print(f"[Tasks Router] Created task: {new_task.title}")
        return new_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}", response_model=List[TaskResponse])
def get_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        print(f"[Tasks Router] Fetched {len(tasks)} tasks for project {project_id}")
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).all()
        print(f"[Tasks Router] Fetched {len(tasks)} tasks")
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.status is not None:
            task.status = task_update.status
        if task_update.priority is not None:
            task.priority = task_update.priority
        if task_update.assignee_id is not None:
            task.assignee_id = task_update.assignee_id
        db.commit()
        db.refresh(task)
        print(f"[Tasks Router] Updated task: {task.title}")
        return task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(task)
        db.commit()
        print(f"[Tasks Router] Deleted task id: {task_id}")
        return {"message": "Task deleted successfully", "id": task_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))