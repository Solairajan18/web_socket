from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()

class WebSocketMessage(BaseModel):
    type: str  # user_message, bot_response, typing, error
    content: str
    timestamp: datetime = datetime.now()

class PersonalDetail(BaseModel):
    category: str
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()

class ChatResponse(BaseModel):
    message: str
    context: Optional[List[str]] = None
    metadata: Dict[str, Any] = {}
