import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from plugins.base_plugin import BasePlugin

class FileSearchPlugin(BasePlugin):
    def __init__(self, bot_core):
        super().__init__(bot_core)
        self.name = "file_search"
        self.description = "Поиск по содержимому файлов на компьютере (индексирование и поиск)"
        self.commands = {
            "проиндексируй": "Создать/обновить индекс для поиска по файлам",
            "найди": "Поиск файлов по содержимому",
            "где файлы": "Показать проиндексированные файлы",
            "очисти индекс": "Удалить индекс поиска"
        }
        
        self.index_dir = "search_index"
        self.default_search_path = "C:/Users/George/Documents"
        
    def handle_message(self, message: str) -> str:
        message_lower = message.lower()
        
        if any(cmd in message_lower for cmd in ["проиндексируй", "создай индекс", "обнови индекс"]):
            return self.create_index()
            
        elif any(cmd in message_lower for cmd in ["найди", "поищи", "ищи"]):

            query = self.extract_query(message, ["найди", "поищи", "ищи"])
            if query:
                return self.search_files(query)
            else:
                return "Укажите, что искать. Например: 'найди отчет' или 'поищи договор'"
                
        elif any(cmd in message_lower for cmd in ["где файлы", "список файлов", "что проиндексировано"]):
            return self.list_indexed_files()
            
        elif any(cmd in message_lower for cmd in ["очисти индекс", "удали индекс", "сбрось индекс"]):
            return self.clear_index()
            
        return ""

    def extract_query(self, message: str, commands: list) -> str:
        """Извлекает поисковый запрос из сообщения"""
        message_lower = message.lower()
        for cmd in commands:
            if cmd in message_lower:
                return message[message_lower.find(cmd) + len(cmd):].strip()
        return message.strip()

    def create_index(self) -> str:
        """Создание индекса для поиска"""
        try:
            schema = Schema(
                path=ID(stored=True, unique=True),
                filename=TEXT(stored=True),
                content=TEXT
            )
            
            if not os.path.exists(self.index_dir):
                os.makedirs(self.index_dir)
            
            ix = index.create_in(self.index_dir, schema)
            
            file_list = self.get_files_list(self.default_search_path)
            
            if not file_list:
                return "❌ Файлы для индексации не найдены!"
            
            writer = ix.writer()
            indexed_count = 0
            
            for file_path in file_list:
                try:
                    if file_path.endswith(('.txt', '.py', '.js', '.html', '.css', '.md', '.csv')):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        writer.add_document(
                            path=file_path,
                            filename=os.path.basename(file_path),
                            content=content
                        )
                        indexed_count += 1
                        
                except Exception as e:
                    continue
            
            writer.commit()
            
            return f"Индекс создан! Проиндексировано файлов: {indexed_count}\n" \
                   f"Папка индекса: {self.index_dir}\n" \
                   f"Теперь можно искать: 'найди [ваш запрос]'"
                   
        except Exception as e:
            return f"Ошибка при создании индекса: {str(e)}"

    def get_files_list(self, directory: str) -> list:
        """Получает список всех файлов в директории"""
        file_list = []
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    full_path = os.path.join(root, file)
                    file_list.append(full_path)
        except Exception as e:
            pass
        return file_list

    def search_files(self, query: str) -> str:
        """Поиск файлов по содержимому"""
        try:
            if not index.exists_in(self.index_dir):
                return "Индекс не найден! Сначала выполните: 'проиндексируй'"
            
            ix = index.open_dir(self.index_dir)
            
            with ix.searcher() as searcher:
                query_parser = QueryParser("content", ix.schema)
                parsed_query = query_parser.parse(query)
                
                results = searcher.search(parsed_query, limit=10)
                
                if len(results) == 0:
                    return f"По запросу '{query}' ничего не найдено"
                
                response = f"Найдено по запросу '{query}': {len(results)} результатов\n\n"
                
                for i, hit in enumerate(results, 1):
                    response += f"{i}.  {hit['filename']}\n"
                    response += f"    {hit['path']}\n"
                    response += "\n"
                
                return response
                
        except Exception as e:
            return f"Ошибка при поиске: {str(e)}"

    def list_indexed_files(self) -> str:
        """Показывает список проиндексированных файлов"""
        try:
            if not index.exists_in(self.index_dir):
                return "Индекс не найден!"
            
            ix = index.open_dir(self.index_dir)
            
            with ix.searcher() as searcher:

                all_docs = list(searcher.documents())
                
                if not all_docs:
                    return "В индексе нет файлов"
                
                response = "Проиндексированные файлы:\n\n"
                
                for i, doc in enumerate(all_docs, 1):
                    response += f"{i}. {doc['filename']}\n"
                    response += f"   {doc['path']}\n"
                    
                    if i >= 20:
                        response += f"\n... и еще {len(all_docs) - 20} файлов"
                        break
                    response += "\n"
                
                return response
                
        except Exception as e:
            return f"Ошибка: {str(e)}"

    def clear_index(self) -> str:
        """Очистка индекса"""
        try:
            import shutil
            if os.path.exists(self.index_dir):
                shutil.rmtree(self.index_dir)
                return "Индекс успешно очищен!"
            else:
                return "ℹИндекс уже очищен или не существует"
        except Exception as e:
            return f"Ошибка при очистке индекса: {str(e)}"