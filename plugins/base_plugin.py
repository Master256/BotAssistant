from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """Базовый класс для всех плагинов"""
    
    def __init__(self, bot_core):
        self.bot = bot_core
        self.name = "base_plugin"
        self.description = "Базовый плагин"
        self.commands = {}
    
    @abstractmethod
    def handle_message(self, message: str) -> str:
        """Обработка сообщения пользователя"""
        pass
    
    def can_handle(self, message: str) -> bool:
        """Проверяет, может ли плагин обработать сообщение"""
        message_lower = message.lower()
        return any(cmd in message_lower for cmd in self.commands.keys())