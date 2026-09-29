from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def generate_chat_response(self, context: str, user_message: str) -> str:
        pass
