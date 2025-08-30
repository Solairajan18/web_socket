from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime

from app.config import settings
from app.models import ChatMessage, WebSocketMessage, PersonalDetail, ChatResponse
from app.database import DatabaseService
from app.llm_service import LLMService

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
db_service = DatabaseService()
llm_service = LLMService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Send typing indicator
            await manager.send_personal_message(
                json.dumps({
                    "type": "typing",
                    "content": "SolAI is thinking... 🤔",
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )

            # Search for relevant context
            context_results = await db_service.search_context(message_data["content"])
            context = [result["content"] for result in context_results]

            # Generate response
            response = await llm_service.generate_response(message_data["content"], context)

            # Send response
            await manager.send_personal_message(
                json.dumps({
                    "type": "bot_response",
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                    "context": context
                }),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "content": str(e),
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )

# REST endpoints
@app.post("/api/details")
async def add_details(detail: PersonalDetail):
    success = await db_service.add_personal_detail(detail)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add personal detail")
    return {"status": "success"}

@app.get("/api/details")
async def get_details():
    details = await db_service.get_all_details()
    return {"details": details}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
