#!/usr/bin/env python3
"""
WebSocket chatbot server using OpenRouter/OpenAI to answer questions about skills, experience, and projects.
Includes fuzzy matching for knowledge-base responses.
No database persistence.
"""

import os
import asyncio
import json
import uuid
import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import difflib

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
# Knowledge Base
# -------------------------
KNOWLEDGE_BASE = {
    "hi": [
        "👋 Hey there! Welcome to my portfolio. How can I assist you?",
        "😊 Hello! Feel free to ask me about my experience, skills, or projects.",
    ],
    "hello": [
        "👋 Hello! I'm Solai, an AWS Cloud Engineer. How can I help you today?",
    ],
    "who are you": [
        "🧑‍💻 I'm Solai, an AWS Cloud Engineer with expertise in Terraform, Python, and cloud automation.",
    ],
    "experience": [
        "💼 I have over five years of experience in the IT industry, focusing on cloud engineering and automation with AWS, Terraform, Python, Pytest, BDD testing, and GitLab CI/CD.",
    ],
    "skills": [
        "🛠️ My key skills include AWS, Terraform, Python, GitLab CI/CD, BDD, Pytest, and cloud automation."
    ],
    "projects": [
        "📂 I worked on mainframe-to-AWS modernization, DB2 to DynamoDB migration, and developed high-availability APIs. You can also check out my projects on my portfolio website: [https://solairajan.online/](https://solairajan.online/)"
    ],
    "contact": [
        "📬 You can reach me via my website: [https://solairajan.online/](https://solairajan.online/), LinkedIn: [https://www.linkedin.com/in/solai-rajan/](https://www.linkedin.com/in/solai-rajan/), email: [solai13kamaraj@gmail.com](mailto:solai13kamaraj@gmail.com), and GitHub: [https://github.com/Solairajan18](https://github.com/Solairajan18)"
    ],
}

def check_knowledge_base(user_text: str) -> str:
    """
    Check the knowledge base for an exact or fuzzy match.
    Returns a random response or None if not found.
    """
    user_text_lower = user_text.lower()

    # 1. Exact substring match
    for key, responses in KNOWLEDGE_BASE.items():
        if key in user_text_lower:
            return random.choice(responses)

    # 2. Fuzzy match using difflib
    match = difflib.get_close_matches(user_text_lower, KNOWLEDGE_BASE.keys(), n=1, cutoff=0.6)
    if match:
        return random.choice(KNOWLEDGE_BASE[match[0]])

    # 3. Not found
    return None

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
        "You are SolAI, a super friendly AI chatbot created by Solai Rajan. Here's your core knowledge:\n\n"
        "ABOUT SOLAI:\n"
        "- AWS Cloud Engineer with 5+ years of IT industry experience\n"
        "- Expertise: AWS, Terraform, Python, GitLab CI/CD, BDD testing, cloud automation\n"
        "- BSc graduate with strong foundation in cloud computing and DevOps\n"
        "- Certified: AWS Solution Architect Associate, Microsoft Azure Fundamentals\n\n"
        "KEY PROJECTS:\n"
        "- Mainframe-to-AWS modernization\n"
        "- DB2 to DynamoDB migration\n"
        "- High-availability API development\n\n"
        "CONTACT INFO:\n"
        "- Portfolio: https://solairajan.online/\n"
        "- LinkedIn: https://www.linkedin.com/in/solai-rajan/\n"
        "- GitHub: https://github.com/Solairajan18\n"
        "- Email: solai13kamaraj@gmail.com\n\n"
        "PERSONALITY:\n"
        "- Always maintain a friendly, professional tone\n"
        "- Use emojis occasionally to keep responses engaging\n"
        "- Keep responses focused on Solai's professional experience and skills\n"
        "- For technical questions, provide specific details from Solai's experience\n"
        "- For casual chat, stay friendly while gently steering back to professional topics\n\n"
        "Remember: You're here to showcase Solai's professional experience and skills while maintaining engaging conversation."
    )
}

PERSONA = DEFAULT_PERSONA

# -------------------------
# OpenRouter call
# -------------------------
async def call_openrouter(messages: list) -> str:
    loop = asyncio.get_running_loop()

    def _sync_call():
        # Add instruction to format response in Markdown
        messages_with_format = messages.copy()
        messages_with_format[0]["content"] += "\nAlways respond in Markdown format with emojis where appropriate. Keep responses focused and professional."
        
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages_with_format,
            extra_headers={"HTTP-Referer": "http://localhost:8000"},
            max_tokens=512,
            temperature=0.4
        )
        response = completion.choices[0].message.content
        
        # Ensure response starts with an emoji if it doesn't already
        if not any(emoji in response[:2] for emoji in ["👋", "🤖", "💼", "🛠️", "📂", "🎓", "⚡", "🌟"]):
            response = "🤖 " + response
            
        return response

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

        # 1. Try LLM first
        try:
            recent = sessions[session_id][-12:]
            model_messages = [{"role": "system", "content": PERSONA.get("system_prompt", "")}]
            for m in recent:
                if m["role"] in ("user", "assistant"):
                    model_messages.append({"role": m["role"], "content": m["content"]})

            logger.info("Calling OpenRouter for session %s ...", session_id)
            assistant_text = await call_openrouter(model_messages)
            assistant_text = assistant_text.strip()
            
            if not assistant_text:
                raise Exception("Empty response from LLM")
                
        except Exception as e:
            logger.warning(f"LLM call failed, falling back to knowledge base: {str(e)}")
            # 2. Fallback to knowledge base if LLM fails
            kb_response = check_knowledge_base(user_text)
            if not kb_response:
                # Format the error message in the same style as rest_api.py
                assistant_text = "❌ I apologize, but I'm having trouble at the moment. Try asking about my skills, experience, or projects!"
            else:
                assistant_text = kb_response

        # append assistant reply
        bot_entry = {"role": "assistant", "content": assistant_text, "ts": datetime.now(timezone.utc).isoformat()}
        sessions[session_id].append(bot_entry)
        persist_session_history(session_id)

        # send response
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
