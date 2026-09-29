from groq import Groq
from backend.ai.provider import AIProvider
from backend.config import settings

class GroqProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.ai_model
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def generate_chat_response(self, context: str, user_message: str) -> str:
        if not self.client:
            return "AI features are currently unavailable because GROQ_API_KEY is not configured."

        system_prompt = f"""You are a helpful algorithmic trading assistant.
Your job is to explain trading concepts, strategy logic, and portfolio status.
You must NOT place trades, modify settings, or claim certainty about future prices.
Present financial predictions as analysis, not guaranteed facts.
Clearly distinguish the deterministic system data from your own explanations.

CONTEXT:
{context}
"""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"An error occurred while communicating with the AI provider: {str(e)}"
