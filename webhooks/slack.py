# backend/webhooks/slack.py
from fastapi import APIRouter, Request, HTTPException
from agents.task_creator import TaskCreatorAgent
from agents.standup_bot import StandupBotAgent
import os

router = APIRouter()

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")


@router.post("/")
async def slack_webhook(request: Request):
    try:
        data = await request.json()

        if data.get("type") == "url_verification":
            return {"challenge": data.get("challenge")}

        event = data.get("event", {})
        event_type = event.get("type", "")

        print(f"[Slack Webhook] Received event: {event_type}")

        if event_type == "message":
            await handle_message(event)

        elif event_type == "app_mention":
            await handle_mention(event)

        return {"success": True, "event": event_type}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Slack Webhook] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_message(event: dict):
    try:
        text = event.get("text", "")
        channel = event.get("channel", "general")
        user = event.get("user", "unknown")
        bot_id = event.get("bot_id")

        if bot_id:
            return

        print(f"[Slack Webhook] Message from {user} in #{channel}: {text}")

        keywords = ["build", "create", "implement", "add feature", "fix", "develop", "need", "require"]
        if any(keyword in text.lower() for keyword in keywords):
            agent = TaskCreatorAgent()
            result = agent.create_tasks_from_slack(
                slack_message=text,
                channel=channel,
            )
            print(f"[Slack Webhook] Created {result.get('total_tasks', 0)} tasks from Slack message")

    except Exception as e:
        print(f"[Slack Webhook] Error handling message: {str(e)}")


async def handle_mention(event: dict):
    try:
        text = event.get("text", "")
        channel = event.get("channel", "general")
        user = event.get("user", "unknown")

        print(f"[Slack Webhook] Mention from {user} in #{channel}: {text}")

        text_lower = text.lower()

        if "standup" in text_lower:
            agent = StandupBotAgent()
            result = agent.generate_async_standup(
                project_name="AI PM Boss",
                sprint_name="Current Sprint",
                developer_updates=[
                    {
                        "name": user,
                        "update": text,
                    }
                ],
            )
            print(f"[Slack Webhook] Standup generated for mention from {user}")

        elif "task" in text_lower or "create" in text_lower:
            agent = TaskCreatorAgent()
            result = agent.create_tasks_from_slack(
                slack_message=text,
                channel=channel,
            )
            print(f"[Slack Webhook] Created {result.get('total_tasks', 0)} tasks from mention")

    except Exception as e:
        print(f"[Slack Webhook] Error handling mention: {str(e)}")


async def send_slack_message(channel: str, message: str):
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "channel": channel,
            "text": message,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers=headers,
                json=payload,
            )
            data = response.json()
            if data.get("ok"):
                print(f"[Slack] Message sent to #{channel}")
            else:
                print(f"[Slack] Error sending message: {data.get('error')}")
    except Exception as e:
        print(f"[Slack] Error: {str(e)}")