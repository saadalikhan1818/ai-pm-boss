# backend/workers/celery_app.py
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ai_pm_boss",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "run-standup-every-morning": {
            "task": "workers.tasks.run_daily_standup",
            "schedule": 86400.0,
        },
        "check-delays-every-hour": {
            "task": "workers.tasks.check_sprint_delays",
            "schedule": 3600.0,
        },
    },
)