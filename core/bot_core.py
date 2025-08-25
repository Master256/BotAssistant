from core.plugin_manager import PluginManager
from utils.history import load_history, save_history

try:
    from ai.model_manager import ModelManager
    AI_AVAILABLE = True
except ImportError as e:
    print(f"ИИ модули не доступны: {e}")
    AI_AVAILABLE = False

class BotCore:
    def __init__(self):
        self.plugin_manager = PluginManager(self)
        
        if AI_AVAILABLE:
            self.model_manager = ModelManager()
        else:
            self.model_manager = None
            print("ИИ функционал отключен")
        
        self.history = load_history()
    
    def process_message(self, message: str) -> str:
        """Обрабатывает сообщение и возвращает ответ"""
        self._save_user_message(message)
        
        plugin_response = self.plugin_manager.get_response(message)
        if plugin_response and plugin_response != "Извините, я не понял ваш вопрос. Попробуйте переформулировать.":
            self._save_bot_response(plugin_response)
            return plugin_response
        
        if self.model_manager and self.model_manager.should_use_ai(message):
            ai_response = self.model_manager.get_ai_response(message, self.history)
            if ai_response and ai_response != "Извините, произошла ошибка при генерации ответа.":
                self._save_bot_response(ai_response)
                return ai_response
        
        default_response = "Извините, я не понял ваш вопрос. Попробуйте переформулировать."
        self._save_bot_response(default_response)
        return default_response
    
    def _save_user_message(self, message: str):
        """Сохраняет сообщение пользователя в историю"""
        self.history.append({
            "sender": "You",
            "message": message
        })
        save_history(self.history)
    
    def _save_bot_response(self, response: str):
        """Сохраняет ответ бота в историю"""
        self.history.append({
            "sender": "Bot", 
            "message": response
        })
        save_history(self.history)
    
    def reload_plugins(self):
        """Перезагружает плагины"""
        self.plugin_manager.reload_plugins()
    
    def get_chat_history(self):
        """Возвращает историю чата для отображения"""
        return self.history
    
    def clear_history(self):
        """Очищает историю чата"""
        self.history = []
        save_history(self.history)
        print("История чата очищена")