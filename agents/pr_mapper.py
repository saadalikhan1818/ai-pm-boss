# backend/agents/pr_mapper.py

from typing import List, Dict


class PRMapperAgent:

    def __init__(self):
        pass

    def map_pr_to_task(
        self,
        pr_title: str,
        pr_description: str,
        pr_state: str,
        tasks: List[Dict]
    ) -> Dict:
        """
        Simple PR to task mapping (no AI, demo-safe)
        """

        pr_text = (pr_title + " " + pr_description).lower()

        best_match = None

        for task in tasks:
            task_title = task.get("title", "").lower()

            # simple keyword match
            if any(word in pr_text for word in task_title.split()):
                best_match = task
                break

        if best_match:
            return {
                "success": True,
                "pr_title": pr_title,
                "pr_state": pr_state,
                "mapping": {
                    "task_id": best_match.get("id"),
                    "task_title": best_match.get("title"),
                    "confidence": 0.85,
                    "reason": "Keyword match between PR and task",
                    "status_update": "in_progress" if pr_state == "open" else "done",
                },
            }

        # fallback
        return {
            "success": False,
            "pr_title": pr_title,
            "pr_state": pr_state,
            "mapping": None,
            "error": "No matching task found",
        }

    def map_multiple_prs(self, prs: List[Dict], tasks: List[Dict]) -> List[Dict]:
        results = []

        for pr in prs:
            result = self.map_pr_to_task(
                pr_title=pr.get("title", ""),
                pr_description=pr.get("description", ""),
                pr_state=pr.get("state", "open"),
                tasks=tasks
            )
            result["pr_number"] = pr.get("number")
            result["pr_url"] = pr.get("url", "")
            results.append(result)

        return results

    def get_status_update(self, pr_state: str, merged: bool) -> str:
        if merged:
            return "done"
        elif pr_state == "open":
            return "in_progress"
        return "todo"