import aiohttp
from typing import Dict, List, Optional
from app.config import settings
from app.models import ChatMessage

class LLMService:
    def __init__(self):
        self.api_url = settings.OPENROUTER_API_URL
        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

    async def generate_response(
        self,
        message: str,
        context: Optional[List[str]] = None
    ) -> str:
        system_prompt = """You are SolAI, a super friendly AI chatbot created by Solai Rajan. 
        Answer questions about Solai Rajan's portfolio, skills, experience, or have a casual, 
        friendly conversation. Always respond in a warm, helpful, and approachable tone using 
        emojis when appropriate. Only introduce yourself as SolAI if specifically asked about 
        your identity. Use the following context about Solai Rajan to provide accurate and 
        personalized responses."""

        if context:
            system_prompt += "\nContext:\n" + "\n".join(context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        payload = {
            "model": settings.MODEL_NAME,
            "messages": messages,
            "max_tokens": settings.MAX_TOKENS,
            "temperature": settings.TEMPERATURE
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_data = await response.text()
                        raise Exception(f"API Error: {error_data}")
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
