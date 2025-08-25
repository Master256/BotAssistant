import importlib
import os
from pathlib import Path

class PluginManager:
    def __init__(self, bot_core):
        self.bot = bot_core
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """Загружает все плагины из папки plugins"""
        plugins_dir = Path("plugins")
        for file in plugins_dir.glob("*.py"):
            if file.name != "__init__.py" and file.name != "base_plugin.py":
                try:
                    module_name = f"plugins.{file.stem}"
                    module = importlib.import_module(module_name)
                    
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            attr.__module__ == module_name and
                            hasattr(attr, 'handle_message')):
                            
                            plugin_instance = attr(self.bot)
                            self.plugins[plugin_instance.name] = plugin_instance
                            print(f"Загружен плагин: {plugin_instance.name}")
                            
                except Exception as e:
                    print(f"Ошибка загрузки плагина {file.name}: {e}")
    
    def get_response(self, message: str) -> str:
        """Получает ответ от подходящего плагина"""
        for plugin_name, plugin in self.plugins.items():
            if plugin.can_handle(message):
                response = plugin.handle_message(message)
                if response:
                    return response
        
        return "Извините, я не понял ваш вопрос. Попробуйте переформулировать."
    
    def reload_plugins(self):
        """Перезагружает все плагины"""
        self.plugins = {}
        self.load_plugins()