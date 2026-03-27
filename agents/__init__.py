# backend/agents/__init__.py
# backend/agents/__init__.py
# ─────────────────────────────────────────────────────────────────────────────
# This file makes the `agents` directory a Python package and exposes all
# agent classes/functions so they can be imported cleanly from anywhere.
#
# Usage example (in a router):
#   from agents import TaskCreatorAgent, DelayPredictorAgent
# ─────────────────────────────────────────────────────────────────────────────

from agents.task_creator import TaskCreatorAgent
from agents.pr_mapper import PRMapperAgent
from agents.delay_predictor import DelayPredictorAgent
from agents.report_generator import ReportGeneratorAgent
from agents.standup_bot import StandupBotAgent

# ─────────────────────────────────────────────────────────────────────────────
# __all__ controls what gets exported when someone does `from agents import *`
# ─────────────────────────────────────────────────────────────────────────────
__all__ = [
    "TaskCreatorAgent",
    "PRMapperAgent",
    "DelayPredictorAgent",
    "ReportGeneratorAgent",
    "StandupBotAgent",
]