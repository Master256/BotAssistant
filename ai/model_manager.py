from .llama_client import LlamaClient
import threading

class ModelManager:
    def __init__(self):
        self.llama_client = LlamaClient()
        self.is_ai_enabled = self.llama_client.is_available
    
    def get_ai_response(self, message: str, chat_history: list = None) -> str:
        """Получает ответ от ИИ"""
        if not self.is_ai_enabled:
            return None
        
        if chat_history:
            context = [msg for msg in chat_history if msg['sender'] in ['You', 'Bot']]
        else:
            context = []
        
        return self.llama_client.generate_response(message, context)
    
    def should_use_ai(self, message: str) -> bool:
        """Определяет, нужно ли использовать ИИ для этого сообщения"""
        if not self.is_ai_enabled:
            return False
        
        message_lower = message.lower()
        
        commands = ['погода', 'weather', 'температура', 'прогноз', 'time', 'время']
        if any(cmd in message_lower for cmd in commands):
            return False
        
        question_words = ['как', 'что', 'почему', 'зачем', 'когда', 'где', 'кто']
        if any(message_lower.startswith(word) for word in question_words):
            return True
        
        if len(message.split()) > 3:
            return True
        
        return False