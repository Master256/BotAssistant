from plugins.base_plugin import BasePlugin
import requests
import urllib.parse

class WeatherPlugin(BasePlugin):
    def __init__(self, bot_core):
        super().__init__(bot_core)
        self.name = "weather"
        self.description = "Плагин для получения погоды"
        self.commands = {
            "погода": "узнать погоду в указанном городе",
            "weather": "get weather in specified city",
            "температура": "текущая температура",
            "прогноз": "прогноз погоды"
        }
        
        self.api_key = "80498edbf70565f402d9b78acb737bfa"
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city_name):
        """Получает погоду для указанного города"""
        if not self.api_key or self.api_key == "ваш_настоящий_api_ключ_здесь":
            return "❌ API ключ не настроен. Получите ключ на openweathermap.org"
        
        try:
            params = {
                'q': city_name,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ru'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 401:
                return "❌ Неверный API ключ. Проверьте ключ на openweathermap.org"
            elif response.status_code == 404:
                return f"❌ Город '{city_name}' не найден."
            
            response.raise_for_status()
            
            data = response.json()
            
            temperature = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            city = data['name']
            country = data['sys']['country']
            
            return (f"Погода в {city}, {country}:\n"
                   f"🌡 Температура: {temperature}°C (ощущается как {feels_like}°C)\n"
                   f"📝 Описание: {description.capitalize()}\n"
                   f"💧 Влажность: {humidity}%")
            
        except requests.exceptions.RequestException as e:
            return f"Ошибка подключения: {e}"
        except Exception as e:
            return f"Произошла ошибка: {e}"
    
    def extract_city(self, message):
        """Извлекает название города из сообщения"""
        for cmd in self.commands.keys():
            message = message.lower().replace(cmd, '').strip()
        
        if not message:
            return "Москва"
        
        return message.strip()
    
    def handle_message(self, message: str) -> str:
        message_lower = message.lower()
        
        if any(cmd in message_lower for cmd in self.commands.keys()):
            city = self.extract_city(message)
            return self.get_weather(city)
        
        return ""