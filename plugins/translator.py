from translate import Translator
from plugins.base_plugin import BasePlugin

class TranslatorPlugin(BasePlugin):
    def __init__(self, bot_core):
        super().__init__(bot_core)
        self.name = "translator"
        self.description = "Перевод текста между языками (локальный)"
        self.commands = {
            "переведи": "Перевести текст. Использование: переведи [текст]",
            "перевод": "Перевести текст"
        }
        
    def can_handle(self, message: str) -> bool:
        message_lower = message.lower()
        return any(message_lower.startswith(cmd) for cmd in self.commands.keys())
    
    def handle_message(self, message: str) -> str:
        message_lower = message.lower()
        
        if message_lower.startswith("переведи") or message_lower.startswith("перевод"):
            text = message[8:].strip() if message_lower.startswith("переведи") else message[7:].strip()
            return self.local_translate(text)
            
        return ""
    
    def local_translate(self, text: str) -> str:
        """Локальный перевод без API"""
        try:
            if not text:
                return "Укажите текст для перевода"
            
            if len(text) > 500:
                return "Текст слишком длинный (максимум 500 символов)"
            
            first_word = text.split()[0].lower() if text.split() else ""
            
            if any(char in 'abcdefghijklmnopqrstuvwxyz' for char in first_word):
                translator = Translator(from_lang="english", to_lang="russian")
                result = translator.translate(text)
                return f"Английский → Русский:\n{result}"
            else:
                translator = Translator(from_lang="russian", to_lang="english")
                result = translator.translate(text)
                return f"Русский → Английский:\n{result}"
                
        except Exception as e:
            return f"Ошибка перевода: {str(e)}"