import os
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from plugins.base_plugin import BasePlugin

class EncryptionPlugin(BasePlugin):
    def __init__(self, bot_core):
        super().__init__(bot_core)
        self.name = "encryption"
        self.description = "Шифрование и дешифрование данных бота (AES-256)"
        self.commands = {
            "зашифруй данные": "Зашифровать файл с историей чатов",
            "расшифруй данные": "Расшифровать файл с историей чатов",
            "сгенерируй ключ": "Сгенерировать новый AES-ключ"
        }
        
        self.key_file = "secret.key"
        self.chat_file = "chat_history.json"
        self.encrypted_file = "chats.encrypted"

    def handle_message(self, message: str) -> str:
        message_lower = message.lower()
        
        if message_lower == "сгенерируй ключ":
            return self.generate_key()
            
        elif message_lower == "зашифруй данные":
            return self.encrypt_data()
            
        elif message_lower == "расшифруй данные":
            return self.decrypt_data()
            
        return ""

    def generate_key(self) -> str:
        """Генерация нового AES-ключа (256 бит)"""
        try:
            key = get_random_bytes(32)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return "Ключ успешно сгенерирован и сохранен в файле 'secret.key'! НИКОМУ НЕ ПОКАЗЫВАЙТЕ ЭТОТ ФАЙЛ."
        except Exception as e:
            return f"Ошибка при генерации ключа: {str(e)}"

    def load_key(self) -> bytes:
        """Загрузка ключа из файла"""
        try:
            with open(self.key_file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return b''

    def encrypt_data(self) -> str:
        """Шифрование данных чата"""
        try:
            key = self.load_key()
            if not key:
                return "Ключ не найден! Сначала выполните 'сгенерируй ключ'."

            if not os.path.exists(self.chat_file):
                return "Файл с историей чатов не найден."
            
            with open(self.chat_file, 'r', encoding='utf-8') as f:
                data = f.read()

            cipher = AES.new(key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))

            iv = base64.b64encode(cipher.iv).decode('utf-8')
            ct = base64.b64encode(ct_bytes).decode('utf-8')
            result = json.dumps({'iv': iv, 'ciphertext': ct})

            with open(self.encrypted_file, 'w') as f:
                f.write(result)

            return f"Данные успешно зашифрованы и сохранены в '{self.encrypted_file}'!"
        
            os.remove(self.chat_file)
            
        except Exception as e:
            return f"Ошибка при шифровании: {str(e)}"

    def decrypt_data(self) -> str:
        """Дешифрование данных чата"""
        try:
            key = self.load_key()
            if not key:
                return "Ключ не найден!"

            if not os.path.exists(self.encrypted_file):
                return "Зашифрованный файл не найден."

            with open(self.encrypted_file, 'r') as f:
                data = json.load(f)

            iv = base64.b64decode(data['iv'])
            ct = base64.b64decode(data['ciphertext'])

            cipher = AES.new(key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')

            with open(self.chat_file, 'w', encoding='utf-8') as f:
                f.write(pt)

            return "Данные успешно расшифрованы! История чатов восстановлена."
            
        except Exception as e:
            return f"Ошибка при дешифровке: {str(e)}. Проверьте ключ."