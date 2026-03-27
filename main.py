import os
import json
import requests
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from groq import Groq
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO") 

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY")) 
MODEL_NAME = "llama-3.3-70b-versatile"

app = FastAPI()

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Database Configuration
DATABASE_URL = "sqlite:///./aipm_boss.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Database Models
class ProjectTable(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)

class TaskTable(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    status = Column(String, default="to-do")
    project_id = Column(Integer)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- HELPER CLASSES ---

class GitHubManager:
    @staticmethod
    def create_issue(title: str, body: str):
        if not GITHUB_TOKEN or not GITHUB_REPO:
            return {"error": "GitHub credentials missing from .env"}
            
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {"title": title, "body": body}
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

# --- TASK & PROJECT MANAGEMENT ROUTES ---

@app.get("/tasks/")
def read_tasks(db: Session = Depends(get_db)):
    return db.query(TaskTable).all()

@app.put("/tasks/{task_id}")
def update_task_status(task_id: int, data: dict, db: Session = Depends(get_db)):
    db_task = db.query(TaskTable).filter(TaskTable.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if "status" in data:
        db_task.status = data["status"]
        db.commit()
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskTable).filter(TaskTable.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Deleted successfully"}

@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    return db.query(ProjectTable).all()

@app.post("/projects/")
def create_project(project: dict, db: Session = Depends(get_db)):
    new_project = ProjectTable(name=project["name"], description=project.get("description", ""))
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

# --- AI AGENT ROUTES ---

@app.get("/agents/architect/{task_id}")
def get_architect_blueprint(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskTable).filter(TaskTable.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    prompt = f"Provide a technical implementation blueprint for this task: {task.title}."
    try:
        completion = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        return {"blueprint": completion.choices[0].message.content}
    except Exception as e:
        return {"blueprint": f"Error: {str(e)}"}

@app.post("/agents/task-creator")
async def task_creator(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    command = data.get("command")
    project_id = data.get("project_id")
    prompt = f"Decompose this command into a JSON list of tasks: {command}. Return ONLY a JSON list, e.g., ['Task 1', 'Task 2']"
    try:
        completion = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        raw = completion.choices[0].message.content.strip()
        # Clean AI markdown formatting
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        tasks = json.loads(raw)
        for t in tasks:
            db.add(TaskTable(title=t, project_id=project_id, status="to-do"))
        db.commit()
        return {"status": "success", "count": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Task Creation failed: {str(e)}")

@app.post("/agents/risk-detector")
async def risk_detector(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    project_id = data.get("project_id")
    tasks = db.query(TaskTable).filter(TaskTable.project_id == project_id).all()
    task_context = ", ".join([t.title for t in tasks])
    prompt = f"Analyze these tasks for potential project risks or blockers: {task_context}. Provide a brief warning."
    try:
        completion = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        return {"risk_report": completion.choices[0].message.content}
    except Exception as e:
        return {"risk_report": f"Risk analysis error: {str(e)}"}

@app.post("/agents/extract-tasks")
async def extract_tasks(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    report = data.get("report")
    project_id = data.get("project_id")
    prompt = f"Extract a JSON list of task titles from this standup report: {report}. Return ONLY the list."
    try:
        completion = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        raw = completion.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        task_list = json.loads(raw)
        for title in task_list:
            db.add(TaskTable(title=title, project_id=project_id, status="to-do"))
        db.commit()
        return {"status": "success", "extracted": task_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to extract tasks")

# --- INTEGRATION ROUTES ---

@app.post("/integrations/github/sync/{task_id}")
async def sync_task_to_github(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskTable).filter(TaskTable.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    prompt = f"Write a professional GitHub Issue description for this task: {task.title}. Include an 'Implementation Plan' section."
    try:
        completion = client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        issue_body = completion.choices[0].message.content
        gh_response = GitHubManager.create_issue(task.title, issue_body)
        
        if "html_url" in gh_response:
            return {"status": "synced", "url": gh_response["html_url"]}
        return {"status": "error", "details": gh_response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Start the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)