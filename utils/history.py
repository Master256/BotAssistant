import json
import os
from datetime import datetime

HISTORY_FILE = "chat_history.json"

def load_history():
    """Загружает историю чата из файла"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as file:
                history = json.load(file)
                
                for item in history:
                    if 'timestamp' not in item:
                        item['timestamp'] = datetime.now().isoformat()
                
                return history
                
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            return []
    return []

def save_history(history):
    """Сохраняет историю чата в файл"""
    try:
        for item in history:
            if 'timestamp' not in item:
                item['timestamp'] = datetime.now().isoformat()
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as file:
            json.dump(history, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")

def get_history_stats():
    """Возвращает статистику истории"""
    history = load_history()
    user_messages = len([m for m in history if m['sender'] == 'You'])
    bot_messages = len([m for m in history if m['sender'] == 'Bot'])
    
    return {
        'total_messages': len(history),
        'user_messages': user_messages,
        'bot_messages': bot_messages,
        'last_updated': datetime.now().isoformat()
    }