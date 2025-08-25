from plugins.base_plugin import BasePlugin

class ExamplePlugin(BasePlugin):
    def __init__(self, bot_core):
        super().__init__(bot_core)
        self.name = "example"
        self.description = "Пример плагина"
        self.commands = {
            "привет": "поприветствовать",
            "hello": "say hello",
            "как дела": "спросить как дела"
        }
    
    def handle_message(self, message: str) -> str:
        message_lower = message.lower()
        
        if "привет" in message_lower or "hello" in message_lower:
            return "Привет! Как у вас дела?"
        
        if "как дела" in message_lower:
            return "У меня всё отлично! Спасибо, что спросили!"
        
        return ""