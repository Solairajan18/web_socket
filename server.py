#!/usr/bin/env python3
"""
WebSocket chatbot server using OpenRouter/OpenAI to answer questions about skills, experience, and projects.
No database persistence.
"""

import os
import asyncio
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from openai import OpenAI
# from dotenv import load_dotenv

# -------------------------
# Config & logging
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("solai-ws")
# load_dotenv()

OPENROUTER_API_URL = os.environ.get("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "openai/gpt-oss-20b:free")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8765))
HISTORY_DIR = Path("./session_history")
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

sessions: Dict[str, List[Dict[str, Any]]] = {}
client = OpenAI(base_url=OPENROUTER_API_URL, api_key=OPENROUTER_API_KEY)

# -------------------------
# Session JSON helpers
# -------------------------
def session_json_path(session_id: str) -> Path:
    return HISTORY_DIR / f"session_{session_id}.json"

def persist_session_history(session_id: str):
    try:
        data = sessions.get(session_id, [])
        with session_json_path(session_id).open("w", encoding="utf-8") as f:
            json.dump({"session_id": session_id, "history": data}, f, ensure_ascii=False, indent=2)
        logger.info("Persisted session %s", session_id)
    except Exception:
        logger.exception("Failed to persist session %s", session_id)

def load_session_history(session_id: str):
    p = session_json_path(session_id)
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8") as f:
            obj = json.load(f)
            return obj.get("history", [])
    except Exception:
        logger.exception("Failed to load session history %s", session_id)
        return []

# -------------------------
# Bot persona
# -------------------------
DEFAULT_PERSONA = {
    "name": "SolAI Chat Bot",
    "system_prompt": (
        "You are SolAI chatbot — friendly, concise, and helpful. "
        "You answer questions about the user's skills, experience, and projects. "
        "Respond in plain text."
    )
}

PERSONA = DEFAULT_PERSONA

# -------------------------
# OpenRouter call
# -------------------------
async def call_openrouter(messages: list) -> str:
    loop = asyncio.get_running_loop()

    def _sync_call():
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            extra_headers={"HTTP-Referer": "http://localhost:8000"},
            max_tokens=512,
            temperature=0.4
        )
        return completion.choices[0].message.content

    return await loop.run_in_executor(None, _sync_call)

# -------------------------
# WebSocket handlers
# -------------------------
async def handle_chat_message(raw: str, websocket) -> None:
    try:
        obj = json.loads(raw)
        user_text = obj.get("message", "").strip()
        if not user_text:
            await websocket.send(json.dumps({"ok": False, "error": "empty message"}))
            return

        session_id = obj.get("session_id") or str(uuid.uuid4())
        sessions.setdefault(session_id, load_session_history(session_id) or [])

        # append user message
        user_entry = {"role": "user", "content": user_text, "ts": datetime.now(timezone.utc).isoformat()}
        sessions[session_id].append(user_entry)

        # model messages
        recent = sessions[session_id][-12:]
        model_messages = [{"role": "system", "content": PERSONA.get("system_prompt", "")}]
        for m in recent:
            if m["role"] in ("user", "assistant"):
                model_messages.append({"role": m["role"], "content": m["content"]})

        logger.info("Calling OpenRouter for session %s ...", session_id)
        assistant_text = await call_openrouter(model_messages)
        assistant_text = assistant_text.strip() or "Sorry, I couldn't generate a response."

        # append assistant reply
        bot_entry = {"role": "assistant", "content": assistant_text, "ts": datetime.now(timezone.utc).isoformat()}
        sessions[session_id].append(bot_entry)
        persist_session_history(session_id)

        # send response first
        response = {
            "ok": True,
            "session_id": session_id,
            "message": assistant_text,
            "role": "assistant",
            "ts": datetime.now(timezone.utc).isoformat()
        }

        try:
            await websocket.send(json.dumps(response))
        except (ConnectionClosedOK, ConnectionClosedError):
            logger.info("Client disconnected before message could be sent")

    except json.JSONDecodeError:
        await websocket.send(json.dumps({"ok": False, "error": "invalid json"}))
    except Exception as e:
        logger.exception("Error in handle_chat_message: %s", e)
        try:
            await websocket.send(json.dumps({"ok": False, "error": str(e)}))
        except (ConnectionClosedOK, ConnectionClosedError):
            logger.info("Client disconnected before error could be sent")


async def ws_handler(websocket):
    logger.info("Client connected: %s", websocket.remote_address)
    try:
        async for raw in websocket:
            try:
                incoming = json.loads(raw)
            except Exception:
                incoming = {"message": raw}

            if incoming.get("cmd") == "history":
                sid = incoming.get("session_id")
                if not sid:
                    await websocket.send(json.dumps({"ok": False, "error": "session_id required for history"}))
                    continue
                history = load_session_history(sid)
                await websocket.send(json.dumps({"ok": True, "session_id": sid, "history": history}))
                continue

            await handle_chat_message(json.dumps(incoming), websocket)

    except (ConnectionClosedOK, ConnectionClosedError):
        logger.info("Client disconnected: %s", websocket.remote_address)
    except Exception:
        logger.exception("Unexpected WS error")

# -------------------------
# Server startup
# -------------------------
async def main():
    logger.info("Starting SolAI WebSocket server on %s:%s", HOST, PORT)
    async with websockets.serve(ws_handler, HOST, PORT, ping_interval=20, ping_timeout=20, max_queue=32):
        logger.info("WebSocket server running.")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down by KeyboardInterrupt...")
