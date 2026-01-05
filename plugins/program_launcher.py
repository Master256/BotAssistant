import subprocess
import os
import platform
from plugins.base_plugin import BasePlugin

class ProgramLauncherPlugin(BasePlugin):
    def __init__(self, bot_core):
        super().__init__(bot_core)
        self.name = "program_launcher"
        self.description = "Запуск программ и приложений на компьютере"
        self.commands = {
            "запусти": "Запустить программу. Использование: запусти [название программы]",
            "открой": "Открыть файл или папку. Использование: открой [путь к файлу]",
            "выполни команду": "Выполнить системную команду",
            "какая система": "Показать информацию о операционной системе"
        }
        
        self.program_paths = {
            'windows': {
                'блокнот': 'notepad.exe',
                'калькулятор': 'calc.exe',
                'браузер': 'start chrome.exe',
                'проводник': 'explorer.exe',
                'панель управления': 'control.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe'
            },
        }
    
    def can_handle(self, message: str) -> bool:
        message_lower = message.lower()
        return any(message_lower.startswith(cmd) for cmd in self.commands.keys())
    
    def handle_message(self, message: str) -> str:
        message_lower = message.lower()
        
        if message_lower.startswith("запусти"):
            program_name = message[7:].strip()
            return self.launch_program(program_name)
            
        elif message_lower.startswith("открой"):
            path = message[6:].strip()
            return self.open_path(path)
            
        elif message_lower.startswith("выполни команду"):
            command = message[15:].strip()
            return self.execute_command(command)
            
        elif message_lower.startswith("какая система"):
            return self.get_system_info()
            
        return "Не понимаю команду. Используй: запусти, открой, выполни команду"
    
    def launch_program(self, program_name: str) -> str:
        """Запуск программы по имени"""
        try:
            system = platform.system().lower()
            
            if program_name.lower() in self.program_paths.get(system, {}):
                program_cmd = self.program_paths[system][program_name.lower()]
                subprocess.Popen(program_cmd, shell=True)
                return f"Запускаю {program_name}..."
            
            subprocess.Popen(program_name, shell=True)
            return f"Пытаюсь запустить: {program_name}"
            
        except Exception as e:
            return f"Ошибка при запуске: {str(e)}"
    
    def open_path(self, path: str) -> str:
        """Открытие файла или папки"""
        try:
            if not os.path.exists(path):
                return f"Путь не существует: {path}"
            
            if os.path.isfile(path):

                os.startfile(path) if platform.system() == 'Windows' else subprocess.Popen(['xdg-open', path])
            elif os.path.isdir(path):

                subprocess.Popen(f'explorer "{path}"' if platform.system() == 'Windows' else ['nautilus', path])
            
            return f"Открываю: {path}"
            
        except Exception as e:
            return f"Ошибка при открытии: {str(e)}"
    
    def execute_command(self, command: str) -> str:
        """Выполнение системной команды"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout if result.stdout else "Команда выполнена успешно"
                return f"Результат:\n{output[:500]}"
            else:
                return f"Ошибка выполнения:\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Команда выполнялась слишком долго (таймаут 30с)"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def get_system_info(self) -> str:
        """Информация о системе"""
        try:
            system = platform.system()
            release = platform.release()
            version = platform.version()
            
            info += f"Версия: {release}\n"
            info += f"Сборка: {version}\n"
            
            if system == "Windows":
                info += f"Процессор: {platform.processor()}\n"
            
            return info
            
        except Exception as e:
            return f"Не удалось получить информацию: {str(e)}"