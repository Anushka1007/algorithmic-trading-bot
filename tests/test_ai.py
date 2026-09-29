import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.routers.ai import get_ai_provider
from backend.ai.provider import AIProvider

class MockAIProvider(AIProvider):
    def generate_chat_response(self, context: str, user_message: str) -> str:
        if not context:
            return "No context provided."
        return "Mock response: " + user_message

def override_get_ai_provider():
    return MockAIProvider()

app.dependency_overrides[get_ai_provider] = override_get_ai_provider
client = TestClient(app)

def test_ai_chat_no_symbol():
    response = client.post("/api/ai/chat", json={"message": "What is my portfolio value?"})
    assert response.status_code == 200
    assert "Mock response: What is my portfolio value?" in response.json()["reply"]

def test_ai_chat_with_symbol():
    # Might fail inside generate_signal if DB/history is missing, but the router catches it
    # and appends an error to context rather than throwing HTTP 500, so we get 200.
    response = client.post("/api/ai/chat", json={"message": "Explain the AAPL signal", "symbol": "AAPL"})
    assert response.status_code == 200
    assert "Mock response: Explain the AAPL signal" in response.json()["reply"]
