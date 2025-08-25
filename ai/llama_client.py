import ollama
import threading
import queue
import time
from typing import Optional

class LlamaClient:
    def __init__(self):
        self.model_name = "llama3:8b-instruct-q4_0"
        self.is_available = False
        self.response_queue = queue.Queue()
        self.check_availability()
    
    def check_availability(self):
        """Проверяет доступность Ollama и модели"""
        try:
            models_response = ollama.list()
            print(f"Ответ от ollama.list(): {models_response}")
            
            model_names = []
            
            if hasattr(models_response, 'models'):
                for model in models_response.models:
                    if hasattr(model, 'name'):
                        model_names.append(model.name)
                    elif hasattr(model, 'model'):
                        model_names.append(model.model)
            elif isinstance(models_response, dict):
                if 'models' in models_response:
                    for model in models_response['models']:
                        if isinstance(model, dict) and 'name' in model:
                            model_names.append(model['name'])
                        elif isinstance(model, str):
                            model_names.append(model)
            else:
                try:
                    for model in models_response:
                        if hasattr(model, 'name'):
                            model_names.append(model.name)
                        elif isinstance(model, dict) and 'name' in model:
                            model_names.append(model['name'])
                        elif isinstance(model, str):
                            model_names.append(model)
                except:
                    pass
            
            print(f"Найдены модели: {model_names}")
            
            if self.model_name in model_names:
                self.is_available = True
                print(f"✅ Модель {self.model_name} доступна")
            else:
                print(f"❌ Модель {self.model_name} не найдена")
                print(f"💡 Доступные модели: {model_names}")
                print("📥 Попробуйте: ollama pull llama3:8b-instruct-q4_0")
                
        except Exception as e:
            print(f"❌ Ошибка при проверке моделей: {e}")
            print("🔧 Убедитесь, что Ollama запущен: ollama serve")
            self.is_available = False
    
    def debug_models(self):
        """Функция для отладки структуры ответа"""
        try:
            models = ollama.list()
            print("=== ДЕБАГ СТРУКТУРЫ ===")
            print(f"Тип ответа: {type(models)}")
            print(f"Содержимое: {models}")
            
            if hasattr(models, '__dict__'):
                print("Атрибуты объекта:", models.__dict__)
            
            print("Попытка 1: direct iteration")
            try:
                for item in models:
                    print(f"  Item: {item}, type: {type(item)}")
            except Exception as e:
                print(f"  Ошибка итерации: {e}")
            
            print("Попытка 2: как словарь")
            try:
                if hasattr(models, 'models'):
                    print(f"  models attribute: {models.models}")
            except Exception as e:
                print(f"  Ошибка доступа к атрибуту: {e}")
                
        except Exception as e:
            print(f"Ошибка отладки: {e}")
    
    def generate_response(self, message: str, context: list = None) -> str:
        """Генерирует ответ с помощью Llama 3"""
        if not self.is_available:
            return "ИИ модель временно недоступна."
        
        try:
            prompt = self._create_prompt(message, context)
            
            start_time = time.time()
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 256
                }
            )
            
            content = self._extract_response_content(response)
            
            response_time = time.time() - start_time
            print(f"⏱ Время ответа ИИ: {response_time:.2f} сек")
            
            return content.strip()
            
        except Exception as e:
            print(f"❌ Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка при генерации ответа."
    
    def _extract_response_content(self, response):
        """Универсальный способ извлечения контента из ответа"""
        try:
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                return response.message.content
            elif hasattr(response, 'message') and isinstance(response.message, dict):
                return response.message.get('content', '')
            elif isinstance(response, dict) and 'message' in response:
                message = response['message']
                if isinstance(message, dict) and 'content' in message:
                    return message['content']
                elif hasattr(message, 'content'):
                    return message.content
            elif hasattr(response, 'content'):
                return response.content
            
            return str(response)
            
        except Exception as e:
            print(f"Ошибка извлечения контента: {e}")
            return "Не удалось обработать ответ модели"
    
    def _create_prompt(self, message: str, context: list = None) -> str:
        """Создает промпт для модели"""
        base_prompt = """Ты - полезный AI ассистент. Отвечай кратко на русском языке.

Правила:
- Будь вежливым и полезным
- Отвечай 1-2 предложениями
- Если вопрос непонятен, уточни
- Не выдумывай информацию

"""
        
        if context:
            context_str = "\nПредыдущий разговор:\n"
            for msg in context[-2:]:
                sender = "Человек" if msg['sender'] == 'You' else "Ты"
                context_str += f"{sender}: {msg['message']}\n"
            base_prompt += context_str
        
        base_prompt += f"\nЧеловек: {message}\nТы:"
        return base_prompt
    
    def generate_async(self, message: str, context: list, callback):
        """Асинхронная генерация ответа"""
        def generate():
            response = self.generate_response(message, context)
            callback(response)
        
        threading.Thread(target=generate, daemon=True).start()